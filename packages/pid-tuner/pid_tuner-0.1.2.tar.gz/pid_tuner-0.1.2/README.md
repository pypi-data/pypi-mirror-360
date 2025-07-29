# pid-tuner

> 🛠️ **FPV PID Tuner** — A professional CLI toolkit for analyzing and tuning PID on FPV drones. Plot gyro vs. PID outputs, zoom in on D‑term spikes, compare flight logs, and get data‑driven tuning suggestions.

[![PyPI Version](https://img.shields.io/pypi/v/pid-tuner)](https://pypi.org/project/pid-tuner)
[![Python](https://img.shields.io/pypi/pyversions/pid-tuner)](https://pypi.org/project/pid-tuner)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://github.com/bmags73/pid-tuner/actions/workflows/ci.yml/badge.svg)](https://github.com/bmags73/pid-tuner/actions)

---

## 🔍 Features

* **Summary**: runtime, total spikes, spike rate, avg & max |D‑term|, and avg throttle at spike times.
* **Plot**: gyro vs. PID output curves; zoomed views of D‑term spikes; optional throttle overlay.
* **Spikes**: detect, filter, page through spike events; export CSVs for detailed analysis.
* **Future**: compare multiple logs side‑by‑side; automated tuning recommendations; Betaflight integration.

---

## 1. Installation

**Requires:** Python 3.8+.

### From PyPI

```bash
pip install pid-tuner
```

### From Source (editable)

```bash
git clone git@github.com:bmags73/pid-tuner.git
cd pid-tuner
pip install -e .
```

---

## 2. Quickstart Guide

Place your Blackbox CSV logs in any folder and run commands against them:

### a) Summary of PID Spikes

```bash
pid-tuner summary \
  --log logs/sample1.csv \
  --axes roll,pitch \
  --window 50 \
  --threshold 2.0
```

### b) Generate Plots

```bash
pid-tuner plot \
  --axes roll,pitch,yaw \
  --overlay-throttle \
  --out-dir graphs/
```

### c) Browse Spike Details

```bash
pid-tuner spikes \
  --axes roll,pitch \
  --min-mag 30 \
  --time-window 0.5,2.0 \
  --page 1 \
  --per-page 20
```

---

## 3. Advanced Usage

### 3.1 Batch Processing Multiple Logs

You can quickly analyze a whole directory of Blackbox CSVs with a simple shell loop:

```bash
for log in logs/*.csv; do
  echo "Processing $log"
  pid-tuner summary --log "$log" --axes roll,pitch,yaw --window 50 --threshold 2.0
  pid-tuner plot    --log "$log" --axes roll,pitch,yaw --out-dir graphs/
  pid-tuner spikes  --log "$log" --axes roll,pitch,yaw --min-mag 30 --time-window 0.5,2.0
done
```

### 3.2 Configuration File Support (Upcoming)

Define your analysis parameters in `config.yml` or `config.json` to run as:

```bash
pid-tuner batch --config config.yml
```

```yaml
# config.yml
logs:
  - logs/flight1.csv
  - logs/flight2.csv
axes: [roll, pitch, yaw]
threshold: 2.5
window: 60
out_dir: graphs/
```

*(This feature is under development — contributions welcome!)*## 4. Contribution & API Reference

### API Docs

Generate API reference with Sphinx + mkdocstrings:

```bash
pip install sphinx mkdocstrings
sphinx-quickstart docs
# update docs/conf.py and index.rst as needed
sphinx-build docs docs/_build/html
```

### Contributing

* Fork the repo and create feature branches.
* Run `pytest` to ensure all tests pass.
* Update/add docstrings and tests for new features.
* Submit a Pull Request with clear description and screenshots.

---

## 5. License

MIT © [bMagSquatch](https://github.com/bmags73)
