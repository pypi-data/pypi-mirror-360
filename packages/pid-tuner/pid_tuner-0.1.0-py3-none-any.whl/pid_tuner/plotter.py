import pandas as pd
import os
import matplotlib.pyplot as plt

def detect_spikes(
        df, 
        axis='roll', 
        window=50, 
        threshold_factor=2.0
    ):

    """
    Return a DataFrame of all D-term spikes for teh given axis.
    Each row has: axis, time_us, d_value (D-term), std_value (rolling std).
    """
    axis_map = {'roll': 0, 'pitch': 1, 'yaw': 2}
    idx = axis_map.get(axis, 0)
    d_col = f'axisD[{idx}]'

    # Compute the rolling standard deviation
    if d_col not in df.columns:
        print(f"⚠ Skipping spike detection for {axis} - {d_col} not found")
        return pd.DataFrame()

    time = df['time_us']
    d_term = df[d_col]

    # compute the rolling standard deviation
    d_std = d_term.rolling(window=window, center=True).std()

    # Threshold: mean + N * std
    threshold = d_std.mean() + threshold_factor * d_std.std()

    # Find all indices where rolling-std exceeds threshold
    spike_idx = d_std[d_std > threshold].index

    # Build event list
    events = []
    for i in spike_idx:
        events.append({
            'axis': axis,
            'time_us': time.iloc[i],
            'd_value': float(d_term.iloc[i]),
            'std_value': float(d_std.iloc[i])
        })

    return pd.DataFrame(events)


def plot_pid_vs_gyro(
        df, 
        axis='roll'
    ):
    axis_map = {'roll': 0, 'pitch': 1, 'yaw': 2}
    idx = axis_map.get(axis, 0)

    # Build column names
    time = df['time_us']
    gyro_col = f'gyroADC[{idx}]'
    pid_p = df[f'axisP[{idx}]']
    pid_d = df.get(f'axisD[{idx}]', 0)  # fallback if missing

    # Total PID output
    pid_total = pid_p + pid_d

    plt.figure(figsize=(12, 6))
    plt.plot(time, df[gyro_col], label='Gyro')
    plt.plot(time, pid_total, label='P + D Output')
    plt.xlabel('Time (µs)')
    plt.ylabel('Degrees/sec')
    plt.title(f'{axis.capitalize()} PID vs Gyro')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs('graphs', exist_ok=True)
    plt.savefig(f'graphs/{axis}_pid_vs_gyro.png')
    print(f"✅ Saved plot to graphs/{axis}_pid_vs_gyro.png")

def plot_dterm_spikes(
        df, 
        axis='roll', 
        zoom_ms=250,
        overlay_throttle=False
    ):
    import numpy as np

    axis_map = {'roll': 0, 'pitch': 1, 'yaw': 2}
    idx = axis_map.get(axis, 0)
    d_col = f'axisD[{idx}]'

    if d_col not in df.columns:
        print(f"⚠  Skipping {axis} — {d_col} not found in log!")
        return

    # Get cleaned columns
    time = df['time_us']
    d_term = df[d_col]

    # Convert time from µs to ms for better granularity
    time_ms = (time - time.min()) / 1000.0

    # Compute moving standard deviation (quick + dirty spike detector)
    window = 50
    d_std = d_term.rolling(window=window).std()

    # Find where D-term exceeds a threshold (tune this!)
    spike_threshold = d_std.mean() + 2 * d_std.std()
    spike_indices = d_std[d_std > spike_threshold].index

    if spike_indices.empty:
        print(f"✅ No significant D-term spikes detected on {axis}")
        return

    # Grab the first spike window to zoom in
    start_idx = max(0, spike_indices[0] - 100)
    end_idx = min(len(df), spike_indices[0] + 100)

    os.makedirs("graphs", exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(
        time_ms[start_idx:end_idx],
        d_term[start_idx:end_idx],
        label='D-Term',
        color='orange'
    )
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('PID D Output')
    ax1.legend(loc='upper left')

    # Overlay throttle on a second y-axis, if requested
    if overlay_throttle and 'rcCommand[3]' in df.columns:
        throttle = df['rcCommand[3]']
        # normalize throttle from raw to percent (assumes range 1000–2000)
        pct = (throttle - throttle.min()) / (throttle.max() - throttle.min()) * 100
        ax2 = ax1.twinx()
        ax2.plot(
            time_ms[start_idx:end_idx],
            pct[start_idx:end_idx],
            label='Throttle (%)',
            linestyle='--'
        )
        ax2.set_ylabel('Throttle (%)')
        ax2.legend(loc='upper right')

    ax1.set_title(f'{axis.capitalize()} D-Term Spike (Zoomed)')
    ax1.grid(True)
    plt.tight_layout()
    plt.xlabel('Time (ms)')
    plt.ylabel('PID D Output')
    plt.title(f'{axis.capitalize()} D-Term Spike (Zoomed)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'graphs/{axis}_dterm_spike.png')
    print(f"⚠  Saved D-term spike zoom to graphs/{axis}_dterm_spike.png")

