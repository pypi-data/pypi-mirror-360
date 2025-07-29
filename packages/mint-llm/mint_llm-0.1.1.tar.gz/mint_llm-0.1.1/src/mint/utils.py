from __future__ import annotations
import os
import json
import urllib.request
from urllib.error import HTTPError
from pathlib import Path
import sys
from tqdm import tqdm
from typing import Callable

from safetensors.torch import load_file, save_file
import torch
from functools import wraps


def skip_outside_pytest() -> Callable:
    """Decorator: replace func with stub if -O/-OO was used."""

    def deco(func):
        if __debug__ or "PYTEST_CURRENT_TEST" in os.environ:
            return func

        @wraps(func)
        def stub(*args, **kwargs):
            pass

        return stub

    return deco


def _merge_shards(files: list[Path], output: Path) -> None:
    if output.exists():
        return

    state_dict: dict[str, torch.Tensor] = {}
    for fp in files:
        state_dict.update(load_file(str(fp)))
    save_file(state_dict, str(output))


def download_sharded_checkpoint(
    source: str, dest_dir: str | Path, *, progress: bool = True
) -> Path:
    """Download all shards referenced by a Hugging Face index file.

    Parameters
    ----------
    source:
        Either a model repository ID or a direct URL to a
        ``*.safetensors.index.json`` file.
    dest_dir:
        Directory in which to store the downloaded checkpoint.
    progress:
        Display a progress bar when ``True`` and stderr is a TTY.

    Returns
    -------
    Path to the merged ``.safetensors`` file.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    if source.startswith("http://") or source.startswith("https://"):
        index_url = source
        base_url = index_url.rsplit("/", 1)[0]
        with urllib.request.urlopen(index_url) as f:
            index = json.load(f)
    else:
        # Assume a HF repo ID
        base_url = f"https://huggingface.co/{source}/resolve/main"
        index_url = f"{base_url}/model.safetensors.index.json"
        with urllib.request.urlopen(index_url) as f:
            index = json.load(f)

    shard_names = sorted(set(index.get("weight_map", {}).values()))
    local_files: list[Path] = []
    iterable: list[str] | tqdm = shard_names
    if progress and sys.stderr.isatty():
        iterable = tqdm(iterable)
    for name in iterable:
        url = f"{base_url}/{name}"
        local_path = dest / name
        if not local_path.exists():
            urllib.request.urlretrieve(url, local_path)
        local_files.append(local_path)

    combined = dest / "model.safetensors"
    _merge_shards(local_files, combined)
    return combined


def download_checkpoint(
    source: str, dest_dir: str | Path, *, progress: bool = True
) -> Path:
    """Download a model checkpoint, merging shards when necessary.

    Parameters
    ----------
    source:
        Hugging Face model ID or direct URL to a checkpoint or index file.
    dest_dir:
        Directory in which to store the downloaded checkpoint.
    progress:
        Display a progress bar when ``True`` and stderr is a TTY.

    Returns
    -------
    Path to the ``.safetensors`` checkpoint file.
    """

    if source.endswith(".safetensors.index.json"):
        return download_sharded_checkpoint(source, dest_dir, progress=progress)

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    if source.startswith("http://") or source.startswith("https://"):
        filename = Path(source).name
        output = dest / filename
        if not output.exists():
            urllib.request.urlretrieve(source, output)
        return output

    base = f"https://huggingface.co/{source}/resolve/main"
    index_url = f"{base}/model.safetensors.index.json"
    try:
        with urllib.request.urlopen(index_url) as f:
            json.load(f)
    except HTTPError as e:
        if e.code != 404:
            raise
        file_url = f"{base}/model.safetensors"
        output = dest / "model.safetensors"
        if not output.exists():
            urllib.request.urlretrieve(file_url, output)
        return output
    else:
        return download_sharded_checkpoint(source, dest_dir, progress=progress)


def load_sharded_state_dict(index_path: str | Path) -> dict[str, torch.Tensor]:
    """Load a state dict from sharded ``.safetensors`` files.

    Parameters
    ----------
    index_path:
        Path to the ``*.safetensors.index.json`` file referencing shard files.
    """
    p = Path(index_path)
    data = json.loads(p.read_text())
    shards = sorted(set(data.get("weight_map", {}).values()))
    base = p.parent
    state_dict: dict[str, torch.Tensor] = {}
    for name in shards:
        state_dict.update(load_file(str(base / name)))
    return state_dict
