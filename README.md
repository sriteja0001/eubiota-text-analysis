# Feedback-text analysis — why one system was picked over the other

Text analysis of human-study feedback comparing **Eubiota** (a multi-agent deep-research system,
labelled `agent`) against a **general chatbot** (`llm`) on gut-microbiome questions. For each
comparison an evaluator chose a winner and wrote a short **free-text reason**; this project analyses
that reasoning — *what makes people prefer one system over the other?*

## Quick start

```bash
uv sync                                        # create the locked env (.venv)
uv run python code_themes.py                   # (re)generate the LLM theme codes -> data/
uv run jupyter lab feedback_text_analysis.ipynb   # walk through the analysis
```

Or run it headlessly:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace feedback_text_analysis.ipynb
```

## Data handling (important)

- **Only the `ANONYMOUS ` files are read** — the loader asserts it, and ignores the non-anonymous
  copies.
- **`/data` is git-ignored** (see `.gitignore`), so no study data is ever pushed to GitHub.
- Two batches are unified (`previous`, `current`); **ties are kept** for the data figures and excluded
  only from the agent-vs-LLM theme comparisons.
- The comments are **preset-heavy**: ~285 usable comments collapse to **86 unique strings** (some
  presets recur 20–40×). The analysis reports the **weighted** view (every evaluation counts) as
  primary and uses the unique strings for clustering/embeddings.

## Theme coding (LLM-coded, auditable)

`code_themes.py` holds the **LLM coding** (Claude Opus 4.8) of each unique comment into 10 quality
themes with **target attribution** — did the comment *praise the chosen winner* or *criticise the
rejected loser* (and with what valence). It writes `data/feedback_theme_codes.csv`, a file you can
open and audit row by row. If the corpus grows, the script asserts the unique-count so stale codes
fail loudly; re-code by extending it (or wire in an Anthropic-API call).

- **Where the 10 themes came from:** a hybrid of the study's own scoring rubric (thoroughness,
  accuracy, actionability, transparency, use-of-resources) and concepts that recurred on a first read
  (specificity, conciseness, clarity/structure, unsupported/speculative claims, retrieval/tool failure).
- **Coverage: 100%** — every one of the 86 unique comments received ≥1 theme, so **no "other" bucket
  was needed** (the notebook computes and prints this).
- A single comment can carry **both** praise and criticism (26 of 86 do), and all tags are kept.

## The figures (all SVG, Arial)

| Fig | What |
|---|---|
| 1 | **Dataset flow** — rows → usable feedback, and wins by system, per batch |
| 2 | **Feedback availability** — % substantive comments by batch & winner (previous batch is mostly blank) |
| 3 | **Feedback length** — words per comment by system, faceted by batch |
| 4 | **Theme frequencies** — share of wins praising each theme, Eubiota vs LLM |
| 5 | **Target attribution** — per theme, praise-of-winner vs criticism-of-loser |
| 6 | **Theme enrichment** — log2 fold-change (Eubiota-win vs LLM-win) with bootstrap CIs (exploratory) |
| 7 | **Co-occurrence** — which reasons are cited together |
| 8 | **Word clouds** — per system (true vector SVG) |
| 9 | **Semantic map** — sentence-transformer embedding of unique comments, sized by usage |
| 10 | **LLM-win deep-dive** — why the chatbot beat the agent, + representative quotes |

Plus a **representative-quote gallery** and a computed **summary**. All figures share one muted,
colourblind-safe palette — **Eubiota = blue, Chatbot = gold** — and are exported as editable-text SVG.

## Headline finding

- **Eubiota (agent)** wins are praised most for **transparency/trace, citations/evidence, and
  thoroughness** — reviewers trust *verifiable, well-sourced* answers.
- **Chatbot (LLM)** wins cluster on **clarity/structure, conciseness, and accuracy of the actual
  answer** — sometimes a *sharper, more readable* reply wins, especially when the agent's retrieval
  failed or its citations were weak/dated.
- Target attribution shows some themes (notably citations) appear heavily as *criticism of the loser*,
  not just praise of the winner — a real driver of rejection.

## Layout

```
eubiota-text-feedback-analysis/
├── .gitignore                    # /data ignored — data never pushed
├── pyproject.toml / uv.lock      # locked env (uv)
├── code_themes.py                # LLM theme coding -> data/feedback_theme_codes.csv (auditable)
├── feedback_text_analysis.ipynb  # the analysis (runs top-to-bottom)
├── data/                         # (git-ignored) ANONYMOUS inputs + derived CSVs
└── figures/                      # figN_*.svg — all SVG, editable Arial text
```
