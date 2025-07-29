from __future__ import annotations

from torch import nn, Tensor
import torch
from typing import NamedTuple, Optional, Tuple, Type
from enum import Enum, unique, auto
from dataclasses import dataclass

from .utils import skip_outside_pytest


@skip_outside_pytest()
def debug_print(*args, **kwargs):
    print(*args, **kwargs)


class LowRankRedistributor(nn.Module):
    @unique
    class Modes(Enum):
        Lerp = auto()
        LogitScale = auto()
        MintScale = auto()
        TopK = auto()
        TopP = auto()
        MinP = auto()
        # Experiments to implement next
        MuddleTopK = (
            auto()
        )  # cross-influence masking where we zero out self-contribution from masked tokens
        MuddleTopP = (
            auto()
        )  # cross-influence masking where we zero out self-contribution from masked tokens
        MuddleMinP = (
            auto()
        )  # cross-influence masking where we zero out self-contribution from masked tokens
        Diff = (
            auto()
        )  # based on mint - logits to delete self-influence, scale like CFG? a * (mint-logits) + logits
        CFG = auto()  # alt name for above ^
        NoConfidence = (
            auto()
        )  # drop out all logit influence where both logits & mint are low-scoring, then re-norm

    # Presets are a stub for now - revisit this later
    @dataclass(frozen=True)
    class Presets(dict):
        class Preset(NamedTuple):
            mode: LowRankRedistributor.Modes
            alpha: float

        Basic: Preset
        Grimm: Preset
        Stable: Preset
        Surreal: Preset

    def __init__(
        self,
        W: Tensor,
        /,
        mode: Modes = Modes.Lerp,
        alpha: float = 0.0,
        device: Optional[torch.device] = None,
    ):
        # Presets are a stub for now - revisit this later
        self._presets = self.Presets(
            Basic=self.Presets.Preset(self.Modes.Lerp, 0.4),
            Grimm=self.Presets.Preset(self.Modes.MintScale, 0.4),
            Stable=self.Presets.Preset(self.Modes.LogitScale, 0.3),
            Surreal=self.Presets.Preset(self.Modes.MintScale, 0.35),
        )

        print = debug_print
        super().__init__()
        print("==================================")
        print("Low Rank Redistributor Initialized")
        print("==================================")
        print(f"- Alpha:    \t{alpha}")
        print(f"- Operation:\t{mode.name}")
        print(f"- Device:   \t{device}")
        print(f"- W.shape:  \t{W.shape}")
        print(f"- W.dtype:  \t{W.dtype}")
        print("==================================")
        # register as buffer so it moves with the module
        self.W: Tensor
        self.register_buffer("W", W)
        self.mode = mode
        self.alpha = alpha
        self._w_type_checked = False
        if device is not None:
            self.to(device)

    def forward(self, logits: Tensor) -> Tensor:
        print = debug_print
        Modes: Type = LowRankRedistributor.Modes
        # Figure out the higher‐precision dtype for this call
        return_type = logits.dtype
        common_dtype = torch.result_type(logits, self.W)

        # 1) Upcast logits if needed, track for casting back
        cast_logits = logits.dtype != common_dtype
        if cast_logits:
            logits = logits.to(common_dtype)

        # 2) Upcast W once if it’s lower precision
        elif not self._w_type_checked:
            if self.W.dtype != common_dtype:
                # replace the buffer in-place so future calls skip this
                self.W = self.W.to(common_dtype)
                self.type(common_dtype)
            self._w_type_checked = True

        # 3) Do your low-rank smoothing + demotion
        print(f"Alpha           :\t{self.alpha}")
        print(f"Original Logits :\n\t{logits}")
        print(f"Pre-minting n   :\t{logits.norm():.4}")

        def _mint_logits(logits: Tensor) -> Tensor:
            return (logits @ self.W) @ self.W.T

        def _normalize(A: Tensor) -> Tuple[Tensor, float]:
            A_n = float(A.norm())
            return A / A_n, A_n

        def _rescale_A_to_B_norm(A: Tensor, B_n: float) -> Tensor:
            return (A / float(A.norm())) * B_n

        def _lerp(
            mint: Tensor, logit: Tensor, a: float | Tensor = self.alpha
        ) -> Tensor:
            """
            Linearly interpolates from Fully mint @ a = 0.0 to logit @ a = 1.0:
                a = 0 -> no original logit
                a = 1 -> all original logit
            """
            return (1 - a) * mint + a * logit

        def _softmax(M: Tensor) -> Tensor:
            scale = M - M.min()
            return scale / scale.max().clamp(min=torch.finfo(common_dtype).eps)

        match self.mode:
            case Modes.Lerp:
                logits, l_n = _normalize(logits)
                minted, _ = _normalize(_mint_logits(logits))
                logits = _lerp(minted, logits)
                logits = _rescale_A_to_B_norm(logits, l_n)

            case Modes.LogitScale:
                l_scale = _softmax(logits.abs())
                logits, l_n = _normalize(logits)
                minted, _ = _normalize(_mint_logits(logits))
                logits = _lerp(minted, logits, (1 - self.alpha * l_scale))
                logits = _rescale_A_to_B_norm(logits, l_n)

            case Modes.MintScale:
                logits, l_n = _normalize(logits.abs())
                minted = _mint_logits(logits)
                m_scale = _softmax(minted)
                minted, _ = _normalize(minted)
                logits = _lerp(minted, logits, self.alpha * m_scale)
                logits = _rescale_A_to_B_norm(logits, l_n)

            # TopK, TopP, and MinP samplers currently mask logits and replace those masked logits with MINT's scores.
            # This could reinforce some of the selcted logits, demote others, or leave some unchanged. However, it
            # doesn't allow those logits' "gained" or "lost" 'energy' to transfer to other tokens. Perhaps we could do
            # something more dynamic here? Perhaps we could mask the original logits, and run MINT with the others
            # as zeros, then, then do the inverse? Replace all the masked tokens with the non-masked spread and
            # Spread the masked tokens's contribution to the unmasked ones? Will need more consideration.
            case Modes.TopK:
                _, topk_idx = logits.topk(round(self.alpha))
                logits, l_n = _normalize(logits)
                minted, _ = _normalize(_mint_logits(logits))
                logits[0, topk_idx].copy_(minted[0, topk_idx])
                logits = _rescale_A_to_B_norm(logits, l_n)

            case Modes.TopP:
                # flatten to a 1-D probability vector
                sf = _softmax(logits).view(-1)  # shape [V]
                prev, end = 1, sf.numel()
                cutoff = max(1, end // 4)

                # binary-search on k, but trim overshoot via cumsum instead of a Python loop
                while True:
                    topk_v, topk_idx = sf.topk(
                        cutoff
                    )  # top-cutoff probs & their indices
                    if cutoff == prev:
                        break
                    if topk_v.sum() > self.alpha:
                        # vectorized trim: find first prefix where cumsum > α
                        cums = topk_v.cumsum(dim=0)
                        over = (cums > self.alpha).nonzero(as_tuple=False)
                        if over.numel():
                            cutoff = round(over[0].item())  # smallest k with mass > α
                            topk_idx = topk_idx[:cutoff]  # keep only those indices
                        break
                    # still under α → adjust low/high and continue
                    prev, cutoff = cutoff, (cutoff + end) // 2
                logits, l_n = _normalize(logits)
                minted, _ = _normalize(_mint_logits(logits))
                logits[0, topk_idx].copy_(minted[0, topk_idx])
                logits = _rescale_A_to_B_norm(logits, l_n)

            case Modes.MinP:
                sf = _softmax(logits)
                logits, l_n = _normalize(logits)
                minted, _ = _normalize(_mint_logits(logits))
                mask = sf.greater(sf.max() * self.alpha)
                logits = (~mask * logits) + (mask * minted)
                logits = _rescale_A_to_B_norm(logits, l_n)

            case _:
                raise Exception(f"Mode not implemented (TODO): {self.mode}")

        print(f"Post minting n  :\t{logits.norm():.4}")
        print(f"MINTED Logits   :\n\t{logits}")
        print("===============================================================")

        # 4) Cast result back to original dtype if we upcasted logits
        if cast_logits:
            return logits.to(return_type)

        return logits
