# AAC Prompt Classifier — Co-op Final Report

**Saumya Suripeddi**
**Co-op term: January – June 2026**

---

## Overview

Over this co-op term I designed and built the **AAC Prompt Classifier**, a web
application that analyzes AAC (Augmentative and Alternative Communication)
letterboarding therapy transcripts. A user uploads a session transcript and the
tool automatically labels every prompt the facilitator gave — by therapy method
(S2C vs RPM), by specific prompt type, and by the lab's detailed prompt-label
scheme — then renders an interactive report and tracks how a student's prompting
mix changes across sessions.

This report focuses on *how I approached the work*: the way I structured the
project, the path it took, the technical decisions I made and why, the problems
I worked through, and what I took away from it.

---

## The goal I was working toward

The lab needed a way to measure, objectively and consistently, what kinds of
prompts a facilitator used in a session. Done by hand, this is slow and
subjective — it means transcribing a recording, reading every line, judging each
prompt, and tallying the results, with different reviewers often disagreeing.
My objective was to turn that manual process into an automated, repeatable
analysis that produces the same labels every time and presents them in a form
the team can actually use.

---

## How I approached the project

I worked in an **iterative, end-to-end-first** way rather than trying to perfect
one piece before moving on. Early on I got a rough version of the whole pipeline
working — read a transcript, classify it, show something on screen — and then
improved each stage in passes. That kept me from over-investing in an approach
before I knew whether it would hold up against real transcripts.

A few principles guided the work:

- **Keep the stages separate.** I split the system into independent steps —
  reading the transcript, classifying the prompts, storing results, computing
  metrics, and rendering the report. Each piece can be understood, tested, and
  changed on its own. This made it far easier to swap out the classification
  approach later without touching everything else.
- **Test the parts I could test deterministically.** The transcript parsing and
  the counting logic have predictable outputs, so I wrote unit tests for them.
  This gave me a safety net while iterating on the rest.
- **Design for being wrong.** Because the analysis relies on an external AI
  service and a database, I built in defensive handling — robust parsing of the
  AI's output and automatic retries on network calls — so a single hiccup
  doesn't break a session.
- **Validate against real data continuously.** I tested against actual sample
  transcripts throughout, not just toy inputs, which is what surfaced the
  limitations of my first approach (below).

---

## Timeline

The project ran across the co-op term in roughly five phases:

| Phase | When | What I did |
|---|---|---|
| **1. Setup & framing** | Early January | Set up the project, defined the problem with the lab, and built a first end-to-end skeleton (`main.py`) with initial "teach / ask / spell" prompt logic. |
| **2. First UI & classification** | Mid–late January | Built the web interface (Streamlit), extracted the classification logic into its own module, and began classifying prompts. |
| **3. Classical ML approach** | Late January – February | Built a traditional machine-learning classifier — TF-IDF text features + logistic regression — trained on a few hundred labeled prompt examples, with evaluation (accuracy, confusion matrix) and a log of the model's mistakes for error analysis. Added the first analysis graphs. |
| **4. Pivot to an LLM** | March | After seeing the trained model's limits, I redesigned the classification around a large language model, writing a detailed rules-based labeling specification covering all three labeling dimensions. |
| **5. Full report, persistence & polish** | April – June | Built the complete visual report (charts, session timeline, cross-session trends, tabbed prompt tables), added the database layer with caching and history/trend tracking, refined the labeling rules, wrote tests, and produced project documentation. |

---

## The key decision: moving from a trained model to an LLM

The most significant turn in the project was switching the classification engine
partway through.

**What I tried first.** I started with a conventional supervised approach: I
assembled labeled prompt datasets, converted the prompt text into numerical
features (TF-IDF), and trained a logistic-regression classifier. I evaluated it
properly — accuracy, a classification report, a confusion matrix — and even
saved out the specific prompts it got wrong so I could study the failure
patterns.

**Why I changed course.** Studying those mistakes made the ceiling clear. The
trained model looked at each prompt in isolation, so it couldn't use context —
and context is exactly what decides many AAC labels (whether "What do you see?"
is open-ended or a clarification depends on what the student just did). It also
only produced one flat label, while the lab needed three independent labeling
dimensions, one of which allows multiple labels at once.

**What I moved to.** I redesigned the classifier around a large language model
guided by a detailed written specification. The real work here wasn't calling an
API — it was *engineering the instructions*: defining each label precisely, with
examples, and writing explicit tie-breaker rules so ambiguous prompts are always
resolved the same way. I also configured the model for deterministic output, so
the same transcript yields the same labels every run — important for a tool
meant to be consistent and trustworthy.

I kept the original ML code archived rather than deleting it, both as a record of
the approach and as a baseline to compare against.

---

## Other decisions I made along the way

- **Caching repeat analyses.** Each analysis calls a paid AI service, so I made
  the tool recognize when the same transcript has already been analyzed for a
  student and reuse the saved result — saving both time and cost.
- **Building the charts by hand.** Rather than pulling in a heavy charting
  library, I drew the report's visuals directly in the browser. This kept the
  tool lightweight and gave me full control so every chart shares one consistent
  color and labeling scheme.
- **Centralizing the label definitions.** All the prompt types, their colors,
  and their descriptions live in one place, so the donut chart, bars, timeline,
  tables, and trend chart always stay in sync — changing a label once updates it
  everywhere.
- **Graceful degradation.** The analysis still runs even if the database is
  unavailable; only the saving and history features quietly step back, so a
  missing connection never blocks the core task.

---

## Problems I worked through

- **Ambiguous prompts.** Many real prompts plausibly fit more than one label.
  I addressed this by writing explicit tie-breaker rules into the specification,
  so borderline cases are decided consistently instead of arbitrarily.
- **Unreliable AI output formatting.** AI responses don't always come back in a
  perfectly clean format. I wrote parsing that tolerates extra text or
  formatting and still reliably extracts the structured results.
- **Flaky network calls.** Database operations occasionally fail transiently, so
  I added automatic retries with increasing wait times to smooth over blips.
- **Speaker ambiguity in transcripts.** The subtitle files don't mark who is
  speaking, so I had to design the labeling instructions to reason about which
  lines are the facilitator's — and I documented this clearly as a known
  limitation and a candidate for future improvement.
- **Keeping the report readable as it grew.** As I added sections, I reworked
  the layout (for example, promoting the per-method counts into their own
  full-width section) so the report stayed clear rather than cramped.

---

## What I learned

- **End-to-end ownership of a real tool.** I took this from an empty repository
  to a working application — designing the architecture, choosing the
  technologies, and making the trade-offs myself.
- **When *not* to use machine learning.** Building, evaluating, and then
  deliberately retiring the trained model taught me to judge an approach against
  the actual requirements (context, multiple labels) rather than defaulting to
  the first technique that comes to mind.
- **Prompt and specification design.** I learned that getting reliable output
  from a language model is mostly about precise, example-driven instructions and
  explicit edge-case rules — and about configuring for reproducibility.
- **Designing for failure.** Working with external services pushed me to build
  in retries, fallbacks, and defensive parsing so the tool stays robust in
  real use.
- **Communicating the work.** I produced documentation at multiple levels — a
  technical specification for engineers and a plain-language overview for
  non-technical readers — which made me think about who each artifact is for.

---

## Current state

The application is **complete and works end to end**: upload a transcript →
automatic three-dimensional classification → saved results → an interactive
report with cross-session trends. It runs locally with a single command and
relies on two configured services (an AI provider and a database). Sample
transcripts and a full set of documentation are included, so the project is in a
clean state for someone else to pick up.

### What's solid
- The full pipeline runs reliably from upload to report.
- Classifications are consistent and reproducible.
- The report directly answers the lab's core question about the S2C/RPM balance,
  and the trend view turns single sessions into a picture of change over time.
- The code is cleanly separated and documented, and the deterministic parts are
  unit-tested.

### What I'd improve with more time
- **A formal accuracy benchmark** — measuring how often the AI's labels match a
  human expert on a held-out labeled set. This is the most valuable next step
  and would let the lab tune and trust the results with confidence.
- **Automatic speaker identification** so the tool doesn't have to infer who is
  talking.
- **Handling very long sessions** by analyzing them in chunks.
- **A downloadable report** (Word/PDF) and **hosting the app online** so
  non-technical team members can use it without any setup.

---

## Summary

I built a working, end-to-end tool that automates a previously slow and
subjective analysis, and I made a deliberate mid-project shift — from a trained
classifier to a specification-driven language model — once the requirements made
clear which approach would actually hold up. Along the way I designed the
architecture, engineered the labeling rules, built the report and persistence
layers, handled the rough edges of working with external services, and
documented it for both technical and non-technical audiences. The result is a
functional tool that meets its core goal, with a clear, well-understood set of
enhancements mapped out for whoever takes it forward.
</content>
