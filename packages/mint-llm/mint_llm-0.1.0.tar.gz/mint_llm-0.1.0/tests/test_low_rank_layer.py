import torch
from mint.low_rank_layer import LowRankRedistributor


def test_low_rank_basic_redistribution():
    W = torch.tensor([[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
    layer = LowRankRedistributor(W, alpha=0.0)
    logits = torch.tensor([0.1, 0.2, 0.3])
    l_n = float(logits.norm())
    minted = ((logits / l_n) @ W) @ W.t()
    m_n = minted.norm()
    minted = (minted / m_n) * l_n
    out = layer(logits)
    assert torch.allclose(out, minted)


def test_low_rank_alpha_demotion():
    W = torch.eye(2)
    alpha = 0.5
    layer = LowRankRedistributor(W, alpha=alpha)
    logits = torch.tensor([1.0, 2.0])
    expected = (1 - alpha) * (logits @ W) @ W.t() + (alpha * logits)
    out = layer(logits)
    assert torch.allclose(out, expected)
