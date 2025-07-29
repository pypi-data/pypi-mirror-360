# PID Tuner CLI

A command-line toolkit for FPV drone PID analysis, including plotting gyro vs. PID, detecting D-term spikes, and browsing spike data.

## 🚀 Installation

Install into your (virtual) environment:

```bash
# Clone this repo and enter its directory
git clone https://github.com/yourusername/pid_tuner.git
cd pid_tuner

# Activate your venv if not already active
source .venv/bin/activate  # or your shell’s activate script

# Install in editable mode (for development):
pip install -e .

# Or install from PyPI:
pip install pid-tuner
```

## 📦 Package Structure

```
src/pid_tuner/
├── __init__.py       # Package entry point
├── cli.py            # Typer app with subcommands: summary, plot, spikes
├── parser.py         # load_log()
├── plotter.py        # plotting and detect_spikes()
└── stats.py          # (optional) summary logic
```

## 📖 Usage Examples

### 1️⃣ Summary of PID Spikes

Show runtime, total spikes, rate, D-term stats, and average throttle:

```bash
pid-tuner summary --axes roll,pitch --window 50 --threshold 2.0
```

### 2️⃣ Generate Plots

Save gyro vs PID and zoomed D-term spikes (with optional throttle overlay):

```bash
pid-tuner plot --axes roll,pitch --overlay-throttle --out-dir graphs
```

### 3️⃣ Browse Spike Details

Detect D-term spikes, save CSVs, then page through spike events:

```bash
pid-tuner spikes --axes roll,pitch --min-mag 50 --time-window 1,3 --page 1 --per-page 10
```

## 🛠️ API Reference

You can generate an API reference from the built-in docstrings using Sphinx or MkDocs with mkdocstrings. Here's a quick Sphinx setup:

1. Install docs dependencies:

   ```bash
   pip install sphinx mkdocstrings
   ```
2. In your project root, run:

   ```bash
   sphinx-quickstart docs
   ```
3. Edit `docs/conf.py`:

   ```python
   extensions = ['mkdocstrings']
   templates_path = ['_templates']
   ```
4. In `docs/index.rst`, add:

   ```rst
   .. toctree::
      :maxdepth: 2
      :caption: Contents:

      api
   ```
5. Create `docs/api.rst`:

   ```rst
   PID Tuner API
   =============

   .. mdinclude:: ../src/pid_tuner/cli.py
      :language: python
   ```
6. Build HTML:

   ```bash
   sphinx-build docs docs/_build/html
   ```

Now open `docs/_build/html/index.html` for the full API.
