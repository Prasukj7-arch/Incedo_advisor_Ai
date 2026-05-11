# pyrefly: ignore [missing-import]
import streamlit as st
import requests
import json
import os
from feature4_compliance import run_compliance_check

# ── CONFIG ─────────────────────────────────────────────────────────────────────
API_BASE = "https://6jg65j6ajh.execute-api.us-east-1.amazonaws.com/prod"
API_KEY = os.environ.get("ADVISOR_AI_KEY", "")
EC2_IP = os.environ.get("EC2_RAG_IP", "54.81.100.34")
RAG_URL = f"http://{EC2_IP}:8000/research"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Advisor AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1F3864;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #1F3864;
    }
    .alert-high {
        background: #fff0f0;
        border-left: 4px solid #dc3545;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .alert-medium {
        background: #fff8e1;
        border-left: 4px solid #ffc107;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .alert-low {
        background: #f0fff4;
        border-left: 4px solid #28a745;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .clean-badge {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .alert-badge {
        background: #ffebee;
        color: #c62828;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .chat-message {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #e3f2fd;
        border-left: 3px solid #1976d2;
    }
    .ai-message {
        background: #f5f5f5;
        border-left: 3px solid #1F3864;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💼 Advisor AI")
    st.markdown("*Intelligent Financial Concierge*")
    st.divider()

    feature = st.radio(
        "Select Feature",
        [
            "📊 Portfolio Chat",
            "🔍 Research Search",
            "👤 Client 360",
            "⚠️ Compliance Monitor"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**AWS Services Active:**")
    st.markdown("🟢 Lambda + API Gateway")
    st.markdown("🟢 DynamoDB (Memory)")
    st.markdown("🟢 Bedrock Llama 3.1")
    st.markdown("🟢 EC2 + ChromaDB (RAG)")
    st.markdown("🟢 CloudWatch (Audit)")
    st.divider()
    st.markdown("*Built on AWS | May 2026*")

# ── Main header ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">💼 Advisor AI — Intelligent Concierge</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered financial advisor assistant | Powered by AWS Bedrock + Llama 3.1</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 1: Portfolio Chat
# ══════════════════════════════════════════════════════════════════════════════
if feature == "📊 Portfolio Chat":
    st.subheader("📊 Portfolio Chat")
    st.markdown("Ask anything about your client portfolios in natural language.")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = "streamlit-session-001"

    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📈 Summarize my book today"):
            st.session_state.quick_query = "Summarize my entire book performance today"
    with col2:
        if st.button("⚠️ Top risks in my book"):
            st.session_state.quick_query = "What are the top risks across all my client portfolios?"
    with col3:
        if st.button("🔄 Rebalancing needed?"):
            st.session_state.quick_query = "Which client portfolios need rebalancing?"

    # Chat display
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">🧑💼 <strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-message">🤖 <strong>Advisor AI:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

    # Input
    user_input = st.chat_input("Ask about portfolios... e.g. 'What are Rahul's top risks?'")

    # Handle quick query buttons
    if "quick_query" in st.session_state and st.session_state.quick_query:
        user_input = st.session_state.quick_query
        st.session_state.quick_query = None

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Analyzing portfolios..."):
            try:
                response = requests.post(
                    f"{API_BASE}/chat",
                    headers=HEADERS,
                    json={"question": user_input, "session_id": st.session_state.session_id},
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

        st.rerun()

    if st.button("🗑️ Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 2: Research Search
# ══════════════════════════════════════════════════════════════════════════════
elif feature == "🔍 Research Search":
    st.subheader("🔍 Research Search (RAG)")
    st.markdown("Search across 5 financial research reports using natural language.")

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Available Reports:**")
        st.markdown("📄 Goldman Sachs — Semiconductors")
        st.markdown("📄 Morgan Stanley — Indian Banking")
        st.markdown("📄 JP Morgan — IT Sector")
        st.markdown("📄 UBS — FMCG India")
        st.markdown("📄 Deutsche Bank — India Macro")

    with col1:
        # Quick search buttons
        st.markdown("**Quick searches:**")
        qcol1, qcol2 = st.columns(2)
        with qcol1:
            if st.button("💻 Semiconductor picks"):
                st.session_state.rag_query = "What are the top picks in semiconductor sector?"
                st.rerun()
            if st.button("🏦 Banking outlook"):
                st.session_state.rag_query = "What is the outlook for Indian banking sector?"
                st.rerun()
        with qcol2:
            if st.button("💻 IT sector outlook"):
                st.session_state.rag_query = "What is the outlook for Indian IT sector?"
                st.rerun()
            if st.button("🇮🇳 India GDP forecast"):
                st.session_state.rag_query = "What is India GDP growth forecast?"
                st.rerun()

        query = st.text_input(
            "Search research reports...",
            value=st.session_state.get("rag_query", ""),
            placeholder="e.g. What are NVIDIA's growth prospects?"
        )

        if st.button("🔍 Search", type="primary") and query:
            with st.spinner("Searching research documents..."):
                try:
                    response = requests.post(
                        RAG_URL,
                        json={"question": query, "session_id": "rag-session"},
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Answer found!")
                        st.markdown("**Answer:**")
                        st.markdown(data["answer"])
                        st.markdown("**Sources:**")
                        for source in data["sources"]:
                            st.markdown(f"📄 `{source}`")
                    else:
                        st.error(f"RAG server error: {response.status_code}")
                except Exception as e:
                    st.error(f"Cannot connect to RAG server: {e}")
                    st.info(f"Make sure EC2 is running at {EC2_IP}:8000")

        if "rag_query" in st.session_state:
            st.session_state.rag_query = ""

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 3: Client 360
# ══════════════════════════════════════════════════════════════════════════════
elif feature == "👤 Client 360":
    st.subheader("👤 Client 360 — Meeting Prep")
    st.markdown("Generate a complete meeting preparation brief for any client instantly.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👩 Priya Sharma\n3pm today", use_container_width=True):
            st.session_state.selected_client = "Priya"
    with col2:
        if st.button("👨 Rahul Mehta\n11am today", use_container_width=True):
            st.session_state.selected_client = "Rahul"
    with col3:
        if st.button("👩🦳 Anita Desai\n10am tomorrow", use_container_width=True):
            st.session_state.selected_client = "Anita"

    client_name = st.text_input(
        "Or type client name:",
        value=st.session_state.get("selected_client", ""),
        placeholder="e.g. Rahul"
    )

    if st.button("📋 Generate Meeting Brief", type="primary") and client_name:
        with st.spinner(f"Preparing brief for {client_name}..."):
            try:
                response = requests.post(
                    f"{API_BASE}/client360",
                    headers=HEADERS,
                    json={"client_name": client_name},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()

                    # Header metrics
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Client", data["client_name"])
                    m2.metric("AUM", f"${data['aum']:,}")
                    m3.metric("Risk Profile", data["risk_profile"])
                    m4.metric("Meeting", data["meeting_time"])

                    # Compliance flags
                    if data["compliance_flags"]:
                        for flag in data["compliance_flags"]:
                            st.markdown(f'<div class="alert-high">⚠️ <strong>COMPLIANCE ALERT:</strong> {flag}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-low">✅ No compliance flags</div>', unsafe_allow_html=True)

                    # Brief
                    st.divider()
                    st.markdown("### Meeting Brief")
                    st.markdown(data["brief"])

                elif response.status_code == 404:
                    st.error(f"Client '{client_name}' not found. Try: Priya, Rahul, or Anita")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

        if "selected_client" in st.session_state:
            st.session_state.selected_client = ""

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 4: Compliance Monitor
# ══════════════════════════════════════════════════════════════════════════════
elif feature == "⚠️ Compliance Monitor":
    st.subheader("⚠️ Compliance Monitor")
    st.markdown("Real-time compliance checks across all client portfolios with CloudWatch audit logging.")

    col1, col2 = st.columns([1, 1])
    with col1:
        check_all = st.button("🔍 Run Full Book Compliance Check", type="primary", use_container_width=True)
    with col2:
        specific_client = st.text_input("Or check specific client:", placeholder="e.g. Rahul")
        check_specific = st.button("Check Client", use_container_width=True)

    if check_all or (check_specific and specific_client):
        client_filter = specific_client if (check_specific and specific_client) else None

        with st.spinner("Running compliance checks..."):
            result = run_compliance_check(client_filter)

        # Summary metrics
        summary = result["summary"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Clients Checked", summary["total_clients_checked"])
        m2.metric("Total Violations", summary["total_violations"])
        m3.metric("High Severity", summary["high_severity_count"],
                  delta=f"{summary['high_severity_count']} alerts" if summary["high_severity_count"] > 0 else None,
                  delta_color="inverse")
        m4.metric("Checked At", summary["checked_at"][:16].replace("T", " "))

        st.divider()

        # Per client results
        for client_result in result["results"]:
            status = client_result["status"]
            badge = f'<span class="alert-badge">🔴 {status}</span>' if status == "ALERT" else \
                    f'<span class="alert-badge" style="background:#fff8e1;color:#856404;">🟡 {status}</span>' if status == "WARNING" else \
                    f'<span class="clean-badge">🟢 {status}</span>'

            with st.expander(
                f"{client_result['client_name']} — {client_result['risk_profile']} — AUM: ${client_result['aum']:,} — {status}",
                expanded=status in ["ALERT", "WARNING"]
            ):
                st.markdown(f"**Status:** {badge}", unsafe_allow_html=True)

                if client_result["violations"]:
                    st.markdown(f"**{client_result['violation_count']} violation(s) found:**")
                    for v in client_result["violations"]:
                        severity_class = "alert-high" if v["severity"] == "HIGH" else \
                                         "alert-medium" if v["severity"] == "MEDIUM" else "alert-low"
                        severity_icon = "🔴" if v["severity"] == "HIGH" else \
                                        "🟡" if v["severity"] == "MEDIUM" else "🟢"
                        st.markdown(f"""
<div class="{severity_class}">
    {severity_icon} <strong>[{v['severity']}] {v['rule_name']}</strong><br>
    <em>{v['description']}</em><br>
    <strong>Action:</strong> {v['action']}
</div>
""", unsafe_allow_html=True)
                else:
                    st.markdown("✅ No compliance violations found.")

                if client_result["violations"]:
                    st.markdown("*Violations logged to AWS CloudWatch for audit trail.*")
