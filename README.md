<div align="center">

# EW Threat Detection

**Military-Grade Electromagnetic Intelligence & Source Localization System**

[![Architecture: Blueprint](https://img.shields.io/badge/architecture-blueprint-000000.svg?style=flat-square)](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM)
[![Standard: High--Integrity](https://img.shields.io/badge/standard-high--integrity-000000.svg?style=flat-square)](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM)
[![Tooling: Ruff](https://img.shields.io/badge/tooling-ruff-000000.svg?style=flat-square)](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM)

English | [简体中文](./README_ZH.md)

</div>

---

## Introduction

**EW Threat Detection** is a distributed tactical platform for high-precision localization of electromagnetic interference. Utilizing a Blueprint-based Flask architecture and automated quality scoring, the system provides a modular foundation for military-grade threat assessment.

---

## Technical Specifications

<details>
<summary><b>Decoupled Architecture</b></summary>

The system has been refactored into modular Blueprints for maximum maintainability:
- **API Blueprint:** `modules/api_routes.py` (Core localization and simulation logic).
- **UI Blueprint:** `modules/ui_routes.py` (Tactical dashboard and static rendering).
- **Factory Pattern:** `app.py` serves as a clean entry point for component initialization.
</details>

<details>
<summary><b>Integrity Verification</b></summary>

Automated tests ensure the reliability of tactical calculations:
- `tests/test_location.py`: Validates positioning algorithm accuracy.
- `tests/test_anomaly.py`: Verifies Z-score and IQR-based anomaly detection logic.
</details>

<details>
<summary><b>Deployment Standard</b></summary>

### Prerequisites
- Python 3.8+
- Modern project management via `pyproject.toml`

### Setup
```bash
# Install tactical dependencies
pip install -r requirements.txt

# Launch mission control
python run.py
```
</details>

---

<div align="center">

&copy; 2026 AsaqeLee. Engineered for electromagnetic superiority.

</div>
