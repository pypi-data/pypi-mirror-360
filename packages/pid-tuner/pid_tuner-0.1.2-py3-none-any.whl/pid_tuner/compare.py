#!/usr/bin/env python3
import os
import subprocess
import glob
import pandas as pd
import matplotlib.pyplot as plt
from shutil import which
from .parser import load_log
from .stats import compute_spike_summary

def compare_logs(
    directory: str,
    axes: list[str],
    window: int,
    threshold: float,
    out_dir: str
) -> pd.DataFrame:
    """
    1) Decode .bbl logs into out_dir/decoded
    2) Move any stray .NN.csv/.NN.event from `directory` into decoded/
    3) Load each CSV, compute per-axis spike stats, and collate into a DataFrame
    4) Save compare_summary.csv and bar plots under out_dir
    """

    # ─── Phase 0: Prep ─────────────────────────────────────────────────────────────
    # flatten comma-separated axes
    axes = [ax.strip() for a in axes for ax in a.split(',')]

    if not which("blackbox_decode"):
        raise RuntimeError(
            "`blackbox_decode` not found in PATH – please install blackbox-tools."
        )

    os.makedirs(out_dir, exist_ok=True)
    decoded_dir = os.path.join(out_dir, "decoded")
    os.makedirs(decoded_dir, exist_ok=True)

    # ─── Phase 1: Decode every .bbl ───────────────────────────────────────────────
    for root, _, files in os.walk(directory):
        for fname in sorted(files):
            if not fname.lower().endswith(".bbl"):
                continue
            src = os.path.join(root, fname)
            print(f"⚙ Decoding {fname}…")
            subprocess.run(
                ["blackbox_decode", src],
                cwd=decoded_dir,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    # ─── Phase 2: Move stray CSV/EVENT files into decoded/ ────────────────────────
    for ext in (".csv", ".event"):
        pattern = os.path.join(directory, f"*.*{ext}")
        for stray in sorted(glob.glob(pattern)):
            dest = os.path.join(decoded_dir, os.path.basename(stray))
            os.replace(stray, dest)

    # ─── Phase 3: Gather all CSVs to process ───────────────────────────────────────
    all_paths = sorted(glob.glob(os.path.join(decoded_dir, "*.csv")))

    # ─── Phase 4: Process logs, compute stats & plots ──────────────────────────────
    records: list[dict] = []

    for log_path in all_paths:
        try:
            df = load_log(log_path)
        except Exception as e:
            print(f"⚠ Failed to load CSV: {log_path}: {e} – skipping.")
            continue

        duration_s = (df['time_us'].iloc[-1] - df['time_us'].iloc[0]) / 1e6
        summary = {
            'filename': os.path.basename(log_path),
            'duration_s': duration_s
        }

        for axis in axes:
            stats = compute_spike_summary(df, axis, window, threshold)
            summary[f"{axis}_spikes"] = stats['count']
            summary[f"{axis}_avg_d"]    = stats['avg_d']
            summary[f"{axis}_max_d"]    = stats['max_d']

        records.append(summary)

    # output summary CSV
    summary_df = pd.DataFrame(records)
    summary_csv = os.path.join(out_dir, "compare_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"✅ Saved comparison summary: {summary_csv}")

    # generate bar plots for each metric & axis
    for metric in ["spikes", "avg_d", "max_d"]:
        for axis in axes:
            col = f"{axis}_{metric}"
            if col not in summary_df.columns:
                continue
            plt.figure()
            summary_df.plot.bar(x="filename", y=col, legend=False)
            plt.title(f"{axis.capitalize()} {metric.replace('_', ' ').title()} per Log")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plot_file = os.path.join(out_dir, f"compare_{axis}_{metric}.png")
            plt.savefig(plot_file)
            plt.close()

    return summary_df
