import os
import shutil
from pathlib import Path

import typer

from .compare import compare_logs

app = typer.Typer(help="PID-Tuner: extract, compare, and plot Blackbox logs.")

@app.command()
def compare(
    directory: Path = typer.Argument(
        ..., exists=True, file_okay=False, dir_okay=True, readable=True,
        help="Path to folder of .bbl files"
    ),
    axes: list[str] = typer.Option(
        ["roll", "pitch"], "--axes", "-a",
        help="Which axes to analyze (comma‐separated)"
    ),
    window: int = typer.Option(
        50, "--window", "-w",
        help="Window size for spike detection"
    ),
    threshold: float = typer.Option(
        2.0, "--threshold", "-t",
        help="Spike detection threshold factor"
    ),
    out_dir: Path = typer.Option(
        Path("pid_tune"), "--out-dir", "-o",
        help="Where to put decoded CSVs, graphs, summary"
    ),
    clean: bool = typer.Option(
        False, "--clean",
        help="Remove intermediate decoded/ folder after running"
    ),
):
    """
    1) Decode all .bbl → .csv/.event under out_dir/decoded  
    2) Compute spikes & metrics → graphs + compare_summary.csv in out_dir  
    3) If --clean: delete that entire decoded/ subfolder  
    """
    # make sure the output directory exists
    os.makedirs(out_dir, exist_ok=True)
    decoded_dir = out_dir / "decoded"

    # do the work (decode → analyze → plot → summary.csv)
    compare_logs(
        directory=str(directory),
        axes=axes,
        window=window,
        threshold=threshold,
        out_dir=str(out_dir),
    )

    # optionally clean up all the intermediate CSVs/events
    if clean and decoded_dir.exists():
        shutil.rmtree(decoded_dir)
        typer.echo(f"🧹 Removed intermediate files: {decoded_dir}")

if __name__ == "__main__":
    app()
