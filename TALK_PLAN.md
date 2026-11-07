# Plan: re-present the FinFlow case study to analyst/DS peers

## Context
New company wants a ~30 min talk (+ Q&A) on the FinFlow case study, focused on
(1) how I work with Claude, (2) HTML as a presentation medium vs their Excel habit,
(3) my thought process. Audience: analysts / DS peers — people who'd copy the workflow.
Decision: the HTML explorer *is* the argument for HTML, so it presents itself.
The only new slides are about the Claude workflow, since that part has no visual yet.

What already exists and gets reused (no rebuild):
- `outputs/payment_explorer.html` — 4 panels (investigation, reach, controls/process, model),
  self-contained, data baked in from `outputs/*.json`.
- `build_log_rail.py` — renders `AI_USAGE_LOG.md` into the explorer's side rail.
- `AI_USAGE_LOG.md` — already has the verification story and the "AI was wrong" table.
- `CLAUDE.md` — the standing instructions; it's the best exhibit for "how I work with Claude".

## Run of show (30 min)
| Min | Block | Medium |
|---|---|---|
| 0–2 | Setup: the brief in one slide, the 3 asks of this talk | new deck, slide 1 |
| 2–12 | **How I work with Claude** | new deck |
| 12–24 | **Thought process, told through the explorer** (doubles as the HTML demo) | live explorer |
| 24–28 | **HTML vs Excel**: what it bought me, what it costs | new deck, 2 slides |
| 28–30 | Takeaways / what I'd do on day one here | new deck |

### Block 1 — How I work with Claude (~1 slides)
Framing: **I let Claude roam free, inside three guardrails.** The guardrails are what
make the freedom safe, so it doesn't need a prompt-by-prompt leash.
1. **Free roam, with guardrails** — one overview slide: the three rails below, and what
   "free roam" means in practice (it reads files, runs code, builds sections on its own).
2. **Guardrail 1 — `CLAUDE.md`** — real excerpt: leakage rules, time split, seeds,
   "every slide number comes from code", "confirm before anything hard to reverse".
   Rules set once, apply to every turn.
3. **Guardrail 2 — git** [MUST] — every step is a commit, so any wrong turn is one revert away.
   That's what makes it cheap to let Claude try things.
4. **Guardrail 3 — plan mode is your best friend** — Claude proposes the plan before
   touching anything; I read it line by line and push back before any code exists. Show a
   real plan + one change I made to it (this talk's own plan is a live example: I added this
   very "guardrails" section in plan review). Tips on the slide:
   - **Write a precise prompt.** Clean spelling and grammar, short, no fuzzy words. A vague
     ask gets a vague plan.
   - **Spend the time on details up front.** Every minute going back and forth in the plan
     saves more later in rework.
   - **Know what "done" looks like.** Have a picture of the end product. If you don't yet,
     make figuring that out the first step of the plan.
   - **Put tests in the plan.** Where it fits, write the check first and build to it
     (test-driven). Here the "tests" were `assert`s on joins and a harness that runs every
     code block on the dashboard against the real CSVs (80/80 values match). Be upfront
     that this repo has no formal unit-test suite.
   - **Pick the model for the job.** In my experience Fable is better in plan mode and
     Opus is better at building. Say plainly this is anecdotal, not something I measured.
5. **Other** — habits from across my work, not just FinFlow. Label the non-FinFlow ones
   as coming from my UMD research repo.
   - **I make the design calls, Claude does the work.** E.g. the 3-try lambda search with
     a fallback was my call; Claude wrote it, ran it, reported back.
   - **Claude as a tutor.** "what is M again", "show it in a trivial example", pasting its
     own sentence back to ask what it means. Understand it before I trust it.
   - **Short prompts for the busywork.** "push", "run it", "make a new pr". Claude handles
     branches, commits, PRs and merge conflicts through `gh`.
   - **Memory notes for scope.** e.g. "this is an MVP, park the deep checks."
   - **Saying no to extra work.** Dropped GPU batching as "little value add".
   - **One PR per change.** 11 merged PRs, each about one thing.
   - **Check against a reference.** "Match the R code numerically" — compare to an outside
     answer, not just Claude's own output.
   - **Long runs left to Claude.** Sims run for hours or days; once a subagent watched a run
     and wrote the report when it finished.
   - **Checking by reading.** Most catches come from something not adding up: "isn't there
     2 break-ins?", "thought we are now at 100?", noticing RAM capped at 13.7 GB.
   - **Plan mode, steered 9 times** while planning this very talk.
   - **By the numbers:** 54 of 64 commits co-authored by Claude, 11 PRs, ~550 shell
     commands (UMD repo; verify with `git log` / `gh pr list` before it goes on a slide).
   - **Habits that cost me.** Slow restart after a break (fix: a status note in the repo);
     stray untracked files piling up.

### Block 2 — Thought process via the explorer (live)
Walk panels in order as a story, one question per panel:
- p1: "what happened?" → how the two devices were found, attack vs normal sessions.
- p2: "how far did it spread?" → reach, the two-wave timeline, "June wasn't a break-in".
- p3: "what should FinFlow do?" → controls ranked by $ saved, honest limits.
- p4: "how do we catch it next time?" → session-level scoring, tiered rules → model.
Open the AI-log rail once mid-demo to show the log lives next to the work.
Prep a fallback: 4 screenshots in case the live page misbehaves on their machine.


## Build steps
1. Re-run `python build_log_rail.py` so the rail matches the current log; check the explorer opens clean.
2. Fill the `_[Danny: ]_` stubs in `AI_USAGE_LOG.md` — Danny writes these; they're the judgment lines
   this audience will ask about.
3. Build the Claude-workflow deck as a small standalone HTML file (`presentation/claude_workflow.html`),
   same visual tokens as the explorer so the switch feels seamless. Keyboard arrows to advance.
   Every number on it pulled from the log/explorer, not retyped from memory.
4. Add one "loop" diagram (inline SVG).
5. Optionally publish both as private Artifacts so the link can be shared after the talk (confirm first).
6. Log this prep work in `AI_USAGE_LOG.md` (slide-prep section) as we go.

## Verification
- Open the deck and explorer in a fresh browser; click every panel and the rail.
- Cross-check each number on the new deck against `AI_USAGE_LOG.md` / explorer text
  (95.4%, 95.7%, $5.20M → $2.52M, 46 vs 0 failed MFA, 80/80 values verified).
- Run `git log` / `gh pr list` in the UMD repo to confirm 54/64 commits and 11 PRs.
- Dry run with a timer; if Block 1 runs long, cut "Other" down to its top 4 bullets.

## Open items for Danny
- **Block 3 (HTML vs Excel) is gone from the plan, but the run of show still gives it
  min 24–28.** Removed on purpose? If yes, those 4 minutes go to the explorer demo or Q&A.
- **This folder isn't a git repo right now.** To claim git as a guardrail honestly, either
  show the repo where it was tracked, or `git init` + commit now and say so. Don't imply
  a commit history that isn't there.
- The `_[Danny: ]_` stubs are the "thought process" in your own words — worth writing before the deck.
