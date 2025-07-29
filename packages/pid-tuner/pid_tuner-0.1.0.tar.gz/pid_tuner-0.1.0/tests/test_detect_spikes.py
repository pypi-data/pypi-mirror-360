import pandas as pd
from pid_tuner.plotter import detect_spikes

def test_detect_spikes_basic():
    # Synthetic D-term: no spikes for first half, big bump in second
    data = {
        "time_us": [0, 1, 2, 3, 4, 5] * 10,
        "axisD[0]": [0]*30 + [100]*30
    }
    df = pd.DataFrame(data)

    # Use a small window so std on zeros is zero, bump is huge
    spikes = detect_spikes(df, axis="roll", window=5, threshold_factor=3.0)

    # All detected spikes should have significant D-term values
    assert spikes["d_value"].abs().max() >= 100
    # Ensure the DataFrame has the expected columns
    assert set(spikes.columns) >= {"axis", "time_us", "d_value", "std_value"}
