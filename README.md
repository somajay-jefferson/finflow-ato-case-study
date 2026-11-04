# FinFlow account-takeover case study

A take-home case study for a Risk Data Scientist role at BILL. A customer of FinFlow
(a made-up AP-payments company) says their account got taken over. This repo figures
out what happened, how far it spread, and what FinFlow should do.

The brief is [FinFlow_Candidate_Brief.pdf](FinFlow_Candidate_Brief.pdf). All data is
synthetic.

## What's here

- [outputs/payment_explorer.html](outputs/payment_explorer.html) — the presentation.
  One self-contained page. Download it and open it in a browser. The last tab covers how
  I worked with Claude.
- [analysis.ipynb](analysis.ipynb) — the analysis. Runs top to bottom on a clean kernel.
- [AI_USAGE_LOG.md](AI_USAGE_LOG.md) — how AI was used, and how its output got checked.
- [build_log_rail.py](build_log_rail.py) — copies the AI-usage log into the dashboard's
  side panel. Run it after editing the log.
- [finflow_case_study_data/](finflow_case_study_data/) — the two given CSVs (also in the
  zip). Never edited.

## The data

Two CSVs, logins (~72k) and payments (~184k), joined on `session_id`. 90 days from
April 1, 2026, all times in UTC.

## Running it

Python 3.11 with pandas, numpy, scikit-learn, scipy, matplotlib, seaborn, plotly and
xgboost. Then open `analysis.ipynb` and run all cells.
