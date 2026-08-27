# BRPI Research Demonstrator
# Research prototype — not for clinical diagnosis or treatment.

## Purpose

Interactive web demonstrator for the **Bivariate Reflux Probability Instrument (BRPI)** concept:
symptom **frequency** and **intensity** are retained as separate dimensions inside an
illustrative logistic equation. This software does **not** diagnose GERD, recommend treatment,
or claim clinical validation.

Specification: [`doc/BRPI_research_demonstrator_build_proposal.md`](doc/BRPI_research_demonstrator_build_proposal.md)

## Stack

- Python 3.12+ (tested with 3.14) / Django 5.2 LTS
- SQLite for local demonstration
- Bootstrap 5 + Plotly.js
- Session-based assessment (no personally identifying data in demonstration mode)

## Quick start

```powershell
cd "e:\papers\GERD diagnosis"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Tests

```powershell
python manage.py test tests
```

The paper-example acceptance test requires:

| Inputs | Expected |
|---|---|
| HF=5, HI=6, RF=4, RI=5, N=2, P=1, S=1, E=1 | η ≈ 1.86, probability ≈ 0.8653 (displayed 0.87), high-probability demonstration zone |

## Workflow

1. Landing — paper example or interactive exploration  
2. Intended-use acknowledgement  
3. Safety / alarm-feature screen (any Yes → no probability)  
4. Seven-day symptom questionnaire  
5. Review  
6. Illustrative report (gauge, contributors, frequency curves, bivariate surface)

## Project layout

```text
├── doc/                      # manuscripts & build proposal
├── config/                   # Django settings / URLs
├── core/                     # landing, about
├── questionnaire/            # forms & constants
├── assessment/               # session workflow
├── model_registry/           # versioned metadata + calculation engine
│   └── engine/               # Django-independent predict() API
├── reports/                  # demonstration report
├── templates/ · static/
├── tests/
├── manage.py
└── requirements.txt
```

## Safety

Every major page shows:

> Research prototype—not for clinical diagnosis or treatment…

Demonstration zones (0.20 / 0.80) are illustrative only. Interactive mode never fabricates a
statistical uncertainty interval; the paper-example mode may show the manuscript’s prewritten
0.74–0.94 illustration, clearly labelled as such.

## Production notes

Set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS` via environment
variables. Use PostgreSQL in deployed research environments. Run `python manage.py check --deploy`
before any hosted release. Do not enable identifiable research data collection without ethics approval.
