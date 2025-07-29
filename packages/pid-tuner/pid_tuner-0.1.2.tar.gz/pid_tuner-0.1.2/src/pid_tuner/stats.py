# src/pid_tuner/stats.py
#!/usr/bin/env python3
"""
stats.py – high‐level summary and utility functions for PID Tuner.
"""

import pandas as pd
from typing import List
from rich.console import Console
from rich.table import Table

from .parser import load_log
from .plotter import detect_spikes


def compute_spike_summary(df, axis, window, threshold_factor):
    """
    - count:   number of spikes
    - avg_d:   average absolute D-term at those spikes
    - max_d:   maximum absolute D-term at those spikes
    """
    spikes = detect_spikes(df, axis=axis, window=window, threshold_factor=threshold_factor)

    # <— if no spikes (or no d_value column), just return zeros
    if spikes.empty or "d_value" not in spikes.columns:
        return {"count": 0, "avg_d": 0.0, "max_d": 0.0}

    mags   = spikes["d_value"].abs()
    count  = len(spikes)
    return {
        "count": count,
        "avg_d": mags.mean(),
        "max_d": mags.max()
    }

def spike_summary(
    log: str,
    axes: List[str] = ["roll", "pitch", "yaw"],
    window: int = 50,
    threshold: float = 2.0
) -> None:
    """
    Load a single Blackbox CSV log, detect spikes on each axis, and print a nice summary table.

    Parameters
    ----------
    log : str
        Path to a Blackbox CSV file.
    axes : List[str]
        List of axes to analyze (e.g., ['roll','pitch','yaw']).
    window : int
        Rolling‐std window size (in samples) for spike detection.
    threshold : float
        Spike threshold as N×σ of the rolling std.
    """
    df = load_log(log)
    # total flight time
    start = df['time_us'].iloc[0]
    end = df['time_us'].iloc[-1]
    duration_s = (end - start) / 1_000_000

    console = Console()
    table = Table(title="PID Spike Summary")
    table.add_column("Axis", style="bold")
    table.add_column("Time (s)", justify="right")
    table.add_column("Spikes", justify="right")
    table.add_column("Rate (spikes/s)", justify="right")
    table.add_column("Avg |D|", justify="right")
    table.add_column("Max |D|", justify="right")
    table.add_column("Avg Throttle", justify="right")

    for axis in axes:
        stats = compute_spike_summary(df, axis, window, threshold)
        rate = stats['count'] / duration_s if duration_s else 0.0
        # approximate throttle at spikes if available
        if 'rcCommand[3]' in df.columns and stats['count'] > 0:
            thr = (
                df.set_index('time_us')
                  .loc[detect_spikes(df, axis, window, threshold)['time_us'], 'rcCommand[3]']
            )
            thr_pct = ((thr - thr.min()) / (thr.max() - thr.min()) * 100).mean()
        else:
            thr_pct = 0.0

        table.add_row(
            axis,
            f"{duration_s:.1f}",
            str(stats['count']),
            f"{rate:.2f}",
            f"{stats['avg_d']:.1f}",
            f"{stats['max_d']:.1f}",
            f"{thr_pct:.1f}%",
        )

    console.print(table)
