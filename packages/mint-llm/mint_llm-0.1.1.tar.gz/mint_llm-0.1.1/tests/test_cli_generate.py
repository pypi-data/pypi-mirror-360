from typer.testing import CliRunner
from typing import Type
from mint.cli import app

import torch

from mint.low_rank_layer import LowRankRedistributor

Modes: Type = LowRankRedistributor.Modes


def test_cli_brew(monkeypatch):
    runner = CliRunner()

    called: dict[str, tuple[object, ...]] = {}

    def fake_load(model, sim, mode, alpha, device):
        called["load"] = (model, sim, mode, alpha, device)

        class Layer:
            def __call__(self, scores):
                return scores

        return object(), object(), Layer()

    def fake_pipeline(task, model=None, tokenizer=None, device=-1):
        called["pipeline"] = (task, model, tokenizer, device)

        def run(prompt, logits_processor=None):
            return [{"generated_text": f"echo: {prompt}"}]

        return run

    monkeypatch.setattr("mint.cli.load_wrapped_model", fake_load)

    class FakeProcessor:
        def __init__(self, layer, alpha=0.0):
            called["proc"] = alpha

        def __call__(self, *_):
            return []

    monkeypatch.setattr("mint.cli.pipeline", fake_pipeline)
    monkeypatch.setattr("mint.cli.SRLogitsProcessor", FakeProcessor)

    result = runner.invoke(
        app,
        [
            "brew",
            "dummy",
            "simdir",
            "--prompt",
            "hi",
            "--alpha",
            "0.5",
        ],
    )

    device = (
        torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
    )

    assert result.exit_code == 0
    assert "echo: hi" in result.stdout
    assert called["load"] == ("dummy", "simdir", Modes.Lerp, 0.5, device)
    assert called["proc"] == 0.5
    assert called["pipeline"][0] == "text-generation"


def test_cli_brew_interactive(monkeypatch):
    runner = CliRunner()

    called: dict[str, tuple[object, ...]] = {}

    def fake_load(model, sim, mode, alpha, device):
        called["load"] = (model, sim, mode, alpha, device)

        class Layer:
            def __call__(self, scores):
                return scores

        return object(), object(), Layer()

    def fake_pipeline(task, model=None, tokenizer=None, device=-1):
        called["pipeline"] = (task, model, tokenizer, device)

        def run(prompt, logits_processor=None):
            return [{"generated_text": f"echo: {prompt}"}]

        return run

    monkeypatch.setattr("mint.cli.load_wrapped_model", fake_load)
    monkeypatch.setattr("mint.cli.pipeline", fake_pipeline)

    result = runner.invoke(
        app,
        ["brew", "dummy", "simdir", "--interactive"],
        input="hello\n\n",
    )

    device = (
        torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
    )
    assert "echo: hello" in result.stdout
    assert called["load"] == ("dummy", "simdir", Modes.Lerp, 0.5, device)
    assert called["pipeline"][0] == "text-generation"
    assert result.exit_code == 0


def test_cli_brew_device(monkeypatch):
    runner = CliRunner()

    called: dict[str, object] = {}

    def fake_load(model, sim, mode, alpha, device):
        called["load_device"] = device

        class Layer:
            def __call__(self, scores):
                return scores

        return object(), object(), Layer()

    def fake_pipeline(task, model=None, tokenizer=None, device=-1):
        called["pipe_device"] = device

        def run(prompt, logits_processor=None):
            return [{"generated_text": f"echo: {prompt}"}]

        return run

    monkeypatch.setattr("mint.cli.load_wrapped_model", fake_load)
    monkeypatch.setattr("mint.cli.pipeline", fake_pipeline)
    monkeypatch.setattr("mint.cli.SRLogitsProcessor", lambda *a, **k: object())

    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    result = runner.invoke(app, ["brew", "dummy", "simdir", "--prompt", "hi"])
    assert result.exit_code == 0
    assert called["pipe_device"] == 0
    assert isinstance(called["load_device"], torch.device)
    assert called["load_device"].type == "cuda"

    called.clear()

    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    result = runner.invoke(app, ["brew", "dummy", "simdir", "--prompt", "hi"])
    assert called["pipe_device"] == -1
    assert called["load_device"].type == "cpu"
    assert isinstance(called["load_device"], torch.device)
    assert result.exit_code == 0
