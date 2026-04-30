import streamlit as st

st.set_page_config(
    page_title="Jalen Bennett — AI Portfolio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
}
.hero h1 { font-size: 2.8rem; font-weight: 700; margin: 0 0 0.4rem 0; }
.hero .subtitle { font-size: 1.15rem; color: #c4b5fd; margin-bottom: 1rem; }
.hero .bio { font-size: 0.97rem; color: #e2e8f0; line-height: 1.7; max-width: 720px; }

.tag {
    display: inline-block;
    background: rgba(139,92,246,0.25);
    color: #c4b5fd;
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 999px;
    padding: 0.25rem 0.85rem;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 0.2rem 0.2rem 0.2rem 0;
}

.project-card {
    background: #1e1e2e;
    border: 1px solid #2d2d3f;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.project-card:hover { border-color: #7c3aed; }
.project-card h3 { margin: 0 0 0.4rem 0; font-size: 1.05rem; color: #f1f5f9; }
.project-card p  { margin: 0 0 0.8rem 0; font-size: 0.88rem; color: #94a3b8; line-height: 1.6; }

.stat-box {
    background: #1e1e2e;
    border: 1px solid #2d2d3f;
    border-radius: 10px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.stat-box .num  { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
.stat-box .label{ font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }

.contact-link {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.35);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #c4b5fd;
    font-size: 0.88rem;
    font-weight: 500;
    text-decoration: none;
    margin-right: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Jalen Bennett</h1>
  <div class="subtitle">AI/LLM Engineer · CS @ UIUC · Available Summer 2026</div>
  <div class="bio">
    I build AI-powered systems that solve real problems — from RAG pipelines and LLM workflow orchestration
    to evaluation harnesses and semantic retrieval engines. I'm obsessed with shipping prototypes that
    actually work, measuring their quality rigorously, and iterating fast based on what I learn.
  </div>
  <br/>
  <span class="tag">Python</span>
  <span class="tag">LangChain / LangGraph</span>
  <span class="tag">RAG Pipelines</span>
  <span class="tag">OpenAI API</span>
  <span class="tag">FastAPI</span>
  <span class="tag">FAISS</span>
  <span class="tag">Prompt Engineering</span>
  <span class="tag">LLM Evaluation</span>
  <span class="tag">React</span>
  <span class="tag">AWS</span>
</div>
""", unsafe_allow_html=True)

# ── Stats ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, num, label in [
    (c1, "3", "AI Projects Shipped"),
    (c2, "4", "LLM APIs Integrated"),
    (c3, "2", "Full-Stack Apps"),
    (c4, "∞", "Iterations Made"),
]:
    with col:
        st.markdown(f"""
        <div class="stat-box">
          <div class="num">{num}</div>
          <div class="label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Projects ─────────────────────────────────────────────────────────────────
st.markdown("### 🚀 Featured Projects")
st.markdown("*Use the sidebar to explore each project interactively.*")

projects = [
    {
        "emoji": "📰",
        "title": "Journalism AI Companion — RAG Article Navigator",
        "desc": "A RAG-powered reader experience that lets you semantically search and Q&A a corpus of news articles. Built with FAISS vector search, LangChain orchestration, prompt guardrails, and rubric-based evaluation. Designed with responsible AI principles: source attribution, bias checks, and transparent confidence scoring.",
        "tags": ["RAG", "FAISS", "LangChain", "OpenAI API", "Streamlit", "Guardrails", "LLM Eval"],
        "page": "Journalism_RAG_Navigator",
    },
    {
        "emoji": "🧪",
        "title": "LLM Workflow Orchestration & Evaluation Harness",
        "desc": "A multi-agent orchestration system with a built-in evaluation harness — unit tests for prompts, rubric-based scoring, and golden dataset benchmarking. Includes full observability: prompt logging, latency tracking, and failure mode capture for responsible iteration before production handoff.",
        "tags": ["LangGraph", "Multi-Agent", "Eval Harness", "Observability", "FastAPI", "PostgreSQL"],
        "page": "Eval_Harness",
    },
    {
        "emoji": "🔍",
        "title": "AI Document Retrieval & Validation System",
        "desc": "Semantic document retrieval that maps user queries to source-of-truth documents using NLP similarity scoring. Features real-time confidence scoring, mismatch flagging, and explicit uncertainty signaling — built for high-stakes information workflows where accuracy matters.",
        "tags": ["Semantic Search", "FAISS", "NLP", "FastAPI", "Responsible AI", "REST API"],
        "page": "Document_Retrieval",
    },
]

for p in projects:
    st.markdown(f"""
    <div class="project-card">
      <h3>{p['emoji']} {p['title']}</h3>
      <p>{p['desc']}</p>
      {''.join(f'<span class="tag">{t}</span>' for t in p['tags'])}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Contact ──────────────────────────────────────────────────────────────────
st.markdown("### 📬 Get in Touch")
st.markdown("""
<a class="contact-link" href="mailto:jalenjbennett@gmail.com">✉️ jalenjbennett@gmail.com</a>
<a class="contact-link" href="https://github.com/jbennett03" target="_blank">🐙 GitHub</a>
<a class="contact-link" href="https://www.linkedin.com/in/jalen-bennett-7721aa250/" target="_blank">💼 LinkedIn</a>
""", unsafe_allow_html=True)
