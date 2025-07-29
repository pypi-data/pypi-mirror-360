from typer.testing import CliRunner

import torch
from safetensors.torch import save_file, load_file

from mint.cli import app


def test_cli_blend_writes_W(tmp_path):
    runner = CliRunner()
    emb = torch.eye(3)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "out"
    result = runner.invoke(app, ["blend", str(emb_file), str(out_dir), "--rank", "2"])
    assert result.exit_code == 0
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (3, 2)


def test_cli_blend_cpu_option(run_test_on_cpu, monkeypatch, tmp_path):
    _ = run_test_on_cpu
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb_cpu.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "sim_cpu"
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(out_dir), "--rank", "1", "--cpu"],
    )
    assert result.exit_code == 0
    assert "Chose device cpu" in result.stdout
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (2, 1)


def test_cli_blend_creates_subdirs(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "nested"
    result = runner.invoke(app, ["blend", str(emb_file), str(out_dir), "--rank", "2"])
    assert result.exit_code == 0
    assert (out_dir / "W.safetensors").exists()
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (2, 2)


def test_cli_blend_vulkan_error(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "vulkan"],
    )
    assert result.exit_code != 0
    assert "Vulkan backend is not yet supported" in result.output


def test_cli_blend_zluda_error(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "zluda"],
    )
    assert result.exit_code != 0
    assert "ZLUDA backend is not yet supported" in result.output


def test_cli_blend_rocm_error(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "rocm"],
    )
    assert result.exit_code != 0
    assert "ROCm backend is not yet supported" in result.output


def test_cli_blend_metal_error(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "metal"],
    )
    assert result.exit_code != 0
    assert "Metal backend is not yet supported" in result.output
