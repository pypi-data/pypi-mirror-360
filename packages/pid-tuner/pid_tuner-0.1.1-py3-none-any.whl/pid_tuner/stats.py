#!/usr/bin/env python3
import os
import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from .parser import load_log
from .plotter import detect_spikes

def spike_summary(
    log: str,
    axes: list[str],
    window: int,
    threshold: float,
    out_dir: str | None = None,
):
    """
    Summarize D-term spikes across axes:
      • total time
      • count, rate, avg/max |D|
      • avg throttle (if available)
    Renders a rich table to the console.
    """
    df = load_log(log)
    # total flight time
    start_us = df["time_us"].iloc[0]
    end_us   = df["time_us"].iloc[-1]
    total_s  = (end_us - start_us) / 1_000_000

    console = Console()
    table = Table(title="PID Spike Summary")
    table.add_column("Axis",            style="bold")
    table.add_column("Time (s)",        justify="right")
    table.add_column("Spikes",          justify="right")
    table.add_column("Rate (spikes/s)", justify="right")
    table.add_column("Avg |D|",         justify="right")
    table.add_column("Max |D|",         justify="right")
    table.add_column("Avg Throttle",    justify="right")

    for axis in axes:
        spikes = detect_spikes(df, axis=axis, window=window, threshold_factor=threshold)
        n = len(spikes)
        # rate, magnitudes
        rate    = n / total_s if total_s else 0.0
        mags    = spikes["d_value"].abs()
        avg_mag = mags.mean() if n else 0.0
        max_mag = mags.max()  if n else 0.0

        # throttle at spike times, normalized 0–100%
        if "rcCommand[3]" in df.columns and n:
            thr = (
                df.set_index("time_us")
                  .loc[spikes["time_us"], "rcCommand[3]"]
            )
            thr_pct = ((thr - thr.min()) / (thr.max() - thr.min()) * 100).mean()
        else:
            thr_pct = 0.0

        table.add_row(
            axis,
            f"{total_s:.1f}",
            str(n),
            f"{rate:.2f}",
            f"{avg_mag:.1f}",
            f"{max_mag:.1f}",
            f"{thr_pct:.1f}%"
        )

    console.print(table)
