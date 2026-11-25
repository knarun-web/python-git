# tap-python — Olist Data Pipeline

A day-by-day Python learning project built on the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Project Structure

```
tap-python/
├── config/
│   ├── config.yaml          # paths, thresholds, file lists
│   └── column_mapping.json  # column rename rules
├── notebooks/
│   ├── day_11.ipynb         # CSV reading with the csv module
│   ├── day_12.ipynb         # Modular functions, type hints, pytest
│   ├── day_13.ipynb         # Data validation, custom exceptions, bad records
│   ├── day_14.ipynb         # Logging, config-driven pipeline, manifest
│   └── day_15.ipynb         # Capstone: full pipeline review
├── src/
│   ├── reader.py            # read_csv() → list of dicts
│   ├── validator.py         # snake_case, column mapping helpers
│   ├── validator13.py       # Row validation, file-level checks, bad records
│   ├── transformer.py       # Type conversion, order totals
│   ├── schema.py            # SchemaError, FileFormatError, SCHEMA definitions
│   └── pipeline.py          # Logging, config loading, output writing, manifest
├── tests/
│   ├── conftest.py          # Adds src/ to sys.path
│   ├── test_day12.py        # Tests for reader, validator, transformer
│   └── test_day13.py        # Tests for schema validation logic
├── data/                    # Raw CSVs — NOT committed (see .gitignore)
├── requirements.txt
└── .gitignore
```

## Setup

**Requirements:** Python 3.11+, Git

```bash
# 1. Clone the repo
git clone https://github.com/knarun-web/python-git.git
cd python-git

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the dataset
# Download from: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Place all CSV files in the data/ folder
```

## Running the Notebooks

```bash
jupyter lab
```

Open any notebook from the `notebooks/` folder and run all cells.

The pipeline reads from `config/config.yaml` — no hardcoded paths anywhere.

## Running Tests

```bash
pytest tests/ -v
```

## Adding a New CSV File (Task 10 — Live Reviewer Challenge)

If a reviewer adds a new CSV with extra or differently-named columns:

1. Add the file to `data/`
2. Add its name to `files:` in `config/config.yaml`
3. Add its required fields under `pipeline.required_fields` in `config/config.yaml`
4. Add any new column renames to `config/column_mapping.json`
5. Re-run `notebooks/day_15.ipynb` — the pipeline picks it up automatically

No Python code changes needed.

## Git Workflow

Each day's work lives on its own feature branch, merged to `main` via a Pull Request:

```
main ← PR#1 (day11) ← PR#2 (day12) ← PR#4 (day13) ← PR#5 (day14) ← PR#6 (day15)
```