# 🦌 StillHunter Prep

A practice app for Hungarian hunter exam candidates. The exam requires identifying wildlife species from a 200-image pool, assessing trophy age groups, and determining harvestability — all under time pressure. This app replicates that experience for study and practice.

## Features

- **Practice** — Random images with free-text or multiple choice answers
- **Exam Simulation** — 15 images with official composition (5 trophy + 3 non-trophy big game + 4 small game + 2 protected + 1 strictly protected), evaluated with official pass/fail rules
- **Trophy Practice** — Species + age group + harvestability assessment for trophy-bearing big game
- **Study** — Browse all species by category and group
- **Statistics** — Accuracy tracking, per-species breakdown, exam history

## Running locally

```bash
# With uv (recommended)
uv sync
uv run streamlit run app.py

# With pip
pip install -r requirements.txt
streamlit run app.py
```

## Running tests

```bash
uv run pytest tests/ -v
```

## Deployment (Streamlit Community Cloud)

1. Push to GitHub
2. Sign in at https://share.streamlit.io
3. Deploy: repo = `sidpromo/stillhunter-prep`, branch = `master`, file = `app.py`

## Project structure

```
├── app.py              # Streamlit app
├── data/species.json   # Species metadata (198 images)
├── images/             # Wildlife photos
├── utils/helpers.py    # Core logic (answer matching, exam composition, evaluation)
├── tests/              # Unit tests (33 tests)
└── generate_species.py # Script to regenerate species.json from filenames
```

## Exam rules

The exam presents 15 images:
- 8 big game (5 trophy-bearing + 3 non-trophy)
- 4 small game
- 2 protected + 1 strictly protected species

**Pass criteria:**
- All big game and small game correctly identified
- At least 2/3 protected species correct (strictly protected must not be missed)
- 4/5 trophy assessments correct (age group + harvestability)

**Instant fail:** confusing a protected species with a huntable one.
