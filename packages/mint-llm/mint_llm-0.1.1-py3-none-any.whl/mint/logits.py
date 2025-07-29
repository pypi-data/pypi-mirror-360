"""Logits-related utilities for MINT.

This module defines helpers for working with token logits during
generation. Currently it exposes :class:`SRLogitsProcessor`, which
applies the :class:`~mint.sr_layer.SimilarityRedistributor` layer.
"""

from transformers.generation.logits_process import LogitsProcessor
import torch


class SRLogitsProcessor(LogitsProcessor):
    """Apply the SimilarityRedistributor during generation."""

    def __init__(self, layer: torch.nn.Module, alpha: float = 0.0) -> None:
        self.layer = layer
        self.alpha = alpha

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        """Transform ``scores`` using the wrapped layer."""
        return self.layer(scores)
