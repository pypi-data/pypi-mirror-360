from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List
import sys
from tqdm import tqdm

import torch
from safetensors.torch import load_file, save_file


def _tensor_size(t: torch.Tensor) -> int:
    return t.element_size() * t.numel()


def split_file(
    path: str,
    *,
    num_shards: int | None = None,
    shard_size: int | None = None,
    output_dir: str | None = None,
    progress: bool = True,
) -> Path:
    """Split a ``.safetensors`` checkpoint into multiple shards.

    Parameters
    ----------
    path:
        Input checkpoint file.
    num_shards:
        Desired number of shards. Mutually exclusive with ``shard_size``.
    shard_size:
        Target shard size in bytes. Mutually exclusive with ``num_shards``.
    output_dir:
        Destination directory for shards and index. Defaults to the
        directory of ``path``.
    progress:
        Display a progress bar when ``True`` and stderr is a TTY.
    """
    if (num_shards is None) == (shard_size is None):
        raise ValueError("Specify exactly one of num_shards or shard_size")

    src = Path(path)
    out_dir = Path(output_dir) if output_dir is not None else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    state = load_file(str(src))
    total_size = sum(_tensor_size(t) for t in state.values())

    if shard_size is None and num_shards is not None:
        shard_size = math.ceil(total_size / num_shards)
    assert shard_size is not None

    shards: List[Dict[str, torch.Tensor]] = []
    current: Dict[str, torch.Tensor] = {}
    current_size = 0

    items = list(state.items())
    iterable: list[tuple[str, torch.Tensor]] | tqdm = items
    if progress and sys.stderr.isatty():
        iterable = tqdm(iterable)
    for name, tensor in iterable:
        size = _tensor_size(tensor)
        if current and current_size + size > shard_size:
            shards.append(current)
            current = {}
            current_size = 0
        current[name] = tensor
        current_size += size
    if current:
        shards.append(current)

    count = len(shards)
    weight_map: Dict[str, str] = {}
    base = src.stem
    pairs = list(enumerate(shards, start=1))
    iterable2: list[tuple[int, Dict[str, torch.Tensor]]] | tqdm = pairs
    if progress and sys.stderr.isatty():
        iterable2 = tqdm(iterable2)
    for idx, shard in iterable2:
        filename = f"{base}-{idx:05d}-of-{count:05d}.safetensors"
        for key in shard:
            weight_map[key] = filename
        save_file(shard, str(out_dir / filename))

    index_path = out_dir / f"{base}.safetensors.index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"metadata": {"total_size": total_size}, "weight_map": weight_map}, f)

    return index_path


def merge_shards(index_file: str, *, progress: bool = False) -> Dict[str, torch.Tensor]:
    """Load tensors from shards referenced by ``index_file``."""
    idx_path = Path(index_file)
    with open(idx_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    weight_map: Dict[str, str] = index["weight_map"]
    out: Dict[str, torch.Tensor] = {}
    shard_list = sorted(set(weight_map.values()))
    iterable3: list[str] | tqdm = shard_list
    if progress and sys.stderr.isatty():
        iterable3 = tqdm(iterable3)
    for shard in iterable3:
        data = load_file(str(idx_path.parent / shard))
        out.update(data)
    return out


def merge_to_file(index_file: str, output_path: str, *, progress: bool = False) -> None:
    """Merge shards referenced by ``index_file`` and write to ``output_path``.

    Parameters
    ----------
    index_file:
        Path to the ``*.safetensors.index.json`` file.
    output_path:
        Destination for the merged checkpoint.
    progress:
        Display a progress bar when ``True`` and stderr is a TTY.
    """
    tensors = merge_shards(index_file, progress=progress)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    save_file(tensors, str(output_path))
