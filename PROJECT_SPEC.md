# AAC Prompt Classifier — Project Specification

> A Streamlit web application that ingests AAC (Augmentative and Alternative
> Communication) letterboarding therapy session transcripts, classifies every
> facilitator prompt along three labeling dimensions using an OpenAI GPT model,
> persists each session to Supabase, and renders an interactive, multi-section
> HTML analytics report including cross-session trends.

---

## 1. Purpose & Background

### 1.1 The problem

In AAC letterboarding therapy, a facilitator (practitioner) supports a
non-speaking or minimally-speaking student in communicating by pointing to
letters on a board. The *kind* of prompting a facilitator uses matters
clinically: too much directive prompting can call into question the
independence/authorship of the student's output, while the right balance of
open-ended and regulating prompts supports genuine communication.

Reviewing a session by hand — listening to a recording, transcribing it, and
tallying what kinds of prompts were used — is slow and subjective. This project
automates that analysis.

### 1.2 What the app does

1. A user uploads an `.srt` transcript of one therapy session.
2. The app extracts the spoken text and sends it to an OpenAI GPT model with a
   detailed classification prompt.
3. The model returns, for **every facilitator utterance**, a structured label
   set across **three independent dimensions** (see §4).
4. The app aggregates those labels into counts and renders a polished HTML
   report: stat cards, a donut chart, distribution bars, a per-method count
   breakdown, a session timeline, a cross-session trend chart, and tabbed
   prompt tables.
5. The classified session is saved to a Supabase table so it can be reloaded
   later and compared across time for the same student.

### 1.3 The two methodologies being compared

The project name "report-comparison" reflects its core analytical goal:
comparing how prompts map onto two competing AAC methodologies.

| Method | Full name | Orientation |
|---|---|---|
| **S2C** | Spelling to Communicate | Motor learning & regulation — guiding the *motor act* of pointing |
| **RPM** | Rapid Prompting Method | Academic engagement & content — emphasizing the *cognitive content* of the response |

A third, independent labeling scheme — **"Diwakar's Lab" prompt types** — is a
12-label, multi-label vocabulary used by the associated research lab to tag
prompts more granularly (e.g. `encouragement`, `dictation`, `gaze_cue`).

---

## 2. Project Evolution (how it was built)

The git history records the project's progression from a classic ML approach to
an LLM-based one:

| Commit | Milestone |
|---|---|
| `2712d77` | Initial commit |
| `3ee60d7` | Added `main.py` |
| `76f9bae` | Created the UI; extracted "teach / ask / spell" logic |
| `6384bc0` | Classified "ask" prompts |
| `96d1c9f` | Removed `.env` from tracking, added to `.gitignore` |
| `a337a7c` | Adding to classifier |
| `9182889` | Added graphs to analyze types and counts of each prompt type |
| `7edd4a4` | Fixed import issues |
| `8480161` | **Switched to OpenAI's API to classify prompt types** |
| `770a2f6` | Added `requirements.txt` |

### 2.1 Phase 1 — Classical ML (now archived)

The first approach trained a **TF-IDF + Logistic Regression** classifier on
labeled prompt examples. This code now lives under [ml/archive/](ml/archive/):

- [ml/archive/prompt_train.py](ml/archive/prompt_train.py) — trains on
  [data/prompts.csv](data/prompts.csv) (`text`, `label` columns; ~337 rows).
- [ml/archive/train.py](ml/archive/train.py) — trains on
  [data/prompt_examples_120 (1).csv](data/) using the richer
  `functional_type` label (Choice / Clarification / Guided / etc.).

Both scripts follow the same pipeline:

```
load CSV → train/test split (80/20) → TF-IDF vectorize (1–2 grams, min_df=2)
        → LogisticRegression → evaluate (accuracy, classification report,
          confusion matrix) → dump model + vectorizer to .pkl → log mistakes
```

Artifacts produced (git-ignored, kept locally): `ml/*.pkl`, plus the split CSVs
`train_features.csv`, `train_target.csv`, `test_features.csv`,
`test_target.csv`, and `model_mistakes.csv` for error analysis.

**Why it was replaced:** A bag-of-words logistic model classifies a single,
flat label and cannot reason about context (e.g. whether "What do you see?" is
*open-ended* or a *clarification* depends on what the student just did). It also
could not produce the three independent label dimensions the lab wanted. The
project moved to an LLM, which classifies with full transcript context and
emits structured multi-dimensional output in one call.

### 2.2 Phase 2 — LLM classification (current)

The current system replaces the trained model with a single OpenAI Chat
Completions call driven by a long, rules-based system prompt
([pipelines/steps/classifier.py](pipelines/steps/classifier.py)). The ML
artifacts are retained for reference/comparison but are not on the runtime path.

---

## 3. Tools, Libraries & Tech Stack

| Layer | Tool | Role |
|---|---|---|
| Language | **Python 3.11+** (venv uses 3.12) | Everything |
| Web UI | **Streamlit** | Single-page app, file upload, inputs, embedded HTML report |
| LLM | **OpenAI** Python SDK (`gpt-4.1-mini`) | Three-dimensional prompt classification |
| Config | **python-dotenv** | Loads API keys from `.env` |
| Data | **pandas** | Aggregation, value counts, DataFrame shaping |
| Persistence | **Supabase** (`supabase-py`) | Stores classified sessions in a Postgres `sessions` table |
| Report | Hand-written **HTML/CSS + vanilla JS** (Canvas API) | Donut, bars, timeline, stacked trend chart — no chart library |
| Classic ML (archived) | **scikit-learn** | TF-IDF + LogisticRegression (Phase 1) |
| Testing | **pytest** | Unit tests for ingest + metrics |
| Lint | **flake8** | Style (max line length 100) |
| Build tasks | **Makefile** | `install` / `run` / `test` / `lint` |
| VCS | **git** | Version control |

`requirements.txt` (runtime): `streamlit`, `openai`, `python-dotenv`, `pandas`,
`supabase`.

---

## 4. The Classification Schema (three dimensions)

Every facilitator utterance is labeled along three independent dimensions. The
model is instructed to **first pick a method, then pick a type from that
method's vocabulary**, and separately apply any number of Diwakar labels.

### Dimension 1 — Method (single label)

| Value | Meaning |
|---|---|
| `s2c` | Motor/regulation-oriented prompting (Spelling to Communicate) |
| `rpm` | Content/academic-oriented prompting (Rapid Prompting Method) |

Decision rule: if a prompt addresses both motor process and content, classify
by *primary intent* — motor → `s2c`, content → `rpm`.

### Dimension 2 — Prompt Type (single label, method-dependent vocabulary)

**If `method = s2c`** — one of:

| Type | Meaning |
|---|---|
| `initiation` | Verbal cue to start movement ("Let's begin.") |
| `continuation` | Verbal cue to continue movement ("Keep going.") |
| `gesture` | Physical/pointing cue |
| `direction` | Verbal spatial cue ("Top row.") |
| `none` | Not really a prompt (acknowledgement, narration, off-task) |

**If `method = rpm`** — one of:

| Type | Meaning |
|---|---|
| `choice` | Offers discrete explicit options |
| `clarification` | Asks the student to confirm/correct/expand prior output |
| `guided` | Scaffolds toward a target via letter cues / hints |
| `open_ended` | Invites a free response, no implied target |
| `reinforcement` | Encourages/affirms without eliciting new info |

The system prompt includes explicit **tie-breaking rules** (e.g. "RPM + letter
cues → `guided` even if phrased as a question"; "S2C + spatial words →
`direction`").

### Dimension 3 — Diwakar's Lab types (multi-label)

A prompt may carry **one or more** of these 12 labels:

`encouragement`, `dictation`, `instruction`, `stm`, `question`, `hands`,
`directional`, `positive_reinforcement`, `gaze_cue`, `physical`, `regulation`,
`focus`.

The model must return at least one Diwakar label per prompt; combinations are
common (e.g. a directional question → `['question', 'directional']`).

### Output contract

The model returns **only** a JSON array; each object has:

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

## 5. Architecture & Code Map

```
report-comparison/
├── app.py                          # Streamlit entry point + report renderer
├── requirements.txt
├── Makefile                        # install / run / test / lint
├── README.md
├── PROJECT_SPEC.md                 # ← this document
├── .env / .env.example             # OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY
│
├── pipelines/
│   └── steps/
│       ├── ingest_transcript.py    # SRT → plain text
│       ├── classifier.py           # OpenAI call + robust JSON parsing
│       ├── database.py             # Supabase persistence + retry
│       └── metrics.py              # counts, df shaping, trend computation
│
├── templates/
│   └── report_template.html        # Full HTML/CSS/JS report (token-replaced)
│
├── tests/
│   └── test_pipeline.py            # pytest: ingest + metrics
│
├── data/                           # Training/example data (classic ML)
│   ├── prompts.csv
│   └── prompt_examples_120 (1).csv
│
├── ml/                             # Phase-1 ML artifacts (.pkl)
│   └── archive/                    # Phase-1 training scripts
│       ├── prompt_train.py
│       └── train.py
│
├── Reports/                        # Sample inputs/outputs
│   ├── transcript.srt
│   ├── transcript2.srt.srt
│   └── VolcanoLessonReport.docx
└── outputs/                        # (empty; git-ignored output dir)
```

### 5.1 Module responsibilities

**[pipelines/steps/ingest_transcript.py](pipelines/steps/ingest_transcript.py)**
- `read_transcript(file_uploaded) -> str` — decodes the uploaded SRT (UTF-8,
  replacing bad bytes) and strips sequence numbers + timestamp lines via regex,
  leaving only spoken text.

**[pipelines/steps/classifier.py](pipelines/steps/classifier.py)**
- `classify_transcript(transcript_text) -> list` — single
  `chat.completions.create` call with `model="gpt-4.1-mini"`, `temperature=0`,
  `seed=42` (for determinism/reproducibility). The system prompt encodes the
  full three-dimension schema (§4).
- `_extract_json(raw)` — defensive parsing: strips ```` ```json ```` fences,
  extracts the `[...]` array even if the model adds prose, then `json.loads`.

**[pipelines/steps/database.py](pipelines/steps/database.py)**
- Lazy Supabase client (`_get_client`) that raises a clear error if
  `SUPABASE_URL` / `SUPABASE_KEY` are missing.
- `_retry(fn, retries=3, delay=1.0)` — exponential backoff wrapper around every
  network call.
- `save_session(...)` — inserts `{file_name, classified_prompts, session_date}`
  plus optional `student_id`, `practitioner`, `topic`.
- `get_session_by_file(student_id, file_name)` — cache lookup (skip GPT if
  already analyzed).
- `get_prior_session`, `get_student_sessions(limit)` (returned oldest-first),
  `load_sessions`.

**[pipelines/steps/metrics.py](pipelines/steps/metrics.py)**
- `count_prompt_types(results)` — `type` value counts → dict.
- `count_methods(results)` — `method` value counts → dict.
- `get_max_counts(counts)`, `results_to_df(results)`.
- `compute_trend_data(sessions)` — builds per-session `{label, topic, total,
  counts, pcts}` over the fixed `ALL_TYPES` order, for the cross-session
  stacked-bar trend chart.

**[app.py](app.py)** — Streamlit page + `render_report(...)`. Holds the
color/label maps for all three dimensions, builds all server-side HTML
fragments, and token-replaces them into the template.

**[templates/report_template.html](templates/report_template.html)** — the
entire report (CSS + markup + vanilla-JS Canvas charts). Receives data through
`{placeholder}` tokens that `app.py` substitutes, including a single
`{chart_data}` / `{trend_data}` JSON blob consumed by the inline scripts.

---

## 6. End-to-End Workflow

```
┌─────────────┐
│  User opens │  streamlit run app.py  →  http://localhost:8501
│  the app    │
└──────┬──────┘
       │ enters Student name / Practitioner / Topic (optional)
       │ uploads transcript.srt, clicks "Analyze"
       ▼
┌──────────────────────────────────────────────────────────────┐
│ app.py  (button handler)                                       │
│                                                                │
│  1. If student_id given → get_session_by_file(student, file)   │
│        ├─ hit  → reuse cached classified_prompts (skip GPT)    │
│        └─ miss → continue                                      │
│                                                                │
│  2. read_transcript(file)         → plain text                 │
│  3. classify_transcript(text)     → JSON list (OpenAI GPT)     │
│  4. save_session(...)             → Supabase insert (+retry)   │
│  5. If ≥2 prior sessions for student:                          │
│        compute_trend_data(prior)  → trend JSON                 │
│  6. render_report(results, file_name, trend_json)              │
└──────┬─────────────────────────────────────────────────────────┘
       ▼
┌──────────────────────────────────────────────────────────────┐
│ render_report                                                  │
│   • results_to_df / count_prompt_types / count_methods         │
│   • pad zero counts for every known type                       │
│   • build server-side HTML fragments:                          │
│       - method tables (S2C / RPM), Diwakar table               │
│       - S2C & RPM legends                                      │
│       - "Counts by method" cards (all known types, incl. 0s)   │
│   • assemble {chart_data} JSON (counts, methods, colorMap,     │
│     typeLabels, sequence)                                      │
│   • token-replace into report_template.html                   │
│   • components.html(...) embeds it in the page                 │
└──────┬─────────────────────────────────────────────────────────┘
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Browser renders the report; inline JS draws charts on Canvas   │
└──────────────────────────────────────────────────────────────┘
```

A separate **Previous Sessions** browser lets the user enter a student name,
load up to 20 saved sessions, pick one, and re-render its report (with trends)
without re-calling GPT.

---

## 7. The Report (rendered output)

[templates/report_template.html](templates/report_template.html) produces, top
to bottom:

1. **Header** — file name + report date.
2. **Stat cards** — Total prompts · Types used · S2C prompts · RPM prompts
   (animated count-up via `requestAnimationFrame`).
3. **Two-column panel row:**
   - *Prompt types* — a donut chart (Canvas) + legend + horizontal
     distribution bars (animated width).
   - *Method breakdown* — S2C vs RPM method cards, a percentage split bar, and
     S2C/RPM legends with descriptions.
4. **Counts by method** *(full-width section)* — three cards (S2C, RPM,
   Diwakar's Lab) listing **every known type with its count, including 0s**, in
   each vocabulary's defined order. *(Added in the most recent work; see §9.)*
5. **Session timeline** — one colored block per prompt in chronological order;
   hovering shows index, method, and text. Blocks dim when a method filter is
   active.
6. **Prompt type trends — prior sessions** — a stacked-bar Canvas chart across
   the student's recent sessions (hidden when fewer than 2 exist).
7. **Classified prompts** — tabbed tables (S2C / RPM / Diwakar's); switching
   tabs also dims non-matching timeline blocks.

All charts are drawn with the raw Canvas 2D API and vanilla JS — no Chart.js or
D3. Color and label maps are defined once in `app.py` and passed to the
template as JSON, so the three dimensions stay visually consistent everywhere.

---

## 8. Configuration & Running

### 8.1 Environment variables (`.env`)

```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://<project-id>.supabase.co
SUPABASE_KEY=<anon-or-service-role-key>
```

Loaded by `python-dotenv` in `classifier.py` and `database.py`. Template lives
in [.env.example](.env.example); `.env` is git-ignored.

### 8.2 Supabase schema

The `sessions` table needs at least:

```sql
create table sessions (
  id                 uuid primary key default gen_random_uuid(),
  file_name          text,
  classified_prompts jsonb,        -- the model's JSON array
  student_id         text,
  practitioner       text,
  topic              text,
  session_date       date,
  created_at         timestamptz default now()
);
```

### 8.3 Commands ([Makefile](Makefile))

```bash
make install          # pip install -r requirements.txt into .venv
make run              # streamlit run app.py   (→ http://localhost:8501)
make test             # pytest tests/ -v
make lint             # flake8 (max-line-length=100)
```

Manual run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # fill in keys
streamlit run app.py
```

### 8.4 Usage

1. (Optional) enter Student name / Practitioner / Topic — student name enables
   caching, history, and the cross-session trend chart.
2. Upload a `.srt` transcript; click **Analyze**.
3. Review the report.
4. Later, use **Previous Sessions** to reload and compare past sessions.

---

## 9. Recent Work (this iteration)

A **"Counts by Method"** section was added to the report (driven from
[app.py](app.py) and rendered in
[templates/report_template.html](templates/report_template.html)):

- Computes, per method, how many prompts fall in each type:
  - **S2C** / **RPM** — counts of each type filtered by `method`.
  - **Diwakar's Lab** — tally across each prompt's `diwakar_labels` list.
- Renders three color-coded cards.
- **Shows every known type, including those with a count of `0`**, in each
  vocabulary's defined order (kept stable rather than sorted by count).
- Promoted from a cramped sub-block inside the "Prompt types" panel to its own
  **full-width section** beneath the donut/bar row and above the Session
  timeline, styled to match the other full-width panels.

---

## 10. Testing & Quality

[tests/test_pipeline.py](tests/test_pipeline.py) covers the deterministic,
non-network parts:

- **Ingest** — SRT header/timestamp stripping, speech retention, empty file.
- **Metrics** — `count_prompt_types` returns a dict with correct values,
  `get_max_counts` (incl. empty), `results_to_df` shape (incl. empty).

The OpenAI call and Supabase I/O are intentionally **not** unit-tested (they
require live credentials); robustness there is handled by `_extract_json` and
`_retry` respectively.

---

## 11. Design Decisions & Rationale

| Decision | Why |
|---|---|
| LLM over trained classifier | Needs full-transcript context + 3 simultaneous label dimensions; a flat bag-of-words model can't do either. |
| `temperature=0`, `seed=42` | Reproducible classifications across runs. |
| `_extract_json` defensive parsing | LLMs occasionally wrap JSON in prose/markdown; this guarantees a parseable array. |
| Server-side HTML + Canvas (no chart lib) | Zero extra JS dependencies; full control over the report's look; renders inside Streamlit's `components.html`. |
| Cache by `student_id + file_name` | Avoids paying for a GPT call when re-viewing an already-analyzed session. |
| `_retry` with exponential backoff | Supabase/network calls are flaky; retries improve reliability without surfacing transient errors. |
| Color/label maps centralized in `app.py` | One source of truth keeps the donut, bars, timeline, tables, and trend chart visually consistent. |
| Method-first → type vocabulary | Mirrors the clinical reasoning order and prevents cross-method type confusion. |

---

## 12. Known Limitations & Future Work

- **Classification quality depends on transcript quality** — speaker labels are
  not explicit in the SRT, so the model infers which utterances are the
  facilitator's; mislabeled speakers degrade results.
- **No automated eval harness** for the LLM output — there's no held-out
  labeled set scoring the current model (the archived ML scripts did produce
  `model_mistakes.csv`, but that's Phase 1).
- **Single-call classification** — very long transcripts could exceed context
  or hit token limits; no chunking is implemented.
- **Cost** — every uncached Analyze is one GPT call over the full transcript.
- **Supabase coupling** — analysis can run without the DB, but saving/history
  silently degrade (warnings only) when credentials are absent.
- Potential next steps: speaker diarization on ingest, a labeled eval set +
  accuracy dashboard, transcript chunking, export to the `.docx` report format
  seen in [Reports/](Reports/), and inter-rater comparison against human labels.
```