# AAC Prompt Classifier — Final Project Report & Handover

**Author:** Saumya Suripeddi
**Date:** June 15, 2026
**Status:** Core build complete — ready for handover

---

## 1. Executive Summary

This project delivers a working web application that automatically analyzes AAC
(Augmentative and Alternative Communication) letterboarding therapy transcripts.
A user uploads a session transcript, and the app labels every prompt the
facilitator gave, then produces an interactive visual report breaking the
session down by prompting style, prompt type, and a detailed research-lab
labeling scheme. Sessions are saved so a student's prompting patterns can be
tracked and compared over time.

The application is **functional end to end**: transcript upload → automated
classification → saved results → rendered report with charts and cross-session
trends. This report documents what was built, what works well, what could be
improved, and what the next person needs to take it forward.

---

## 2. Goals vs. Outcomes

| Goal | Status | Notes |
|---|---|---|
| Ingest real session transcripts (`.srt`) | ✅ Done | Strips timing/numbering, returns clean text |
| Automatically classify every facilitator prompt | ✅ Done | Three independent labeling dimensions |
| Compare S2C vs RPM prompting methods | ✅ Done | Method split + per-method type counts |
| Support the research lab's detailed label set | ✅ Done | 12-label multi-label "Diwakar's Lab" scheme |
| Visual, shareable report | ✅ Done | Stat cards, donut, bars, timeline, trends, tables |
| Persist sessions & track a student over time | ✅ Done | Saved to database; cross-session trend chart |
| Avoid re-paying for repeat analysis | ✅ Done | Caches results by student + file |
| Formal accuracy evaluation of the AI labels | ⚠️ Partial / future | No held-out scored eval yet (see §6) |

---

## 3. What Was Built (my contributions)

### 3.1 The classification engine
- Designed and wrote a detailed, rules-based classification prompt that labels
  each facilitator utterance across **three dimensions**:
  1. **Method** — S2C (motor/regulation) vs RPM (academic/content).
  2. **Prompt type** — a specific type drawn from the chosen method's
     vocabulary (e.g. *direction*, *choice*, *open-ended*).
  3. **Research-lab labels** — one or more of twelve fine-grained tags.
- Included explicit tie-breaking rules so borderline prompts are labeled
  consistently.
- Built defensive parsing so the system reliably extracts structured results
  even if the AI's response formatting varies.

### 3.2 The data pipeline
- **Transcript ingestion** — converts uploaded subtitle files into clean text.
- **Metrics & aggregation** — tallies prompts by type and method, and computes
  per-session distributions used for the trend chart.
- **Database layer** — saves each analyzed session, reloads past sessions,
  caches repeat analyses, and retries automatically on flaky network calls.

### 3.3 The report & user interface
- A single-page app where a user enters session details, uploads a transcript,
  and clicks **Analyze**.
- A custom-built visual report containing: headline stat cards, a prompt-type
  donut chart, distribution bars, a method-split breakdown, a **Counts by
  Method** section, a session timeline, a cross-session trend chart, and tabbed
  tables of every classified prompt.
- A **Previous Sessions** browser to reload and review past sessions without
  re-running the AI.

### 3.4 Evolution of the approach
- Began with a traditional trained machine-learning model (TF-IDF + logistic
  regression) on a few hundred labeled examples.
- Replaced it with an AI language-model approach because the trained model
  couldn't use session context or produce multiple labeling dimensions at once.
  The earlier work is archived for reference.

### 3.5 Supporting work
- Unit tests for the deterministic parts of the pipeline (ingestion + metrics).
- Project documentation: a technical specification, a non-technical overview,
  and this final report.
- Developer tooling: a Makefile (`install` / `run` / `test` / `lint`), a
  dependency list, and an environment-variable template.

---

## 4. Current State

- The app runs locally with a single command and is usable end to end.
- It depends on two external services configured via environment variables:
  - An **OpenAI API key** (for the classification).
  - A **Supabase** database (for saving and reloading sessions).
- Analysis still works if the database is unavailable — only saving and history
  features degrade gracefully (the user sees a warning, not a crash).
- Sample transcripts are included for testing.

---

## 5. What Works Really Well

- **End-to-end automation.** A messy, manual analysis task is now a few clicks:
  upload, analyze, read the report. This is the project's core win.
- **Rich, multi-dimensional labeling.** Every prompt is labeled three ways at
  once, with the AI reading the full session for context — something the
  original trained model could not do.
- **Consistent, reproducible results.** The classifier is configured for
  deterministic output, so the same transcript yields the same labels run to
  run. Detailed rules keep borderline cases labeled consistently.
- **A genuinely useful report.** The visuals are clear and purpose-built: the
  method split and the per-method counts directly answer the lab's central
  question about S2C vs RPM prompting balance.
- **Cross-session trends.** Once a student has multiple sessions, the trend
  chart shows how their prompting mix shifts over time — a real clinical value-
  add, not just a single snapshot.
- **Cost-aware and resilient.** Repeat analyses are cached (no duplicate AI
  charges), and database calls retry automatically, so transient network blips
  don't break a session.
- **Clean, well-separated code.** Ingestion, classification, storage, metrics,
  and presentation are each isolated, which makes the system easy to read and
  extend.

---

## 6. What Could Work a Little Better

- **No formal accuracy scorecard.** The biggest open item: there's no held-out,
  human-labeled test set measuring how often the AI's labels match expert
  judgment. Adding this would let the lab trust and tune the results with
  confidence. *(The archived early model did log its mistakes; the current AI
  approach should get an equivalent evaluation.)*
- **Speaker identification is implicit.** Transcripts don't clearly mark who is
  speaking, so the AI infers which lines are the facilitator's. Cleaner
  speaker-labeled transcripts — or an automated speaker-detection step — would
  improve accuracy.
- **Very long sessions.** A whole transcript is analyzed in one pass, which
  could hit size limits for unusually long sessions. Splitting long transcripts
  into chunks would make it more robust.
- **Report export.** The report is viewed in the browser but can't yet be
  downloaded as a Word or PDF file. A sample Word report exists in the project,
  suggesting this is a desired finishing touch.
- **Hosting.** The app currently runs locally. Deploying it to a shared URL
  would let non-technical team members use it without any setup.
- **Configuration friendliness.** Setup requires creating an environment file
  with two service keys and a database table. A short setup checklist (or a
  guided first-run) would smooth onboarding for the next person.

---

## 7. Handover Notes (for the next person)

### 7.1 Getting it running
1. Create a Python virtual environment and install dependencies
   (`make install`).
2. Copy the environment template to `.env` and fill in the OpenAI and Supabase
   keys.
3. Ensure the Supabase `sessions` table exists (schema is documented in the
   technical spec).
4. Start the app (`make run`) and open the local URL it prints.

### 7.2 Where to look in the code
- **Classification logic & the AI prompt** — `pipelines/steps/classifier.py`
- **Transcript parsing** — `pipelines/steps/ingest_transcript.py`
- **Saving/loading sessions** — `pipelines/steps/database.py`
- **Counting & trend data** — `pipelines/steps/metrics.py`
- **The app, report assembly, and all label/color definitions** — `app.py`
- **The report's look and charts** — `templates/report_template.html`
- **Tests** — `tests/test_pipeline.py` (`make test`)

### 7.3 Supporting documents
- **Technical specification** — `PROJECT_SPEC.md` (full architecture & details)
- **Non-technical overview** — `PROJECT_OVERVIEW.md` (plain-language summary)
- **This report** — `FINAL_REPORT.md`

### 7.4 Suggested first tasks for whoever takes over
1. Build a small human-labeled evaluation set and measure the AI's accuracy.
2. Add transcript chunking for long sessions.
3. Add a "Download report" (PDF/Word) button.
4. Deploy to a shared URL for non-technical users.

---

## 8. Conclusion

The project meets its core objective: it turns raw AAC therapy transcripts into
consistent, multi-dimensional, visual analyses, and tracks them over time. The
pipeline is complete, the code is cleanly organized and documented, and the
remaining items are well-understood enhancements rather than missing
fundamentals. It is in a solid state to hand over.
</content>
