#!/usr/bin/env python3

import typer
from .parser import load_log
from .plotter import plot_pid_vs_gyro, plot_dterm_spikes, detect_spikes
from .stats import spike_summary
from rich.console import Console
from rich.table import Table

app = typer.Typer()


@app.command("summary")
def summary(
    log: str = typer.Option(
        "logs/sample_log.csv", "--log", "-l",
        help="Path to your Blackbox CSV file"
    ),
    axes: List[str] = typer.Option(
        ["roll", "pitch", "yaw"], "--axes", "-a",
        help="Which axes to include in the summary"
    ),
    window: int = typer.Option(
        50, "--window", "-w",
        help="Rolling‐std window size (in samples) for spike detection"
    ),
    threshold: float = typer.Option(
        2.0, "--threshold", "-t",
        help="Spike threshold as N×σ of the rolling std"
    ),
):
    """
    Show high-level stats: runtime, number of spikes, spike rate,
    average & max |D-term|, and average throttle at spike times.
    """
    df = load_log(log)

    # Total flight duration in seconds
    start_us = df["time_us"].iloc[0]
    end_us   = df["time_us"].iloc[-1]
    total_time_s = (end_us - start_us) / 1_000_000

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
        n_spikes = len(spikes)
        rate     = n_spikes / total_time_s if total_time_s else 0.0
        mags     = spikes["d_value"].abs()
        avg_mag  = mags.mean() if n_spikes else 0.0
        max_mag  = mags.max()  if n_spikes else 0.0

        if "rcCommand[3]" in df.columns and n_spikes:
            thr_series = (
                df.set_index("time_us")
                  .loc[spikes["time_us"], "rcCommand[3]"]
            )
            thr_pct = (
                ((thr_series - thr_series.min()) /
                 (thr_series.max() - thr_series.min()) * 100)
                .mean()
            )
        else:
            thr_pct = 0.0

        table.add_row(
            axis,
            f"{total_time_s:.1f}",
            str(n_spikes),
            f"{rate:.2f}",
            f"{avg_mag:.1f}",
            f"{max_mag:.1f}",
            f"{thr_pct:.1f}%",
        )

    console.print(table)


@app.command("plot")
def plot(
    log: str = typer.Option(
        "logs/sample_log.csv", "--log", "-l",
        help="Path to your Blackbox CSV file"
    ),
    axes: List[str] = typer.Option(
        ["roll", "pitch", "yaw"], "--axes", "-a",
        help="Which axes to plot"
    ),
    overlay_throttle: bool = typer.Option(
        False, "--overlay-throttle", "-o",
        help="Overlay rcCommand[3] (throttle) on the D-term spike plots"
    ),
    out_dir: str = typer.Option(
        "graphs", "--out-dir",
        help="Directory to save plots"
    ),
):
    """
    Generate PID vs gyro and D-term zoom plots.
    """
    df = load_log(log)
    os.makedirs(out_dir, exist_ok=True)

    for axis in axes:
        typer.secho(f"Plotting {axis}…", bold=True)
        plot_pid_vs_gyro(df, axis=axis)
        plot_dterm_spikes(df, axis=axis, overlay_throttle=overlay_throttle)


@app.command("spikes")
def spikes_cmd(
    log: str = typer.Option(
        "logs/sample_log.csv", "--log", "-l",
        help="Path to your Blackbox CSV file"
    ),
    axes: List[str] = typer.Option(
        ["roll", "pitch", "yaw"], "--axes", "-a",
        help="Which axes to process"
    ),
    window: int = typer.Option(
        50, "--window", "-w",
        help="Rolling‐std window size for spike detection"
    ),
    threshold: float = typer.Option(
        2.0, "--threshold", "-t",
        help="Spike threshold as N×σ"
    ),
    min_mag: float = typer.Option(
        0.0, "--min-mag",
        help="Filter out spikes with abs(D) < this value"
    ),
    time_window: str = typer.Option(
        None, "--time-window",
        help="Time window in seconds as two values: start,end"
    ),
    page: int = typer.Option(
        1, "--page",
        help="Which page of results to show"
    ),
    per_page: int = typer.Option(
        10, "--per-page",
        help="Rows per page"
    ),
    out_dir: str = typer.Option(
        "graphs", "--out-dir",
        help="Directory to save spike CSVs"
    ),
):
    """
    Detect spikes, save full CSVs, and page through details.
    """
    df = load_log(log)
    os.makedirs(out_dir, exist_ok=True)
    console = Console()

    for axis in axes:
        spikes = detect_spikes(df, axis=axis, window=window, threshold_factor=threshold)

        # 1) Filter by magnitude
        if min_mag > 0.0:
            spikes = spikes[spikes["d_value"].abs() >= min_mag]

        # 2) Filter by time window (comma-separated "start,end")
        if time_window:
            try:
                start_s, end_s = map(float, time_window.split(","))
            except ValueError:
                typer.secho(
                    "Invalid --time-window format. Use two numbers separated by a comma, e.g. 1,3",
                    fg=typer.colors.RED,
                )
                raise typer.Exit(code=1)

            start_us = start_s * 1_000_000
            end_us   = end_s * 1_000_000
            spikes = spikes[
                (spikes["time_us"] >= start_us) &
                (spikes["time_us"] <= end_us)
            ]

        # 3) Save full CSV
        csv_path = os.path.join(out_dir, f"{axis}_dterm_spikes.csv")
        spikes.to_csv(csv_path, index=False)
        typer.secho(
            f"Saved {len(spikes)} spikes for {axis} → {csv_path}",
            fg=typer.colors.GREEN
        )

        # 4) Pagination
        total = len(spikes)
        pages = (total + per_page - 1) // per_page
        if page < 1 or page > pages:
            typer.secho(
                f"Page {page} out of range (1–{pages}). Showing page 1 instead.",
                fg=typer.colors.YELLOW
            )
            page = 1
        start_idx = (page - 1) * per_page
        end_idx   = start_idx + per_page
        page_df   = spikes.iloc[start_idx:end_idx]

        # 5) Display table
        table = Table(title=f"{axis.capitalize()} Spikes (Page {page}/{pages})")
        table.add_column("Idx",      style="dim", width=4)
        table.add_column("Time (ms)", justify="right")
        table.add_column("D Value",  justify="right")
        table.add_column("Std Dev",  justify="right")
        table.add_column("Throttle", justify="right")

        # Precompute time in ms
        times_ms = (page_df["time_us"] - page_df["time_us"].min()) / 1000.0
        # And throttle %
        thr_pct = None
        if "rcCommand[3]" in df.columns:
            thr = df.set_index("time_us").loc[page_df["time_us"], "rcCommand[3]"]
            thr_pct = (thr - thr.min()) / (thr.max() - thr.min()) * 100

        for i, row in enumerate(page_df.itertuples()):
            tms = f"{times_ms.iloc[i]:.1f}"
            dv  = f"{row.d_value:.1f}"
            sd  = f"{row.std_value:.1f}"
            th  = f"{thr_pct.iloc[i]:.0f}%" if thr_pct is not None else "n/a"
            table.add_row(str(start_idx + i + 1), tms, dv, sd, th)

        console.print(table)


if __name__ == "__main__":
    app()
