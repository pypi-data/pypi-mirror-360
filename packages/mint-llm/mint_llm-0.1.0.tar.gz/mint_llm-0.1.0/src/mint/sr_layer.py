from __future__ import annotations

from torch import nn
import torch


class SimilarityRedistributor(nn.Module):
    """Redistribute token logits using a sparse similarity matrix."""

    def __init__(
        self, sparse_S: torch.Tensor, alpha: float = 0.0, vocab_size: int | None = None
    ) -> None:
        """Create a new layer.

        Parameters
        ----------
        sparse_S:
            Sparse similarity matrix of shape ``(V, V)``.
        alpha:
            Strength of demotion for the original logits. ``0`` disables demotion.
        vocab_size:
            Expected vocabulary size of the similarity matrix. ``None`` disables
            the check.
        """
        super().__init__()
        if not sparse_S.is_sparse:
            raise ValueError("S must be a sparse tensor")
        if sparse_S.ndim != 2:
            raise ValueError("S must be 2-D")
        rows, cols = sparse_S.shape
        if rows != cols:
            raise ValueError("S must be square")
        if vocab_size is not None and rows != vocab_size:
            raise ValueError(
                f"S has shape {sparse_S.shape}, expected vocabulary size {vocab_size}"
            )
        self.register_buffer("S", sparse_S)
        self.alpha = float(alpha)
        self.vocab_size = rows

    def forward(self, logits: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        """Apply redistribution to ``logits``."""
        redistributed = torch.sparse.mm(self.S, logits.unsqueeze(-1)).squeeze(-1)
        if self.alpha > 0:
            redistributed = redistributed - self.alpha * logits
        return redistributed
