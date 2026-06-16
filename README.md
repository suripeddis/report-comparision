# AAC Prompt Classifier

A Streamlit web app that analyzes Augmentative and Alternative Communication (AAC) letterboarding therapy session transcripts. Upload an SRT file and the app classifies every facilitator prompt into one of five evidence-based categories using GPT-4.

## Prompt categories

| Category | Description |
|---|---|
| **Choice** | Offers the student discrete, explicit options |
| **Clarification** | Asks the student to confirm or expand on something they already communicated |
| **Guided** | Scaffolds toward a specific answer via letter cues or directional hints |
| **Open-ended** | Invites a free response with no constraints or implied target |
| **Reinforcement** | Encourages effort or regulates emotion without eliciting new information |

## Project structure

```
.
├── app.py                        # Streamlit entry point
├── requirements.txt
├── .env.example                  # Copy to .env and fill in your keys
├── Makefile                      # Common dev tasks
├── pipelines/
│   └── steps/
│       ├── classifier.py         # OpenAI GPT-4 classification
│       ├── database.py           # Supabase persistence
│       ├── ingest_transcript.py  # SRT parsing
│       └── metrics.py            # Aggregation helpers
├── templates/
│   └── report_template.html      # Embedded HTML report
├── tests/
│   └── test_pipeline.py
└── data/                         # Sample / training data
```

## Setup

### 1. Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/account/api-keys)
- A [Supabase](https://supabase.com) project with a `sessions` table

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY
```

### 4. Run the app

```bash
streamlit run app.py
# or: make run
```

## Usage

1. Open the app in your browser (default: `http://localhost:8501`).
2. Upload an `.srt` transcript file.
3. Click **Analyze**.
4. Review the prompt distribution chart and the classified prompt table.

## Development

```bash
make test    # Run unit tests
make lint    # Lint with flake8
```

## Database schema

The `sessions` table in Supabase should have at minimum:

```sql
create table sessions (
  id          uuid primary key default gen_random_uuid(),
  file_name   text,
  results     jsonb,
  created_at  timestamptz default now()
);
```
