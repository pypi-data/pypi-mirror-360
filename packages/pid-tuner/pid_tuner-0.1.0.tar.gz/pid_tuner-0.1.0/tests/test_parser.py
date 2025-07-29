import pandas as pd
import tempfile
from pid_tuner.parser import load_log

def test_load_log_normalizes_columns(tmp_path, capsys):
    # Create a small CSV with messy headers
    csv = tmp_path / "sample.csv"
    df_in = pd.DataFrame({
        " time (us)": [0, 1000],
        " axisP[0]": [1, 2],
        "axisD[0] ": [0.1, 0.2]
    })
    df_in.to_csv(csv, index=False)

    # Load & capture stdout
    df = load_log(str(csv))
    captured = capsys.readouterr()

    # It should print loading info…
    assert "Loading log" in captured.out
    assert "Normalized columns" in captured.out

    # And columns should be renamed to time_us, axisP[0], axisD[0]
    assert list(df.columns) == ["time_us", "axisP[0]", "axisD[0]"]
    # And data preserved
    assert df["axisP[0]"].tolist() == [1, 2]
    assert df["axisD[0]"].tolist() == [0.1, 0.2]
