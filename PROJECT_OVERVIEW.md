# AAC Prompt Classifier — Project Overview

*A plain-language guide to what this project is, what it does, and how it works.*

---

## What this project is, in one sentence

It's a web tool that reads a transcript of an AAC therapy session, automatically
labels every prompt the facilitator gave, and turns it into a clear visual
report — so you can see, at a glance, what kinds of prompting happened and how a
student's sessions change over time.

---

## The problem it solves

In AAC (Augmentative and Alternative Communication) letterboarding therapy, a
facilitator helps a non-speaking or minimally-speaking person communicate by
pointing to letters on a board. *How* the facilitator prompts matters a great
deal:

- Some prompts gently guide the **physical act** of pointing — steadying an arm,
  cueing a breath, indicating which row of the board to look at. This kind of
  motor- and regulation-focused prompting is the hallmark of the **S2C
  (Spelling to Communicate)** approach.
- Other prompts focus on the **thinking and content** — asking a question,
  offering choices, inviting an open-ended response. This kind of academic,
  content-focused prompting is the hallmark of the **RPM (Rapid Prompting
  Method)** approach.

The balance between these two kinds of prompting is clinically meaningful. A
session heavy on physical guidance looks very different — and raises different
questions about the student's independence — than a session built around
open-ended questions. Researchers and practitioners want to measure that
balance objectively.

The trouble is that doing this by hand is painful. Someone has to listen to a
recording, transcribe it, read through every line, decide what kind of prompt
each one was, and tally it all up. It takes a long time, and two different
reviewers might label the same prompt differently. **This tool automates that
entire analysis and applies the same labeling rules every time, consistently.**

---

## Who it's for

- **Practitioners / facilitators** who want a clear summary of how they prompted
  during a session, and how their style changes across sessions with a student.
- **Researchers** studying AAC methods, who need consistent, structured labels
  across many sessions to spot patterns.
- **Supervisors and reviewers** who want an at-a-glance, objective picture of a
  session without watching the whole recording.

---

## What you do with it (the experience, step by step)

1. **Open the app** in a web browser. It's a single page — nothing to install
   for the person using it.
2. **Enter a few details** (all optional):
   - the **student's name** — adding this is what unlocks history and
     trend-tracking across multiple sessions;
   - the **practitioner's name**;
   - a short **session topic** (e.g. "Volcano lesson"), which becomes a helpful
     label on the trend chart later.
3. **Upload a transcript file** of the session. The tool expects an `.srt` file
   — the same simple subtitle/caption format used for videos, which most
   transcription tools can produce.
4. **Click "Analyze."** The tool reads the transcript and labels every prompt
   the facilitator gave. This usually takes a few moments.
5. **Review the report** — a single page of charts and tables showing what kinds
   of prompts were used and in what proportions (described in detail below).
6. **Come back any time.** Saved sessions can be reloaded from a "Previous
   Sessions" list, and once a student has more than one session on file, the
   report automatically includes a chart showing how their prompt mix has
   shifted over time.

A nice convenience: if you analyze the exact same transcript for the same
student again, the tool recognizes it and instantly reuses the earlier result
instead of re-doing the analysis — which is both faster and avoids unnecessary
cost.

---

## How it labels each prompt (the heart of the tool)

This is the core of what the project does. For **every single thing the
facilitator says to the student**, the tool answers three separate questions.
Think of them as three independent "tags" applied to each prompt.

### Question 1 — Which *overall style* of therapy does this prompt belong to?

Each prompt is sorted into one of two well-known AAC approaches:

- **S2C (Spelling to Communicate)** — prompts focused on the **physical and
  regulatory** side of the activity: guiding movement, steadying the body,
  helping the student stay regulated, and indicating where on the board to
  point.
  *Examples:* "Find the top row." · "Take a breath and reset." · "Open your
  hand." · "Eyes on the board."

- **RPM (Rapid Prompting Method)** — prompts focused on the **academic and
  content** side: questions, choices, and engagement with ideas and information.
  *Examples:* "What is the main idea of the paragraph?" · "Choose: volcano or
  earthquake?" · "Tell me about the character."

Some prompts touch on both at once. The rule the tool follows is to label by the
prompt's **main intent** — if it's mostly about the physical act of pointing,
it's S2C; if it's mostly about the content of the answer, it's RPM.

### Question 2 — What *specific kind* of prompt is it?

Once the overall style is decided, the prompt gets a more precise label drawn
from that style's vocabulary:

**If it's an S2C (physical/regulatory) prompt, it's one of:**

- **Initiation** — a cue to *start* moving. *("Let's begin." / "Go ahead.")*
- **Continuation** — a cue to *keep going* with movement already underway.
  *("Keep going." / "What comes next?")*
- **Gesture** — a physical or pointing cue (the facilitator points to or taps
  near the board, or demonstrates the motion).
- **Direction** — a spatial cue about *where* to point. *("Top row." / "Move
  your arm right.")*
- **None** — not really a prompt at all (an acknowledgement, narration, or
  off-task remark).

**If it's an RPM (academic/content) prompt, it's one of:**

- **Choice** — offering the student specific options to pick from. *("Do you
  want this one, or this one?")*
- **Clarification** — asking the student to confirm, correct, or expand on
  something they already communicated. *("Did you mean 'brings,' or something
  else?")*
- **Guided** — nudging the student toward a specific intended answer using hints
  or letter cues. *("It starts with S — find it.")*
- **Open-ended** — inviting a free response with no particular answer in mind.
  *("What are you noticing in this picture?")*
- **Reinforcement** — encouragement that affirms effort or keeps the student
  going, without asking for new information. *("You're doing great, keep
  going.")*

Because some prompts are genuinely ambiguous, the tool follows a set of
"tie-breaker" rules so that borderline cases are always handled the same way.
For example: an RPM prompt that includes letter cues is labeled *Guided* even if
it's phrased as a question; an S2C prompt using spatial words like "top" or
"right" is labeled *Direction*.

### Question 3 — What *detailed research labels* apply?

Finally, each prompt is tagged with one **or more** of twelve fine-grained labels
used by the research lab. Unlike the first two questions, a single prompt can
carry several of these at once. The twelve labels are:

*Encouragement, Dictation, Instruction, Short-term-memory support, Question,
Hands (hand guidance), Directional, Positive reinforcement, Gaze cue, Physical
(physical assistance), Regulation, and Focus.*

For example, a prompt like *"Look up here — what did the character feel?"* might
be tagged both **Question** and **Directional** at the same time. A prompt like
*"Yes! That's exactly right, keep trying!"* might be tagged both **Positive
reinforcement** and **Encouragement**. This multi-label scheme captures nuance
that a single label would miss.

---

## A quick worked example

Suppose the transcript contains this facilitator line:

> "Great effort — now find the top row."

The tool would label it roughly like this:

- **Style:** S2C (it's about the physical act of pointing, not content).
- **Specific kind:** Direction (it names a spatial location, "the top row").
- **Research labels:** Encouragement (the "great effort" part) *and* Directional
  (the spatial cue).

Every prompt in the session gets this treatment, and then the tool counts it all
up to build the report.

---

## What the report shows you

The report is a single, polished page. Reading top to bottom, it contains:

- **Headline numbers** — four big figures at the top: the total number of
  prompts in the session, how many distinct prompt types appeared, how many were
  S2C, and how many were RPM. This is the quick "size and shape" of the session.

- **Prompt-type breakdown** — a donut (ring) chart and a set of horizontal bars
  showing the mix of prompt types — which types dominated and which were rare.

- **Method breakdown** — a clear side-by-side of how the session split between
  the S2C and RPM approaches, shown both as counts and as percentages, with a
  visual split bar. This directly answers the central question: *how much of
  this session was physical-guidance prompting versus content prompting?*

- **Counts by method** — three side-by-side cards (one for S2C, one for RPM, one
  for the research lab's labels). Each card lists exactly how many of *every*
  prompt type appeared — including the types that didn't come up at all, shown
  as zero, so nothing is hidden and the full picture is always visible.

- **Session timeline** — a colorful strip where each small block represents one
  prompt, laid out in the order they actually happened during the session.
  Hovering over a block reveals the exact words of that prompt. This lets you
  see the *rhythm* of a session — for instance, whether physical prompts
  clustered at the start and content prompts came later.

- **Trends over time** — when a student has more than one saved session, this
  chart shows how their prompt mix has shifted from session to session. It's the
  feature that turns single snapshots into a story of progress.

- **Full prompt list** — searchable tables of every prompt, organized by
  approach, so you can read the exact wording of each prompt alongside its
  labels and verify the analysis for yourself.

---

## How it works behind the scenes (the short version)

1. **Reading the transcript.** The tool takes the uploaded subtitle file and
   strips out the line numbers and timing information, leaving just the spoken
   words.

2. **Labeling with AI.** The cleaned-up transcript is sent to a large language
   model — the same kind of AI technology behind tools like ChatGPT — together
   with a detailed set of written instructions describing exactly how to label
   each prompt across all three of the dimensions above. The AI reads the whole
   session (so it understands context) and returns a structured list of every
   facilitator prompt with its labels. Importantly, the tool is configured so
   that the *same transcript produces the same labels every time* — the results
   are consistent and repeatable, not random.

3. **Counting and charting.** The tool tallies up all the labels and builds the
   charts and tables in the report.

4. **Saving and remembering.** Each analyzed session is stored in a secure
   online database. That's what allows sessions to be reloaded later, compared
   over time, and reused (so the same transcript is never analyzed — or paid
   for — twice).

---

## The tools used to build it

In plain terms, the project is assembled from a handful of components:

- **A web-app framework** that turns the underlying code into an interactive web
  page, handling the file upload, the input boxes, and the embedded report.
- **An AI language model** (from OpenAI) that performs the actual prompt
  classification — this is the "brain" of the analysis.
- **An online database** (a service called Supabase) that securely stores each
  session's results and powers the history and trend-tracking features.
- **Custom-built charts**, drawn directly in the web browser rather than using
  off-the-shelf charting software. Building them by hand gave the report a
  consistent, tailored look and kept the colors and labels uniform across every
  section.

*(Earlier in development, the project used a simpler, traditional machine-
learning model trained on a few hundred example prompts. That approach was
replaced by the AI language model because the language model can read the full
context of a session and apply all three labeling dimensions at once — something
the simpler model couldn't do. The older approach is kept on file for
reference.)*

---

## How the project came together

The project evolved through two distinct phases:

1. **First approach — a trained model.** Early on, a traditional
   machine-learning model was trained on a few hundred example prompts, learning
   to recognize prompt types from patterns of words. It worked for assigning a
   single, simple label, but it couldn't take context into account — it looked
   at each prompt in isolation — and it couldn't produce the multiple,
   simultaneous labeling dimensions the research called for.

2. **Current approach — an AI language model.** The project then switched to a
   modern AI language model guided by a carefully written set of labeling rules.
   This produces richer, context-aware labels across all three dimensions in a
   single step. The detailed instructions and tie-breaker rules are what make
   its output consistent and aligned with how a human expert would label. This
   is the approach that powers the app today.

This progression — from a narrow trained model to a flexible, rule-guided AI —
is itself one of the more instructive outcomes of the project.

---

## Honest limitations

No tool is perfect, and it's worth being clear about where this one has room to
grow:

- **It depends on the quality of the transcript.** Subtitle files don't clearly
  mark who is speaking, so the AI has to infer which lines are the facilitator's
  (versus the student, a parent, or an observer). A messy or ambiguous
  transcript makes that harder and can reduce accuracy.

- **There's no formal accuracy scorecard yet.** The labels are consistent and
  follow detailed rules, but the project hasn't yet measured, on a set of
  expert-labeled examples, exactly how often the AI agrees with a human expert.
  Establishing that benchmark is the most valuable next step.

- **Very long sessions could hit a size limit.** The whole transcript is
  analyzed in one pass, which works well for typical sessions but could run into
  limits for unusually long ones.

- **Each fresh analysis has a small cost.** Because it uses a paid AI service,
  every new analysis costs a little (re-viewing an already-saved session is
  free).

- **It currently runs locally.** Using it means running the app on a computer
  set up for it, rather than visiting a public website.

---

## Where it could go next

- **An accuracy dashboard** comparing the AI's labels against a set of
  human-reviewed prompts, to measure and build trust in the results.
- **Automatic speaker identification** in the transcript, so the tool doesn't
  have to guess who is talking.
- **Handling very long sessions** by analyzing them in smaller pieces.
- **A "Download report" button** to export the report as a Word document or PDF
  for sharing and record-keeping.
- **Hosting it online** at a shared web address, so any team member can use it
  without any setup.

---

## In summary

This project takes a slow, subjective, manual task — figuring out what kinds of
prompts a facilitator used in an AAC session — and turns it into a fast,
consistent, automated analysis with a clear visual report. It labels every
prompt three different ways, measures the balance between the two main therapy
methods, and tracks how a student's sessions change over time. It's a working,
end-to-end tool, with a well-understood set of enhancements that would take it
even further.
</content>
