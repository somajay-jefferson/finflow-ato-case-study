# AI-Usage Log

**Tool:** Claude Code (Opus 5), in the terminal / VS Code.
**Deliverables it touched:** `analysis.ipynb`, the interactive dashboard, this log.

---

## 1. Researching and understanding the problem

- Extracted the text from `FinFlow_Candidate_Brief.pdf` and had it summarise the setup,
  the three label fields and the deliverables.
- Had it profile the two CSVs before I formed any hypothesis: shapes, dtypes, null
  counts, cardinality, and whether the `session_id` join actually holds.
- Used it as a sounding board on the **label semantics** — what `dispute_flag`,
  `ops_review_result` and `txn_fraud_label` each mean and when each becomes available.
  That conversation is what produced the leakage rules I worked under.
- Asked it to check my own hypotheses rather than confirm them. When I suggested the
  attacker's device might belong to a shared bookkeeper serving all five customers, it
  tested and disproved it — the devices have **zero history before 22 April**.

_[Danny: ]_

## 2. Data processing, coding, and model building

- **Standing instructions before any code.** Wrote `CLAUDE.md` first: the 4-hour cap, the
  leakage rules, time-based splits, fixed seeds, notebook runs top to bottom. Then had it
  build `analysis.ipynb` section by section at my pace, rather than hand me a finished file
  I had not watched being made.
- **Point-in-time features only.** New device, new country, MFA-failure counts, running
  device-to-customer counts and expanding per-customer medians, every one derived from
  `login_ts` so nothing uses information that did not exist when the payment was submitted.
- **Join integrity as `assert`, not `print`,** so a broken join stops the notebook instead
  of quietly producing a wrong number. `session_id` is the key: **0 payments without a
  session, 1,944 sessions (2.7%) without a payment,** and a `validate="m:1"` merge returning
  exactly 184,432 rows. The same checking turned up a limit worth knowing — no payment
  ever lands more than **99 minutes** after its login, so sessions here are capped in a way
  real AP sessions are not, which bounds anything session-scoped.
- **Compared two model framings** — score the payment, or score the login session — on a
  time-based split, with ablations to show which features were actually load-bearing.
- **The sharpest finding came from a chart, not a model.** Rebuilding the break-in timeline
  around episodes showed **June was not a break-in at all**: zero failed MFA challenges
  across the three repeat-victim accounts, against 46 in April. So the MFA lockout cannot
  fire on the second wave; it prevents that money only by locking the account back in April.
  A real qualification on its 95.7%, and I only found it by asking why a chart showed one
  episode when three customers were hit twice.

_[Danny: ]_

## 3. Verifying AI output

**Standing checks**

- Any number that could reach a slide is recomputed a second way before it counts.
- Join sanity every time: row counts before/after, orphans, user/org consistency.
- I built a harness that **executes every code block on the dashboard** against the real
  CSVs and compares the values in its comments to what actually runs.
  Current state: **80/80 values verified, 24/24 blocks executable.**
- Audited the published dashboard end to end against the CSVs, recomputing every headline
  from scratch — the payment and session counts, the $5.86M, the five victim orgs,
  precision and recall, the four-indicator sweep. **All reproduced.** Every defect it
  turned up sat in the prose or the chart maths, never in the analysis underneath.

**The pattern worth naming:** none of the errors below threw an exception. Every one
produced a confident, plausible, wrong answer.

**Three modes, not one.** Recomputing a number catches one class of error: the arithmetic
is wrong. Reading for sense catches the other, where the arithmetic is fine and the
sentence sitting on top of it is not. So the checking ran three ways.

- **Independent investigation, then reconciliation** — early on, while I was still
  deciding what was true. I worked the data myself alongside it and compared conclusions,
  rather than take its first pass as the starting point.
- **Delegation with sampled query checks** — once we had agreed on the picture. It led;
  I pulled queries at intervals and ran them myself.
- **A standing read-for-sense pass** over everything it produced, asking one question of
  every claim: does this sentence match what the code actually establishes?

**The third mode is the one that earned its keep.** Four examples, every one caught by
reading rather than recomputing:

- *“Isn't there 2 break-ins?”* The chart was anchored on the first episode. Chasing that
  surfaced that **June was not a break-in at all** — zero failed MFA challenges against 46
  in April — a real qualification on the lockout's 95.7% that nothing else had caught.
- *“MFA passing in June is expected if the device is familiar.”* It had written that the
  April credentials still worked, asserting a cause this data does not record. An
  over-claim, not a wrong number.
- *“So a login attempt on that device but not a fraud session is marked as deterred?”*
  The comment said "blocked." The code said "did not move money." Both were true, but the
  code had not earned the word.
- *“Is 'I' Danny or Claude?”* Two rows had the attribution backwards, crediting me with
  work it had done.

Every one is the same shape: **the computation was correct and the sentence describing it
was not.** Recomputation would not have caught any of them, because the numbers were real.

### Where the AI was wrong

| What happened | How it was caught | Outcome |
|---|---|---|
| **A feature that leaked the future.** "Device seen at more than one customer" was computed over all 90 days, so it knew a device would *later* appear elsewhere. Reported **100% recall at 100% precision**. | The perfect score is what made me look. At the moment of the first fraudulent payment that device had only been seen at one customer — the rule could not have fired. | Rebuilt as a forward pass. Recall fell to 95.4%. |

Nine other defects were caught and fixed the same way. Among them: an MFA-burst feature that returned exactly 0% recall, which proved to be an index-alignment bug rather than a dead signal; a headline that used a conditional-upside figure as if it were the baseline; a chart that offered a circular row as evidence; and an over-claim about credential rotation that I caught in conversation.

### Where I disagreed and was right

| What I pushed back on | What changed |
|---|---|
| I suggested "foreign **and new for that user**" instead of a plain foreign-login count. | It replaced the weaker indicator. The org-level score went from a continuous spread to **two clusters with nothing between them** — 100 customers at zero, five at four — so the alert threshold stopped being a judgement call. |

Four other pushbacks changed the deliverable, the largest being the cross-customer headline: I asked how FinFlow could have known on 22 April when the customer's report came later, and with no dispute or review timestamp anywhere in the data it dropped from **$5.20M** to the **$2.52M** that survives the question.

_[Danny: ]_
