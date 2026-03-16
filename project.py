import os
import re
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import streamlit_mermaid as st_mermaid

# ---------------------------------------------------------------------------
# 1. PAGE CONFIG & STYLING
# ---------------------------------------------------------------------------
st.set_page_config(page_title="CU Blueprint AI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
section.main > div { background: #f8fafc; }
.title-text {
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800; font-size: 2.8rem; text-align: center; padding: 1rem 0 0.25rem;
}
.subtitle-text { text-align: center; color: #6b7280; font-size: 1.05rem; margin-bottom: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. API KEY SETUP
# ---------------------------------------------------------------------------
# ENTER YOUR KEY HERE:
API_KEY = "AIzaSyA4Ll9mA-wodm2MZv_8MWDo2NSk8gbBwi4"  # <-- REPLACE with your actual API key

# ---------------------------------------------------------------------------
# 3. SYSTEM PROMPT & LOGIC
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are 'CU Blueprint AI Architect'.
Help Chandigarh University students convert MST/Final exam topics into clear structural logic.

Rules:
- Use ## for main concepts, ### for sub-points.
- Bold all key engineering terms.
- ALWAYS end with a Mermaid.js flowchart inside a ```mermaid code block.
- Use 'graph TD' or 'flowchart TD' for the diagram.
"""

def extract_mermaid(text: str) -> tuple[str, str]:
    pattern = r"```mermaid\s*([\s\S]*?)```"
    match = re.search(pattern, text)
    if match:
        mermaid_code = match.group(1).strip()
        clean_text = text[: match.start()].strip()
        return clean_text, mermaid_code
    return text.strip(), ""

# ---------------------------------------------------------------------------
# 4. SIDEBAR & INPUT
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🛠️ CU Engineer's Toolkit")
    mode = st.radio("Input Mode", ["Text / Code Query", "Scan Handwritten Notes"])
    st.divider()
    st.info("💡 Pro Tip: Upload photos of handwritten BEEE or Physics notes for best results.")

st.markdown("<h1 class='title-text'>⚡ CU Blueprint AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Structural Logic Architect for Chandigarh University</p>", unsafe_allow_html=True)

query_content = []

if mode == "Text / Code Query":
    user_input = st.text_area("Paste topic or code:", placeholder="e.g. Logic for C File Handling", height=150)
    if user_input:
        query_content.append(user_input)
else:
    uploaded_file = st.file_uploader("Upload note photo:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Note Scanned", width=400)
        query_content.append(img)
        query_content.append("Analyze these handwritten notes. Convert logic into a breakdown and a Mermaid flowchart.")

# ---------------------------------------------------------------------------
# 5. EXECUTION & OUTPUT
# ---------------------------------------------------------------------------
if st.button("🏗️ Build Logic Architecture", disabled=not query_content):
    client = genai.Client(api_key=API_KEY)
    with st.spinner("🚀 Architecting..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", # Using stable flash for speed
                contents=query_content,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                ),
            )
            text_part, mermaid_code = extract_mermaid(response.text)
            
            col_left, col_right = st.columns(2, gap="large")
            with col_left:
                st.markdown("### 📝 Engineering Breakdown")
                st.markdown(text_part)
            with col_right:
                st.markdown("### 📊 Logic Visualisation")
                if mermaid_code:
                    st_mermaid.st_mermaid(mermaid_code, height="500px")
                else:
                    st.warning("No diagram logic found. Try being more specific!")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("CU Blueprint AI · HackOPhobia 2026")