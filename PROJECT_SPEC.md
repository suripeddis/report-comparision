# AAC Prompt Classifier — Technical Spec

> A Streamlit web app that reads an AAC (Augmentative and Alternative
> Communication) therapy session transcript, uses an OpenAI model to label every
> prompt the facilitator gave (in three ways), saves each session to a Supabase
> database, and builds an interactive HTML report — including a chart that shows
> how a student's prompt mix changes across sessions.

---

## 1. Purpose & Background

### 1.1 The problem

In AAC letterboarding therapy, a facilitator helps a non-speaking or
minimally-speaking student communicate by pointing to letters on a board. The
*kind* of prompting the facilitator uses matters: too much directive prompting
can raise questions about whether the words are really the student's own, while
a good balance of open questions and calming/regulating prompts supports real
communication.

Doing this review by hand — listening to a recording, writing it down, and
counting the kinds of prompts — is slow and easy to disagree on. This project
does that counting automatically and the same way every time.

### 1.2 What the app does

1. A user uploads an `.srt` transcript of one session.
2. The app pulls out the spoken text and sends it to an OpenAI model along with a
   detailed set of labeling instructions.
3. The model returns, for **every prompt the facilitator gave**, a set of labels
   across **three separate questions** (see §4).
4. The app counts up those labels and builds an HTML report: summary cards, a
   donut chart, bars, a per-method count breakdown, a session timeline, a
   cross-session line chart, and tables of every prompt.
5. The labeled session is saved to a Supabase table so it can be reopened later
   and compared over time for the same student.

### 1.3 The two methods being compared

The project's goal is to compare how prompts line up with two well-known AAC
methods:

| Method | Full name | Focus |
|---|---|---|
| **S2C** | Spelling to Communicate | The *physical act* of pointing — movement and staying regulated |
| **RPM** | Rapid Prompting Method | The *content* of the answer — questions, choices, ideas |

There is also a third, separate set of labels — the **"Diwakar's Lab" types** —
a list of 12 more detailed tags the research lab uses (for example
`encouragement`, `dictation`, `gaze_cue`). A prompt can have more than one of
these at once.

---

## 2. How the project was built

The git history shows the project moving from a trained machine-learning model
to an AI language model:

| Commit | Step |
|---|---|
| `2712d77` | Initial commit |
| `3ee60d7` | Added `main.py` |
| `76f9bae` | Built the UI; pulled out the "teach / ask / spell" logic |
| `6384bc0` | Classified "ask" prompts |
| `96d1c9f` | Stopped tracking `.env`, added it to `.gitignore` |
| `a337a7c` | More work on the classifier |
| `9182889` | Added graphs for prompt types and counts |
| `7edd4a4` | Fixed import issues |
| `8480161` | **Switched to OpenAI's API to classify prompts** |
| `770a2f6` | Added `requirements.txt` |

### 2.1 Phase 1 — a trained model (now archived)

The first version trained a **TF-IDF + Logistic Regression** classifier on
example prompts. (TF-IDF turns text into numbers based on which words appear;
logistic regression then predicts a label from those numbers.) That code now
lives in [ml/archive/](ml/archive/):

- [ml/archive/prompt_train.py](ml/archive/prompt_train.py) — trains on
  [data/prompts.csv](data/prompts.csv) (`text`, `label` columns; ~337 rows).
- [ml/archive/train.py](ml/archive/train.py) — trains on
  [data/prompt_examples_120 (1).csv](data/) using the richer `functional_type`
  label (Choice / Clarification / Guided / etc.).

Both scripts do the same steps:

```
read CSV → split into train/test (80/20) → turn text into numbers (TF-IDF)
        → train Logistic Regression → check accuracy (report + confusion matrix)
        → save the model + vectorizer as .pkl → log the wrong guesses
```

Files produced (kept locally, not in git): `ml/*.pkl`, the split CSVs
(`train_features.csv`, etc.), and `model_mistakes.csv` for studying errors.

**Why it was replaced:** this kind of model gives one flat label and can't use
context — for example, whether "What do you see?" is *open-ended* or a
*clarification* depends on what the student just did, which the model can't see.
It also can't produce the three separate labels the lab wanted. An AI language
model can read the whole transcript for context and return all three labels in
one go.

### 2.2 Phase 2 — AI language model (current)

The current system replaces the trained model with one OpenAI call driven by a
long, rules-based instruction prompt
([pipelines/steps/classifier.py](pipelines/steps/classifier.py)). The old
ML files are kept for reference but are not used when the app runs.

---

## 3. Tools & Tech Stack

| Layer | Tool | What it does |
|---|---|---|
| Language | **Python 3.11+** | Everything |
| Web UI | **Streamlit** | Single-page app: inputs, file upload, embedded report |
| AI model | **OpenAI** Python SDK (`gpt-4.1-mini`) | Labels each prompt three ways |
| Config | **python-dotenv** | Reads keys from `.env` when running locally |
| Data | **pandas** | Counting and table shaping |
| Database | **Supabase** (`supabase-py`) | Saves labeled sessions in a Postgres `sessions` table |
| Report | Hand-written **HTML/CSS + plain JS** (Canvas) | Donut, bars, timeline, line chart — no chart library |
| Old ML (archived) | **scikit-learn** | TF-IDF + Logistic Regression (Phase 1) |
| Testing | **pytest** | Tests for transcript reading + counting |
| Lint | **flake8** | Style check (max line length 100) |
| Tasks | **Makefile** | `install` / `run` / `test` / `lint` |
| Version control | **git** | History |
| Hosting | **Streamlit Community Cloud** | Runs the deployed app from GitHub |

`requirements.txt` (what the app needs to run): `streamlit`, `openai`,
`python-dotenv`, `pandas`, `supabase`.

---

## 4. How prompts are labeled (three questions)

Every facilitator prompt gets labeled by answering three separate questions. The
model is told to **first pick a method, then pick a type from that method's
list**, and separately add any number of Diwakar labels.

### Question 1 — Method (pick one)

| Value | Meaning |
|---|---|
| `s2c` | About movement/regulation (Spelling to Communicate) |
| `rpm` | About content/academics (Rapid Prompting Method) |

Rule: if a prompt is about both movement and content, label it by its **main
point** — movement → `s2c`, content → `rpm`.

### Question 2 — Prompt type (pick one; the list depends on the method)

**If `method = s2c`** — one of:

| Type | Meaning |
|---|---|
| `initiation` | Cue to start moving ("Let's begin.") |
| `continuation` | Cue to keep moving ("Keep going.") |
| `gesture` | A physical or pointing cue |
| `direction` | A spatial cue ("Top row.") |
| `none` | Not really a prompt (acknowledgement, narration, off-task) |

**If `method = rpm`** — one of:

| Type | Meaning |
|---|---|
| `choice` | Offers clear options to pick from |
| `clarification` | Asks the student to confirm/fix/expand something they said |
| `guided` | Nudges toward a target answer with hints or letter cues |
| `open_ended` | Invites a free answer, no target in mind |
| `reinforcement` | Encourages or affirms without asking for new info |

The instruction prompt also has **tie-breaker rules** for the tricky cases (for
example: "RPM + letter cues → `guided`, even if it's phrased as a question";
"S2C + spatial words → `direction`").

### Question 3 — Diwakar's Lab types (pick one or more)

A prompt can carry **one or more** of these 12 labels:

`encouragement`, `dictation`, `instruction`, `stm`, `question`, `hands`,
`directional`, `positive_reinforcement`, `gaze_cue`, `physical`, `regulation`,
`focus`.

The model must return at least one per prompt; combinations are common (e.g. a
directional question → `['question', 'directional']`).

### What the model returns

The model returns **only** a JSON list; each item looks like:

```json
{
  "timestamp": "00:01:23",
  "prompt_text": "Find the top row.",
  "method": "s2c",
  "type": "direction",
  "diwakar_labels": ["directional", "instruction"]
}
```

---

## 5. Code Map

```
report-comparison/
├── app.py                          # Streamlit app + report builder
├── requirements.txt
├── Makefile                        # install / run / test / lint
├── README.md
├── PROJECT_SPEC.md                 # ← this document (technical)
├── PROJECT_OVERVIEW.md             # plain-language overview
├── COOP_FINAL_REPORT.md            # co-op final report
├── FINAL_REPORT.md                 # handover/completion report
├── .env / .env.example             # OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY
│
├── pipelines/
│   └── steps/
│       ├── ingest_transcript.py    # SRT file → plain text
│       ├── classifier.py           # OpenAI call + safe JSON parsing
│       ├── database.py             # Supabase save/load + retries
│       └── metrics.py              # counts, table shaping, trend data
│
├── templates/
│   └── report_template.html        # The full report (HTML/CSS/JS, filled in by app.py)
│
├── tests/
│   └── test_pipeline.py            # pytest: transcript reading + counting
│
├── data/                           # Example data (old ML phase)
│   ├── prompts.csv
│   └── prompt_examples_120 (1).csv
│
├── ml/                             # Phase-1 model files (.pkl)
│   └── archive/                    # Phase-1 training scripts
│
├── Reports/                        # Sample inputs/outputs
│   ├── transcript.srt
│   ├── transcript2.srt.srt
│   └── VolcanoLessonReport.docx
└── outputs/                        # (empty; git-ignored)
```

### 5.1 What each file does

**[ingest_transcript.py](pipelines/steps/ingest_transcript.py)**
- `read_transcript(file_uploaded) -> str` — reads the uploaded SRT file and
  removes the line numbers and timestamps, leaving just the spoken words.

**[classifier.py](pipelines/steps/classifier.py)**
- `classify_transcript(transcript_text) -> list` — makes one
  `chat.completions.create` call with `model="gpt-4.1-mini"`, `temperature=0`,
  and `seed=42` (these last two make it give the same answer each time). The
  instruction prompt holds the full three-question setup from §4.
- `_get_client()` / `_get_secret(name)` — build the OpenAI client only when
  first needed, reading the API key from the environment **or** from Streamlit's
  secrets (so it works both locally and when hosted). See §8.1.
- `_extract_json(raw)` — safely reads the model's reply: strips
  ```` ```json ```` fences, pulls out the `[...]` list even if the model adds
  extra text, then parses it.

**[database.py](pipelines/steps/database.py)**
- `_get_client()` / `_get_secret(name)` — build the Supabase client only when
  first needed, reading `SUPABASE_URL` / `SUPABASE_KEY` from the environment or
  Streamlit's secrets; gives a clear error if they're missing.
- `_retry(fn, retries=3, delay=1.0)` — re-runs a network call up to 3 times,
  waiting a bit longer after each failure, so a brief network hiccup doesn't
  break things.
- `save_session(...)` — saves `{file_name, classified_prompts, session_date}`
  plus optional `student_id`, `practitioner`, `topic`.
- `get_session_by_file(student_id, file_name)` — looks up a saved session so the
  app can skip a fresh OpenAI call.
- `get_prior_session`, `get_student_sessions(limit)` (returned oldest-first),
  `load_sessions`.

**[metrics.py](pipelines/steps/metrics.py)**
- `count_prompt_types(results)` — counts how many of each `type`.
- `count_methods(results)` — counts how many of each `method`.
- `get_max_counts(counts)`, `results_to_df(results)`.
- `compute_trend_data(sessions, current_file=None, current_date=None)` — for
  each session, builds `{label, topic, total, counts, pcts}` over a fixed type
  order, which feeds the cross-session line chart. When `current_file` (and
  optionally `current_date`) is given, it also returns `currentIndex` — the
  position of the session being viewed — so the chart can pin it as the
  always-shown "current" line.

**[app.py](app.py)** — the Streamlit page plus `render_report(...)`. It holds
the color/label maps for all three questions, builds the HTML pieces, and fills
them into the template.

**[report_template.html](templates/report_template.html)** — the whole report
(CSS + HTML + plain-JS Canvas charts). `app.py` fills in `{placeholder}` slots,
including one `{chart_data}` / `{trend_data}` JSON blob the scripts read.

---

## 6. Start-to-finish flow

```
┌─────────────┐
│  User opens │  locally: python -m streamlit run app.py → http://localhost:8501
│  the app    │  hosted:  the Streamlit Community Cloud URL (see §8.4)
└──────┬──────┘
       │ enters Student / Practitioner / Topic (optional)
       │ uploads transcript.srt, clicks "Analyze"
       ▼
┌──────────────────────────────────────────────────────────────┐
│ app.py  (Analyze button)                                       │
│                                                                │
│  1. If a student name is given → get_session_by_file(...)      │
│        ├─ found    → reuse saved labels (skip OpenAI)          │
│        └─ not found → keep going                              │
│                                                                │
│  2. read_transcript(file)         → plain text                 │
│  3. classify_transcript(text)     → JSON list (OpenAI)         │
│  4. save_session(...)             → Supabase insert (+retry)   │
│  5. If 2+ past sessions exist:                                 │
│        compute_trend_data(...)    → trend JSON                 │
│  6. render_report(results, file_name, trend_json)              │
└──────┬─────────────────────────────────────────────────────────┘
       ▼
┌──────────────────────────────────────────────────────────────┐
│ render_report                                                  │
│   • count prompt types and methods                             │
│   • build the HTML pieces:                                     │
│       - S2C / RPM prompt tables, Diwakar table                 │
│       - S2C & RPM legends                                      │
│       - "Counts by method" cards                               │
│   • build the {chart_data} JSON                                │
│   • fill it all into report_template.html                      │
│   • components.html(...) shows it on the page                  │
└──────┬─────────────────────────────────────────────────────────┘
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Browser shows the report; JS draws the charts on Canvas        │
└──────────────────────────────────────────────────────────────┘
```

A separate **Previous Sessions** area lets the user type a student name, load up
to 20 saved sessions, pick one, and re-open its report (with trends) without
calling OpenAI again.

---

## 7. The report (what's on the page)

[report_template.html](templates/report_template.html) builds, top to bottom:

1. **Header** — file name + date.
2. **Summary cards** — Total prompts · Types used · S2C prompts · RPM prompts
   (the numbers count up when the page loads).
3. **Two-column row:**
   - *Prompt types* — a donut chart + legend + horizontal bars.
   - *Method breakdown* — S2C vs RPM cards, a percentage split bar, and S2C/RPM
     legends with short descriptions.
4. **Counts by method** *(full-width)* — three cards (S2C, RPM, Diwakar's Lab).
   Each card lists the method's known types in order, **including ones with a
   count of 0**, and **also lists any other type that actually showed up** in
   the data (so prompts the model tagged with an off-list type are still shown,
   not hidden).
5. **Session timeline** — one colored block per prompt, in order; hovering shows
   its number, method, and text. Blocks dim when a method tab is active.
6. **Prompt type trends — prior sessions** — a **line chart** comparing
   sessions (hidden until there are 2+). The **prompt types run along the
   x-axis**, the y-axis is the **percentage share**, and **each line is one
   session** (so at each prompt type you compare the sessions' dots). Each dot
   has a value label, plus gridlines and % labels. **Hovering** a line or point
   shows a tooltip with the session, prompt type, its share, and the exact
   count.
   - **Session selector:** the session this report is for is the **pinned
     "current" line** (always shown — its chip reads "Session N (current)" and
     can't be toggled off). **Chips** let you add/remove any other session to
     compare against it — pick any combination, or **All**. The chart opens
     showing just the current session. (Driven by the `currentIndex` from
     `compute_trend_data`; up to 12 recent sessions are available to choose.)
7. **Classified prompts** — tabbed tables (S2C / RPM / Diwakar's); switching tabs
   also dims the non-matching timeline blocks.

All charts are drawn with the plain Canvas API and plain JS — no Chart.js or D3.
The colors and labels are defined once in `app.py` and passed to the template, so
everything stays consistent across the charts and tables.

---

## 8. Setup & Running

### 8.1 Keys / config

The app needs three values:

```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://<project-id>.supabase.co
SUPABASE_KEY=<anon-or-service-role-key>
```

How they're read (handled by `_get_secret` in `classifier.py` and
`database.py`):

- **Locally** — from a `.env` file, loaded by `python-dotenv`. The template is
  [.env.example](.env.example); the real `.env` is git-ignored.
- **When hosted on Streamlit Cloud** — from the app's **Secrets** (set in the
  dashboard as TOML). The code checks the environment first, then falls back to
  `st.secrets`, so the same code works in both places.

### 8.2 Supabase table

The `sessions` table needs at least:

```sql
create table sessions (
  id                 uuid primary key default gen_random_uuid(),
  file_name          text,
  classified_prompts jsonb,        -- the model's JSON list
  student_id         text,
  practitioner       text,
  topic              text,
  session_date       date,
  created_at         timestamptz default now()
);
```

### 8.3 Commands ([Makefile](Makefile))

```bash
make install          # install requirements into .venv
make run              # streamlit run app.py   (→ http://localhost:8501)
make test             # pytest tests/ -v
make lint             # flake8 (max line length 100)
```

Run by hand:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # fill in the keys
python -m streamlit run app.py
```

> Tip: use `python -m streamlit ...` so Streamlit runs under the same Python
> that has the packages installed (avoids "module not found" mix-ups between
> different Python installs).

### 8.4 Deployment (Streamlit Community Cloud)

- The app is hosted on **Streamlit Community Cloud**, deployed from the GitHub
  repo `suripeddis/report-comparision` (branch `main`, main file `app.py`).
- The three keys are set in the app's **Settings → Secrets** (TOML), not in the
  repo.
- A new push to `main` redeploys the app.
- The deployed app is public, so anyone with the link can run analyses (which
  use the OpenAI key) — access can be limited in the app's sharing settings.

### 8.5 Using it

1. (Optional) enter Student / Practitioner / Topic — the student name turns on
   saving, history, and the trend chart.
2. Upload a `.srt` transcript; click **Analyze**.
3. Read the report.
4. Later, use **Previous Sessions** to reopen and compare past sessions.

---

## 9. Recent changes

- **Counts by method (S2C / RPM / Diwakar's Lab cards).** Each card shows the
  method's known types in order, including 0s, **and now also shows any other
  type that actually appeared** in the data (so nothing is hidden). Counts come
  from `_method_type_items()` in [app.py](app.py). This section is its own
  full-width block beneath the donut/bar row.
- **Trend chart rebuilt as a session-comparison line chart.** In
  [report_template.html](templates/report_template.html), the cross-session
  chart went from stacked bars → a line chart, then was reoriented so **prompt
  types run along the x-axis and each line is one session** (the clearest way to
  compare two sessions side by side). It has value labels at each dot, gridlines,
  and **hover tooltips**. The whole chart is now drawn by a single `render(indices)`
  function so it can be redrawn for any chosen set of sessions.
- **Session selector with a pinned "current" session.** The report's own session
  is always shown (pinned, non-removable); chips let you add/remove any other
  session to compare against it, or show **All**. Backed by `currentIndex` from
  `compute_trend_data` (which now takes `current_file`/`current_date`), and the
  recent-session limit was raised from 6 to 12.
- **Keys now also read from Streamlit secrets.** `classifier.py` and
  `database.py` build their clients lazily and read keys from the environment or
  `st.secrets`, so the app works both locally and when hosted.

---

## 10. Testing

[tests/test_pipeline.py](tests/test_pipeline.py) covers the parts with
predictable output:

- **Transcript reading** — removing line numbers/timestamps, keeping the speech,
  handling an empty file.
- **Counting** — `count_prompt_types` returns the right counts, `get_max_counts`
  (including empty input), `results_to_df` shape (including empty input).

The OpenAI call and Supabase reads/writes are **not** unit-tested because they
need live keys; instead they're made sturdy by `_extract_json` (safe parsing)
and `_retry` (re-tries on failure).

---

## 11. Why things were done this way

| Choice | Why |
|---|---|
| AI model instead of a trained classifier | Needs full-transcript context + 3 labels at once; the simple model can't do either |
| `temperature=0`, `seed=42` | Same input → same labels every run |
| `_extract_json` safe parsing | Models sometimes wrap JSON in extra text; this still gets a clean list |
| Build clients lazily + read `st.secrets` | Works locally and when hosted; fails with a clear message if keys are missing |
| Hand-built HTML + Canvas (no chart library) | No extra dependencies; full control; fits inside Streamlit's `components.html` |
| Cache by `student_id + file_name` | No paying for a repeat OpenAI call when re-opening a session |
| `_retry` with growing wait | Network calls sometimes blip; retries keep it reliable |
| Colors/labels defined once in `app.py` | One source of truth keeps every chart and table consistent |
| Pick method first, then type | Matches how a clinician reasons and avoids mixing the two type lists |

---

## 12. Known limits & what's next

- **Results depend on transcript quality** — SRT files don't say who is talking,
  so the model has to guess which lines are the facilitator's; unclear
  transcripts lower accuracy.
- **No accuracy scorecard yet** — there's no set of human-labeled prompts to
  measure how often the model agrees with an expert. (The old ML phase logged its
  mistakes, but that was Phase 1.) This is the most useful next step.
- **One call per transcript** — very long sessions could hit size limits; the
  transcript isn't split into pieces.
- **Cost** — each fresh Analyze is one OpenAI call over the whole transcript
  (re-opening a saved session is free).
- **Database is optional but limited without it** — analysis still runs if
  Supabase is unavailable, but saving and history just show a warning.
- **Known data quirk** — the model sometimes tags a prompt with `method: s2c`
  but a `type` from the RPM/Diwakar list (e.g. "guided"). The report now shows
  these honestly (§9), but tightening the classifier rules so S2C prompts get
  S2C types is a good follow-up.
- **Other next steps** — detect speakers automatically, add an accuracy
  dashboard, split long transcripts, add a downloadable Word/PDF report, and
  compare the model's labels against human reviewers.
```
