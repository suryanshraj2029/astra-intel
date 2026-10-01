import io
import os
import base64
import re
import time
from html import escape

import fitz
import pytesseract
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ASTRA INTEL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>
    /* ================= ASTRA INTEL PREMIUM UI ================= */
    :root {
        --astra-bg: #050a13;
        --astra-panel: rgba(10, 20, 36, .82);
        --astra-panel-2: rgba(14, 28, 48, .72);
        --astra-border: rgba(91, 132, 181, .24);
        --astra-blue: #60a5fa;
        --astra-cyan: #22d3ee;
        --astra-text: #eef6ff;
        --astra-muted: #8ea3bd;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(37,99,235,.16), transparent 25%),
            radial-gradient(circle at 92% 16%, rgba(34,211,238,.09), transparent 22%),
            radial-gradient(circle at 50% 100%, rgba(30,64,175,.10), transparent 34%),
            #050a13;
        color: var(--astra-text);
    }

    [data-testid="stHeader"] {
        background: rgba(5,10,19,.55);
        backdrop-filter: blur(14px);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07101d 0%, #050a13 100%);
        border-right: 1px solid rgba(96,165,250,.12);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Hero */
    .hero {
        position: relative;
        overflow: hidden;
        padding: 38px 44px 34px;
        border: 1px solid rgba(96,165,250,.24);
        border-radius: 28px;
        background:
            linear-gradient(145deg, rgba(15,32,55,.96), rgba(5,13,24,.98)),
            #091323;
        box-shadow: 0 30px 90px rgba(0,0,0,.38), inset 0 1px rgba(255,255,255,.045);
        margin-bottom: 26px;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 420px;
        height: 420px;
        left: 18%;
        top: -300px;
        border-radius: 50%;
        background: rgba(37,99,235,.20);
        filter: blur(80px);
        pointer-events: none;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -100px;
        bottom: -170px;
        border-radius: 50%;
        background: rgba(34,211,238,.09);
        filter: blur(65px);
        pointer-events: none;
    }

    .hero-inner {
        position: relative;
        z-index: 2;
    }

    .hero-topline {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #8dbcf0;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 14px rgba(52,211,153,.8);
    }

    .hero-logo {
        width: 112px;
        height: 112px;
        object-fit: cover;
        border-radius: 24px;
        border: 1px solid rgba(245,200,76,.42);
        box-shadow: 0 18px 50px rgba(0,0,0,.42), 0 0 38px rgba(245,200,76,.10);
        margin-bottom: 18px;
    }

    .hero-title {
        position: relative;
        font-size: clamp(40px, 5vw, 62px);
        line-height: 1;
        font-weight: 850;
        letter-spacing: -2.4px;
        margin: 0;
        color: #f8fbff;
    }

    .hero-title-accent {
        color: #7dd3fc;
    }

    .astra-subtitle {
        margin-top: 14px;
        color: #d6e5f5;
        font-size: 19px;
        line-height: 1.5;
        font-weight: 600;
        text-align: left;
        max-width: 820px;
    }

    .astra-description {
        margin-top: 6px;
        color: #879ab2;
        font-size: 14px;
        line-height: 1.75;
        text-align: left;
        max-width: 820px;
    }

    .badge-row {
        display: flex;
        gap: 9px;
        flex-wrap: wrap;
        margin-top: 21px;
    }

    .badge {
        border: 1px solid rgba(96,165,250,.18);
        border-radius: 999px;
        padding: 7px 12px;
        color: #b9cce1;
        background: rgba(255,255,255,.035);
        font-size: 11px;
        font-weight: 650;
        backdrop-filter: blur(8px);
    }

    /* Section headings */
    .section-label {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 32px;
        margin-bottom: 13px;
        font-size: 14px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #d7e6f7;
    }

    .section-label span {
        display: inline-block;
        width: 5px;
        height: 22px;
        border-radius: 10px;
        background: linear-gradient(180deg, var(--astra-blue), var(--astra-cyan));
        box-shadow: 0 0 18px rgba(34,211,238,.25);
    }

    /* File uploader */
    div[data-testid="stFileUploader"] {
        border: 1px solid rgba(96,165,250,.20);
        border-radius: 20px;
        padding: 10px;
        background: linear-gradient(145deg, rgba(13,29,49,.86), rgba(7,16,29,.92));
        box-shadow: 0 18px 48px rgba(0,0,0,.18);
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #365679 !important;
        border-radius: 15px !important;
        background: rgba(59,130,246,.035) !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #60a5fa !important;
        background: rgba(59,130,246,.065) !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        padding: 17px 18px;
        border: 1px solid rgba(96,165,250,.16);
        border-radius: 17px;
        background: linear-gradient(145deg, rgba(15,31,51,.84), rgba(8,17,29,.88));
        box-shadow: 0 12px 30px rgba(0,0,0,.16);
    }

    [data-testid="stMetricLabel"] {
        color: #8196ae !important;
    }

    [data-testid="stMetricValue"] {
        color: #f3f8ff !important;
        font-weight: 800;
    }

    /* Inputs */
    [data-testid="stTextInput"] input {
        background: #091524 !important;
        border: 1px solid #263e5b !important;
        border-radius: 14px !important;
        color: #f4f8ff !important;
        padding: 13px 15px !important;
        min-height: 48px;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6, 0 0 24px rgba(59,130,246,.12) !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #294563;
        background: linear-gradient(145deg, #11243b, #0b1728);
        color: #dcecff;
        font-weight: 700;
        min-height: 42px;
        transition: .18s ease;
    }

    .stButton > button:hover {
        border-color: #4f8fd4;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 10px 25px rgba(37,99,235,.14);
    }

    /* Summary / answer / evidence cards */
    .summary-shell {
        border: 1px solid rgba(96,165,250,.18);
        border-radius: 20px;
        padding: 20px 22px;
        background: linear-gradient(145deg, rgba(13,28,48,.88), rgba(7,16,28,.92));
        box-shadow: 0 15px 42px rgba(0,0,0,.18);
        margin: 8px 0 18px;
    }

    .summary-chip {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: rgba(34,211,238,.07);
        border: 1px solid rgba(34,211,238,.16);
        color: #9be7f4;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .evidence-card {
        padding: 19px 20px;
        margin: 10px 0;
        border: 1px solid rgba(96,165,250,.18);
        border-radius: 17px;
        background: linear-gradient(145deg, rgba(12,27,47,.86), rgba(7,16,28,.88));
        box-shadow: 0 10px 30px rgba(0,0,0,.15);
    }

    .evidence-card:hover {
        border-color: rgba(96,165,250,.32);
    }

    .evidence-meta {
        color: #8398b1;
        font-size: 12px;
        margin-top: 11px;
    }

    .answer-card {
        padding: 24px 26px;
        border: 1px solid rgba(96,165,250,.28);
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(16,37,64,.92), rgba(7,17,30,.97));
        margin: 10px 0 16px;
        box-shadow: 0 18px 48px rgba(0,0,0,.22), inset 0 1px rgba(255,255,255,.035);
        line-height: 1.85;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid rgba(96,165,250,.16) !important;
        border-radius: 15px !important;
        background: rgba(9,20,34,.72) !important;
        overflow: hidden;
    }

    [data-testid="stExpander"] summary:hover {
        background: rgba(59,130,246,.045);
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 14px;
        border-width: 1px;
    }

    /* Dividers */
    hr {
        border-color: rgba(96,165,250,.10) !important;
    }

    .small-note {
        color: #7f91aa;
        font-size: 12px;
    }

    @media (max-width: 800px) {
        .block-container { padding-top: 1rem; }
        .hero { padding: 27px 22px 25px; border-radius: 22px; }
        .hero-title { font-size: 40px; }
        .hero-logo { width: 90px; height: 90px; }
        .astra-subtitle { font-size: 17px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. ENVIRONMENT + GEMINI
# ============================================================

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None


# ============================================================
# 4. OCR CONFIGURATION
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
OCR_MIN_TEXT_LENGTH = 50

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    TESSERACT_AVAILABLE = True
else:
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
    except Exception:
        TESSERACT_AVAILABLE = False


# ============================================================
# 5. CONSTANTS + SESSION STATE
# ============================================================

MIN_SIMILARITY = 0.35
MAX_CONTEXT_CHARS = 18000
MAX_SUMMARY_CHARS = 100000

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# 6. LOAD EMBEDDING MODEL
# ============================================================

@st.cache_resource

def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


try:
    model = load_embedding_model()
except Exception as e:
    st.error("Could not load the embedding model.")
    st.exception(e)
    st.stop()


# ============================================================
# 7. HEADER
# ============================================================

logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "astra_logo.jpeg")
logo_html = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as logo_file:
        logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
    logo_html = f'<img class="hero-logo" src="data:image/jpeg;base64,{logo_b64}" alt="ASTRA Logo">'
else:
    logo_html = '<div style="font-size:72px;margin-bottom:18px;">🛡️</div>'

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-inner">
            <div class="hero-topline"><span class="live-dot"></span> ASTRA SOFTWARE TEAM • INTELLIGENCE PLATFORM</div>
            {logo_html}
            <div class="hero-title">ASTRA <span class="hero-title-accent">INTEL</span></div>
            <div class="astra-subtitle">AI-Powered Defence Document Intelligence System</div>
            <div class="astra-description">Upload defence or research PDFs, search across your documents, and get grounded answers with page-level evidence.</div>
            <div class="badge-row">
                <div class="badge">📄 PDF Intelligence</div>
                <div class="badge">🔎 Semantic Search</div>
                <div class="badge">🤖 Gemini AI</div>
                <div class="badge">📍 Page-Level Evidence</div>
                <div class="badge">🔍 OCR Support</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 8. HELPER FUNCTIONS
# ============================================================

def create_chunks(text, chunk_size=1000, overlap=150):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def perform_ocr(page):
    """Render a PDF page and extract text with Tesseract."""
    try:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(image).strip()
    except Exception:
        return ""


def extract_pdf_pages(uploaded_file):
    """Return page-aware text, using OCR for image/scanned pages."""
    pdf_bytes = uploaded_file.getvalue()
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    if len(pdf) == 0:
        return []

    pages = []

    for page_index in range(len(pdf)):
        page = pdf[page_index]
        text = page.get_text("text").strip()
        method = "Text Extraction"

        if len(text) < OCR_MIN_TEXT_LENGTH and TESSERACT_AVAILABLE:
            ocr_text = perform_ocr(page)
            if len(ocr_text.strip()) > len(text):
                text = ocr_text.strip()
                method = "OCR"

        pages.append({
            "filename": uploaded_file.name,
            "page": page_index + 1,
            "text": text,
            "method": method,
        })

    return pages


def build_chunks(pages):
    chunks = []
    for page in pages:
        for text_chunk in create_chunks(page["text"]):
            chunks.append({
                "filename": page["filename"],
                "page": page["page"],
                "text": text_chunk,
            })
    return chunks


def search_chunks(question, chunks, chunk_embeddings, top_k=5):
    question_embedding = model.encode([question])
    similarities = cosine_similarity(question_embedding, chunk_embeddings)[0]
    ranked_indexes = similarities.argsort()[::-1]

    results = []
    for index in ranked_indexes[:top_k]:
        results.append({
            "filename": chunks[index]["filename"],
            "page": chunks[index]["page"],
            "text": chunks[index]["text"],
            "score": float(similarities[index]),
        })
    return results


def build_context(results, max_chars=MAX_CONTEXT_CHARS):
    parts = []
    current_size = 0

    for result in results:
        part = (
            f"Document: {result['filename']}\n"
            f"Page: {result['page']}\n"
            f"Content:\n{result['text']}\n"
        )

        if current_size + len(part) > max_chars:
            break

        parts.append(part)
        current_size += len(part)

    return "\n---\n".join(parts)


def call_gemini(prompt, max_output_tokens=1200):
    """Call Gemini with retry logic for temporary service errors."""
    if client is None:
        raise RuntimeError(
            "Gemini client is not available. Check GEMINI_API_KEY in .env."
        )

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.7-flash",
    ]

    last_error = None

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        ),
                        max_output_tokens=max_output_tokens,
                    ),
                )

                text = getattr(response, "text", None)
                if text and text.strip():
                    return text.strip(), model_name

                raise RuntimeError("Gemini returned an empty response.")

            except Exception as e:
                last_error = e
                error_text = str(e).lower()

                transient = any(token in error_text for token in [
                    "503", "unavailable", "high demand", "429",
                    "resource_exhausted", "500", "502", "504",
                    "deadline exceeded", "timeout",
                ])

                if not transient:
                    break

                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        f"Gemini models were unavailable after retries: {last_error}"
    )


def ask_gemini(question, context, chat_history):
    previous_conversation = ""
    for item in chat_history[-5:]:
        previous_conversation += (
            f"User: {item['question']}\n"
            f"Assistant: {item['answer']}\n\n"
        )

    prompt = f"""
You are ASTRA INTEL, a document question-answering assistant.

Answer the current question using ONLY the retrieved document context.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts, numbers, names, page numbers, or document names.
3. If the answer is not supported by the context, say exactly:
   "I could not find the answer in the uploaded documents."
4. Keep the answer concise and easy to understand.
5. Directly answer the current question.
6. Previous conversation is only for understanding context; it is NOT evidence.
7. Use document names and page numbers only when supported by the retrieved context.

PREVIOUS CONVERSATION:
{previous_conversation}

RETRIEVED DOCUMENT CONTEXT:
{context}

CURRENT QUESTION:
{question}
"""

    return call_gemini(prompt, max_output_tokens=1200)


def build_summary_document_text(pages):
    """Build page-labelled text for the summary model.

    Each page is kept separate so Gemini can cite real page numbers instead of
    guessing where information came from.
    """
    page_blocks = []
    for page in pages:
        text = page.get("text", "").strip()
        if text:
            page_blocks.append(
                f"[Page {page['page']}]\n{text}"
            )

    document_text = "\n\n--- PAGE BREAK ---\n\n".join(page_blocks)

    if len(document_text) <= MAX_SUMMARY_CHARS:
        return document_text

    # Preserve the beginning, middle and end instead of only the first/last
    # pages. This gives the summary model a better view of long documents.
    third = MAX_SUMMARY_CHARS // 3
    return (
        document_text[:third]
        + "\n\n[Middle content omitted because the document is very long]\n\n"
        + document_text[third:third * 2]
        + "\n\n[Middle content omitted because the document is very long]\n\n"
        + document_text[-third:]
    )


def generate_ai_summary(filename, pages):
    """Generate a structured, page-aware AI summary for one PDF only."""
    if client is None:
        return None, None

    document_text = build_summary_document_text(pages)
    if not document_text.strip():
        return None, None

    prompt = f"""
You are ASTRA INTEL, an AI document intelligence assistant.

Create a clear, student-friendly summary of ONLY this uploaded PDF.
Use ONLY the supplied document text. Do not use outside knowledge.
Do not invent facts, names, numbers, conclusions, methods, or page numbers.

IMPORTANT PAGE-CITATION RULE:
- The document text contains real page markers such as [Page 1].
- Every bullet in KEY POINTS and IMPORTANT DETAILS MUST end with a page citation
  in this exact format: [Page X] or [Pages X, Y].
- Use only page numbers that actually appear in the supplied document text.
- If a point is supported by several pages, list the relevant pages.
- Do not make up page numbers.

Return EXACTLY these four sections and nothing else:

EXECUTIVE SUMMARY:
Write 4-6 simple sentences explaining what the document is about, its purpose,
and its most important message. End the final sentence with the relevant page
citation, for example [Pages 1, 2].

KEY POINTS:
- Write 5-7 important points. Keep each point concise and student-friendly.
- Every point MUST end with [Page X] or [Pages X, Y].

MAIN TOPICS:
- List 4-6 major topics, sections, or themes found in the document.
- Add the relevant page citation to every topic.

IMPORTANT DETAILS:
- Write 3-5 important technical facts, requirements, findings, methods,
  definitions, or conclusions explicitly supported by the document.
- Every point MUST end with [Page X] or [Pages X, Y].

Additional rules:
- Paraphrase instead of copying long passages.
- Do not add general knowledge.
- Do not treat missing information as a fact.
- If the document does not contain enough information for a section, write:
  "Not clearly stated in the document."
- Keep the summary useful for a 3rd-semester CSE student.

DOCUMENT NAME: {filename}

DOCUMENT TEXT:
{document_text}
"""

    try:
        return call_gemini(prompt, max_output_tokens=1800)
    except Exception:
        return None, None


def split_summary_sections(summary_text):
    pattern = r"(?=EXECUTIVE SUMMARY:|KEY POINTS:|MAIN TOPICS:|IMPORTANT DETAILS:)"
    sections = re.split(pattern, summary_text)
    return [section.strip() for section in sections if section.strip()]


def get_valid_page_numbers(pages):
    return {int(page["page"]) for page in pages}


def clean_summary_line(line, valid_pages):
    """Keep Gemini's page citations only when they refer to real PDF pages."""
    line = line.strip()
    if not line:
        return ""

    line = re.sub(r"^[-•*]\s*", "", line)

    def replace_pages(match):
        numbers = [int(n) for n in re.findall(r"\d+", match.group(1))]
        valid = [n for n in numbers if n in valid_pages]
        if not valid:
            return ""
        if len(valid) == 1:
            return f"[Page {valid[0]}]"
        return "[Pages " + ", ".join(str(n) for n in valid) + "]"

    # Normalize [Page X], [Pages X, Y], and similar variants.
    line = re.sub(
        r"\[(?:Pages?|pages?)\s+([^\]]+)\]",
        replace_pages,
        line,
    )
    return line.strip()


def local_summary(pages):
    """Simple extractive fallback summary if Gemini is unavailable."""
    sentences = []
    for page in pages:
        text = re.sub(r"\s+", " ", page["text"]).strip()
        if not text:
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if len(sentence.split()) >= 8:
                sentences.append((page["page"], sentence.strip()))

    unique = []
    seen = set()
    for page, sentence in sentences:
        key = sentence.lower()
        if key not in seen:
            seen.add(key)
            unique.append((page, sentence))
        if len(unique) >= 8:
            break

    if not unique:
        return "No readable summary could be generated from this document."

    lines = [
        "### 🧠 Local Document Summary",
        "The following points were extracted directly from the uploaded document:",
        "",
    ]
    for page, sentence in unique:
        lines.append(f"• {sentence} _(Page {page})_")
    return "\n".join(lines)


def show_ai_summary(summary_text, pages):
    """Render the structured Gemini summary without changing the rest of the app."""
    valid_pages = get_valid_page_numbers(pages)

    for section in split_summary_sections(summary_text):
        if section.startswith("EXECUTIVE SUMMARY:"):
            body = section.replace("EXECUTIVE SUMMARY:", "", 1).strip()
            st.markdown("### 🧠 Executive Summary")
            st.write(body)

        elif section.startswith("KEY POINTS:"):
            body = section.replace("KEY POINTS:", "", 1).strip()
            st.markdown("### 🔑 Key Points")
            for line in body.splitlines():
                line = clean_summary_line(line, valid_pages)
                if line:
                    st.write(f"• {line}")

        elif section.startswith("MAIN TOPICS:"):
            body = section.replace("MAIN TOPICS:", "", 1).strip()
            st.markdown("### 📚 Main Topics")
            for line in body.splitlines():
                line = clean_summary_line(line, valid_pages)
                if line:
                    st.write(f"• {line}")

        elif section.startswith("IMPORTANT DETAILS:"):
            body = section.replace("IMPORTANT DETAILS:", "", 1).strip()
            st.markdown("### 📌 Important Details")
            for line in body.splitlines():
                line = clean_summary_line(line, valid_pages)
                if line:
                    st.write(f"• {line}")

def local_fallback_answer(question, results):
    if not results:
        return "I could not find the answer in the uploaded documents."

    keywords = re.findall(r"\b[a-zA-Z]{3,}\b", question.lower())
    stop_words = {
        "what", "when", "where", "which", "who", "why", "how",
        "does", "did", "are", "is", "was", "were", "the", "this",
        "that", "these", "those", "about", "from", "with", "into",
        "for", "and", "you", "your", "document", "documents",
    }
    keywords = [word for word in keywords if word not in stop_words]

    candidates = []
    for result in results:
        for sentence in re.split(r"(?<=[.!?])\s+", result["text"]):
            sentence = sentence.strip()
            if len(sentence.split()) < 5:
                continue

            lower = sentence.lower()
            matches = sum(1 for word in keywords if word in lower)
            score = matches * 2 + result["score"]
            candidates.append((score, sentence, result))

    candidates.sort(key=lambda x: x[0], reverse=True)

    if not candidates:
        return results[0]["text"]

    selected = candidates[:3]
    return "\n\n".join(f"• {item[1]}" for item in selected)


def unique_sources(results):
    sources = []
    for result in results:
        source = f"{result['filename']} — Page {result['page']}"
        if source not in sources:
            sources.append(source)
    return sources


# ============================================================
# 9. UPLOAD DOCUMENTS
# ============================================================

st.markdown(
    '<div class="section-label"><span></span>Upload Documents</div>',
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "📤 Upload one or more PDF documents",
    type=["pdf"],
    accept_multiple_files=True,
    help="You can upload multiple defence/research PDFs."
)

if not uploaded_files:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📄 Upload PDF")
    with col2:
        st.info("🔎 Search semantically")
    with col3:
        st.info("🤖 Ask grounded questions")

    if not TESSERACT_AVAILABLE:
        st.caption(
            "OCR is currently unavailable because Tesseract was not detected. "
            "Normal text PDFs will still work."
        )
    st.stop()


# ============================================================
# 10. PROCESS PDFs
# ============================================================

pages = []

with st.spinner("📚 Processing PDF documents..."):
    for uploaded_file in uploaded_files:
        try:
            document_pages = extract_pdf_pages(uploaded_file)
        except Exception as e:
            st.error(f"Could not open {uploaded_file.name}.")
            with st.expander("Technical details"):
                st.exception(e)
            continue

        if not document_pages:
            st.warning(f"{uploaded_file.name} contains no readable pages.")
            continue

        pages.extend(document_pages)


if not pages:
    st.error("No readable pages were found in the uploaded PDFs.")
    if not TESSERACT_AVAILABLE:
        st.info("For scanned PDFs, install Tesseract OCR and restart the app.")
    st.stop()


readable_pages = [page for page in pages if page["text"].strip()]

if not readable_pages:
    st.error("No readable text was found in the uploaded PDFs.")
    if not TESSERACT_AVAILABLE:
        st.info("Scanned PDFs require Tesseract OCR for text extraction.")
    st.stop()

chunks = build_chunks(readable_pages)

if not chunks:
    st.error("No text chunks could be created from the documents.")
    st.stop()


# ============================================================
# 11. DOCUMENT STATUS
# ============================================================

st.markdown(
    '<div class="section-label"><span></span>Document Status</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("PDFs", len(uploaded_files))
with col2:
    st.metric("Pages", len(pages))
with col3:
    st.metric("Text Chunks", len(chunks))
with col4:
    ocr_pages = sum(1 for page in pages if page["method"] == "OCR")
    st.metric("OCR Pages", ocr_pages)

for filename in dict.fromkeys(page["filename"] for page in pages):
    file_pages = [page for page in pages if page["filename"] == filename]
    st.caption(
        f"📄 {filename} — {len(file_pages)} page(s) — "
        f"{sum(1 for p in file_pages if p['method'] == 'OCR')} OCR page(s)"
    )


# ============================================================
# 12. AI SUMMARY
# ============================================================

st.markdown(
    '<div class="section-label"><span></span>AI Document Summary</div>',
    unsafe_allow_html=True,
)

if client is None:
    st.warning(
        "⚠️ Gemini is not configured. The app will show a local extractive summary instead."
    )

for filename in dict.fromkeys(page["filename"] for page in pages):
    document_pages = [page for page in pages if page["filename"] == filename]

    with st.expander(f"📄 {filename}", expanded=True):
        with st.spinner(f"Generating AI summary for {filename}..."):
            ai_summary, summary_model = generate_ai_summary(filename, document_pages)

        if ai_summary:
            st.success(f"🤖 AI-generated summary using {summary_model}")
            show_ai_summary(ai_summary, document_pages)
            st.caption(
                f"📄 Summary grounded in {len(document_pages)} page(s) of {filename}."
            )
        else:
            st.warning(
                "Gemini was unavailable for this summary. "
                "Showing a local document summary instead."
            )
            st.markdown(local_summary(document_pages))


# ============================================================
# 13. CREATE EMBEDDINGS
# ============================================================

st.markdown(
    '<div class="section-label"><span></span>Semantic Document Search</div>',
    unsafe_allow_html=True,
)

with st.spinner("🔎 Creating semantic embeddings..."):
    try:
        chunk_texts = [chunk["text"] for chunk in chunks]
        chunk_embeddings = model.encode(chunk_texts)
    except Exception as e:
        st.error("Could not create embeddings.")
        st.exception(e)
        st.stop()

st.success("✅ Semantic search is ready across all uploaded documents.")


# ============================================================
# 14. CHAT HISTORY
# ============================================================

st.markdown(
    '<div class="section-label"><span></span>Conversation</div>',
    unsafe_allow_html=True,
)

if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

if st.session_state.chat_history:
    for number, item in enumerate(st.session_state.chat_history, start=1):
        with st.expander(f"Q{number}: {item['question']}", expanded=False):
            st.write(item["answer"])
            if item.get("sources"):
                st.caption("📄 Sources: " + " | ".join(item["sources"]))


# ============================================================
# 15. ASK QUESTION
# ============================================================

st.markdown(
    '<div class="section-label"><span></span>Ask ASTRA INTEL</div>',
    unsafe_allow_html=True,
)

question = st.text_input(
    "Enter your question about the uploaded documents:",
    key="current_question",
    placeholder="Example: What is the main objective of this document?",
)

if question.strip():
    with st.spinner("🔎 Searching the uploaded documents..."):
        try:
            results = search_chunks(
                question,
                chunks,
                chunk_embeddings,
                top_k=5,
            )
        except Exception as e:
            st.error("Search failed.")
            st.exception(e)
            st.stop()

    if not results:
        st.warning("No relevant information was found.")
        st.stop()

    best_score = results[0]["score"]
    st.caption(f"Best semantic similarity score: {best_score:.2f}")

    if best_score < MIN_SIMILARITY:
        st.warning(
            "⚠️ The retrieved information may not be sufficiently relevant to the question. "
            "Try asking a more specific question about the uploaded document."
        )
    else:
        st.markdown(
            '<div class="section-label"><span></span>Evidence Retrieved</div>',
            unsafe_allow_html=True,
        )

        for index, result in enumerate(results, start=1):
            st.markdown(
                f"""
                <div class="evidence-card">
                    <strong>Relevant Section {index}</strong>
                    <div style="margin-top:8px;line-height:1.6;">{escape(result['text'])}</div>
                    <div class="evidence-meta">
                        📄 {escape(result['filename'])} &nbsp;|&nbsp;
                        Page {result['page']} &nbsp;|&nbsp;
                        Similarity {result['score']:.2f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        context = build_context(results)

        st.markdown(
            '<div class="section-label"><span></span>ASTRA INTEL Answer</div>',
            unsafe_allow_html=True,
        )

        gemini_used = False
        gemini_model = None
        gemini_error = None

        with st.spinner("🤖 Generating grounded answer..."):
            try:
                answer, gemini_model = ask_gemini(
                    question,
                    context,
                    st.session_state.chat_history,
                )
                gemini_used = True
            except Exception as e:
                gemini_error = str(e)
                answer = local_fallback_answer(question, results)

        st.markdown(
            f'<div class="answer-card">{escape(answer).replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

        if gemini_used:
            st.success(f"🤖 Answer generated using Gemini ({gemini_model}).")
        else:
            st.warning("⚠️ Gemini was unavailable, so a local document fallback was used.")
            if gemini_error:
                with st.expander("Technical Gemini error"):
                    st.code(gemini_error)

        source_pairs = unique_sources(results)
        st.info("📄 Sources: " + " | ".join(source_pairs))

        st.session_state.chat_history.append({
            "question": question,
            "answer": answer,
            "sources": source_pairs,
        })


# ============================================================
# 16. DOCUMENT CONTENT
# ============================================================

st.markdown(
    '<div class="section-label"><span></span>Document Content</div>',
    unsafe_allow_html=True,
)

for filename in dict.fromkeys(page["filename"] for page in pages):
    document_pages = [page for page in pages if page["filename"] == filename]

    with st.expander(f"📄 {filename}"):
        for page in document_pages:
            method = page.get("method", "Text Extraction")
            with st.expander(f"Page {page['page']} — {method}"):
                if page["text"].strip():
                    st.write(page["text"])
                else:
                    st.info("No readable text on this page.")


# ============================================================
# 17. FOOTER
# ============================================================

st.markdown(
    """
    <div style="text-align:center;margin-top:48px;padding:22px 0 4px;border-top:1px solid #1e2b3f;color:#6f8098;font-size:12px;">
        <strong style="color:#9fb0c8;">ASTRA INTEL</strong>
        &nbsp;•&nbsp; AI-Powered Defence Document Intelligence<br>
        Document-grounded analysis • Page-aware evidence • OCR support
    </div>
    """,
    unsafe_allow_html=True,
)
