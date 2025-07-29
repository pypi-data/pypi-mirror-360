from __future__ import annotations
import sys
import os
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Iterable, NamedTuple, Optional, TypeIs, TypeVar
from enum import Flag, auto

import torch
import torch.linalg

from torch import Tensor, tensor, dtype
from torch._prims_common import DeviceLikeType

from tqdm import tqdm

from .utils import skip_outside_pytest


# Recommended Chunk limit 128-256 MiB
# Recommended Buffer limit 1-2 GiB
# Recommended VRAM % limit 60-90%
# Based on RTX 3080 with 10Gb VRAM
@dataclass(frozen=True)
class MemoryLimits:
    MAX_VRAM_PERCENT: float = 0.8  # 80%
    MAX_FLUSH: int = 128 * 1024**2  # 128 MiB
    MAX_BUFFER: int = 1 * 1024**3  # 1 GiB (8 flushes)


class QSR(NamedTuple):
    Q: Tensor
    S: Tensor
    R: Tensor


class ISVD_QSR(NamedTuple):
    qsr: QSR
    buffer: VectorBuffer
    q0: Tensor
    W: Optional[Tensor]
    max_rank: Optional[int]
    tol: Optional[float]
    dtype: Optional[torch.dtype]
    device: Optional[DeviceLikeType]


class VectorBuffer:
    @dataclass(frozen=True)
    class BufferLimits:
        CHUNK_SIZE: int
        BUFFER_SIZE: int

    __LIMITS: BufferLimits

    @property
    def CHUNK_SIZE(self: VectorBuffer) -> int:
        return self.__LIMITS.CHUNK_SIZE

    @property
    def BUFFER_SIZE(self: VectorBuffer) -> int:
        return self.__LIMITS.BUFFER_SIZE

    def __init__(
        self,
        dtype: Optional[dtype] = None,
        device: Optional[DeviceLikeType] = None,
        chunk_size: int = MemoryLimits.MAX_FLUSH,
        max_buffer: int = MemoryLimits.MAX_BUFFER,
        max_vram_percent: float = MemoryLimits.MAX_VRAM_PERCENT,
    ):
        """
        Args:
            - dtype: Optional[dtype] = None,
            - device: Optional[DeviceLikeType] = None,
            - chunk_size: how many bits to flush per mini-SVD
            - max_buffer:  how many bits to accumulate before forced flush
        Automatic:
            - flush_cols: how columns the current chunk_size accounts for
            - max_cols:  how columns the current max_buffer accounts for
            - M: the current rotational basis of the buffer
            - buffer: the current column buffer
        """
        self.__dtype = dtype
        self.__device = device
        self.__LIMITS: VectorBuffer.BufferLimits = self.BufferLimits(
            chunk_size, max_buffer
        )
        if (
            torch.cuda.is_available()
            and device is not None
            and torch.device(device).type == "cuda"
        ):
            torch.cuda.set_per_process_memory_fraction(max_vram_percent)
        self.__max_chunk_cols: int = 0
        self.__max_buffer_cols: int = 0
        # pending rotation to apply to ANY column when it gets flushed:
        self.__M: Optional[Tensor] = None
        # list of “raw” (kx1) column projections
        self.__buffer: Optional[list[Tensor]] = None

    def __flush_chunk(self: VectorBuffer, qsr: QSR):
        if not (assert_not_none(self.__buffer) and assert_not_none(self.__M)):
            return

        # Unpack QSR
        _, S, R = qsr
        k = S.shape[0]

        # compact SVD on [S | C] # C is chunk expressed on current basis M
        Y = torch.hstack(
            [S, self.__M @ torch.hstack(self.__buffer[: self.__max_chunk_cols])]
        )
        Qy, Sy, Ry = svd(Y, full_matrices=False)
        Ry.t_()
        S.diagonal().copy_(Sy)
        i, n = R.shape[0], Ry.shape[0] - k
        R_top = R @ Ry[:k, :]
        R.resize_(i + n, k)
        R[:i, :].copy_(R_top)
        R[i:, :].copy_(Ry[k:, :])

        # Delete chunk after processing
        del self.__buffer[: self.__max_chunk_cols]

        # absorb *this* rotation into our pending M
        matmul(Qy.T, self.__M, out=self.__M)

    def __flush_all(self: VectorBuffer, qsr: QSR):
        while self.__buffer:
            self.__flush_chunk(qsr)

    def __push(self: VectorBuffer, col: Tensor):
        if self.__M is None or self.__buffer is None:
            self.__prepare_buffer(col)
        if assert_not_none(self.__M) and assert_not_none(self.__buffer):
            self.__buffer.append(col)

    def __prepare_buffer(self: VectorBuffer, col: Tensor) -> None:
        if assert_none(self.__M) and assert_none(self.__buffer):
            assert_shape(col, 0, 1)
            col_size = col.numel() * col.element_size()
            self.__max_chunk_cols = self.CHUNK_SIZE // col_size
            self.__max_buffer_cols = self.BUFFER_SIZE // col_size
            self.__M = torch.eye(col.shape[0], dtype=self.__dtype, device=self.__device)
            self.__buffer = []

    def __reset(self: VectorBuffer) -> None:
        if assert_not_none(self.__M) and assert_not_none(self.__buffer):
            self.__max_chunk_cols = 0
            self.__max_buffer_cols = 0
            self.__M = None
            self.__buffer = None

    @staticmethod
    def _check_empty() -> Callable:
        def deco(func) -> Callable:
            @wraps(func)
            def wrapper(self: VectorBuffer, *args, **kwargs):
                result = func(self, *args, **kwargs)
                self.__check_empty()
                return result

            return wrapper

        return deco

    def __check_empty(self: VectorBuffer):
        if self.__buffer is not None and len(self.__buffer) == 0:
            self.__reset()

    @_check_empty()
    def process(
        self: VectorBuffer, qsr: QSR, projection: Tensor, res_norm_sq: float, tol: float
    ) -> bool:
        """
        Called once per new column:

        Args:
            - qsr: QSR NamedTuple containing Q_0, S, R tensors
            - projection: the (kx1) vector in the *original* Q-basis
            - res_norm_sq: float
            - tol: float

        Returns:
          True  = residual ≥ tol  → we flushed *everything*, updated S,R, rebased `projection` in-place,
                                   and you should CONTINUE the rest of your update on _that_ projection.

          False = residual < tol  → we either just buffered, or flushed one mini-chunk + buffered,
                                   and you should QUIT this update and move to the next input.
        """
        if self.__buffer is None or self.__M is None:
            self.__prepare_buffer(projection)
        if not (assert_not_none(self.__buffer) and assert_not_none(self.__M)):
            # This return will never be hit because in debug the check will assert, and in prod it will always pass
            return False

        # Case 1: projection below tolerance
        if res_norm_sq < tol**2:
            if len(self.__buffer) < self.__max_buffer_cols:
                # Case 1a: buffer not yet full → just stash and exit
                self.__push(projection.clone())
                return False
            else:
                # Case 1b: buffer full but projection below tol → flush _one_ chunk, then stash, then exit
                self.__flush_chunk(qsr)
                self.__push(projection.clone())
                return False

        # Case 2: residual ≥ tol → flush *everything* and continue update
        self.__flush_all(qsr)

        # now rebase the working projection exactly once
        projection.copy_(self.__M @ projection)
        return True

    @_check_empty()
    def finalize(self, qsr: QSR):
        """
        After ALL your columns have been `process`ed and your outer update loop is done,
        call `finalize()` once to sync the global basis (Q) at end of processing.

        Args:
            - qsr: QSR NamedTuple containing Q, S, R tensors
        """
        self.__flush_all(qsr)
        if self.__M is not None:
            matmul(qsr.Q, self.__M.T, out=qsr.Q)


T = TypeVar("T")


def assert_not_none(v: Optional[T]) -> TypeIs[T]:
    if __debug__ or "PYTEST_CURRENT_TEST" in os.environ:
        assert v is not None
    return True


def assert_none(v: Optional[T]) -> TypeIs[None]:
    if __debug__ or "PYTEST_CURRENT_TEST" in os.environ:
        assert v is None
    return True


@skip_outside_pytest()
def assert_dtype(T: Tensor, dtype: Optional[dtype] = None) -> None:
    if dtype is not None:
        assert T.dtype == dtype, f"Tensor type was {T.dtype} instead of {dtype}"


@skip_outside_pytest()
def assert_py_float(v) -> None:
    assert isinstance(
        v, float
    ), f"Expected a python floating point value, got {type(v)}"


@skip_outside_pytest()
def assert_proper_qsr(
    Q: Tensor,
    S: Tensor,
    R: Tensor,
    W: Optional[Tensor] = None,
    dtype: Optional[dtype] = None,
) -> None:
    if dtype is not None:
        all(assert_dtype(x, dtype) for x in ((Q, S, R) if W is None else (Q, S, R, W)))
    else:
        all(
            assert_dtype(x, Q.dtype) for x in ((Q, S, R) if W is None else (Q, S, R, W))
        )

    Qm, Qk = Q.shape
    Sk, Sk = S.shape
    Rl, Rk = R.shape
    if W is None:
        assert Qm > 0, f"m <= 0, Qm = {Qm}"
    else:
        Wm, Wm = W.shape
        assert Qm == Wm, f"m mismatch Qm = {Qm}, Wm = {Wm}"
    assert Rl > 0, f"l <= 0, Rl = {Rl}"
    assert Qk == Sk and Sk == Rk, f"k mismatch, Qk = {Qk}, Sk = {Sk}, Rk = {Rk}"


@skip_outside_pytest()
def assert_shape(
    T: Tensor, a: int, b: Optional[int] = None, dtype: Optional[dtype] = None
) -> None:
    assert_dtype(T, dtype)
    assert isinstance(T, Tensor)
    A, B, one, two = [0, 0, True, True]
    if b is None:
        assert T.dim() == 1, "Shape was supposed to be 1 dimensional, got {}".format(
            T.dim()
        )
        A = T.shape[0]
        assert a == 0 or A == a, "Shape failed assert: [{}] != [{}]".format(
            A, f"{a}" if a != 0 else ">0"
        )
    else:
        assert T.dim() == 2, "Shape was supposed to be 2 dimensional, got {}".format(
            T.dim()
        )
        A, B = T.shape
        one = a == 0 or A == a
        two = b == 0 or B == b
        assert one and two, "Shape failed assert: [{},{}] != [{},{}]".format(
            A, B, f"{a}" if a != 0 else ">0", f"{b}" if b != 0 else ">0"
        )


def matmul(A: Tensor, B: Tensor, out: Tensor):
    if out.device.type == "cuda":
        torch.matmul(A, B, out=out)
    else:
        out.copy_(A @ B)


def svd(Y: Tensor, full_matrices: bool = False) -> QSR:
    base_type = Y.dtype
    with torch.no_grad():
        if base_type == torch.bfloat16:
            qsr = torch.linalg.svd(Y.to(torch.float32), full_matrices=full_matrices)
            return QSR(*(x.to(base_type) for x in qsr))
        return QSR(*torch.linalg.svd(Y, full_matrices=full_matrices))


def initialize_isvd(
    initial_vector: Tensor,
    *,
    W: Optional[Tensor] = None,
    max_rank: Optional[int] = None,
    tol: Optional[float] = None,
    dtype: Optional[dtype] = None,
    device: Optional[DeviceLikeType] = None,
) -> ISVD_QSR:
    """
    Initializes the ISVD decomposition using the first column of data.

    Args:
        initial_vector (Tensor): First column of the data matrix (shape [m, 1]).
    Optional:
        max_rank (int): The maximum rank to estimate Q, S, R to.
        tol (float): Tolerance threshold for accepting new orthogonal directions.
        W (Tensor): Weighting matrix for the generalized inner product (shape [m, m]).

    Returns:
        Q (Tensor): Initial orthonormal basis (shape [m, 1]).
        S (Tensor): Initial singular value (shape [1, 1]).
        R (Tensor): Initial right singular vector placeholder (1x1 identity matrix).
    """
    assert_dtype(initial_vector, dtype)

    S = (
        initial_vector.norm(keepdim=True)
        if W is None
        else torch.sqrt(initial_vector.T @ (W @ initial_vector))
    )

    Q = initial_vector / S.item()
    R = torch.eye(1, dtype=dtype, device=device)
    assert_proper_qsr(Q, S, R, W, dtype)
    return ISVD_QSR(
        QSR(Q, S, R),
        VectorBuffer(dtype=dtype, device=device),
        torch.eye(1, dtype=dtype, device=device),
        W,
        max_rank,
        tol,
        dtype,
        device,
    )


def update_isvd4(isvd_qsr: ISVD_QSR, new_col: Tensor) -> ISVD_QSR:
    """
    Performs an incremental update step for ISVD with buffering of low-residual components.

    Args:
        - ISVD_QSR unpacks to:
            - QSR unpacks to:
                - Q (Tensor): Current left singular vectors (shape [m, k]).
                - S (Tensor): Current singular values (shape [k, k]).
                - R (Tensor): Current right singular vectors (shape [l, k]).

            - buffer: VectorBuffer: Class managing low-residual vectors to accumulate and flush later.
            - Q_0: Tensor: Augmented orthogonalization basis used to compact buffered projections.
            - W: Optional[Tensor]
            - max_rank: Optional[int]
            - tol: Optional[float]
            - dtype: Optional[torch.dtype]
            - device: Optional[DeviceLikeType]
        - new_col (Tensor): New column vector (shape [m]) to incorporate.

    Returns:
        - ISVD_QSR
    """
    # Unpack Tuples
    (Q, S, R), buffer, Q_0, W, max_rank, tol0, dtype, device = isvd_qsr
    k = S.shape[0]
    m = Q.shape[0]
    tol = max(compute_tolerance(new_col), tol0 if tol0 is not None else 0.0)

    # Verify Args
    assert_proper_qsr(Q, S, R, W, dtype)
    assert_py_float(tol)
    assert_dtype(Q_0, dtype)
    assert_dtype(new_col, dtype)

    # Calculate Projection and Residual
    projection = (Q.T @ new_col) if W is None else (Q.T @ (W @ new_col))
    residual = new_col - (Q @ projection)

    residual_norm_sq = (
        residual.T @ residual if W is None else residual.T @ (W @ residual)
    )
    assert_shape(projection, k, 1)
    assert_shape(residual, m, 1)
    assert_shape(residual_norm_sq, 1, 1)

    if buffer.process(QSR(Q_0, S, R), projection, residual_norm_sq.item(), tol):

        # Orthonormalize residual and optionally reproject
        residual_norm = residual_norm_sq.sqrt().item()
        residual = residual / residual_norm
        assert_dtype(residual, dtype)
        if W is None:
            if (residual.T @ Q[:, 0]).abs().item() > tol:
                residual = residual - (Q @ (Q.T @ residual))
                residual_norm1 = residual.norm().item()
                residual = residual / residual_norm1
        else:
            if (residual.T @ (W @ Q[:, 0])).abs().item() > tol:
                residual = residual - (Q @ (Q.T @ (W @ residual)))
                residual_norm1 = (residual.T @ (W @ residual)).sqrt().item()
                residual = residual / residual_norm1

        assert_shape(residual, m, 1)
        assert_py_float(residual_norm)
        Y = torch.vstack(
            [
                torch.hstack([S, projection]),
                torch.hstack(
                    [
                        torch.zeros(k, dtype=dtype, device=device),
                        tensor([residual_norm], dtype=dtype, device=device),
                    ]
                ),
            ]
        )
        assert_dtype(Y, dtype)

        Qy, Sy, Ry = svd(Y, full_matrices=False)
        Ry.t_()
        assert_proper_qsr(Qy, Sy.diag(), Ry)

        # Decide to Grow or Truncate
        Q_0 = torch.block_diag(Q_0, tensor([[1.0]], dtype=dtype, device=device)) @ Qy
        if (max_rank is None or k < max_rank) and Sy[k] > tol:
            # Grow
            Q = torch.hstack([Q, residual]) @ Q_0
            S = torch.diag(Sy)
            R1 = Ry[:k, : k + 1]
            R2 = Ry[k:, : k + 1]
            R = torch.vstack([R @ R1, R2])
            Q_0 = torch.eye(k + 1, dtype=dtype, device=device)
        else:
            # Truncate
            Q = torch.hstack([Q, residual]) @ Q_0[:, :k]
            S = torch.diag(Sy[:k])
            R1 = Ry[:k, :k]
            R2 = Ry[k:, :k]
            R = torch.vstack([R @ R1, R2])
            Q_0 = torch.eye(k, dtype=dtype, device=device)

        assert_proper_qsr(Q, S, R, W, dtype)

    return ISVD_QSR(QSR(Q, S, R), buffer, Q_0, W, max_rank, tol0, dtype, device)


def update_isvd4_check(isvd_qsr: ISVD_QSR) -> QSR:
    """
    Final cleanup step to flush any remaining buffered projections after streaming.

    Args:
        - ISVD_QSR unpacks to:
            - QSR unpacks to:
                - Q (Tensor): Current left singular vectors (shape [m, k]).
                - S (Tensor): Current singular values (shape [k, k]).
                - R (Tensor): Current right singular vectors (shape [l, k]).

            - buffer: VectorBuffer: Class managing low-residual vectors to accumulate and flush later.
            - Q_0: Tensor: Augmented orthogonalization basis used to compact buffered projections.
            - W: Optional[Tensor]
            - max_rank: Optional[int]
            - tol: Optional[float]
            - dtype: Optional[torch.dtype]
            - device: Optional[DeviceLikeType]

    Returns:
        Q (Tensor): Finalized left singular vectors after flushing.
        S (Tensor): Finalized singular values.
        R (Tensor): Finalized right singular vectors.
    """
    # Unpack args
    (Q, S, R), buffer, _, W, _, _, dtype, _ = isvd_qsr
    assert_proper_qsr(Q, S, R, W, dtype)
    buffer.finalize(QSR(Q, S, R))
    return QSR(Q, S, R)


def compute_tolerance(M: Tensor) -> float:
    eps = torch.finfo(M.dtype).eps
    return eps**0.4


def compute_ortho_loss(M: Tensor, W=None) -> float:
    """
    Measures average off-diagonal correlation of columns in M (optionally after
    applying a preconditioner). Returns 0.0 for perfectly orthonormal columns.

    Args:
      M       (nxk): matrix whose columns you want to test.
      precond (kxk): optional linear map applied before checking orthogonality.
      eps     float: small constant to avoid div‐by‐zero.

    Returns:
      mean(|G_ij|) over i≠j, where
        G = (M^T (precond @ M)) / sqrt(diag(...)*diag(...)).
    """
    G = M.T @ M if W is None else M.T @ (W @ M)
    d = torch.diag(G).clamp(torch.finfo(G.dtype).eps).sqrt()
    G = G / d[:, None] / d[None, :]
    G.fill_diagonal_(0.0)
    return float(G.abs_().mean())


def compute_error(test: Tensor, truth: Tensor) -> float:
    """
    Returns an error in [0,1), where:
      0.0 = perfect match
      →1.0 as ||test-truth|| grows unbounded relative to ||truth||
    """
    # raw relative error
    num = torch.norm(test - truth, p="fro").item()
    den = torch.norm(truth, p="fro").item()
    if den == 0.0:
        # define: zero truth & zero test → zero error; else → maximal error
        return 0.0 if num == 0.0 else 1.0

    r = num / den
    return r / (1.0 + r)


def run_isvd4(
    M: Tensor,
    *,
    W: Optional[Tensor] = None,
    max_rank: Optional[int] = None,
    tol: Optional[float] = None,
    dtype: Optional[torch.dtype] = None,
    device: Optional[DeviceLikeType] = None,
    progress: bool = False,
) -> QSR:
    isvd_qsr = initialize_isvd(
        M[:, 0:1], W=W, max_rank=max_rank, tol=tol, dtype=dtype, device=device
    )

    iterable: Iterable[int] = range(1, M.shape[1])
    if progress and sys.stderr.isatty():
        iterable = tqdm(iterable)

    for i in iterable:
        isvd_qsr = update_isvd4(
            isvd_qsr, M[:, i : i + 1]
        )  # should be made in-place with no return
    return update_isvd4_check(isvd_qsr)


# TODO: @torch.jit.script try to use this in a more limited capacity, later
def run_isvd4_cosine_sim(
    E: Tensor,
    *,
    W: Optional[Tensor] = None,
    max_rank: Optional[int] = None,
    tol: Optional[float] = None,
    dtype: Optional[torch.dtype] = None,
    device: Optional[DeviceLikeType] = None,
    progress: bool = False,
) -> QSR:
    # Setup variables
    Ern = normalize_cosine_sim_factor(E)
    col: Tensor = Ern.mv(Ern[0])
    col_view_size = (Ern.shape[0], 1)
    assert_shape(col, E.shape[0])
    assert_shape(col.view(col_view_size), E.shape[0], 1)
    isvd_qsr = initialize_isvd(
        col.view(col_view_size),
        W=W,
        max_rank=max_rank,
        tol=tol,
        dtype=dtype,
        device=device,
    )
    """
    Incrementally compute a low-rank factor W whose Gram approximates the
    cosine-similarity matrix of E and yields a valid correlation matrix.


    Note on finishing steps:
      - A spectral-norm division step ensures no overall ℓ₂-amplification.
      - A final row-normalization enforces exact self-similarity =1.
      - Together, they guarantee a valid correlation matrix, but strict
        operator-norm ≤1 is only ensured up to the first step (before
        row-normalization).

     Args:
      E (Tensor [nxd]): raw embedding matrix.
      W (Optional[Tensor]): initial low-rank factor for warm start (nxk).
      max_rank (Optional[int]): maximum rank for incremental SVD truncation.
      tol (Optional[float]): SVD tolerance for growing/truncation decisions.
      dtype (Optional[torch.dtype]): dtype for internal Q/S/R factors.
      device (Optional[DeviceLikeType]): device to perform computation on.
      progress (bool): if True and stderr is a TTY, show a tqdm progress bar.

    Returns:
      QSR: namedtuple with
        • Q (nxk): left singular vectors,
        • S (k, ): singular values,
        • R (nxk): (right singular vectors) subspace factor,
      such that Q @ diag(S) @ R.T is a low-rank approximation of the
      cosine-similarity matrix of E.
    """

    # TODO: Consider and benchmark torch.linalg.pca_lowrank
    # and torch.linalg.svd_lowrank as drop-in replacements for
    # run_isvd4_cosine_sim

    iterable: Iterable[int] = range(1, E.shape[0])
    if progress and sys.stderr.isatty():
        iterable = tqdm(iterable)

    for i in iterable:
        col_i: Tensor = torch.mv(Ern, Ern[i]).clone()
        assert_shape(col_i, E.shape[0])
        assert_shape(col_i.view(col_view_size), E.shape[0], 1)
        isvd_qsr = update_isvd4(
            isvd_qsr, col_i.view(col_view_size)
        )  # should be made in-place with no return
    return update_isvd4_check(isvd_qsr)


def spectral_normalize_Q_to_W(qsr: QSR) -> Tensor:
    """
    Eigendecompose C_sym, clamp negatives, divide by λ_max, and
    rotate Q to form W_interim = Q U sqrt(λ/λ_max).
    Returns W_interim (nxk).
    """

    def _C_sym_from_QSR(qsr: QSR) -> Tensor:
        """
        Given Q, S, R from your incremental SVD of the cosine matrix,
        build the symmetrized small matrix C_sym = ½ (S RᵀQ + QᵀR S).
        Returns C_sym (kxk).
        """
        Q, S, R = qsr
        M = R.T @ Q
        return 0.5 * (S @ M + M.T @ S)

    C_sym = _C_sym_from_QSR(qsr)
    eigvals, U = torch.linalg.eigh(C_sym)
    lam_clamped = torch.clamp(eigvals, min=0.0)
    lam_norm = lam_clamped / lam_clamped.max().clamp(min=torch.finfo(qsr.Q.dtype).eps)
    return (qsr.Q @ U) * torch.sqrt(lam_norm)


def row_sum_normalize(W: Tensor) -> Tensor:
    """
    Scale W so that the maximum absolute row-sum of M = W @ W.T becomes 1.
    In practice:
      • Compute col_sum = Σ_j W[j,:]  (shape k)
      • Compute row_sums = W @ col_sum (shape n)
      • Let factor = sqrt(max_i |row_sums[i]|), clamped ≥ eps
      • Return W / factor
    """
    # Σ_j W[j,:]
    col_sum = W.sum(dim=0)  # shape (k,)
    # each row‐sum of W W^T
    row_sums = W @ col_sum  # shape (n,)
    # divisor √(max abs row‐sum)
    max_rs = row_sums.abs().max().clamp(min=torch.finfo(W.dtype).eps)
    factor = torch.sqrt(max_rs)
    return W / factor


class FinalOperations(Flag):
    SpectralNorm = auto()
    RowNorm = auto()


def build_final_w_matrix(
    qsr: QSR,
    final_ops: FinalOperations = FinalOperations(0),
) -> Tensor:
    """
    Full pipeline: symmetrize → (opt) spectral_norm → (opt) row_norm.
    """
    W = (
        spectral_normalize_Q_to_W(qsr)
        if FinalOperations.SpectralNorm in final_ops
        else qsr.Q @ qsr.S.sqrt()
    )
    if FinalOperations.RowNorm in final_ops:
        W = row_sum_normalize(W)
    return W


def normalize_cosine_sim_factor(E: Tensor) -> Tensor:
    return E / E.norm(dim=1)[:, None]
