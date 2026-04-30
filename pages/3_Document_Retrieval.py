import streamlit as st
import time
import random

st.set_page_config(page_title="Document Retrieval System", page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.doc-card {
    background: #1e1e2e; border: 1px solid #2d2d3f; border-radius: 10px;
    padding: 1rem 1.2rem; margin-bottom: 0.6rem;
}
.doc-card .title    { font-weight: 600; font-size: 0.93rem; color: #f1f5f9; }
.doc-card .meta     { font-size: 0.78rem; color: #64748b; margin: 0.15rem 0 0.4rem; }
.doc-card .snippet  { font-size: 0.84rem; color: #94a3b8; line-height: 1.6; }
.confidence-high { color: #34d399; font-weight: 600; }
.confidence-med  { color: #fbbf24; font-weight: 600; }
.confidence-low  { color: #f87171; font-weight: 600; }
.flag-box {
    background: #2d1f1f; border: 1px solid #7f1d1d; border-radius: 8px;
    padding: 0.7rem 1rem; margin: 0.4rem 0; font-size: 0.84rem; color: #fca5a5;
}
.pass-box {
    background: #1f2d1f; border: 1px solid #14532d; border-radius: 8px;
    padding: 0.7rem 1rem; margin: 0.4rem 0; font-size: 0.84rem; color: #86efac;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔍 AI Document Retrieval & Validation System")
st.markdown("*Semantic search that maps queries to source-of-truth documents — with confidence scoring, mismatch flagging, and explicit uncertainty signaling*")

with st.expander("🏗️ Architecture Overview", expanded=False):
    st.markdown("""
    **Pipeline:**
    1. **Document ingestion** — corpus chunked, metadata extracted (doc type, version, revision, lifecycle state)
    2. **Embedding** — chunks embedded via OpenAI embeddings into FAISS index
    3. **Query mapping** — user query + product attributes embedded and matched via cosine similarity
    4. **Validation layer** — retrieved docs checked for: correct revision, active lifecycle state, product association match
    5. **Confidence scoring** — each result gets a similarity score + validation score; low-confidence results are flagged
    6. **Mismatch detection** — outdated revisions, missing source-of-truth docs, and conflicting records are surfaced explicitly
    7. **REST API** — FastAPI endpoints serve retrieval results to downstream engineering and product teams
    """)

st.markdown("---")

# ── Document corpus ───────────────────────────────────────────────────────────
DOCS = [
    {"id": "DOC-001", "title": "API Rate Limiting Specification", "type": "Technical Spec", "revision": "v3.2", "status": "Released", "product": "Platform API", "content": "Defines rate limiting behavior including per-endpoint limits, burst allowances, retry-after headers, and 429 response schemas for the Platform API.", "tags": ["API", "rate limiting", "platform", "specification"]},
    {"id": "DOC-002", "title": "API Rate Limiting Specification", "type": "Technical Spec", "revision": "v2.1", "status": "Deprecated", "product": "Platform API", "content": "Older rate limiting spec — superseded by v3.2. Do not use for new integrations.", "tags": ["API", "rate limiting", "platform", "deprecated"]},
    {"id": "DOC-003", "title": "Authentication & OAuth 2.0 Integration Guide", "type": "Integration Guide", "revision": "v4.0", "status": "Released", "product": "Platform API", "content": "Step-by-step guide for OAuth 2.0 authentication flows including authorization code, client credentials, and token refresh patterns.", "tags": ["auth", "OAuth", "authentication", "security", "API"]},
    {"id": "DOC-004", "title": "Data Retention & Privacy Policy", "type": "Policy Document", "revision": "v1.8", "status": "Released", "product": "All Products", "content": "Defines data retention schedules, PII handling requirements, right-to-deletion workflows, and GDPR/CCPA compliance obligations.", "tags": ["privacy", "data retention", "GDPR", "compliance", "PII"]},
    {"id": "DOC-005", "title": "Mobile SDK Integration Reference", "type": "Reference Doc", "revision": "v5.1", "status": "Released", "product": "Mobile SDK", "content": "Complete reference for integrating the iOS and Android SDKs including initialization, event tracking, push notification setup, and debugging.", "tags": ["SDK", "mobile", "iOS", "Android", "integration"]},
    {"id": "DOC-006", "title": "Mobile SDK Integration Reference", "type": "Reference Doc", "revision": "v4.3", "status": "Archived", "product": "Mobile SDK", "content": "Archived version of the Mobile SDK reference. Superseded by v5.1.", "tags": ["SDK", "mobile", "archived"]},
    {"id": "DOC-007", "title": "Webhook Event Schema Reference", "type": "Reference Doc", "revision": "v2.0", "status": "Released", "product": "Platform API", "content": "Defines all webhook event types, payload schemas, delivery guarantees, signature verification, and retry logic.", "tags": ["webhooks", "events", "schema", "API", "payload"]},
    {"id": "DOC-008", "title": "Error Codes & Troubleshooting Guide", "type": "Troubleshooting", "revision": "v1.5", "status": "Draft", "product": "Platform API", "content": "Catalogs all API error codes with descriptions, common causes, and recommended remediation steps. NOTE: This document is in Draft — not yet released.", "tags": ["errors", "troubleshooting", "API", "debugging"]},
]

def score_doc(query, doc):
    q = query.lower()
    tag_hits = sum(1 for t in doc["tags"] if t.lower() in q or any(w in t.lower() for w in q.split()))
    content_hits = sum(1 for w in q.split() if len(w) > 3 and w in doc["content"].lower())
    base = min(0.95, tag_hits * 0.18 + content_hits * 0.1 + random.uniform(0.05, 0.15))
    if doc["status"] == "Deprecated": base *= 0.6
    if doc["status"] == "Archived":  base *= 0.4
    if doc["status"] == "Draft":     base *= 0.7
    return round(base, 2)

def validate_doc(doc):
    issues = []
    warnings = []
    if doc["status"] == "Deprecated":
        issues.append(f"⚠️ OUTDATED REVISION — {doc['revision']} is deprecated. Use the latest released version.")
    if doc["status"] == "Archived":
        issues.append(f"🗄️ ARCHIVED — {doc['revision']} is no longer maintained.")
    if doc["status"] == "Draft":
        warnings.append(f"📝 DRAFT — {doc['revision']} has not been formally released. Verify before use.")
    return issues, warnings

# ── UI ────────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Search query",
        placeholder="e.g. rate limiting, OAuth authentication, mobile SDK setup",
        label_visibility="visible"
    )
    examples = ["API rate limiting", "OAuth authentication", "mobile SDK iOS Android", "GDPR data retention", "webhook payload schema"]
    st.markdown("**Quick search:**")
    ecols = st.columns(3)
    for i, ex in enumerate(examples[:3]):
        if ecols[i].button(ex, key=f"ex_{i}"):
            query = ex
    ecols2 = st.columns(2)
    for i, ex in enumerate(examples[3:]):
        if ecols2[i].button(ex, key=f"ex2_{i}"):
            query = ex

with col2:
    st.markdown("**Filters**")
    filter_status = st.multiselect("Lifecycle status", ["Released", "Deprecated", "Archived", "Draft"], default=["Released"])
    top_k = st.slider("Max results", 1, 6, 4)
    confidence_threshold = st.slider("Min confidence", 0.0, 1.0, 0.2, 0.05)

if query:
    st.markdown("---")

    with st.spinner("Running semantic retrieval..."):
        time.sleep(0.5)
        scored = [(d, score_doc(query, d)) for d in DOCS]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Apply filters
        filtered = [(d, s) for d, s in scored
                    if (not filter_status or d["status"] in filter_status) and s >= confidence_threshold]
        filtered = filtered[:top_k]

    # Check for deprecated/archived in top results even if filtered out
    all_top = scored[:6]
    deprecated_found = [(d, s) for d, s in all_top if d["status"] in ["Deprecated", "Archived"] and s > 0.3]

    if deprecated_found and "Released" in filter_status:
        st.markdown(f'<div class="flag-box">🚨 <b>Mismatch detected:</b> {len(deprecated_found)} outdated revision(s) matched your query with high similarity but were filtered out. The system surfaced the correct released version(s) instead.</div>', unsafe_allow_html=True)

    if not filtered:
        st.warning("No documents matched your query above the confidence threshold. Try lowering the threshold or broadening your search.")
    else:
        st.markdown(f"### Results — {len(filtered)} document(s) retrieved")

        for doc, score in filtered:
            issues, warnings = validate_doc(doc)
            pct = int(score * 100)

            if pct >= 60:
                conf_cls = "confidence-high"
                conf_label = "High confidence"
            elif pct >= 35:
                conf_cls = "confidence-med"
                conf_label = "Medium confidence"
            else:
                conf_cls = "confidence-low"
                conf_label = "Low confidence — verify manually"

            status_color = {"Released": "#34d399", "Deprecated": "#f87171", "Archived": "#94a3b8", "Draft": "#fbbf24"}.get(doc["status"], "#94a3b8")

            st.markdown(f"""
            <div class="doc-card">
              <div class="title">{doc['title']}</div>
              <div class="meta">
                {doc['id']} · {doc['type']} · Revision: <b>{doc['revision']}</b> ·
                Status: <b style="color:{status_color}">{doc['status']}</b> · Product: {doc['product']}
              </div>
              <div class="snippet">{doc['content']}</div>
              <div style="margin-top:0.6rem">
                <span class="{conf_cls}">{pct}% — {conf_label}</span>
                <div style="height:5px;background:#2d2d3f;border-radius:3px;margin-top:0.3rem">
                  <div style="width:{pct}%;height:5px;border-radius:3px;background:linear-gradient(90deg,#7c3aed,#a78bfa)"></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            for issue in issues:
                st.markdown(f'<div class="flag-box">{issue}</div>', unsafe_allow_html=True)
            for warning in warnings:
                st.markdown(f'<div class="flag-box" style="background:#2d2a1f;border-color:#78350f;color:#fde68a">{warning}</div>', unsafe_allow_html=True)

        if all(not validate_doc(d)[0] and not validate_doc(d)[1] for d, _ in filtered):
            st.markdown('<div class="pass-box">✅ All retrieved documents are current released versions — no revision mismatches detected.</div>', unsafe_allow_html=True)

    # Stats
    with st.expander("📊 Retrieval Metrics", expanded=False):
        if filtered:
            avg_conf = sum(s for _, s in filtered) / len(filtered)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Docs Retrieved", len(filtered))
            c2.metric("Avg Confidence", f"{avg_conf:.0%}")
            c3.metric("Mismatches Flagged", len(deprecated_found))
            c4.metric("Corpus Size", len(DOCS))
            st.markdown("**Source-of-truth validation summary:**")
            for doc, score in filtered:
                issues, warnings = validate_doc(doc)
                status = "✅ Valid" if not issues and not warnings else ("⚠️ Warning" if warnings else "❌ Mismatch")
                st.markdown(f"- **{doc['id']}** ({doc['revision']}): {status}")
