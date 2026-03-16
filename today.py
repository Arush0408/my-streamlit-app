import os
import re
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import streamlit_mermaid as st_mermaid

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Aagni AI", page_icon="⚡", layout="wide")

# ── STYLING ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
section.main > div { background: #f8fafc; }

.title-text {
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800; font-size: 2.8rem;
    text-align: center; padding: 1rem 0 0.25rem; line-height: 1.2;
}
.subtitle-text {
    text-align: center; color: #6b7280;
    font-size: 1.05rem; margin-bottom: 1.8rem;
}
div.stButton > button {
    background: linear-gradient(90deg, #1e3a8a, #3b82f6);
    color: white; font-weight: 700; border: none;
    border-radius: 8px; padding: 0.6rem 2rem;
    font-size: 1rem; transition: opacity 0.2s;
}
div.stButton > button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

# ── API KEY ────────────────────────────────────────────────────────────────────
# Replace the empty string below with your new Gemini API key
GEMINI_API_KEY = "AIzaSyA8A-xttanBxX8dsnVC0SXncm3SFU4GaVw"   # <── PASTE YOUR KEY HERE

def get_api_key() -> str:
    # 1. Hardcoded key above (quickest for local dev)
    if GEMINI_API_KEY.strip():
        return GEMINI_API_KEY.strip()
    # 2. .streamlit/secrets.toml
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # 3. Environment variable
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    # 4. Nothing found — show a friendly error
    st.error(
        "⚠️ **No API key found.**\n\n"
        "Open `cu_blueprint_ai.py` and paste your Gemini API key into the "
        "`GEMINI_API_KEY = \"\"` line near the top of the file."
    )
    st.stop()

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
MODEL_ID = "gemini-2.5-flash-lite"

SYSTEM_PROMPT = """\
You are 'CU Blueprint AI Architect'.
Help Chandigarh University students convert MST/Final exam topics into clear structural logic.

Rules:
- Use ## for main concepts, ### for sub-points.
- Bold all key engineering terms.
- Keep explanations concise and exam-focused.
- ALWAYS end your response with a Mermaid.js flowchart inside a ```mermaid``` code block.
- The flowchart must be hierarchical, well-labelled, and syntax-error free.
- Use only valid Mermaid syntax: graph TD or flowchart TD.
"""

# ── HELPERS ────────────────────────────────────────────────────────────────────
def extract_mermaid(text: str) -> tuple[str, str]:
    """Split response into (prose, mermaid_code). Returns ('', '') for mermaid if absent."""
    match = re.search(r"```mermaid\s*([\s\S]*?)```", text)
    if match:
        return text[: match.start()].strip(), match.group(1).strip()
    return text.strip(), ""

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛠️ Engineer's Toolkit")
    st.info("Optimised for CU MSTs & Lab Exams")
    mode = st.radio("Input Mode", ["Text / Code Query", "Scan Handwritten Notes"])
    st.divider()
    st.caption("HackOPhobia 2026 · CU Blueprint AI")

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("<h1 class='title-text'>⚡ Aagni AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle-text'>Structural Logic Architect for Chandigarh University Engineers</p>",
    unsafe_allow_html=True,
)

# ── INPUT ──────────────────────────────────────────────────────────────────────
query_content: list = []

if mode == "Text / Code Query":
    user_input = st.text_area(
        "Paste your code or MST topic:",
        placeholder="e.g. 'BEEE Transformer Phasor Diagram Logic'  or  paste a code snippet",
        height=160,
    )
    if user_input.strip():
        query_content.append(user_input.strip())
else:
    uploaded_file = st.file_uploader(
        "Upload a photo of your handwritten notes / diagrams:",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Note scanned ✔", width=420)
        query_content.append(img)
        query_content.append(
            "Analyse these handwritten notes. Convert the core logic into a "
            "professional engineering breakdown and a Mermaid flowchart."
        )

generate_btn = st.button("🏗️ Build Logic Architecture", disabled=not query_content)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── GENERATION ─────────────────────────────────────────────────────────────────
if generate_btn and query_content:
    with st.spinner("🚀 Gemini is architecting your blueprint…"):
        try:
            client = genai.Client(api_key=get_api_key())
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=query_content,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                ),
            )
            text_part, mermaid_code = extract_mermaid(response.text)
            st.session_state.last_result = (text_part, mermaid_code)
        except Exception as exc:
            st.error(f"**API Error:** {exc}")
            st.session_state.last_result = None

# ── OUTPUT ─────────────────────────────────────────────────────────────────────
if st.session_state.last_result:
    text_part, mermaid_code = st.session_state.last_result
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("### 📝 Engineering Breakdown")
        st.markdown(text_part)

    with col_right:
        st.markdown("### 📊 Logic Visualisation")
        if mermaid_code:
            try:
                st_mermaid.st_mermaid(mermaid_code, height="520px")
                with st.expander("View Mermaid source"):
                    st.code(mermaid_code, language="mermaid")
            except Exception as exc:
                st.warning("⚠️ Mermaid rendering failed — showing raw source instead.")
                st.code(mermaid_code, language="mermaid")
                st.caption(f"Render error: {exc}")
        else:
            st.info("No flowchart was generated for this query.")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption("© 2026 Aagni AI · Built with Gemini API & Streamlit · HackOPhobia")