import sys
from pathlib import Path
from typing import cast, Type

import typer
import torch
from transformers.pipelines import pipeline
from transformers.modeling_utils import PreTrainedModel
from transformers.tokenization_utils import PreTrainedTokenizer

from . import __version__
from .extract import extract_embeddings
from .wrapper import load_wrapped_model
from .logits import SRLogitsProcessor
from .utils import download_checkpoint
from .safetensors import split_file, merge_to_file
from .similarity import build_low_rank_isvd4
from .low_rank_layer import LowRankRedistributor

Modes: Type = LowRankRedistributor.Modes

app = typer.Typer(help="Meaning-Informed Next-token Transformation CLI")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the package version and exit.",
        is_eager=True,
    ),
) -> None:
    """Entry point for the CLI.

    Parameters
    ----------
    ctx:
        Invocation context provided by Typer.
    version:
        When ``True``, print the package version and exit.
    """
    if version:
        typer.echo(__version__)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(
            "Use MINT to pick, chop, crush, extract, blend, and brew checkpoints."
        )
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def pick(
    source: str,
    dest: str = typer.Argument("."),
    progress: bool = typer.Option(True, "--progress/--no-progress"),
) -> None:
    """Download a checkpoint from Hugging Face.

    Parameters
    ----------
    src:
        Hugging Face model ID or direct URL to a checkpoint or index file.
    dest:
        Directory in which to store the downloaded ``model.safetensors``.
    progress:
        Show a progress bar during the download when ``True`` and stderr is a TTY.
    """

    path = download_checkpoint(source, dest, progress=progress)
    typer.echo(str(path))


@app.command()
def extract(
    src: str,
    dest: str,
    progress: bool = typer.Option(True, "--progress/--no-progress"),
) -> None:
    """Extract embedding matrix from a checkpoint.

    Parameters
    ----------
    src:
        Path to the model checkpoint containing embeddings. A
        ``*.safetensors.index.json`` file automatically loads and merges shards.
    dest:
        File in which to store the extracted embeddings.
    progress:
        Show a progress bar when ``True``.
    """

    extract_embeddings(src, dest, progress=progress)


@app.command()
def chop(
    checkpoint: str,
    output_dir: str,
    shards: int | None = typer.Option(None, "--shards", "-n"),
    size_mb: int | None = typer.Option(None, "--size-mb", "-s"),
    progress: bool = typer.Option(True, "--progress/--no-progress"),
) -> None:
    """Split a checkpoint into multiple shards.

    Parameters
    ----------
    checkpoint:
        Path to the input checkpoint file.
    output_dir:
        Directory where shards and the index will be written.
    shards:
        Desired number of shards. Mutually exclusive with ``size_mb``.
    size_mb:
        Target shard size in megabytes. Mutually exclusive with ``shards``.
    progress:
        Show a progress bar when ``True`` and stderr is a TTY.
    """

    size_bytes = size_mb * 1024 * 1024 if size_mb is not None else None
    split_file(
        checkpoint,
        num_shards=shards,
        shard_size=size_bytes,
        output_dir=output_dir,
        progress=progress,
    )
    typer.echo(f"Shards written to {output_dir}")


@app.command()
def blend(
    src: str,
    dest: str,
    cpu: bool = typer.Option(
        False, "--cpu", help="Force CPU even if a GPU is available"
    ),
    gpu: int | None = typer.Option(None, "--gpu", help="Select GPU index to use"),
    sdk: str | None = typer.Option(
        None,
        "--sdk",
        help="Acceleration backend (CUDA, Vulkan, ZLUDA, etc.)",
    ),
    rank: int = typer.Option(
        1024, "--rank", "-r", help="Target rank of the low‑rank factor W"
    ),
    keep_residual: bool = typer.Option(
        False, "--keep-residual", help="Write sparse residual R as well"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print resource estimates and exit"
    ),
) -> None:
    """Build the low-rank similarity factor **W** (and optional residual **R**)\
    for *src* embeddings and write them into *dest*.

    Parameters
    ----------
    src:
        Path to the embeddings tensor to factorize.
    dest:
        Directory where ``W.safetensors`` will be saved.
    cpu, gpu, sdk:
        Device selection flags.
    rank:
        Target rank of the factorization.
    keep_residual:
        When ``True``, also write ``R.safetensors``.
    dry_run:
        Print resource estimates and exit without writing files.
    """

    device = "cpu"
    if not cpu:
        gpu_index = gpu if gpu is not None else 0
        sdks = [sdk.lower()] if sdk is not None else ["cuda"]
        for name in sdks:
            if name == "cuda":
                if torch.cuda.is_available():
                    device = f"cuda:{gpu_index}"
                    break
                continue
            elif name == "vulkan":
                raise typer.BadParameter(
                    "Vulkan backend is not yet supported; coming soon"
                )
            elif name == "zluda":
                raise typer.BadParameter(
                    "ZLUDA backend is not yet supported; coming soon"
                )
            elif name == "rocm":
                raise typer.BadParameter(
                    "ROCm backend is not yet supported; coming soon"
                )
            elif name == "metal":
                raise typer.BadParameter(
                    "Metal backend is not yet supported; coming soon"
                )
            else:
                raise typer.BadParameter(f"Unknown backend: {name}")
    print(f"Chose device {device}")
    build_low_rank_isvd4(
        src,
        dest,
        rank=rank,
        keep_residual=keep_residual,
        device=device,
        dry_run=dry_run,
    )
    if not dry_run:
        typer.echo(str(Path(dest) / "W.safetensors"))


@app.command()
def crush(
    src: str,
    dest: str,
    progress: bool = typer.Option(True, "--progress/--no-progress"),
) -> None:
    """Merge a sharded checkpoint into a single file.

    Parameters
    ----------
    src:
        Path to a ``*.safetensors.index.json`` file.
    dest:
        Destination for the merged ``.safetensors`` checkpoint.
    progress:
        Show a progress bar while merging when ``True`` and stderr is a TTY.
    """

    merge_to_file(src, dest, progress=progress)


@app.command()
def infuse(
    model: str,
    similarity_dir: str,
    dest: str,
    *,
    mode: str = typer.Option(
        "Lerp", help="Mode used to combine similarities with original Logits"
    ),
    alpha: float = typer.Option(
        0.0, help="Demotion strength for original logits", min=0.0, max=1.0
    ),
) -> None:
    """Load a model and attach a redistribution layer.

    Parameters
    ----------
    model:
        Local directory containing the model to modify.
    similarity_dir:
        Directory containing ``W.safetensors`` to load.
    dest:
        Directory where the modified model will be saved.
    mode:
        Mode used to combine similarities with original Logits.
    alpha:
        Demotion strength for the original logits.
    """
    assert alpha >= 0.0 and alpha <= 1e6
    mpath = Path(model)
    if not mpath.exists() or not mpath.is_dir():
        raise typer.BadParameter(f"model must be an existing directory: {model}")

    mdl = cast(
        PreTrainedModel,
        load_wrapped_model(str(mpath), similarity_dir, mode=Modes[mode], alpha=alpha),
    )
    Path(dest).mkdir(parents=True, exist_ok=True)
    mdl.save_pretrained(dest)
    typer.echo(f"Model infused with similarity data saved to {dest}")


@app.command(name="brew")
def generate(
    model: str,
    similarity_dir: str,
    mode: str = typer.Option(
        "Lerp",
        "--mode",
        help="Mode used to combine similarities with original Logits",
    ),
    alpha: float = typer.Option(
        0.5, "--alpha", help="Demotion strength for original logits", min=0.0, max=1.0
    ),
    prompt: str | None = typer.Option("The quick brown fox jumps over the", "--prompt"),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Read prompts from stdin until EOF",
    ),
) -> None:
    """Generate text using a model wrapped with the SR layer.

    Parameters
    ----------
    model:
        Name or path of the model to load.
    similarity_dir:
        Directory containing ``W.safetensors`` to apply.
    prompt:
        Optional prompt passed directly to the model.
    interactive:
        If ``True``, read prompts from ``stdin`` until EOF.
    mode:
        Mode used to combine similarities with original Logits.
    alpha:
        Demotion strength for original logits
    """
    assert alpha >= 0.0 and alpha <= 1e6
    lr_mode = Modes[mode]
    device = (
        torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
    )
    mdl, tokenizer, layer = load_wrapped_model(
        model, similarity_dir, mode=lr_mode, alpha=alpha, device=device
    )
    pipe_device = 0 if device.type == "cuda" else -1
    proc = SRLogitsProcessor(layer, alpha)
    pipe = pipeline(
        "text-generation",
        model=cast(PreTrainedModel, mdl),
        tokenizer=cast(PreTrainedTokenizer, tokenizer),
        device=pipe_device,
    )

    def run(p: str) -> None:
        outputs = pipe(p, logits_processor=[proc])
        typer.echo(outputs[0]["generated_text"])

    if prompt is not None and not interactive:
        print("Generation with similarity transformation:\n")
        run(prompt)
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                break
            print("Generation with similarity transformation:\n")
            run(line)


if __name__ == "__main__":
    app()
