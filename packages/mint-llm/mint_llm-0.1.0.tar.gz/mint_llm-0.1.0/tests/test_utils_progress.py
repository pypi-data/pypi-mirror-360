import io
import json
import sys

import torch
from safetensors.torch import save_file

from mint import utils
from mint.safetensors import split_file, merge_to_file


def test_download_checkpoint_uses_tqdm(monkeypatch, tmp_path):
    calls = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr(sys.stderr, "isatty", lambda: True)
    monkeypatch.setattr("mint.utils.tqdm", fake_tqdm)

    def fake_urlopen(url):
        class F(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        if url.endswith("index.json"):
            data = json.dumps({"weight_map": {"a": "shard1"}}).encode()
            return F(data)
        raise RuntimeError("unexpected url")

    def fake_urlretrieve(url, filename):
        save_file({"a": torch.zeros(1)}, str(filename))

    monkeypatch.setattr(utils.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(utils.urllib.request, "urlretrieve", fake_urlretrieve)

    utils.download_checkpoint("dummy", tmp_path, progress=True)

    assert calls


def test_split_file_uses_tqdm(monkeypatch, tmp_path):
    tensors = {"a": torch.zeros(1)}
    src = tmp_path / "model.safetensors"
    save_file(tensors, str(src))

    calls = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr(sys.stderr, "isatty", lambda: True)
    monkeypatch.setattr("mint.safetensors.tqdm", fake_tqdm)

    split_file(str(src), num_shards=1, output_dir=str(tmp_path), progress=True)

    assert calls


def test_merge_to_file_uses_tqdm(monkeypatch, tmp_path):
    tensors = {"a": torch.zeros(1)}
    shard = tmp_path / "model-00001-of-00001.safetensors"
    save_file(tensors, str(shard))
    index = tmp_path / "model.safetensors.index.json"
    index.write_text(json.dumps({"weight_map": {"a": shard.name}}))

    out = tmp_path / "merged.safetensors"

    calls = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr(sys.stderr, "isatty", lambda: True)
    monkeypatch.setattr("mint.safetensors.tqdm", fake_tqdm)

    merge_to_file(str(index), str(out), progress=True)

    assert calls
