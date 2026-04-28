from html import escape
from pathlib import Path

import requests
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "Uploaded Files"

API_URL = "http://127.0.0.1:8000/query"
INGEST_URL = "http://127.0.0.1:8000/ingest"
HEALTH_URL = "http://127.0.0.1:8000/"


st.set_page_config(
    page_title="Knowledge Studio",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #05020a;
                --panel: rgba(18, 9, 34, 0.88);
                --panel-2: rgba(28, 13, 52, 0.92);
                --panel-3: rgba(41, 19, 74, 0.82);
                --line: rgba(233, 213, 255, 0.14);
                --line-strong: rgba(233, 213, 255, 0.26);
                --text: #fbf7ff;
                --muted: #c8b7e2;
                --quiet: #8f79b6;
                --violet: #8b5cf6;
                --violet-2: #a855f7;
                --pink: #e879f9;
                --cyan: #67e8f9;
                --green: #74f2bf;
                --red: #fb7185;
                --shadow: 0 24px 64px rgba(0, 0, 0, 0.44);
            }

            .stApp {
                background:
                    linear-gradient(145deg, #05020a 0%, #0d061b 42%, #160b2b 72%, #24103e 100%);
                color: var(--text);
            }

            .stApp:before {
                content: "";
                position: fixed;
                inset: 0;
                pointer-events: none;
                background-image:
                    linear-gradient(rgba(255, 255, 255, 0.032) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.032) 1px, transparent 1px);
                background-size: 36px 36px;
                mask-image: linear-gradient(180deg, rgba(0,0,0,0.82), rgba(0,0,0,0.12));
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            [data-testid="stSidebar"] {
                background: rgba(7, 3, 15, 0.96);
                border-right: 1px solid var(--line);
            }

            [data-testid="stSidebar"] * {
                color: var(--text);
            }

            .main .block-container {
                max-width: 1360px;
                padding-top: 1rem;
                padding-bottom: 2.6rem;
            }

            h1, h2, h3, p, div, span, label {
                letter-spacing: 0;
            }

            p, label, .stMarkdown, .stCaptionContainer {
                color: var(--muted);
            }

            .topbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                padding: 0.78rem 0.88rem;
                margin-bottom: 1rem;
                border: 1px solid var(--line);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.055);
                box-shadow: var(--shadow);
                backdrop-filter: blur(18px);
            }

            .brand-wrap {
                display: flex;
                align-items: center;
                gap: 0.78rem;
                min-width: 0;
            }

            .brand-mark {
                width: 44px;
                height: 44px;
                border-radius: 8px;
                background: linear-gradient(135deg, var(--cyan), var(--violet-2), var(--pink));
                box-shadow: 0 16px 42px rgba(168, 85, 247, 0.35);
            }

            .brand-title {
                color: var(--text);
                font-size: 1.05rem;
                font-weight: 950;
                line-height: 1.12;
            }

            .brand-subtitle {
                color: var(--quiet);
                font-size: 0.78rem;
                font-weight: 750;
                margin-top: 0.18rem;
            }

            .top-actions {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                justify-content: flex-end;
                gap: 0.55rem;
            }

            .pill {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                padding: 0.42rem 0.7rem;
                border-radius: 999px;
                border: 1px solid var(--line);
                color: var(--muted);
                background: rgba(255, 255, 255, 0.045);
                font-size: 0.78rem;
                font-weight: 850;
                white-space: nowrap;
            }

            .pill.online {
                color: #bbf7d0;
                border-color: rgba(116, 242, 191, 0.26);
                background: rgba(34, 197, 94, 0.09);
            }

            .pill.offline {
                color: #fecdd3;
                border-color: rgba(251, 113, 133, 0.28);
                background: rgba(244, 63, 94, 0.10);
            }

            .rail-card,
            .studio-card,
            .vault-card,
            .answer-card,
            .source-card {
                border: 1px solid var(--line);
                border-radius: 8px;
                background:
                    linear-gradient(180deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.035));
                box-shadow: var(--shadow);
                backdrop-filter: blur(18px);
            }

            .rail-card,
            .vault-card {
                padding: 1rem;
                margin-bottom: 0.85rem;
            }

            .studio-card {
                padding: 1.05rem;
                margin-bottom: 0.85rem;
                background:
                    linear-gradient(145deg, rgba(139, 92, 246, 0.16), rgba(255, 255, 255, 0.05) 45%, rgba(232, 121, 249, 0.10));
            }

            .card-kicker {
                color: var(--cyan);
                font-size: 0.72rem;
                font-weight: 950;
                text-transform: uppercase;
                margin-bottom: 0.48rem;
            }

            .card-title {
                color: var(--text);
                font-size: 1.08rem;
                line-height: 1.18;
                font-weight: 950;
                margin-bottom: 0.45rem;
            }

            .card-copy {
                color: var(--muted);
                font-size: 0.88rem;
                line-height: 1.5;
                margin: 0;
            }

            .focus-title {
                color: var(--text);
                font-size: clamp(2rem, 4vw, 4.55rem);
                line-height: 0.95;
                font-weight: 950;
                margin: 0.15rem 0 0.8rem;
            }

            .focus-copy {
                max-width: 760px;
                color: #d8caef;
                font-size: 0.98rem;
                line-height: 1.62;
                margin: 0;
            }

            .rail-stat {
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 0.75rem;
                align-items: end;
                padding: 0.78rem 0;
                border-bottom: 1px solid rgba(233, 213, 255, 0.10);
            }

            .rail-stat:last-child {
                border-bottom: 0;
            }

            .rail-stat span {
                color: var(--quiet);
                font-size: 0.76rem;
                font-weight: 850;
                text-transform: uppercase;
            }

            .rail-stat strong {
                color: var(--text);
                font-size: 1.18rem;
                font-weight: 950;
            }

            .flow-step {
                display: grid;
                grid-template-columns: 26px 1fr;
                gap: 0.7rem;
                margin-top: 0.72rem;
                align-items: start;
            }

            .flow-dot {
                width: 26px;
                height: 26px;
                border-radius: 8px;
                border: 1px solid rgba(103, 232, 249, 0.26);
                background: rgba(103, 232, 249, 0.08);
            }

            .flow-step strong {
                color: var(--text);
                font-size: 0.88rem;
            }

            .flow-step p {
                color: var(--quiet);
                font-size: 0.78rem;
                line-height: 1.38;
                margin: 0.16rem 0 0;
            }

            .prompt-strip {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.62rem;
                margin: 0.9rem 0 0.4rem;
            }

            .prompt-tile {
                min-height: 82px;
                border: 1px solid rgba(233, 213, 255, 0.13);
                background: rgba(255, 255, 255, 0.045);
                border-radius: 8px;
                padding: 0.75rem;
            }

            .prompt-tile strong {
                display: block;
                color: var(--text);
                font-size: 0.83rem;
                margin-bottom: 0.25rem;
            }

            .prompt-tile span {
                display: block;
                color: var(--quiet);
                font-size: 0.75rem;
                line-height: 1.32;
            }

            .answer-card {
                padding: 1.08rem;
                margin-top: 0.9rem;
                border-left: 4px solid var(--pink);
            }

            .answer-label {
                color: var(--quiet);
                font-size: 0.72rem;
                font-weight: 950;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }

            .answer-card p,
            .source-card p {
                color: var(--muted);
                font-size: 0.95rem;
                line-height: 1.75;
                margin: 0;
                white-space: pre-wrap;
            }

            .answer-card strong,
            .source-card strong {
                color: var(--text);
            }

            .source-card {
                padding: 0.95rem;
                margin-bottom: 0.75rem;
            }

            .source-card p {
                font-size: 0.87rem;
                margin-top: 0.42rem;
            }

            .file-row {
                display: flex;
                justify-content: space-between;
                gap: 0.8rem;
                padding: 0.68rem 0;
                border-bottom: 1px solid rgba(233, 213, 255, 0.10);
            }

            .file-row:last-child {
                border-bottom: 0;
            }

            .file-row strong {
                color: var(--text);
                font-size: 0.84rem;
                overflow-wrap: anywhere;
            }

            .file-row span {
                color: var(--quiet);
                font-size: 0.76rem;
                white-space: nowrap;
            }

            .empty-state {
                min-height: 170px;
                display: grid;
                place-items: center;
                text-align: center;
                padding: 1.4rem;
                border: 1px dashed rgba(233, 213, 255, 0.20);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.035);
            }

            .empty-state strong {
                color: var(--text);
                display: block;
                margin-bottom: 0.35rem;
            }

            .stButton > button,
            [data-testid="stFormSubmitButton"] button {
                min-height: 2.74rem;
                border-radius: 8px;
                border: 1px solid rgba(233, 213, 255, 0.22);
                background: linear-gradient(135deg, #7c3aed 0%, #a855f7 46%, #e879f9 100%);
                color: white;
                font-weight: 920;
                box-shadow: 0 15px 34px rgba(168, 85, 247, 0.28);
            }

            .stButton > button:hover,
            [data-testid="stFormSubmitButton"] button:hover {
                color: white;
                border-color: rgba(103, 232, 249, 0.5);
                box-shadow: 0 20px 46px rgba(232, 121, 249, 0.28);
            }

            .stButton > button:disabled,
            [data-testid="stFormSubmitButton"] button:disabled {
                background: rgba(255, 255, 255, 0.055);
                color: rgba(251, 247, 255, 0.42);
                border-color: rgba(233, 213, 255, 0.12);
                box-shadow: none;
            }

            .stTextArea textarea,
            .stTextInput input {
                min-height: 150px;
                border-radius: 8px;
                border: 1px solid rgba(233, 213, 255, 0.18);
                color: var(--text);
                background: rgba(255, 255, 255, 0.055);
            }

            .stTextArea textarea:focus,
            .stTextInput input:focus {
                border-color: rgba(232, 121, 249, 0.75);
                box-shadow: 0 0 0 1px rgba(232, 121, 249, 0.25);
            }

            [data-testid="stFileUploaderDropzone"] {
                min-height: 142px;
                border-radius: 8px;
                border: 1px dashed rgba(233, 213, 255, 0.34);
                background: rgba(255, 255, 255, 0.045);
            }

            [data-testid="stFileUploaderDropzone"]:hover {
                border-color: rgba(232, 121, 249, 0.72);
                background: rgba(168, 85, 247, 0.12);
            }

            [data-testid="stTabs"] button {
                color: var(--muted);
                font-weight: 900;
            }

            [data-testid="stTabs"] button[aria-selected="true"] {
                color: var(--text);
            }

            [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
                background: var(--pink);
            }

            .stAlert,
            .stExpander {
                border-radius: 8px;
                border: 1px solid var(--line);
                background: rgba(255, 255, 255, 0.055);
            }

            hr {
                border-color: rgba(233, 213, 255, 0.10);
            }

            @media (max-width: 1100px) {
                .prompt-strip {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }

                .focus-title {
                    font-size: 2.6rem;
                }
            }

            @media (max-width: 740px) {
                .topbar {
                    align-items: flex-start;
                    flex-direction: column;
                }

                .top-actions {
                    justify-content: flex-start;
                }

                .prompt-strip {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def api_is_online() -> bool:
    try:
        response = requests.get(HEALTH_URL, timeout=2)
        return response.ok
    except requests.RequestException:
        return False


def get_uploaded_files() -> list[Path]:
    UPLOAD_DIR.mkdir(exist_ok=True)
    return sorted(
        [path for path in UPLOAD_DIR.iterdir() if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def ask_api(question: str) -> tuple[str, list[dict]]:
    response = requests.post(API_URL, json={"query": question}, timeout=180)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "No response available."), result.get("sources", [])


def set_prompt(prompt: str) -> None:
    st.session_state.question_input = prompt


def render_sources(sources: list[dict]) -> None:
    if not sources:
        st.info("No source previews were returned for this answer.")
        return

    for index, source in enumerate(sources, start=1):
        metadata = source.get("metadata") or {}
        file_name = (
            metadata.get("source") or metadata.get("file_name") or "Uploaded document"
        )
        page = metadata.get("page")
        title = Path(str(file_name)).name

        if page is not None:
            title = f"{title} - page {int(page) + 1}"

        content = source.get("content") or "No preview available."
        st.markdown(
            f"""
            <div class="source-card">
                <strong>Source {index}: {escape(title)}</strong>
                <p>{escape(content)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_file_vault(files: list[Path]) -> None:
    if files:
        rows = "".join(
            [
                f'<div class="file-row">'
                f'<strong>{escape(path.name)}</strong>'
                f'<span>{format_size(path.stat().st_size)}</span>'
                f'</div>'
                for path in files[:8]
            ]
        )
    else:
        rows = (
            '<div class="empty-state">'
            '<div>'
            '<strong>No files yet</strong>'
            '<p>Upload a document to begin.</p>'
            '</div>'
            '</div>'
        )

    html = (
        '<div class="vault-card">'
        '<div class="card-kicker">Current Files</div>'
        f'{rows}'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


inject_styles()

uploaded_files = get_uploaded_files()
api_online = api_is_online()

st.session_state.setdefault("question_input", "")
st.session_state.setdefault("last_answer", "")
st.session_state.setdefault("last_sources", [])
st.session_state.setdefault("last_question", "")


with st.sidebar:
    st.markdown("### Knowledge Studio")
    st.caption(f"Query: {API_URL}")
    st.caption(f"Ingest: {INGEST_URL}")
    st.caption(f"Uploads: {UPLOAD_DIR}")


status_class = "online" if api_online else "offline"
status_text = "Online" if api_online else "Offline"

st.markdown(
    f"""
    <div class="topbar">
        <div class="brand-wrap">
            <div class="brand-mark"></div>
            <div>
                <div class="brand-title">Knowledge Studio</div>
                <div class="brand-subtitle">Private RAG workspace for uploaded documents</div>
            </div>
        </div>
        <div class="top-actions">
            <span class="pill {status_class}">Backend {status_text}</span>
            <span class="pill">{len(uploaded_files)} document(s)</span>
            <span class="pill">Mistral pipeline</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

rail_col, studio_col, vault_col = st.columns([0.72, 1.58, 0.9], gap="large")

with rail_col:
    st.markdown(
        f"""
        <div class="rail-card">
            <div class="card-kicker">Assistant</div>
            <div class="card-title">Grounded AI Analyst</div>
            <p class="card-copy">Answers only from retrieved document context, with evidence kept visible.</p>
            <div class="rail-stat">
                <span>Documents</span>
                <strong>{len(uploaded_files)}</strong>
            </div>
            <div class="rail-stat">
                <span>Retriever</span>
                <strong>Top 3</strong>
            </div>
            <div class="rail-stat">
                <span>Status</span>
                <strong>{status_text}</strong>
            </div>
        </div>
        <div class="rail-card">
            <div class="card-kicker">Flow</div>
            <div class="flow-step">
                <div class="flow-dot"></div>
                <div><strong>Upload</strong><p>Add source files to the vault.</p></div>
            </div>
            <div class="flow-step">
                <div class="flow-dot"></div>
                <div><strong>Index</strong><p>Process content into searchable chunks.</p></div>
            </div>
            <div class="flow-step">
                <div class="flow-dot"></div>
                <div><strong>Ask</strong><p>Generate answers with source previews.</p></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with studio_col:
    st.markdown(
        """
        <div class="studio-card">
            <div class="card-kicker">Question Studio</div>
            <h1 class="focus-title">Ask your documents.</h1>
            <p class="focus-copy">Choose a prompt starter or write your own question, then let the assistant retrieve the most relevant passages before answering.</p>
            <div class="prompt-strip">
                <div class="prompt-tile"><strong>Briefing</strong><span>Summarize the important points.</span></div>
                <div class="prompt-tile"><strong>Risks</strong><span>Find gaps and limitations.</span></div>
                <div class="prompt-tile"><strong>Timeline</strong><span>Extract dates and deliverables.</span></div>
                <div class="prompt-tile"><strong>Next Step</strong><span>Identify what needs attention.</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prompt_cols = st.columns(4)
    prompt_buttons = [
        ("Briefing", "Summarize the most important points from my uploaded documents."),
        ("Risks", "What risks, gaps, or limitations are mentioned in the documents?"),
        ("Timeline", "Extract important dates, names, milestones, and deliverables."),
        ("Next Step", "What should I focus on first based on these documents?"),
    ]
    for column, (label, prompt) in zip(prompt_cols, prompt_buttons):
        with column:
            st.button(
                label, on_click=set_prompt, args=(prompt,), use_container_width=True
            )

    with st.form("question_form", clear_on_submit=False):
        st.text_area(
            "Question",
            key="question_input",
            placeholder="Ask a precise question about the uploaded documents...",
            height=170,
        )
        ask_clicked = st.form_submit_button("Generate Answer", disabled=not api_online)

    if ask_clicked:
        question = st.session_state.question_input.strip()
        if not question:
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Retrieving relevant context and preparing the answer..."):
                try:
                    answer, sources = ask_api(question)
                    st.session_state.last_answer = answer
                    st.session_state.last_sources = sources
                    st.session_state.last_question = question
                except requests.RequestException as exc:
                    st.error(f"Query API unavailable: {exc}")
                except ValueError:
                    st.error("The API returned an invalid response.")

    if st.session_state.last_answer:
        answer_tab, evidence_tab, question_tab = st.tabs(
            ["Answer", "Evidence", "Question"]
        )
        with answer_tab:
            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="answer-label">AI Response</div>
                    <p>{escape(st.session_state.last_answer)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with evidence_tab:
            render_sources(st.session_state.last_sources)
        with question_tab:
            st.markdown(
                f"""
                <div class="source-card">
                    <strong>Last Question</strong>
                    <p>{escape(st.session_state.last_question)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="answer-card">
                <div class="answer-label">Waiting</div>
                <p>Your answer will appear here after the first query, with evidence in a separate tab.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with vault_col:
    st.markdown(
        """
        <div class="vault-card">
            <div class="card-kicker">Document Vault</div>
            <div class="card-title">Sources</div>
            <p class="card-copy">Drop in PDFs, DOCX files, or text files, then refresh the index.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload source file",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX, TXT",
    )

    if uploaded_file:
        file_path = UPLOAD_DIR / uploaded_file.name
        file_path.write_bytes(uploaded_file.getbuffer())
        uploaded_files = get_uploaded_files()
        st.success(f"{uploaded_file.name} uploaded.")

    process_clicked = st.button(
        "Process Vault",
        disabled=not api_online or not uploaded_files,
        use_container_width=True,
    )

    if process_clicked:
        with st.spinner("Indexing document chunks..."):
            try:
                response = requests.post(INGEST_URL, timeout=120)
                if response.ok:
                    result = response.json()
                    st.success(result.get("message", "Documents processed."))
                else:
                    st.error("The ingestion API returned an error.")
            except requests.RequestException as exc:
                st.error(f"Ingestion API unavailable: {exc}")

    render_file_vault(uploaded_files)
