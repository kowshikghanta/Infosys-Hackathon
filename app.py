"""MeetingMind AI - Streamlit Dashboard
"Turn meeting conversations into accountable action."
Infosys Hack-AI-Thon MVP
"""

import io
import json
import logging
from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st

from src.schemas import MeetingAnalysis, ActionItem
from src.sample_data import get_sample_meeting_text, get_sample_analysis
from src.providers.qualcomm import QualcommAIProvider
from src.providers.base import (
    AIProviderError,
    AuthenticationError,
    QuotaExceededError,
    ProviderTimeoutError,
    ProviderConnectionError,
    MalformedResponseError,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Page Configuration ---
st.set_page_config(
    page_title="MeetingMind AI — Action Extractor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown(
    """
    <style>
    /* Global Typography & Spacing */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
        font-weight: 400;
    }
    .badge-live {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-sample {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fcd34d;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-unconfigured {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .warning-card {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .warning-danger-card {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .evidence-quote {
        font-style: italic;
        color: #64748b;
        background: #f8fafc;
        border-left: 3px solid #cbd5e1;
        padding: 6px 10px;
        margin-top: 6px;
        font-size: 0.88rem;
    }
    .clarification-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 6px;
        padding: 8px 12px;
        margin-top: 8px;
        color: #1e40af;
        font-size: 0.9rem;
    }
    .decision-confirmed {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .decision-tentative {
        background-color: #fff7ed;
        border-left: 4px solid #f97316;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State Initialization ---
if "current_analysis" not in st.session_state:
    st.session_state["current_analysis"] = None
if "meeting_notes_text" not in st.session_state:
    st.session_state["meeting_notes_text"] = ""
if "meeting_title_input" not in st.session_state:
    st.session_state["meeting_title_input"] = ""
if "meeting_date_input" not in st.session_state:
    st.session_state["meeting_date_input"] = date.today().isoformat()
if "task_status_overrides" not in st.session_state:
    st.session_state["task_status_overrides"] = {}

# Instantiate Provider
provider = QualcommAIProvider()
is_configured, config_message = provider.is_configured()

# --- Sidebar: Provider Architecture & Diagnostic Controls ---
with st.sidebar:
    st.title("⚙️ AI Architecture")
    st.markdown("**Provider:** Qualcomm AI Playground")

    # Connection Status
    if is_configured:
        st.markdown(
            '<div class="badge-live">● Live AI: Configured</div>',
            unsafe_allow_html=True,
        )
        model_choices = ["DeepSeek-R1-Distill-Llama-70B", "Llama-3.1-8B", "Llama-3.3-70B", "Qwen-QwQ-32B"]
        curr_idx = model_choices.index(provider.model_name) if provider.model_name in model_choices else 0
        selected_model = st.selectbox(
            "Selected Model",
            options=model_choices,
            index=curr_idx,
            key="sidebar_model_select"
        )
        provider.model_name = selected_model
        st.caption(f"**Endpoint:** `{provider.endpoint_url}`")
    else:
        st.markdown(
            '<div class="badge-unconfigured">○ Live AI: Not Configured</div>',
            unsafe_allow_html=True,
        )
        st.caption("No `QUALCOMM_API_KEY` detected in environment.")

    st.divider()

    # Diagnostic Test Button (Lightweight, single test request)
    st.subheader("🔍 Endpoint Diagnostic")
    if st.button("Test Connection Ping", use_container_width=True):
        with st.spinner("Connecting to Qualcomm AI Playground..."):
            ok, diag_msg = provider.test_connection()
            if ok:
                st.success(diag_msg)
            else:
                st.error(diag_msg)

    st.divider()

    # Setup Instructions
    with st.expander("📖 Configuration Guide", expanded=not is_configured):
        st.markdown(
            """
            To activate **Live AI Mode**:
            1. Create `.env` in the project root
            2. Paste your Cirrascale credentials:
            ```bash
            INFERENCE_CLOUD_API_KEY=00d216...
            INFERENCE_CLOUD_ENDPOINT=https://aisuite.cirrascale.com/apis/v2
            QUALCOMM_MODEL_NAME=llama-3.1-8B
            ```
            3. Click **Test Connection Ping** above.

            *Budget Guard*: Exactly 1 extraction request per analysis to protect your $3 credit budget.
            """
        )

    st.divider()
    st.caption("MeetingMind AI v1.0 • Infosys Hack-AI-Thon")


# --- Main Header ---
st.markdown('<div class="main-title">MeetingMind AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Turn meeting conversations into accountable action.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    **Objective:** Unstructured notes contain hidden decisions, deadlines, tasks, and unassigned commitments. 
    MeetingMind AI applies deep extraction paired with a **deterministic validation layer** to guarantee no responsibility slips through the cracks.
    """
)

st.divider()


# --- Meeting Input Section ---
st.subheader("1. Meeting Details & Transcript")

col_meta1, col_meta2 = st.columns([2, 1])
with col_meta1:
    meeting_title_val = st.text_input(
        "Meeting Title (Optional)",
        value=st.session_state["meeting_title_input"],
        placeholder="e.g. Dashboard Release Sync",
        key="title_input",
    )
with col_meta2:
    meeting_date_val = st.text_input(
        "Meeting Date (Optional)",
        value=st.session_state["meeting_date_input"],
        key="date_input",
    )

meeting_text = st.text_area(
    "Meeting Notes / Transcript",
    value=st.session_state["meeting_notes_text"],
    height=160,
    placeholder="Paste raw meeting notes, transcript excerpts, or bullet points here...",
    key="notes_area",
)

# Button Toolbar
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 4])

with col_btn1:
    analyze_clicked = st.button("🚀 Analyze Meeting", type="primary", use_container_width=True)

with col_btn2:
    load_sample_clicked = st.button("📋 Load Realistic Sample Notes", use_container_width=True)

with col_btn3:
    if st.button("🔄 Reset / Clear", use_container_width=False):
        st.session_state["meeting_notes_text"] = ""
        st.session_state["meeting_title_input"] = ""
        st.session_state["current_analysis"] = None
        st.session_state["task_status_overrides"] = {}
        st.rerun()

# Handle Loading Sample Notes
if load_sample_clicked:
    sample_notes = get_sample_meeting_text()
    st.session_state["meeting_notes_text"] = sample_notes
    st.session_state["meeting_title_input"] = "Dashboard Release Sync"
    st.session_state["meeting_date_input"] = "2026-10-11"
    # Load sample analysis deterministically
    st.session_state["current_analysis"] = get_sample_analysis()
    st.session_state["task_status_overrides"] = {}
    st.rerun()

# Handle Analyze Action
if analyze_clicked:
    if not meeting_text.strip():
        st.warning("⚠️ Please paste meeting notes or click 'Load Realistic Sample Notes' first.")
    else:
        st.session_state["meeting_notes_text"] = meeting_text
        st.session_state["meeting_title_input"] = meeting_title_val
        st.session_state["meeting_date_input"] = meeting_date_val
        st.session_state["task_status_overrides"] = {}

        if is_configured:
            # Live AI Mode
            with st.spinner(f"⚡ Analyzing via Qualcomm AI Playground ({provider.model_name})..."):
                try:
                    analysis_result = provider.extract_meeting_action_items(
                        transcript=meeting_text,
                        meeting_title=meeting_title_val,
                        meeting_date=meeting_date_val,
                    )
                    st.session_state["current_analysis"] = analysis_result
                    st.success("Analysis extracted and verified successfully via Qualcomm AI!")
                except AuthenticationError as err:
                    st.error(f"🔐 Authentication Error: {err.message}")
                    st.info("💡 You can explore the application using **Load Realistic Sample Notes**.")
                except QuotaExceededError as err:
                    st.error(f"⏳ Quota / Rate Limit Exceeded: {err.message}")
                    st.info("💡 You can explore the full dashboard using **Load Realistic Sample Notes**.")
                except ProviderTimeoutError as err:
                    st.error(f"⏱️ Timeout: {err.message}")
                except ProviderConnectionError as err:
                    st.error(f"🌐 Connection Failure: {err.message}")
                except MalformedResponseError as err:
                    st.error(f"⚠️ Response Validation Error: {err.message}")
                except AIProviderError as err:
                    st.error(f"❌ AI Extraction Failed: {err.message}")
        else:
            # Provider not configured -> guide user and explain
            st.error(
                "❌ **Live AI is not configured**: Missing `QUALCOMM_API_KEY` in environment. "
                "Per hackathon requirements, live requests cannot proceed without verified credentials."
            )
            col_err1, col_err2 = st.columns([1, 1])
            with col_err1:
                st.info("👉 Click **'Load Realistic Sample Notes'** to test the complete dashboard deterministically.")
            with col_err2:
                if st.button("Load Pre-computed Sample Verification Now", type="secondary"):
                    st.session_state["current_analysis"] = get_sample_analysis()
                    st.rerun()


# --- Results Section ---
analysis: Optional[MeetingAnalysis] = st.session_state.get("current_analysis")

if analysis:
    st.divider()

    # Mode Indicator Banner
    if analysis.is_sample_data:
        st.markdown(
            '<div class="badge-sample">🟡 Sample Data — Not Live AI Output (Deterministic Verification)</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="badge-live">🟢 Live AI Inference Result — Qualcomm AI Playground ({provider.model_name})</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### 2. Executive Extraction Results")

    # High-level Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    total_tasks = len(analysis.action_items)
    missing_owners = sum(1 for item in analysis.action_items if not item.owner)
    tentative_tasks = sum(1 for item in analysis.action_items if item.is_tentative)
    unresolved_decisions = sum(1 for d in analysis.decisions if d.status == "tentative")
    total_warnings = len(analysis.accountability_warnings)

    with m_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Extracted Tasks</div>
                <div class="metric-value">{total_tasks}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Unassigned Tasks</div>
                <div class="metric-value" style="color: {'#ef4444' if missing_owners > 0 else '#1e293b'};">{missing_owners}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Tentative Commitments</div>
                <div class="metric-value" style="color: {'#f59e0b' if tentative_tasks > 0 else '#1e293b'};">{tentative_tasks}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Accountability Alerts</div>
                <div class="metric-value" style="color: {'#ef4444' if total_warnings > 0 else '#166534'};">{total_warnings}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --- Structured Tabs ---
    tab_tasks, tab_accountability, tab_decisions, tab_summary, tab_export = st.tabs([
        "📋 Action Items Dashboard",
        "⚠️ Accountability & Gaps (Core)",
        "⚖️ Decisions & Risks",
        "📄 Executive Summary",
        "💾 Export & JSON Data",
    ])

    # === TAB 1: Action Items Dashboard ===
    with tab_tasks:
        st.markdown("#### Action Items Dashboard")
        st.caption("Review, filter, and update task progress. Task status updates are session-bound.")

        # Filters
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])

        with filter_col1:
            search_query = st.text_input("🔍 Search task description", placeholder="Filter by keyword...", key="task_search")

        # Distinct filter options
        all_owners = sorted(list({item.owner or "Unassigned" for item in analysis.action_items}))
        with filter_col2:
            owner_filter = st.selectbox("Owner", ["All"] + all_owners, key="owner_filter")

        with filter_col3:
            priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low", "Unknown"], key="priority_filter")

        with filter_col4:
            status_filter = st.selectbox(
                "Status",
                ["All", "Not started", "In progress", "Completed", "Needs clarification"],
                key="status_filter",
            )

        # Apply Filters & Session Overrides
        filtered_items = []
        for item in analysis.action_items:
            # Apply session status override if user edited it
            effective_status = st.session_state["task_status_overrides"].get(item.id, item.status)

            # Text search filter
            if search_query and search_query.lower() not in item.task.lower():
                continue

            # Owner filter
            item_owner_display = item.owner or "Unassigned"
            if owner_filter != "All" and item_owner_display != owner_filter:
                continue

            # Priority filter
            if priority_filter != "All" and item.priority.lower() != priority_filter.lower():
                continue

            # Status filter
            formatted_status = effective_status.replace("_", " ").capitalize()
            if status_filter != "All" and formatted_status != status_filter:
                continue

            filtered_items.append((item, effective_status))

        if not filtered_items:
            st.info("No action items match the selected filter criteria.")
        else:
            # Table-style expandable view with interactive status editing
            for item, current_status in filtered_items:
                priority_color = {
                    "high": "🔴 High",
                    "medium": "🟡 Medium",
                    "low": "🔵 Low",
                    "unknown": "⚪ Unknown",
                }.get(item.priority, item.priority)

                status_label = {
                    "not_started": "Not started",
                    "in_progress": "In progress",
                    "completed": "Completed",
                    "needs_clarification": "Needs clarification",
                }.get(current_status, current_status)

                owner_display = item.owner if item.owner else "⚠️ Unassigned"
                deadline_display = item.deadline_text if item.deadline_text else "⚠️ Not stated"

                with st.expander(f"**{item.id}: {item.task}** | Owner: `{owner_display}` | Due: `{deadline_display}` | {priority_color}", expanded=True):
                    col_det1, col_det2, col_det3 = st.columns([2, 1, 1])

                    with col_det1:
                        st.markdown(f"**Description:** {item.task}")
                        if item.evidence:
                            st.markdown(f'<div class="evidence-quote">“{item.evidence}”</div>', unsafe_allow_html=True)

                    with col_det2:
                        st.markdown(f"**Owner:** `{owner_display}`")
                        st.markdown(f"**Deadline:** `{deadline_display}`")
                        st.markdown(f"**Priority:** {priority_color}")

                    with col_det3:
                        # Interactive Status Selectbox
                        status_options = ["not_started", "in_progress", "completed", "needs_clarification"]
                        status_display_map = {
                            "not_started": "Not started",
                            "in_progress": "In progress",
                            "completed": "Completed",
                            "needs_clarification": "Needs clarification",
                        }
                        current_idx = status_options.index(current_status) if current_status in status_options else 0

                        new_status = st.selectbox(
                            "Update Status",
                            options=status_options,
                            index=current_idx,
                            format_func=lambda s: status_display_map[s],
                            key=f"status_select_{item.id}",
                        )
                        if new_status != current_status:
                            st.session_state["task_status_overrides"][item.id] = new_status
                            st.rerun()

                        # Confidence signal
                        st.caption(f"Confidence Signal: **{item.confidence:.0%}** *(Indicative LLM signal)*")

                    # If missing information is flagged
                    if item.missing_information:
                        missing_tags = ", ".join(item.missing_information)
                        st.warning(f"⚠️ Flagged missing elements: **{missing_tags}**")

                    if item.suggested_clarification:
                        st.markdown(
                            f'<div class="clarification-box">💡 <b>Clarification question:</b> {item.suggested_clarification}</div>',
                            unsafe_allow_html=True,
                        )

    # === TAB 2: Accountability & Missing-Information Analysis ===
    with tab_accountability:
        st.markdown("#### 🛡️ Accountability & Missing-Information Analysis")
        st.markdown(
            """
            *Core Differentiator:* MeetingMind AI strictly forbids inventing people, deadlines, or false clarity.
            The deterministic validation engine isolates unassigned responsibilities, vague dates, unconfirmed assignments, 
            and undecided technical forks to generate targeted follow-ups.
            """
        )

        if not analysis.accountability_warnings:
            st.success("✅ No accountability gaps, unassigned tasks, or ambiguous commitments were detected.")
        else:
            # Group warnings by category
            category_titles = {
                "missing_owner": "👤 Tasks Missing Designated Owners",
                "missing_deadline": "📅 Tasks Missing Explicit Deadlines",
                "tentative_assignment": "❓ Tentative or Unconfirmed Commitments",
                "vague_commitment": "⏳ Vague Timelines or Commitments ('soon', 'asap')",
                "unresolved_decision": "⚖️ Unresolved Technical / Architecture Decisions",
                "conflicting_information": "⚔️ Conflicting or Duplicate Deliverables",
            }

            warnings_by_cat = {}
            for w in analysis.accountability_warnings:
                warnings_by_cat.setdefault(w.category, []).append(w)

            for cat, warn_list in warnings_by_cat.items():
                cat_header = category_titles.get(cat, cat.replace("_", " ").title())
                st.markdown(f"##### {cat_header} ({len(warn_list)})")

                for w in warn_list:
                    card_class = "warning-danger-card" if cat in ("missing_owner", "tentative_assignment") else "warning-card"
                    task_badge = f"`{w.task_id}` " if w.task_id else ""

                    st.markdown(
                        f"""
                        <div class="{card_class}">
                            <strong>{task_badge}{w.subject}</strong><br/>
                            <p style="margin: 6px 0 4px 0; color: #334155;">{w.reason}</p>
                            {f'<div class="evidence-quote">“{w.evidence}”</div>' if w.evidence else ''}
                            <div class="clarification-box">💡 <b>Recommended Clarification Question:</b> {w.suggested_clarification}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # === TAB 3: Decisions & Risks ===
    with tab_decisions:
        dec_col, risk_col = st.columns(2)

        with dec_col:
            st.markdown("#### ⚖️ Confirmed & Tentative Decisions")
            if not analysis.decisions:
                st.info("No explicit decisions identified in the notes.")
            else:
                for d in analysis.decisions:
                    is_confirmed = d.status == "confirmed"
                    card_style = "decision-confirmed" if is_confirmed else "decision-tentative"
                    status_badge = "✅ Confirmed Decision" if is_confirmed else "⚠️ Tentative Proposal / Undecided"

                    st.markdown(
                        f"""
                        <div class="{card_style}">
                            <strong>{status_badge}</strong><br/>
                            <p style="margin: 4px 0; font-size: 0.95rem;">{d.description}</p>
                            {f'<div class="evidence-quote">“{d.evidence}”</div>' if d.evidence else ''}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("#### ❓ Open Questions")
            if not analysis.open_questions:
                st.caption("No open questions recorded.")
            else:
                for q in analysis.open_questions:
                    st.markdown(f"- {q}")

        with risk_col:
            st.markdown("#### ⚠️ Risks, Blockers & Mitigations")
            if not analysis.risks:
                st.info("No critical blockers or risks detected.")
            else:
                for r in analysis.risks:
                    st.markdown(
                        f"""
                        <div class="warning-card">
                            <strong>Risk: {r.description}</strong><br/>
                            {f'<div class="evidence-quote">“{r.evidence}”</div>' if r.evidence else ''}
                            {f'<div class="clarification-box">🎯 <b>Suggested Follow-up:</b> {r.suggested_follow_up}</div>' if r.suggested_follow_up else ''}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # === TAB 4: Executive Summary ===
    with tab_summary:
        st.markdown(f"#### Executive Summary: {analysis.meeting_title or 'Meeting Overview'}")
        if analysis.meeting_date:
            st.caption(f"**Meeting Date:** {analysis.meeting_date}")

        st.markdown(
            f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <p style="font-size: 1.05rem; line-height: 1.6; color: #1e293b; margin: 0;">{analysis.summary}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("##### Key Topics Discussed")
        if analysis.key_topics:
            topic_pills = " ".join([f"`{t}`" for t in analysis.key_topics])
            st.markdown(topic_pills)
        else:
            st.caption("No specific topics isolated.")

        st.divider()
        with st.expander("📖 Original Source Notes"):
            st.text(st.session_state["meeting_notes_text"])

    # === TAB 5: Export & Raw JSON Data ===
    with tab_export:
        st.markdown("#### Export Structured Deliverables")
        st.caption("Download sanitized data tables for team distribution or Jira / Asana import.")

        export_col1, export_col2 = st.columns(2)

        # CSV Export Preparation
        csv_rows = []
        for item in analysis.action_items:
            eff_status = st.session_state["task_status_overrides"].get(item.id, item.status)
            csv_rows.append(
                {
                    "Task ID": item.id,
                    "Task Description": item.task,
                    "Owner": item.owner if item.owner else "Unassigned",
                    "Deadline": item.deadline_text if item.deadline_text else "Not stated",
                    "Priority": item.priority.capitalize(),
                    "Status": eff_status.replace("_", " ").capitalize(),
                    "Confidence": f"{item.confidence:.0%}",
                    "Evidence Quote": item.evidence,
                    "Missing Information": "; ".join(item.missing_information),
                }
            )
        csv_df = pd.DataFrame(csv_rows)
        csv_buffer = io.StringIO()
        csv_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue().encode("utf-8")

        # JSON Export Preparation
        json_str = analysis.model_dump_json(indent=2)
        json_data = json_str.encode("utf-8")

        with export_col1:
            st.download_button(
                label="📥 Download Action Items (CSV)",
                data=csv_data,
                file_name=f"meeting_action_items_{analysis.meeting_date or 'latest'}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )
            st.dataframe(csv_df, use_container_width=True)

        with export_col2:
            st.download_button(
                label="📥 Download Full Analysis (JSON)",
                data=json_data,
                file_name=f"meeting_analysis_{analysis.meeting_date or 'latest'}.json",
                mime="application/json",
                use_container_width=True,
            )
            st.json(json.loads(json_str))
