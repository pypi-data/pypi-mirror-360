import pandas as pd

def load_log(csv_path):
    print(f"Loading log from {csv_path}")
    df = pd.read_csv(csv_path)

    # DEBUG: Show what we've got before strip/replace
    print("▶ Raw columns:", df.columns.tolist())

    # Clean up column names
    df.columns = (
            df.columns 
              .str.strip()                                  # remove leading/trailing whitespaces
              .str.replace(' ', '_')                        # spaces -> underscores
              .str.replace(r'[^\w\[\]\.]+', '', regex=True) # strip weird chars

    )
    print("✔ Normalized columns:", df.columns.tolist())

    print(f"Loaded {len(df)} entries")
    return df
