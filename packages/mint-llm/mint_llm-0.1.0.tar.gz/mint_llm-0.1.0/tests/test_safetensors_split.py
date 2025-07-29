from mint.safetensors import split_file, merge_shards
from safetensors.torch import save_file
import torch
from typer.testing import CliRunner
from mint.cli import app


def test_split_and_merge(tmp_path):
    tensors = {
        "a": torch.arange(6, dtype=torch.float32).reshape(2, 3),
        "b": torch.ones(3, 2),
    }
    src = tmp_path / "model.safetensors"
    save_file(tensors, str(src))

    index = split_file(str(src), num_shards=2, output_dir=str(tmp_path))
    merged = merge_shards(str(index))

    for key in tensors:
        assert torch.equal(tensors[key], merged[key])


def test_cli_chop(tmp_path):
    tensors = {"a": torch.arange(4, dtype=torch.float32)}
    src = tmp_path / "model.safetensors"
    save_file(tensors, str(src))
    out_dir = tmp_path / "out"

    runner = CliRunner()
    result = runner.invoke(app, ["chop", str(src), str(out_dir), "--shards", "1"])
    assert result.exit_code == 0

    shard = out_dir / "model-00001-of-00001.safetensors"
    index = out_dir / "model.safetensors.index.json"
    assert shard.exists() and index.exists()

    merged = merge_shards(str(index))
    assert torch.equal(merged["a"], tensors["a"])
