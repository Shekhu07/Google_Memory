"""Google Photos retrieval discovery engine: public demo (Hugging Face Space).

Tabs:
  1. Try a memory: describe a photo you can't find; see the clues the engine
     extracts and how real people with the same clues fared.
  2. Compare retrieval problems: hypotheses ranked by the pre-registered rule,
     plus breakdowns by era, failure stage and clue type.
  3. How it works: pipeline, funnel counts, audit, limitations.

Env: GROQ_API_KEY (Space secret). Optional: DEMO_MODEL, DEMO_TOKEN_CAP, DEMO_MAX_CHARS.
"""
import os

import gradio as gr
import pandas as pd
from sentence_transformers import SentenceTransformer

import demo_core as core
from engine.groq import DailyBudgetReached, GroqClient

DEMO_MODEL = os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b")
DEMO_TOKEN_CAP = int(os.environ.get("DEMO_TOKEN_CAP", "60000"))
# The cap is enforced through data/interim/groq_usage.json, and a Space filesystem is
# ephemeral: a rebuild or wake-from-sleep re-clones the repo and resets the counter.
# So this is a per-container-life cap, not a true daily one. That is acceptable only
# because DEMO_MODEL is deliberately NOT the pipeline model - the worst case is this
# demo losing live extraction for a while, never the pipeline losing its budget.
MAX_CHARS = int(os.environ.get("DEMO_MAX_CHARS", "500"))

bundle = core.load_bundle()
episodes = bundle["episodes"]
embedder = SentenceTransformer(bundle["manifest"].get("embed_model",
                                                      "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"))
client = GroqClient(DEMO_MODEL, daily_cap=DEMO_TOKEN_CAP) if os.environ.get("GROQ_API_KEY") else None

EXAMPLES = [
    "That small café we went to during our Goa trip.",
    "The picture of the medicine I took when I was sick last year.",
    "bimari ke time jo dawai ki photo li thi, pichle saal",
    "The receipt for the washing machine, I think it was around Diwali two years ago",
    "My dad's photos from the family wedding, before he passed away",
]


SHORT_ERA = {"pre_ask": "before Ask Photos", "ask_launch": "Ask Photos launch", "hybrid": "hybrid", "toggle": "toggle"}


def _human(value) -> str:
    return value.replace("_", " ") if isinstance(value, str) else value


def _table(rows: list) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame({"": ["No data yet"]})
    df = pd.DataFrame([{k: _human(v) for k, v in r.items()} for r in rows])
    df.columns = [_human(c) for c in df.columns]
    return df


def _shown(rows: list) -> gr.Dataframe:
    """A results table that only appears once there is something in it."""
    df = pd.DataFrame([{k: _human(v) for k, v in r.items()} for r in rows])
    return gr.Dataframe(value=df, visible=bool(rows))


def _fmt(values: list) -> str:
    return ", ".join(v.replace("_", " ") for v in values) if values else "none identified"


def analyse(memory: str):
    memory = (memory or "").strip()[:MAX_CHARS]
    if not memory:
        return "Describe a photo you're trying to find.", _shown([]), _shown([])

    notes, extracted = [], None
    if client is None:
        notes.append("Live extraction is off (no API key). Showing text-similarity matches only.")
    else:
        try:
            extracted = core.extract_memory(client, memory)
        except DailyBudgetReached:
            notes.append("The demo's daily model budget is used up. Showing text-similarity matches only.")
        except Exception as e:  # network or model failure: degrade, don't crash the demo
            notes.append(f"Live extraction failed ({type(e).__name__}). Showing text-similarity matches only.")

    query_vec = embedder.encode([memory], normalize_embeddings=True)[0]
    matches = core.similar_episodes(bundle, query_vec, extracted)

    lines = []
    if extracted:
        hyps = [f"**{h}** – {core.HYPOTHESIS_NAMES[h]}" for h in extracted["hypotheses"]]
        # cues_lost is not shown: the small demo model marks every unstated field as "lost".
        lines += [
            "### What the engine reads in your memory",
            f"- **Looking for:** {extracted['asset_type'].replace('_', ' ')}",
            f"- **Clues you still have:** {_fmt(extracted['cues_retained'])}",
            f"- **Language:** {extracted['query_language'].replace('_', ' ')}",
            *([f"- **Retrieval problems your description already shows:** {'; '.join(hyps)}"] if hyps else []),
            "",
            f"<sub>Extracted live by `{DEMO_MODEL}` with the same prompt the pipeline used "
            f"(the pipeline itself ran on gpt-oss-120b).</sub>",
        ]
    lines += [f"> {n}" for n in notes]

    cue_rows = core.cue_outcomes(episodes, extracted["cues_retained"]) if extracted else []
    match_rows = [{
        "what they said": f"[{m['evidence'][:160]}]({m['url']})" if m["url"] else m["evidence"][:160],
        "clues": _fmt(m["cues_retained"]), "where it broke": m["failure_stage"],
        "hypotheses": ", ".join(m["hypotheses"]) or "—",
        "source": m["source"], "when": f"{m['date'][:7]} ({SHORT_ERA[m['era']]})", "match": m["match"],
    } for m in matches]
    return "\n".join(lines), _shown(cue_rows), _shown(match_rows)


def fixture_banner() -> str:
    m = bundle["manifest"]
    if m.get("fixture"):
        return (f"> ⚠️ **Development fixture:** this build uses {m.get('n_episodes')} trial extractions, "
                "not the full corpus. Numbers below are not findings.")
    return f"Built from **{m.get('n_episodes', len(episodes))}** extracted posts."


def audit_markdown() -> str:
    audit = bundle["audit"]
    if not audit or not audit.get("agreement"):
        return "_Audit report not included in this build yet._"
    ag, v = audit["agreement"], audit["verdict"]
    rows = "\n".join(f"| {f} | {x.get('agreement', x.get('mean_jaccard'))} | {x.get('kappa', '—')} |"
                     for f, x in ag["fields"].items())
    return (f"**Second model:** `{audit['audit_model']}` ({audit['independence'].replace('_', ' ')}), "
            f"blind to the first model's answers, on a stratified sample of {ag['n']} posts.\n\n"
            f"| field | agreement / overlap | kappa |\n|---|---|---|\n{rows}\n\n"
            f"Exact-quote check: primary {ag['evidence_verified']['primary']:.0%}, "
            f"audit {ag['evidence_verified']['audit']:.0%}.\n\n"
            f"**Verdict:** {v.get('status')}; top-2 primary {v.get('primary_top2')}, audit {v.get('audit_top2')}.")


HOW_IT_WORKS = """
### Unit of analysis: a retrieval episode, not a review
Each post is turned into a structured record of **one attempt to find a photo**: what the person still remembered,
what they'd lost, what they typed, where it broke, what they did instead and how it ended. General complaints about
search are kept too, but labelled as such, so they're never counted as episodes.

### Pipeline
1. **Collect**: Play Store reviews (English + Hindi, Jan 2024 onward), App Store reviews (8 countries),
   YouTube comments on Ask Photos and photo-search videos. No author names are stored.
2. **Keyword filter** (free): keeps posts that talk about searching, finding or scrolling.
3. **Model screen** (`gpt-oss-120b`): relevant or not. Binary, because a trial showed models can't reliably split
   "episode" from "complaint" at this stage.
4. **Extraction** (`gpt-oss-120b`): fixed vocabularies for every field; each record carries a quote that must appear
   word-for-word in the post.
5. **Audit** (`qwen3.8-27b`, a different model family): re-extracts a stratified sample blind and with a
   separately written prompt; agreement and ranking stability are reported below.
6. **Compare**: hypotheses written down *before* the data was seen are ranked by a pre-registered rule:
   share of specific attempts supporting it × share of those that ended badly.

### Limitations
- Groq free tier: the model stages ran on a **1,200-post sample** drawn evenly across sources and eras,
  not on every keyword match.
- Play Store dominates the sample (~80%). Reddit is planned via Apify but not yet included.
- Most reviews don't say whether the person eventually found the photo, so the pre-registered score rests on
  a smaller pool than the headline counts.
- H6 was added after looking at trial data and is reported as post-hoc.
"""


with gr.Blocks(title="Photo Retrieval Discovery Engine") as demo:
    gr.Markdown("# Why can't people find photos they remember?\n"
                "A discovery engine over public Google Photos reviews and comments. "
                "Independent research prototype, not affiliated with Google.")
    gr.Markdown(fixture_banner())

    with gr.Tab("Try a memory"):
        memory = gr.Textbox(label="Describe a photo you're trying to find", lines=3, max_length=MAX_CHARS,
                            placeholder="e.g. the medicine I photographed when I was sick last year")
        go = gr.Button("Analyse", variant="primary")
        gr.Examples(EXAMPLES, inputs=memory)
        summary = gr.Markdown()
        cue_df = gr.Dataframe(label="How real people with these clues fared", show_label=True,
                              interactive=False, wrap=True, visible=False)
        match_df = gr.Dataframe(label="Most comparable real posts (quotes link to the original)", show_label=True,
                                interactive=False, wrap=True, datatype="markdown", visible=False,
                                column_widths=["38%", "17%", "13%", "9%", "8%", "10%", "5%"])
        go.click(analyse, inputs=memory, outputs=[summary, cue_df, match_df])
        memory.submit(analyse, inputs=memory, outputs=[summary, cue_df, match_df])

    with gr.Tab("Compare retrieval problems"):
        gr.Markdown("### Hypotheses ranked by the pre-registered rule")
        gr.Dataframe(_table(core.ranking_table(episodes)), interactive=False, wrap=True)
        gr.Markdown("### Which problems show up in each era (share of posts)")
        gr.Dataframe(_table(core.by_era(episodes, "hypotheses", core.HYPOTHESES, list_field=True)),
                     interactive=False, wrap=True)
        gr.Markdown("### Where retrieval breaks, by era")
        gr.Dataframe(_table(core.by_era(episodes, "failure_stage", core.failure_values(episodes))),
                     interactive=False, wrap=True)
        gr.Markdown("### What people remember, and how it goes")
        gr.Dataframe(_table(core.cue_table(episodes)), interactive=False, wrap=True)

    with gr.Tab("How it works"):
        gr.Markdown(HOW_IT_WORKS)
        gr.Markdown("### Funnel")
        gr.Dataframe(_table(core.funnel_rows(bundle["funnel"])), interactive=False)
        gr.Markdown("### Audit")
        gr.Markdown(audit_markdown())

if __name__ == "__main__":
    demo.launch()
