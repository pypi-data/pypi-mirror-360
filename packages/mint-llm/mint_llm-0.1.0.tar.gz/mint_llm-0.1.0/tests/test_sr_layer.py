import torch
import pytest

from mint.sr_layer import SimilarityRedistributor


def _sparse(matrix: torch.Tensor) -> torch.Tensor:
    indices = matrix.nonzero().t()
    values = matrix[matrix != 0]
    return torch.sparse_coo_tensor(indices, values, matrix.shape)


def test_sr_layer_basic_redistribution():
    dense = torch.tensor([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    S = _sparse(dense)
    layer = SimilarityRedistributor(S)
    logits = torch.tensor([0.1, 0.2, 0.3])
    out = layer(logits)
    expected = torch.tensor([0.2, 0.1, 0.3])
    assert torch.allclose(out, expected)


def test_sr_layer_alpha_demotion():
    dense = torch.tensor([[0.0, 1.0], [1.0, 0.0]])
    S = _sparse(dense)
    layer = SimilarityRedistributor(S, alpha=0.5)
    logits = torch.tensor([1.0, 2.0])
    redistributed = torch.sparse.mm(S, logits.unsqueeze(-1)).squeeze(-1)
    expected = redistributed - 0.5 * logits
    out = layer(logits)
    assert torch.allclose(out, expected)


def test_sr_layer_requires_sparse():
    with pytest.raises(ValueError):
        SimilarityRedistributor(torch.zeros(2, 2))


def test_sr_layer_vocab_mismatch():
    S = _sparse(torch.eye(2))
    with pytest.raises(ValueError):
        SimilarityRedistributor(S, vocab_size=3)
