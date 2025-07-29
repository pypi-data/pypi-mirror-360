from typer.testing import CliRunner
from typing import Type
from mint.cli import app
from mint import __version__

from tests.utils.download_model import download_model, MODEL_PATH

import torch
from safetensors.torch import load_file, save_file

from mint.low_rank_layer import LowRankRedistributor

Modes: Type = LowRankRedistributor.Modes

DOWNLOADED = download_model()


def get_model(tmp_path):
    if DOWNLOADED:
        state_dict = load_file(str(MODEL_PATH))
        for key, value in state_dict.items():
            if "embedding" in key or "embed_tokens" in key:
                return MODEL_PATH, value
        raise RuntimeError("No embedding tensor found in downloaded model")
    embeddings = torch.arange(6, dtype=torch.float32).reshape(2, 3)
    model_file = tmp_path / "model.safetensors"
    save_file({"embed_tokens.weight": embeddings}, str(model_file))
    return model_file, embeddings


def test_cli_main():
    runner = CliRunner()
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Use MINT to pick, chop, crush" in result.stdout
    assert "Usage:" in result.stdout


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_extract(tmp_path):
    runner = CliRunner()
    model_file, expected = get_model(tmp_path)

    out_file = tmp_path / "embeddings.safetensors"
    result = runner.invoke(app, ["extract", str(model_file), str(out_file)])
    assert result.exit_code == 0
    saved = load_file(str(out_file))["embedding"]
    assert torch.equal(saved, expected)


def test_cli_extract_duplicate_embeddings(tmp_path):
    runner = CliRunner()
    emb1 = torch.zeros(2, 3)
    emb2 = torch.ones(2, 3)
    model_file = tmp_path / "model.safetensors"
    save_file({"embedding.weight": emb1, "embed_tokens.weight": emb2}, str(model_file))

    out_file = tmp_path / "embeddings.safetensors"
    result = runner.invoke(app, ["extract", str(model_file), str(out_file)])
    assert result.exit_code != 0
    assert "Expected one embedding tensor" in str(result.exception)


def test_cli_extract_creates_subdirs(tmp_path):
    runner = CliRunner()
    model_file, expected = get_model(tmp_path)

    out_file = tmp_path / "out" / "embeddings.safetensors"
    result = runner.invoke(app, ["extract", str(model_file), str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    saved = load_file(str(out_file))["embedding"]
    assert torch.equal(saved, expected)


def test_cli_extract_pt(tmp_path):
    runner = CliRunner()
    embeddings = torch.arange(6, dtype=torch.float32).reshape(2, 3)
    model_file = tmp_path / "model.pt"
    torch.save({"embed_tokens.weight": embeddings}, model_file)

    out_file = tmp_path / "embeddings.safetensors"
    result = runner.invoke(app, ["extract", str(model_file), str(out_file)])
    assert result.exit_code == 0
    saved = load_file(str(out_file))["embedding"]
    assert torch.equal(saved, embeddings)


def test_cli_infuse(monkeypatch, tmp_path):
    runner = CliRunner()

    called: dict[str, object] = {}

    class DummyModel:
        def save_pretrained(self, path: str) -> None:
            called["save"] = path

    def fake_attach(model, sim, mode, alpha):
        called["attach"] = (model, sim, mode, alpha)
        return DummyModel()

    monkeypatch.setattr("mint.cli.load_wrapped_model", fake_attach)

    model_dir = tmp_path / "model"
    model_dir.mkdir()
    out_dir = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "infuse",
            str(model_dir),
            "simdir",
            str(out_dir),
            "--mode",
            "Lerp",
            "--alpha",
            "0.5",
        ],
    )

    assert result.exit_code == 0
    assert f"Model infused with similarity data saved to {out_dir}" in result.stdout
    assert called["attach"] == (str(model_dir), "simdir", Modes.Lerp, 0.5)
    assert called["save"] == str(out_dir)


def test_cli_pick(monkeypatch, tmp_path):
    runner = CliRunner()

    def fake_download(src, dest, progress=True):
        p = tmp_path / "model.safetensors"
        p.write_text("dummy")
        assert dest == str(tmp_path)
        return p

    monkeypatch.setattr("mint.cli.download_checkpoint", fake_download)

    result = runner.invoke(app, ["pick", "mymodel", str(tmp_path)])

    assert result.exit_code == 0
    assert "model.safetensors" in result.stdout


def test_cli_extract_progress(monkeypatch, tmp_path):
    runner = CliRunner()
    model_file, _ = get_model(tmp_path)

    calls: list[bool] = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr("mint.extract.tqdm", fake_tqdm)

    out_file = tmp_path / "embeddings.safetensors"
    result = runner.invoke(app, ["extract", str(model_file), str(out_file)])

    assert result.exit_code == 0
    assert calls


def test_cli_extract_no_progress(monkeypatch, tmp_path):
    runner = CliRunner()
    model_file, _ = get_model(tmp_path)

    calls: list[bool] = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr("mint.extract.tqdm", fake_tqdm)

    out_file = tmp_path / "embeddings.safetensors"
    result = runner.invoke(
        app, ["extract", str(model_file), str(out_file), "--no-progress"]
    )

    assert result.exit_code == 0
    assert not calls
