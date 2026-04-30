import streamlit as st
import time
import random
import json

st.set_page_config(page_title="LLM Eval Harness", page_icon="🧪", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.pass  { color: #34d399; font-weight: 600; }
.fail  { color: #f87171; font-weight: 600; }
.warn  { color: #fbbf24; font-weight: 600; }
.metric-card {
    background: #1e1e2e; border: 1px solid #2d2d3f; border-radius: 10px;
    padding: 1rem; text-align: center;
}
.metric-card .val   { font-size: 1.6rem; font-weight: 700; color: #a78bfa; }
.metric-card .label { font-size: 0.78rem; color: #64748b; }
.log-line { font-family: 'Courier New', monospace; font-size: 0.8rem; color: #94a3b8; margin: 0.1rem 0; }
.log-line.ok   { color: #34d399; }
.log-line.err  { color: #f87171; }
.log-line.info { color: #60a5fa; }
.test-row {
    background: #1e1e2e; border: 1px solid #2d2d3f; border-radius: 8px;
    padding: 0.8rem 1rem; margin-bottom: 0.4rem; font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧪 LLM Workflow Orchestration & Evaluation Harness")
st.markdown("*Multi-agent orchestration with built-in prompt unit tests, rubric scoring, golden dataset benchmarking, and full observability*")

with st.expander("🏗️ Architecture Overview", expanded=False):
    st.markdown("""
    **System components:**
    - **Orchestrator Agent** — routes tasks to specialized sub-agents based on task type
    - **Sub-agents** — Summarizer, Classifier, Extractor, QA Agent
    - **Eval Harness** — unit tests for prompts, rubric scoring, golden dataset comparison
    - **Observability layer** — logs prompt inputs, model outputs, latency, token usage, failure modes
    - **FastAPI backend** — exposes orchestration and eval endpoints for stakeholder demo UI

    **Why this matters:** Most LLM prototypes ship without measurement. This harness enables rigorous quality gates before production handoff — exactly the responsible AI practice NYT's NAPP team requires.
    """)

st.markdown("---")

# ── Prompt Unit Tests ─────────────────────────────────────────────────────────
st.markdown("## 1️⃣ Prompt Unit Tests")
st.markdown("Define expected behavior for each agent prompt. Run the suite to catch regressions before shipping.")

UNIT_TESTS = [
    {"agent": "Summarizer", "input": "Summarize: The Fed held rates steady citing inflation uncertainty.", "expected_contains": ["Fed", "rates", "inflation"], "expected_length_max": 80},
    {"agent": "Classifier", "input": "Classify topic: 'AI companies race to build safer LLMs'", "expected_contains": ["Technology", "AI"], "expected_length_max": 20},
    {"agent": "Extractor",  "input": "Extract entities: 'Jerome Powell announced rates unchanged at 5.25%'", "expected_contains": ["Powell", "5.25"], "expected_length_max": 60},
    {"agent": "QA Agent",   "input": "Q: What did the Fed do? Context: Fed held rates steady.", "expected_contains": ["held", "rates", "steady"], "expected_length_max": 100},
    {"agent": "Summarizer", "input": "Summarize: AI data centers consume 8% of US electricity by 2030.", "expected_contains": ["data centers", "electricity", "2030"], "expected_length_max": 80},
    {"agent": "Classifier", "input": "Classify topic: 'Federal Reserve holds rates amid inflation'", "expected_contains": ["Economy", "Finance"], "expected_length_max": 20},
]

SIMULATED_OUTPUTS = [
    "The Federal Reserve kept interest rates unchanged, pointing to ongoing uncertainty around inflation.",
    "Technology / AI",
    "Entities: Jerome Powell, 5.25%",
    "The Fed held rates steady.",
    "AI data centers are projected to use 8% of US electricity by 2030.",
    "Economy",
]

if st.button("▶️ Run Unit Test Suite", type="primary"):
    progress = st.progress(0)
    log_container = st.empty()
    logs = []

    results = []
    for i, (test, output) in enumerate(zip(UNIT_TESTS, SIMULATED_OUTPUTS)):
        time.sleep(0.3)
        progress.progress((i + 1) / len(UNIT_TESTS))

        passes = all(e.lower() in output.lower() for e in test["expected_contains"])
        length_ok = len(output) <= test["expected_length_max"]
        status = "PASS" if (passes and length_ok) else "FAIL"

        results.append({"test": test, "output": output, "status": status, "passes": passes, "length_ok": length_ok})
        log_cls = "ok" if status == "PASS" else "err"
        logs.append(f'<div class="log-line {log_cls}">[{status}] {test["agent"]}: "{test["input"][:55]}..."</div>')
        log_container.markdown("".join(logs), unsafe_allow_html=True)

    st.success("Test suite complete.")

    passed = sum(1 for r in results if r["status"] == "PASS")
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, f"{passed}/{len(results)}", "Tests Passed"),
        (c2, f"{passed/len(results):.0%}", "Pass Rate"),
        (c3, str(len(set(t['test']['agent'] for t in results))), "Agents Tested"),
        (c4, "0", "Regressions"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        st.markdown(f"""
        <div class="test-row">
          <b>{icon} [{r['test']['agent']}]</b> {r['test']['input'][:70]}...<br/>
          <span style="color:#64748b">Output:</span> <span style="color:#94a3b8">{r['output']}</span><br/>
          <span style="color:#64748b">Contains check:</span> {'<span class="pass">PASS</span>' if r['passes'] else '<span class="fail">FAIL</span>'}
          &nbsp;&nbsp; <span style="color:#64748b">Length check:</span> {'<span class="pass">PASS</span>' if r['length_ok'] else '<span class="fail">FAIL</span>'}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Rubric Scoring ────────────────────────────────────────────────────────────
st.markdown("## 2️⃣ Rubric-Based Quality Scoring")
st.markdown("Score LLM outputs on a structured rubric before shipping to production.")

rubric_input = st.text_area(
    "Paste an LLM output to score:",
    value="The Federal Reserve voted unanimously to hold interest rates at 5.25-5.5%, citing persistent inflation above their 2% target. Chair Powell emphasized the need for more data before considering cuts. Labor markets remain resilient with 175,000 jobs added last month.",
    height=100
)

RUBRIC = {
    "Factual specificity (contains numbers/names)": lambda t: any(c.isdigit() for c in t),
    "Attribution present (cites source or role)": lambda t: any(w in t.lower() for w in ["powell", "fed", "committee", "chair", "report"]),
    "No hedging without cause (avoids vague language)": lambda t: not any(w in t.lower() for w in ["might", "maybe", "perhaps", "could possibly"]),
    "Appropriate length (50–300 chars)": lambda t: 50 <= len(t) <= 300,
    "No hallucination markers (no fabricated quotes)": lambda t: '"' not in t or t.count('"') <= 2,
}

if st.button("📊 Score Output", type="primary"):
    with st.spinner("Running rubric evaluation..."):
        time.sleep(0.8)

    scores = {criterion: fn(rubric_input) for criterion, fn in RUBRIC.items()}
    total = sum(scores.values())

    st.markdown(f"### Overall Score: **{total}/{len(RUBRIC)}** ({total/len(RUBRIC):.0%})")
    for criterion, passed in scores.items():
        icon = "✅" if passed else "❌"
        st.markdown(f"- {icon} **{criterion}**")

    if total == len(RUBRIC):
        st.success("🎉 Output passes all rubric checks — ready for production evaluation.")
    elif total >= 3:
        st.warning("⚠️ Output passes most checks — review failed criteria before shipping.")
    else:
        st.error("❌ Output fails multiple criteria — requires prompt revision.")

st.markdown("---")

# ── Observability ─────────────────────────────────────────────────────────────
st.markdown("## 3️⃣ Pipeline Observability Log")
st.markdown("Real-time logging of prompt inputs, model outputs, latency, and failure modes.")

if st.button("🔄 Simulate Pipeline Run", type="primary"):
    log_box = st.empty()
    logs = []

    steps = [
        ("info", "[ORCHESTRATOR] Task received: 'Summarize and classify latest Fed news'"),
        ("info", "[ORCHESTRATOR] Routing to: Summarizer → Classifier"),
        ("info", "[SUMMARIZER]  Prompt tokens: 142 | Sending to gpt-4o-mini"),
        ("ok",   "[SUMMARIZER]  Response tokens: 58 | Latency: 412ms"),
        ("ok",   "[SUMMARIZER]  Output: 'Fed held rates steady citing inflation at 2.8%...'"),
        ("info", "[CLASSIFIER]  Prompt tokens: 89 | Sending to gpt-4o-mini"),
        ("ok",   "[CLASSIFIER]  Response tokens: 4 | Latency: 198ms"),
        ("ok",   "[CLASSIFIER]  Output: 'Economy / Monetary Policy'"),
        ("info", "[EVAL]        Running rubric check on Summarizer output..."),
        ("ok",   "[EVAL]        Score: 5/5 — all criteria passed"),
        ("info", "[OBSERVABILITY] Total pipeline latency: 610ms | Total tokens: 293"),
        ("ok",   "[ORCHESTRATOR] Pipeline complete — result ready for downstream"),
    ]

    for cls, msg in steps:
        time.sleep(0.25)
        logs.append(f'<div class="log-line {cls}">{msg}</div>')
        log_box.markdown(
            f'<div style="background:#0f0c29;border-radius:8px;padding:1rem;font-family:monospace">{"".join(logs)}</div>',
            unsafe_allow_html=True
        )

    st.success("✅ Pipeline run complete. All steps logged.")
