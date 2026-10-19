"""AI Code Doctor: Modern AI-Powered Python Bug Detector & Unit Test Generator.

Built with Python, Streamlit, Google Gemini AI (GenAI SDK), and Pytest.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Ensure current directory is on pythonpath
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.analyzer import (
    analyze_python_code_ast,
    build_unified_diff,
    create_executable_test_code,
    extract_code_fence,
)
from core.gemini_service import GeminiService
from core.sample_codes import SAMPLE_SNIPPETS
from core.test_runner import run_tests_in_sandbox

# Load environment configuration
load_dotenv()

TEST_FOLDER = Path("generated_tests")
TEST_FOLDER.mkdir(exist_ok=True)
TEST_FILE = TEST_FOLDER / "test_generated.py"

# ==============================================================================
# STREAMLIT APP CONFIGURATION & THEMING
# ==============================================================================
st.set_page_config(
    page_title="AI Code Doctor | Intelligent Python Quality Suite",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom responsive CSS with modern glassmorphism cards and clean badges
st.markdown(
    """
    <style>
    /* Global & Typography */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 28px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
    }
    
    .hero-title {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 16px;
        margin-bottom: 0px;
        line-height: 1.5;
    }

    .metric-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .badge-info {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    .badge-success {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    .badge-warn {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .dark-mode-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
    }

    /* Streamlit button enhancements */
    div.stButton > button:first-child {
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        font-weight: 600;
        padding: 10px 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if "code_input" not in st.session_state:
    st.session_state["code_input"] = SAMPLE_SNIPPETS["Classic Math & Collection Bugs"]["code"]

if "bug_report" not in st.session_state:
    st.session_state["bug_report"] = ""

if "test_suite" not in st.session_state:
    st.session_state["test_suite"] = ""

if "refactored_code" not in st.session_state:
    st.session_state["refactored_code"] = ""

if "complexity_analysis" not in st.session_state:
    st.session_state["complexity_analysis"] = ""

if "test_results" not in st.session_state:
    st.session_state["test_results"] = None

if "history" not in st.session_state:
    st.session_state["history"] = []

# ==============================================================================
# SIDEBAR CONTROLS & API CONFIGURATION
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")

    env_api_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Gemini API Key",
        value=env_api_key,
        type="password",
        help="Reads from .env by default. You can override it here.",
    )

    selected_model = st.selectbox(
        "Target AI Model",
        options=[
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash",
            "gemini-flash-latest",
            "gemini-3.1-flash-lite",
        ],
        index=0,
        help="Fast and reliable Google Gemini models with automatic failover.",
    )

    gemini_svc = GeminiService(api_key=user_api_key, default_model=selected_model)

    if gemini_svc.is_configured():
        st.success("API Key detected")
    else:
        st.warning("GEMINI_API_KEY is not set.")
        st.caption("Provide an API key in `.env` or input it above to enable AI features.")

    if st.button("🔌 Test API Connection", use_container_width=True):
        with st.spinner("Pinging Gemini API..."):
            diag = gemini_svc.test_connection()
        if diag["success"]:
            st.success(f"✅ {diag['message']}")
        else:
            st.error(f"❌ {diag['message']}")

    st.divider()

    st.markdown("### 📚 Bug Presets")
    selected_preset = st.selectbox(
        "Load Example Code",
        options=list(SAMPLE_SNIPPETS.keys()),
        index=0,
    )

    if st.button("📋 Load Selected Preset", use_container_width=True):
        st.session_state["code_input"] = SAMPLE_SNIPPETS[selected_preset]["code"]
        st.session_state["bug_report"] = ""
        st.session_state["test_suite"] = ""
        st.session_state["refactored_code"] = ""
        st.session_state["complexity_analysis"] = ""
        st.session_state["test_results"] = None
        st.rerun()

    st.caption(SAMPLE_SNIPPETS[selected_preset]["description"])

    st.divider()

    # Upload local python file
    uploaded_file = st.file_uploader("📂 Upload Python Script (.py)", type=["py"])
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode("utf-8")
            if content and content != st.session_state["code_input"]:
                st.session_state["code_input"] = content
                st.success(f"Loaded {uploaded_file.name}")
                st.rerun()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")

    st.divider()
    st.caption("AI Code Doctor v2.0 • MIT License • Production Ready")

# ==============================================================================
# MAIN HERO HEADER
# ==============================================================================
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">🧪 AI Code Doctor</div>
        <div class="hero-subtitle">
            Next-generation automated Python bug diagnosis, pytest generation, AST static analysis, and sandboxed test execution.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# CODE INPUT & STATIC ANALYSIS PRE-FLIGHT
# ==============================================================================
col_code, col_ast = st.columns([7, 3])

with col_code:
    st.subheader("💻 Python Source Code")
    code_input = st.text_area(
        "Enter Python code to inspect, test, and fix:",
        value=st.session_state["code_input"],
        height=320,
        key="code_editor",
    )
    # Sync with session state
    st.session_state["code_input"] = code_input

with col_ast:
    st.subheader("🔍 AST Live Inspector")
    ast_result = analyze_python_code_ast(code_input)

    if ast_result.is_valid_syntax:
        st.markdown(
            f"""
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:12px; margin-bottom:12px;">
                <span class="metric-badge badge-success">✓ Syntax Valid</span>
                <span class="metric-badge badge-info">{ast_result.loc} LOC</span>
                <span class="metric-badge badge-info">{len(ast_result.functions)} Functions</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if ast_result.functions:
            st.caption("Discovered Callables:")
            for fn in ast_result.functions[:6]:
                st.code(f"def {fn['name']}({', '.join(fn['args'])}) -> line {fn['lineno']}", language="python")

        if ast_result.complexity_hints:
            for hint in ast_result.complexity_hints:
                st.warning(f"⚠️ {hint}")
    else:
        st.markdown(
            f"""
            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:12px; margin-bottom:12px;">
                <span class="metric-badge badge-warn">Syntax Error</span>
                <div style="color:#991b1b; font-size:13px; margin-top:6px;">{ast_result.syntax_error}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==============================================================================
# ACTION ACTION BUTTONS
# ==============================================================================
b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)

with b_col1:
    btn_detect = st.button("🐞 Detect Bugs", use_container_width=True)

with b_col2:
    btn_tests = st.button("🧪 Generate Tests", use_container_width=True)

with b_col3:
    btn_refactor = st.button("🔧 Auto-Fix & Refactor", use_container_width=True)

with b_col4:
    btn_complexity = st.button("📈 Complexity Analysis", use_container_width=True)

with b_col5:
    btn_full = st.button("🚀 Full Quality Suite", type="primary", use_container_width=True)

# Validation guard
has_action = btn_detect or btn_tests or btn_refactor or btn_complexity or btn_full
if has_action:
    if not code_input.strip():
        st.warning("⚠️ Please provide Python code in the editor above before running analysis.")
        st.stop()
    if not gemini_svc.is_configured():
        st.error("❌ Gemini API Key is required. Please set it in your `.env` or in the sidebar.")
        st.stop()

# Execution triggers
if btn_detect or btn_full:
    with st.spinner("🔍 Gemini is performing deep bug diagnosis..."):
        try:
            report = gemini_svc.detect_bugs(code_input)
            st.session_state["bug_report"] = report
            st.session_state["history"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "action": "Bug Detection",
                "model": selected_model,
            })
        except Exception as e:
            st.error(f"Failed to detect bugs: {e}")

if btn_tests or btn_full:
    with st.spinner("🧪 Generating pytest test suite..."):
        try:
            raw_tests = gemini_svc.generate_pytest_suite(code_input)
            cleaned_tests = extract_code_fence(raw_tests)
            executable_tests = create_executable_test_code(code_input, cleaned_tests)

            st.session_state["test_suite"] = executable_tests
            # Write out to generated_tests
            TEST_FILE.write_text(executable_tests, encoding="utf-8")
            st.session_state["history"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "action": "Unit Test Generation",
                "model": selected_model,
            })
        except Exception as e:
            st.error(f"Failed to generate tests: {e}")

if btn_refactor or btn_full:
    with st.spinner("🔧 Refactoring code & fixing edge cases..."):
        try:
            refactored = gemini_svc.generate_refactored_code(
                code_input,
                bug_report=st.session_state.get("bug_report", "")
            )
            st.session_state["refactored_code"] = refactored
            st.session_state["history"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "action": "Code Refactoring",
                "model": selected_model,
            })
        except Exception as e:
            st.error(f"Failed to refactor code: {e}")

if btn_complexity or btn_full:
    with st.spinner("📈 Calculating algorithmic complexity..."):
        try:
            complexity = gemini_svc.explain_code_and_complexity(code_input)
            st.session_state["complexity_analysis"] = complexity
            st.session_state["history"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "action": "Complexity Analysis",
                "model": selected_model,
            })
        except Exception as e:
            st.error(f"Failed to analyze complexity: {e}")

# ==============================================================================
# TABULATED RESULTS WORKSPACE
# ==============================================================================
tab_bugs, tab_tests, tab_refactor, tab_complexity, tab_export = st.tabs([
    "🐞 Bug Report",
    "🧪 Pytest Suite & Sandbox",
    "🔧 Refactored Code & Diff",
    "📈 Complexity & Architecture",
    "📦 Export & Session Data",
])

# ----------------- TAB 1: BUGS -----------------
with tab_bugs:
    if st.session_state["bug_report"]:
        st.markdown(st.session_state["bug_report"])
    else:
        st.info("💡 Click **Detect Bugs** or **Full Quality Suite** above to initiate intelligent defect inspection.")

# ----------------- TAB 2: TESTS & SANDBOX -----------------
with tab_tests:
    if st.session_state["test_suite"]:
        t_col1, t_col2 = st.columns([6, 4])
        with t_col1:
            st.subheader("Generated Pytest Suite")
            st.code(st.session_state["test_suite"], language="python")

            st.download_button(
                label="📥 Download test_generated.py",
                data=st.session_state["test_suite"],
                file_name="test_generated.py",
                mime="text/x-python",
                use_container_width=True,
            )

        with t_col2:
            st.subheader("⚡ Sandboxed Test Execution")
            st.write("Execute the generated tests directly in an isolated test sandbox using `pytest`.")

            if st.button("▶️ Run Tests in Sandbox", type="primary", use_container_width=True):
                with st.spinner("Running tests in isolated environment..."):
                    exec_result = run_tests_in_sandbox(st.session_state["test_suite"])
                    st.session_state["test_results"] = exec_result

            if st.session_state["test_results"]:
                res = st.session_state["test_results"]
                if res.is_success:
                    st.success(f"🎉 All Tests Passed! ({res.passed} passed in {res.duration}s)")
                else:
                    st.error(f"⚠️ Test Failures: {res.failed} failed, {res.passed} passed, {res.errors} errors ({res.duration}s)")

                st.caption(f"Status Summary: `{res.summary_line}`")

                with st.expander("📄 View Pytest Standard Output"):
                    st.code(res.raw_stdout or "No stdout recorded.", language="text")

                if res.raw_stderr:
                    with st.expander("⚠️ View Standard Error Output"):
                        st.code(res.raw_stderr, language="text")
    else:
        st.info("💡 Click **Generate Tests** to produce a complete pytest suite with automated execution support.")

# ----------------- TAB 3: REFACTOR & DIFF -----------------
with tab_refactor:
    if st.session_state["refactored_code"]:
        cleaned_refactored = extract_code_fence(st.session_state["refactored_code"])

        diff_view = build_unified_diff(
            original=code_input,
            refactored=cleaned_refactored,
            from_title="Original Code",
            to_title="AI Refactored Code",
        )

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.subheader("Refactored Python Code")
            st.code(cleaned_refactored, language="python")

            st.download_button(
                label="📥 Download Refactored Code",
                data=cleaned_refactored,
                file_name="refactored_solution.py",
                mime="text/x-python",
            )

        with r_col2:
            st.subheader("Unified Code Diff")
            if diff_view.strip():
                st.code(diff_view, language="diff")
            else:
                st.success("No structural diff detected (code is already optimal).")

        with st.expander("📝 Refactoring Notes & Explanations"):
            st.markdown(st.session_state["refactored_code"])
    else:
        st.info("💡 Click **Auto-Fix & Refactor** to generate clean, PEP 8 compliant, bug-fixed code with a unified diff.")

# ----------------- TAB 4: COMPLEXITY -----------------
with tab_complexity:
    if st.session_state["complexity_analysis"]:
        st.markdown(st.session_state["complexity_analysis"])
    else:
        st.info("💡 Click **Complexity Analysis** to inspect time/space algorithmic Big-O characteristics.")

# ----------------- TAB 5: EXPORT & METADATA -----------------
with tab_export:
    st.subheader("📦 Session Export & Audit Bundle")
    st.write("Export your complete bug audit report, test suites, and refactored code for CI/CD documentation or code reviews.")

    export_payload = {
        "export_timestamp": datetime.now().isoformat(),
        "model_used": selected_model,
        "source_code": code_input,
        "ast_analysis": ast_result.to_dict(),
        "bug_report": st.session_state.get("bug_report", ""),
        "test_suite": st.session_state.get("test_suite", ""),
        "refactored_code": st.session_state.get("refactored_code", ""),
        "complexity_analysis": st.session_state.get("complexity_analysis", ""),
    }

    json_str = json.dumps(export_payload, indent=2)

    st.download_button(
        label="📥 Download Complete Audit Report (.json)",
        data=json_str,
        file_name="ai_code_doctor_audit.json",
        mime="application/json",
    )

    if st.session_state["history"]:
        st.markdown("#### 🕒 Session Action Log")
        for item in reversed(st.session_state["history"]):
            st.caption(f"• **{item['timestamp']}** — {item['action']} ({item['model']})")

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#64748b; font-size:14px; padding:12px 0;">
        <b>🧪 AI Code Doctor</b> • Open Source Autonomous Python Quality Engineering Suite<br>
        Powered by Python 3.11+ • Streamlit • Google Gemini AI • Pytest
    </div>
    """,
    unsafe_allow_html=True,
)