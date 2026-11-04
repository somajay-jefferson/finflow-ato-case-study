# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

For what the analysis does and how to run it, read [README.md](README.md) — it's
kept current and this file won't repeat it. This file is about how to work in
this repo, not what's in it.

## What this repo is

A take-home case study for a **Risk Data Scientist** interview at BILL. The
prompt is [FinFlow_Candidate_Brief.pdf](FinFlow_Candidate_Brief.pdf): a customer
of a (fictional) AP-payments company called FinFlow says their account got taken
over. Figure out what happened, how far it spreads, and what FinFlow should do.

The brief sets three hard constraints that shape every decision here:

- **2–4 hours of work, do not exceed 4.** Depth beats breadth. If something
  would take an hour and only maybe pays off, skip it and write down that we
  skipped it.
- **AI use is allowed and encouraged, but must be logged.** There is a required
  AI-usage log deliverable (see below). Assume anything Claude does here ends up
  described in that log.
- **Everything has to be defensible in a 45-minute panel.** If I can't explain a
  line of code or a number out loud, it shouldn't be in the deliverable. Prefer
  the simpler method that's easy to defend over the fancier one that isn't.

Three deliverables are due:

1. Code / notebook that runs top to bottom, no manual fixups.
2. A presentation: ~10 min of findings, then panel Q&A.
3. An AI-usage log in four parts — research, coding/modeling, slide prep, and
   how AI output got verified (must include at least one example where the AI
   was wrong or I disagreed with it).

## Response style

- Keep it succinct and precise. No filler, no restating what was just
  discussed, no summarizing the repo back before acting.
- Write like a college freshman talks: plain words, short sentences, casual
  tone. Skip the jargon and the corporate-sounding phrasing. This goes for
  code comments, README text, and slide copy too, not just chat replies.
- Confirm before anything hard to reverse or visible outside this machine:
  `git push`, creating/deleting a GitHub repo, changing repo visibility,
  force-push, rewriting history, emailing or uploading anything to the
  recruiter. Everything else (local edits, running scripts, `git add`/`commit`
  locally) can proceed without asking.
- Say it out loud when a change affects a **deliverable** — a number on a slide,
  a headline finding, the model's reported performance. Don't let those shift
  silently; I have to defend them in the panel.
- When there's a judgment call in the analysis (a threshold, a cutoff, a
  definition of "compromised"), state the assumption plainly instead of burying
  it. Assumptions are an explicit part of the grade.

## Data

Two CSVs in [finflow_case_study_data/](finflow_case_study_data/), joined on
`session_id`. All synthetic, no real PII, safe to paste snippets of into chat.

- `logins.csv` (~72k rows) — one row per session: user, org, timestamp, device
  fingerprint, IP country/region, VPN flag, new-device flag, MFA
  triggered/result, success flag.
- `transactions.csv` (~184k rows) — one row per payment: org, user, timestamp,
  amount, currency, transfer type (ACH / wire / virtual card / international
  wire / check), vendor, when the vendor was added, vendor bank country,
  new-bank-account flag, approval-bypassed flag, `session_id`, and three label
  fields.

Timestamps are UTC. Data covers ~90 days starting 2026-04-01.

Never edit the CSVs or the zip. They're the given inputs. Anything derived goes
in a separate file.

## The three labels (read this before touching modeling)

The brief documents three label fields on purpose, and mixing them up is the
main trap in this exercise:

- `dispute_flag` — the customer complained. Customer-initiated, so it only
  exists when someone *noticed*, and it lags the transaction by days or weeks.
- `ops_review_result` — outcome of a risk-ops review
  (`cleared` / `low_risk` / `high_risk` / `confirmed_fraud`). **Null when ops
  didn't review the transaction**, and ops does not review everything. Null is
  not "clean," it's "unknown."
- `txn_fraud_label` — final adjudicated outcome after full investigation. Best
  ground truth in the dataset, but in real life it arrives long after the money
  moved.

Rules that follow from that:

- `txn_fraud_label` is the training/eval target. `dispute_flag` and
  `ops_review_result` are **not** features — they're downstream of the fraud
  being discovered, so using them as inputs leaks the answer. If a feature would
  not have existed at the moment the payment was submitted, it can't be a
  feature. Call this out if it sneaks in.
- Don't treat `ops_review_result` nulls as negatives. Say what was done with
  them instead.
- Evaluate on the point-in-time question ("score this payment as it comes in"),
  not the hindsight one.

## Coding conventions

- Python 3.11. Installed and ready: `pandas` 3.0.5, `numpy` 2.4.6,
  `scikit-learn` 1.9.0, `scipy` 1.17.1, `matplotlib` 3.11.1, `seaborn` 0.13.2,
  `plotly` 7.0.0, `xgboost` 3.2.0, and Jupyter (`notebook` 7.6.2). Don't add
  anything past that list without checking first.
- Having xgboost available doesn't mean reach for it. Start with logistic
  regression or a small tree — it's easier to explain a coefficient to the panel
  than a boosted ensemble. Move up only if the simple model clearly isn't
  enough, and be ready to say why.
- Static plots (matplotlib/seaborn) for anything going on a slide. Plotly is
  fine for poking at the data in the notebook, but interactive charts don't
  survive a screenshot.
- Analysis lives in a notebook or a script that runs **top to bottom on a clean
  kernel**. No cells that only work if run out of order, no hand-patched state.
  That's a stated grading criterion.
- Load the CSVs from their relative path, not an absolute `F:\...` path. The
  panel may run this on their own machine.
- Set a random seed anywhere there's randomness (train/test split, model init,
  sampling) so the numbers in the slides match a re-run.
- Split by time, not randomly. This is fraud data with a campaign in it —
  a random split lets the model see the future.
- Every number that ends up on a slide should be produced by code in the repo.
  If a figure changes, regenerate the slide asset; don't hand-edit it to match.
- Comment the *why*, not the *what*. "capping at 99th pct because 3 orgs have
  million-dollar wires that swamp the scale" is useful; "# cap outliers" isn't.

## Verifying work

- There's no test suite. Verify by running the notebook/script end to end and
  eyeballing the output, not by reading the diff.
- Sanity-check joins every time: row counts before and after, how many
  transactions have no matching session, how many sessions have no transaction.
  A silent inner join dropping rows is the easiest way to get a wrong headline
  number.
- When Claude produces a number that becomes a finding, check it a second way
  (a groupby that should agree, a manual filter on a handful of rows) before it
  goes in a slide.
- Keep a running scratch list of anything surprising or suspicious in the data.
  The brief explicitly asks for it.

## The AI-usage log

[AI_USAGE_LOG.md](AI_USAGE_LOG.md) is a required deliverable, and it gets
written **as we go**, not reconstructed at the end. Its four sections are fixed
by the brief — don't rename or merge them.

- Claude appends a bullet before finishing any turn where it generated real
  code, produced a number that could end up on a slide, or made a judgment call
  on Danny's behalf. Bullets only; the brief says lightweight.
- **Section 4 is the one that rots.** The moment something Claude produced turns
  out to be wrong, write the bullet *before* fixing it, and include what tipped
  us off. That "how did you catch it" part is what the panel will dig into, and
  it's unrecoverable an hour later.
- Division of labor: Claude logs the *facts* (what was asked, what it generated,
  what broke, what the numbers were). Danny writes the *judgment* lines (why he
  accepted, overrode, or rewrote it). The work has to be his to defend, so
  don't put reasoning in his mouth — leave `_[Danny: ]_` stubs instead.
- Backup if we both forget: the raw session transcript lives at
  `~/.claude/projects/f--BILL-Take-home/*.jsonl` and can be mined to fill gaps.
  Use it as a safety net, not the plan.
