from __future__ import annotations

from uuid import uuid4

import streamlit as st

from .errors import QueryExecutionError
from .llm import LLMConfigurationError, LLMResponseError
from .logging_config import get_logger
from .runtime import Runtime
from .service import QuestionValidationError
from .sql_guard import SQLValidationError


_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink: #15251f; --muted: #69776f; --mint: #b9f5d0; --lime: #d8f36b; --paper: #f5f7ef; --line: #dbe4d9; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
    p, label, [data-testid="stMarkdownContainer"] { font-family: 'DM Sans', sans-serif; }
    .hero { padding: 2rem 0 1rem; border-bottom: 1px solid var(--line); }
    .eyebrow { color: #3d765d; font-size: .75rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
    .hero h1 { font-size: clamp(2.4rem, 6vw, 5rem); line-height: .98; margin: .35rem 0 1rem; max-width: 760px; }
    .hero p { color: var(--muted); max-width: 650px; font-size: 1.05rem; }
    .stButton > button { border-radius: 6px; border: 1px solid var(--ink); background: var(--lime); color: var(--ink); font-weight: 700; }
    [data-testid="stTextArea"] textarea, .stTextArea textarea {
        border: 1px solid #a9b9ae; border-radius: 6px; background: #ffffff !important;
        color: #15251f !important; caret-color: #15251f !important; font-size: 1rem;
        -webkit-text-fill-color: #15251f !important;
    }
    [data-testid="stTextArea"] textarea::placeholder, .stTextArea textarea::placeholder {
        color: #69776f !important; opacity: 1 !important;
    }
    [data-testid="stTextArea"] textarea::selection, .stTextArea textarea::selection {
        background: #b9f5d0; color: #15251f;
    }
</style>
"""


def _is_authenticated(runtime: Runtime) -> bool:
    if not runtime.settings.access_token:
        return True
    if st.session_state.get("authenticated"):
        return True
    st.markdown("### Sign in to InsightSQL")
    token = st.text_input("Access token", type="password")
    if st.button("Continue"):
        if token == runtime.settings.access_token:
            st.session_state["authenticated"] = True
            st.rerun()
        st.error("The access token is not valid.")
    return False


def render(runtime: Runtime) -> None:
    logger = get_logger()
    if not _is_authenticated(runtime):
        st.stop()

    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="hero"><div class="eyebrow">Workforce intelligence / read-only</div>'
        '<h1>Ask your data<br>what matters.</h1>'
        '<p>InsightSQL turns plain-English workforce questions into transparent, validated SQLite queries.</p></div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### InsightSQL")
        st.caption("AI-powered workforce analytics assistant")
        st.divider()
        st.markdown("**Connected data**")
        st.code(str(runtime.settings.database_path), language="text")
        st.caption(f"Maximum rows per answer: {runtime.settings.max_rows}")
        if runtime.settings.openai_api_key:
            st.success(f"GPT connected · {runtime.settings.openai_model}")
        else:
            st.warning("Demo mode · configure OPENAI_API_KEY for free-form questions")
        st.divider()
        st.markdown("**Try asking**")
        for example in (
            "How many employees are in each department?",
            "Which projects are currently active?",
            "Show average salary by department.",
        ):
            st.caption(example)

    left, right = st.columns([1.25, .75], gap="large")
    with left:
        st.markdown("### Ask a question")
        with st.form("question_form", clear_on_submit=False):
            question = st.text_area(
                "Question",
                placeholder="e.g. Which department has the most employees?",
                height=130,
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Generate answer", type="primary", use_container_width=True)

        if submitted:
            request_id = uuid4().hex
            if not question.strip():
                st.warning("Enter a question to begin.")
            else:
                try:
                    with st.spinner("Understanding the question and checking the query..."):
                        response = runtime.service.ask(question)
                    st.session_state["last_response"] = response
                    logger.info(
                        "query_completed rows=%s duration_ms=%.0f",
                        response.result.row_count,
                        response.result.duration_ms,
                        extra={"request_id": request_id},
                    )
                    st.success(f"Answer ready in {response.result.duration_ms:.0f} ms")
                except (LLMConfigurationError, LLMResponseError) as exc:
                    logger.warning("query_generation_failed error_type=%s", type(exc).__name__, extra={"request_id": request_id})
                    runtime.database.add_history(question.strip(), None, "ERROR", str(exc))
                    st.error(str(exc))
                except QuestionValidationError as exc:
                    st.warning(str(exc))
                except SQLValidationError:
                    logger.warning("query_blocked reason=sql_validation", extra={"request_id": request_id})
                    runtime.database.add_history(question.strip(), None, "BLOCKED", "The generated SQL did not pass the read-only policy.")
                    st.error("The generated query did not pass the read-only safety policy.")
                except QueryExecutionError:
                    logger.warning("query_execution_failed", extra={"request_id": request_id})
                    runtime.database.add_history(question.strip(), None, "ERROR", "Approved query could not be completed.")
                    st.error("The data source could not complete this request. Try a simpler question.")
                except Exception:
                    logger.exception("query_failed", extra={"request_id": request_id})
                    runtime.database.add_history(question.strip(), None, "ERROR", "Unexpected application error")
                    st.error("Something went wrong while running the question. Check the application logs and try again.")

        response = st.session_state.get("last_response")
        if response:
            st.markdown("### Answer")
            display_rows = [dict(zip(response.result.columns, row)) for row in response.result.rows]
            st.dataframe(display_rows, use_container_width=True, hide_index=True)
            if response.result.truncated:
                st.caption(f"Showing the first {runtime.settings.max_rows} rows. Refine the question for a smaller result.")
            st.caption(f"{response.result.row_count} rows · {response.result.duration_ms:.0f} ms")

    with right:
        st.markdown("### Query details")
        response = st.session_state.get("last_response")
        if response:
            st.info(response.generated.explanation)
            with st.expander("View validated SQL", expanded=True):
                st.code(response.generated.sql, language="sql")
        else:
            st.caption("Your validated SQL and query context will appear here.")

    st.divider()
    st.markdown("### Recent questions")
    for item in runtime.database.history():
        label = f"{item.status} · {item.created_at.strftime('%Y-%m-%d %H:%M')} · {item.question}"
        with st.expander(label):
            if item.sql:
                st.code(item.sql, language="sql")
            if item.error:
                st.caption(item.error)
