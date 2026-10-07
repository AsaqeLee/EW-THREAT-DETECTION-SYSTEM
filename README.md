# EW Threat Detection System

English | [简体中文](./README_ZH.md)

Distributed **electromagnetic interference** detection and source-localization prototype built with Python and Flask. The application exposes localization / simulation APIs and a browser dashboard for experimentation and coursework-style demos.

## Overview

The server is assembled with Flask blueprints:

- **API** — `modules/api_routes.py` (localization and simulation endpoints)
- **UI** — `modules/ui_routes.py` (dashboard and static pages)
- **Factory** — `app.py` / `run.py` as the application entry

Supporting modules include anomaly detection (`modules/anomaly_detector.py`), geodetic helpers, and a data simulator.

## Features / scope

- Blueprint-based Flask layout separating API and UI
- Localization algorithm utilities under `modules/`
- Anomaly scoring helpers (including Z-score / IQR-oriented tests)
- Automated tests under `tests/` (e.g. `test_location.py`, `test_anomaly.py`)
- Frontend assets under `static/` and `templates/`

## Requirements

- Python 3.8+
- Packages listed in `requirements.txt`
- Project metadata in `pyproject.toml` (Ruff / packaging)

## Getting started

```bash
git clone https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM.git
cd EW-THREAT-DETECTION-SYSTEM
pip install -r requirements.txt
python run.py
```

Run tests:

```bash
pytest tests/
```

## Project layout

```text
.
├── app.py
├── run.py
├── modules/
│   ├── api_routes.py
│   ├── ui_routes.py
│   ├── location_algorithm.py
│   ├── anomaly_detector.py
│   └── …
├── static/
├── templates/
├── tests/
└── requirements.txt
```

## Status / limitations

Prototype / research dashboard. It is **not** a certified military or operational EW product. Accuracy depends on sensor geometry and simulated inputs. Prefer measured language when describing results.

## License

MIT. See [LICENSE](LICENSE).
