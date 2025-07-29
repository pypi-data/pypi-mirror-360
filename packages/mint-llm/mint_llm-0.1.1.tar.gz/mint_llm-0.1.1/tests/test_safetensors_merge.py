from __future__ import annotations

import json
import torch
from safetensors.torch import load_file, save_file
from mint.safetensors import merge_to_file
from mint.cli import app
from typer.testing import CliRunner


def _create_sharded(tmp_path):
    tensors = {
        "a": torch.zeros(1),
        "b": torch.ones(1),
    }
    original = tmp_path / "model.safetensors"
    save_file(tensors, str(original))

    shard1 = tmp_path / "model-00001-of-00002.safetensors"
    shard2 = tmp_path / "model-00002-of-00002.safetensors"
    save_file({"a": tensors["a"]}, str(shard1))
    save_file({"b": tensors["b"]}, str(shard2))

    index = tmp_path / "model.safetensors.index.json"
    index.write_text(json.dumps({"weight_map": {"a": shard1.name, "b": shard2.name}}))
    return original, index


def test_merge_shards(tmp_path):
    original, index = _create_sharded(tmp_path)
    out = tmp_path / "merged.safetensors"
    merge_to_file(str(index), str(out))

    expected = load_file(str(original))
    merged = load_file(str(out))
    assert expected.keys() == merged.keys()
    for k in expected:
        assert torch.equal(expected[k], merged[k])


def test_cli_crush(tmp_path):
    original, index = _create_sharded(tmp_path)
    out = tmp_path / "merged.safetensors"

    runner = CliRunner()
    result = runner.invoke(app, ["crush", str(index), str(out)])
    assert result.exit_code == 0

    expected = load_file(str(original))
    merged = load_file(str(out))
    assert expected.keys() == merged.keys()
    for k in expected:
        assert torch.equal(expected[k], merged[k])
