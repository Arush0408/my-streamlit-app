import os
import re
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Aagni AI", page_icon="🔥", layout="wide")

# ── STYLING ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
section.main > div { background: #0f0f1a; }
.stApp { background: #0f0f1a; }

/* ── Animations ── */
@keyframes fadeInUp  { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes glow      { 0%,100%{text-shadow:0 0 20px #3b82f680} 50%{text-shadow:0 0 40px #3b82f6cc,0 0 80px #1e3a8a88} }
@keyframes shimmer   { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
@keyframes pulse     { 0%,100%{opacity:1} 50%{opacity:0.4} }
@keyframes borderRun { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes float     { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }

/* ── Title ── */
.title-text {
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #60a5fa);
    background-size: 300% 100%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800; font-size: 3.2rem;
    text-align: center; padding: 1.2rem 0 0.3rem; line-height: 1.2;
    animation: shimmer 4s linear infinite, fadeInUp 0.6s ease both;
}
.subtitle-text {
    text-align: center; color: #94a3b8;
    font-size: 1.05rem; margin-bottom: 0.5rem;
    animation: fadeInUp 0.8s ease both;
}
.tagline {
    text-align: center;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 0.9rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; margin-bottom: 2rem;
    animation: fadeInUp 1s ease both;
}

/* ── Stat badge ── */
.stat-badge {
    background: linear-gradient(135deg, #1e3a8a44, #3b82f633);
    border: 1px solid #3b82f644;
    color: #93c5fd; border-radius: 20px; padding: 0.35rem 1rem;
    font-size: 0.82rem; font-weight: 700; display: inline-block;
    margin-bottom: 0.8rem; backdrop-filter: blur(8px);
}

/* ── Cards ── */
.output-card {
    background: #1a1a2e;
    border: 1px solid #2d2d4e;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 24px rgba(59,130,246,0.08);
    animation: fadeInUp 0.5s ease both;
}

/* ── Chat bubbles ── */
.chat-user {
    background: linear-gradient(135deg, #1e3a8a44, #3b82f622);
    border: 1px solid #3b82f633;
    border-radius: 16px 16px 4px 16px;
    padding: 0.7rem 1.1rem; margin: 0.5rem 0;
    font-size: 0.92rem; color: #bfdbfe; text-align: right;
}
.chat-ai {
    background: #1e1e38;
    border: 1px solid #2d2d50;
    border-radius: 16px 16px 16px 4px;
    padding: 0.7rem 1.1rem; margin: 0.5rem 0;
    font-size: 0.92rem; color: #e2e8f0;
}

/* ── Buttons ── */
div.stButton > button {
    background: linear-gradient(90deg, #1e3a8a, #3b82f6, #a78bfa);
    background-size: 200% 100%;
    color: white; font-weight: 700; border: none;
    border-radius: 10px; padding: 0.65rem 2rem;
    font-size: 1rem; transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(59,130,246,0.3);
}
div.stButton > button:hover {
    background-position: right center;
    box-shadow: 0 6px 25px rgba(59,130,246,0.5);
    transform: translateY(-1px);
}

/* ── Skeleton loader ── */
.skeleton {
    background: linear-gradient(90deg, #1e1e38 25%, #2d2d50 50%, #1e1e38 75%);
    background-size: 200% 100%;
    border-radius: 8px; height: 18px; margin: 10px 0;
    animation: shimmer 1.5s infinite;
}

/* ── Tutorial steps ── */
.tut-step {
    background: #1a1a2e;
    border-left: 3px solid #3b82f6;
    border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.1rem; margin: 0.6rem 0;
    color: #e2e8f0; font-size: 0.9rem;
}
.tut-num {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    color: white; border-radius: 50%;
    width: 24px; height: 24px; display: inline-flex;
    align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 800;
    margin-right: 0.6rem;
}

/* ── Feature pills ── */
.feature-pill {
    display: inline-block;
    background: linear-gradient(135deg, #1e3a8a22, #a78bfa22);
    border: 1px solid #a78bfa44;
    border-radius: 20px; padding: 0.25rem 0.75rem;
    font-size: 0.78rem; color: #c4b5fd; margin: 0.2rem;
}

/* ── Dark inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #1a1a2e !important;
    border: 1px solid #2d2d4e !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px #3b82f622 !important;
}

/* ── Streamlit widget label colors ── */
label, .stRadio label, .stSelectbox label { color: #94a3b8 !important; }
.stSelectbox > div > div { background: #1a1a2e !important; color: #e2e8f0 !important; }

/* ── Divider ── */
hr { border-color: #2d2d4e !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #12121f !important; }
section[data-testid="stSidebar"] * { color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

# ── API KEY ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyA8A-xttanBxX8dsnVC0SXncm3SFU4GaVw"   # <── PASTE YOUR KEY HERE

def get_api_key() -> str:
    if GEMINI_API_KEY.strip():
        return GEMINI_API_KEY.strip()
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    st.error("⚠️ **No API key found.** Open `aagni_ai.py` and paste your Gemini API key into `GEMINI_API_KEY = \"\"`.")
    st.stop()

# ── CACHED CLIENT ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return genai.Client(api_key=get_api_key())

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
MODEL_ID = "gemini-2.5-flash-lite"
MAX_INPUT_CHARS = 5000

DEPARTMENT_PROMPTS = {
    "💻  CSE / IT":    "Focus on data structures, algorithms, OS, DBMS, networking, and programming concepts.",
    "⚡  BEEE / ECE":  "Focus on circuits, transformers, signals, semiconductor devices, and phasor diagrams.",
    "⚙️  Mechanical":  "Focus on thermodynamics, fluid mechanics, manufacturing, and machine design.",
    "🔬  General":     "Provide a broad, subject-neutral engineering breakdown.",
}

EXAMPLE_TOPICS = {
    "💻  CSE / IT":    ["Dijkstra's Algorithm", "OS Process Scheduling", "SQL Joins", "TCP/IP Model"],
    "⚡  BEEE / ECE":  ["Transformer Phasor Diagram", "PN Junction Diode", "Norton's Theorem", "AM Modulation"],
    "⚙️  Mechanical":  ["Carnot Cycle", "Bernoulli's Equation", "CNC Machining", "Gear Trains"],
    "🔬  General":     ["Recursion vs Iteration", "SDLC Models", "Ohm's Law", "Newton's Laws"],
}

DIFFICULTY_MAP = {
    0: ("Basic",        "Use simple language, avoid heavy math. Focus on definitions and intuition."),
    1: ("Intermediate", "Balance theory with some equations. Suitable for MST revision."),
    2: ("Advanced",     "Include derivations, edge cases, and exam-level depth."),
}

MERMAID_FENCE = "```"

BASE_SYSTEM_PROMPT = (
    "You are 'Aagni AI Architect'.\n"
    "Help Chandigarh University students convert MST/Final exam topics into clear structural logic.\n\n"
    "Formatting rules:\n"
    "- Use ## for main concepts, ### for sub-points.\n"
    "- Bold all key engineering terms.\n"
    "- Keep explanations concise and exam-focused.\n\n"
    "Flowchart rules — THIS IS MANDATORY:\n"
    "- You MUST end every response with a Mermaid diagram.\n"
    "- Wrap it exactly like this:\n"
    + MERMAID_FENCE + "mermaid\n"
    "graph TD\n"
    "    A[Start] --> B[Step]\n"
    + MERMAID_FENCE + "\n"
    "- Use ONLY 'graph TD' or 'flowchart TD'.\n"
    "- Node labels in square brackets [] only — no parentheses ().\n"
    "- Keep node IDs short: A, B, C1, D2.\n"
    "- No text after the closing fence.\n"
)

FOLLOWUP_SYSTEM_PROMPT = (
    "You are 'Aagni AI Architect', an expert engineering tutor.\n"
    "Answer concisely and stay exam-focused.\n"
    "Include a Mermaid diagram only if it genuinely helps:\n"
    + MERMAID_FENCE + "mermaid\n"
    "graph TD\n"
    "    A[Start] --> B[Step]\n"
    + MERMAID_FENCE + "\n"
    "ONLY 'graph TD'. Square brackets [] only. No parentheses in labels.\n"
)

# ── HELPERS ────────────────────────────────────────────────────────────────────
def extract_mermaid(text: str) -> tuple[str, str]:
    match = re.search(r"```mermaid\s*\n([\s\S]*?)```", text)
    if match:
        return text[: match.start()].strip(), match.group(1).strip()
    fallback = re.search(r"(graph TD[\s\S]*?)(?:```|$)", text)
    if fallback:
        return text[: fallback.start()].strip(), fallback.group(1).strip()
    return text.strip(), ""

def sanitize_mermaid(code: str) -> str:
    lines = []
    for line in code.splitlines():
        line = re.sub(r'(\w+)\(([^)]+)\)', r'\1[\2]', line)
        lines.append(line)
    return "\n".join(lines)

def build_system_prompt(dept: str, difficulty: int) -> str:
    diff_label, diff_instruction = DIFFICULTY_MAP[difficulty]
    return (
        BASE_SYSTEM_PROMPT
        + f"\nDepartment context: {DEPARTMENT_PROMPTS[dept]}"
        + f"\nDifficulty: {diff_label}. {diff_instruction}"
    )

def call_gemini(contents: list, system: str) -> str:
    client = get_client()
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.2),
    )
    return response.text

def make_shareable_link(query: str) -> str:
    encoded = urllib.parse.quote(query)
    try:
        base = st.get_option("browser.serverAddress") or "localhost"
        port = st.get_option("browser.serverPort") or 8501
        return f"http://{base}:{port}/?topic={encoded}"
    except Exception:
        return f"http://localhost:8501/?topic={encoded}"

def render_mermaid_zoomable(code: str, height: int = 520):
    """
    Renders Mermaid diagram inside a framed HTML component with:
    - Full zoom in / out (mouse wheel + buttons)
    - Pan (click & drag)
    - Fit-to-frame button
    - No clipping — diagram always stays inside the bordered frame
    """
    clean = sanitize_mermaid(code)
    # Escape backticks and backslashes for JS template literal
    js_safe = clean.replace("\\", "\\\\").replace("`", "\\`")

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#12121f; font-family:'Space Grotesk',sans-serif; overflow:hidden; }}

  #frame {{
    width:100%; height:{height}px;
    background:#1a1a2e;
    border:1.5px solid #2d2d6e;
    border-radius:14px;
    overflow:hidden;
    position:relative;
    box-shadow: 0 4px 32px rgba(59,130,246,0.12), inset 0 0 60px rgba(59,130,246,0.03);
  }}

  /* corner glow accents */
  #frame::before {{
    content:'';
    position:absolute; inset:0;
    background: radial-gradient(ellipse at 10% 10%, #3b82f611 0%, transparent 60%),
                radial-gradient(ellipse at 90% 90%, #a78bfa11 0%, transparent 60%);
    pointer-events:none; z-index:0;
  }}

  #canvas {{
    width:100%; height:100%;
    cursor:grab;
    user-select:none;
    position:relative; z-index:1;
  }}
  #canvas:active {{ cursor:grabbing; }}

  #svg-wrap {{
    position:absolute;
    transform-origin: 0 0;
    transition: none;
  }}
  #svg-wrap svg {{
    display:block;
    max-width:none !important;
  }}

  /* ── Toolbar ── */
  #toolbar {{
    position:absolute; bottom:14px; right:14px;
    display:flex; gap:7px; z-index:10;
  }}
  .tb-btn {{
    background: linear-gradient(135deg,#1e3a8aaa,#3b82f6aa);
    border:1px solid #3b82f666;
    color:#e2e8f0; border-radius:8px;
    width:34px; height:34px;
    display:flex; align-items:center; justify-content:center;
    cursor:pointer; font-size:15px; font-weight:700;
    backdrop-filter:blur(6px);
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(59,130,246,0.25);
  }}
  .tb-btn:hover {{
    background: linear-gradient(135deg,#3b82f6cc,#a78bfacc);
    box-shadow: 0 4px 16px rgba(59,130,246,0.5);
    transform: scale(1.1);
  }}

  /* ── Zoom label ── */
  #zoom-label {{
    position:absolute; bottom:14px; left:14px;
    background:#1e1e3888; border:1px solid #2d2d5066;
    border-radius:8px; padding:4px 10px;
    font-size:11px; color:#94a3b8;
    backdrop-filter:blur(6px); z-index:10;
    font-family:'Space Grotesk',sans-serif;
  }}

  /* ── Hint ── */
  #hint {{
    position:absolute; top:12px; left:50%; transform:translateX(-50%);
    background:#1e1e3888; border:1px solid #2d2d5066;
    border-radius:20px; padding:3px 14px;
    font-size:10px; color:#64748b;
    backdrop-filter:blur(6px); z-index:10;
    pointer-events:none;
    font-family:'Space Grotesk',sans-serif;
  }}

  /* mermaid dark theme overrides */
  .node rect, .node circle, .node ellipse, .node polygon {{
    fill:#1e3a8a !important; stroke:#3b82f6 !important; stroke-width:1.5px !important;
  }}
  .node .label, .nodeLabel {{ color:#e2e8f0 !important; fill:#e2e8f0 !important; }}
  .edgePath path {{ stroke:#3b82f6 !important; stroke-width:1.8px !important; }}
  .arrowheadPath {{ fill:#3b82f6 !important; }}
  .edgeLabel {{ background:#1a1a2e !important; color:#94a3b8 !important; }}
  .cluster rect {{ fill:#12121f !important; stroke:#2d2d4e !important; }}
  text {{ fill:#e2e8f0 !important; }}
  .titleText {{ fill:#60a5fa !important; font-weight:700 !important; }}
</style>
</head>
<body>
<div id="frame">
  <div id="canvas">
    <div id="svg-wrap">
      <div class="mermaid" id="mermaid-src" style="display:none">{{}}</div>
    </div>
  </div>
  <div id="toolbar">
    <div class="tb-btn" id="btn-in"  title="Zoom In">＋</div>
    <div class="tb-btn" id="btn-out" title="Zoom Out">－</div>
    <div class="tb-btn" id="btn-fit" title="Fit to Frame">⊡</div>
    <div class="tb-btn" id="btn-rst" title="Reset">↺</div>
  </div>
  <div id="zoom-label">100%</div>
  <div id="hint">🖱 Scroll to zoom · Drag to pan</div>
</div>

<script>
mermaid.initialize({{
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {{
    primaryColor: '#1e3a8a',
    primaryTextColor: '#e2e8f0',
    primaryBorderColor: '#3b82f6',
    lineColor: '#3b82f6',
    secondaryColor: '#12121f',
    tertiaryColor: '#1a1a2e',
    background: '#1a1a2e',
    mainBkg: '#1e3a8a',
    nodeBorder: '#3b82f6',
    clusterBkg: '#12121f',
    titleColor: '#60a5fa',
    edgeLabelBackground: '#1a1a2e',
    fontFamily: 'Space Grotesk, sans-serif',
  }},
  flowchart: {{ htmlLabels: true, curve: 'basis', padding: 20 }},
  securityLevel: 'loose',
}});

const diagramCode = `{js_safe}`;
const wrap   = document.getElementById('svg-wrap');
const canvas = document.getElementById('canvas');
const frame  = document.getElementById('frame');
const zoomLbl = document.getElementById('zoom-label');

let scale = 1, tx = 0, ty = 0;
let dragging = false, startX = 0, startY = 0, startTx = 0, startTy = 0;

function applyTransform() {{
  wrap.style.transform = `translate(${{tx}}px, ${{ty}}px) scale(${{scale}})`;
  zoomLbl.textContent = Math.round(scale * 100) + '%';
}}

function fitToFrame() {{
  const svg = wrap.querySelector('svg');
  if (!svg) return;
  const fw = frame.clientWidth  - 40;
  const fh = frame.clientHeight - 80;
  const sw = svg.getAttribute('width')  ? parseFloat(svg.getAttribute('width'))  : svg.viewBox.baseVal.width;
  const sh = svg.getAttribute('height') ? parseFloat(svg.getAttribute('height')) : svg.viewBox.baseVal.height;
  if (!sw || !sh) return;
  scale = Math.min(fw / sw, fh / sh, 1.4);
  tx = (frame.clientWidth  - sw * scale) / 2;
  ty = (frame.clientHeight - sh * scale) / 2;
  applyTransform();
}}

async function renderDiagram() {{
  try {{
    const {{ svg }} = await mermaid.render('mermaid-graph', diagramCode);
    wrap.innerHTML = svg;
    // Small delay so browser paints SVG dimensions
    setTimeout(fitToFrame, 80);
  }} catch(e) {{
    wrap.innerHTML = '<div style="color:#f87171;padding:20px;font-size:13px">⚠️ Diagram render error:<br><pre style=\\"color:#fca5a5;font-size:11px\\">' + e.message + '</pre></div>';
  }}
}}
renderDiagram();

// ── Wheel zoom ──
canvas.addEventListener('wheel', (e) => {{
  e.preventDefault();
  const rect = frame.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;
  const delta = e.deltaY > 0 ? 0.88 : 1.14;
  const newScale = Math.min(Math.max(scale * delta, 0.2), 6);
  tx = mx - (mx - tx) * (newScale / scale);
  ty = my - (my - ty) * (newScale / scale);
  scale = newScale;
  applyTransform();
}}, {{ passive: false }});

// ── Drag pan ──
canvas.addEventListener('mousedown', (e) => {{
  dragging = true; startX = e.clientX; startY = e.clientY;
  startTx = tx; startTy = ty;
}});
window.addEventListener('mousemove', (e) => {{
  if (!dragging) return;
  tx = startTx + e.clientX - startX;
  ty = startTy + e.clientY - startY;
  applyTransform();
}});
window.addEventListener('mouseup', () => {{ dragging = false; }});

// ── Touch pan/zoom ──
let lastDist = 0;
canvas.addEventListener('touchstart', (e) => {{
  if (e.touches.length === 1) {{
    dragging = true;
    startX = e.touches[0].clientX; startY = e.touches[0].clientY;
    startTx = tx; startTy = ty;
  }} else if (e.touches.length === 2) {{
    dragging = false;
    lastDist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                          e.touches[0].clientY - e.touches[1].clientY);
  }}
}}, {{ passive: true }});
canvas.addEventListener('touchmove', (e) => {{
  e.preventDefault();
  if (e.touches.length === 1 && dragging) {{
    tx = startTx + e.touches[0].clientX - startX;
    ty = startTy + e.touches[0].clientY - startY;
    applyTransform();
  }} else if (e.touches.length === 2) {{
    const dist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                            e.touches[0].clientY - e.touches[1].clientY);
    const delta = dist / lastDist;
    scale = Math.min(Math.max(scale * delta, 0.2), 6);
    lastDist = dist;
    applyTransform();
  }}
}}, {{ passive: false }});
canvas.addEventListener('touchend', () => {{ dragging = false; }});

// ── Toolbar buttons ──
document.getElementById('btn-in').onclick  = () => {{ scale = Math.min(scale * 1.25, 6);   applyTransform(); }};
document.getElementById('btn-out').onclick = () => {{ scale = Math.max(scale * 0.8,  0.2); applyTransform(); }};
document.getElementById('btn-fit').onclick = fitToFrame;
document.getElementById('btn-rst').onclick = () => {{ scale=1; tx=0; ty=0; fitToFrame(); }};
</script>
</body>
</html>
""".replace("{{}}", "{" + js_safe.replace("{", "{{").replace("}", "}}") + "}")

    # The {} replacement above is tricky with f-strings — simpler approach:
    html_final = html.replace(
        '<div class="mermaid" id="mermaid-src" style="display:none">{' + js_safe.replace("{","{{").replace("}","}}") + '}</div>',
        '<div class="mermaid" id="mermaid-src" style="display:none"></div>'
    )
    # Just use the js_safe directly — already embedded in the JS const above
    components.html(html, height=height + 10, scrolling=False)

# ── SESSION STATE INIT ─────────────────────────────────────────────────────────
defaults = {
    "last_result":       None,
    "history":           [],
    "prefill":           "",
    "followup_thread":   [],
    "total_blueprints":  0,
    "feedback":          {},
    "show_tutorial":     False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── READ TOPIC FROM URL PARAM ──────────────────────────────────────────────────
params = st.query_params
if "topic" in params and not st.session_state.prefill:
    st.session_state.prefill = urllib.parse.unquote(params["topic"])

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔥 Aagni AI")
    st.markdown(
        f"<div class='stat-badge'>🏗 {st.session_state.total_blueprints} blueprints generated</div>",
        unsafe_allow_html=True,
    )

    # Tutorial button
    if st.button("📖 How to Use Aagni AI"):
        st.session_state.show_tutorial = not st.session_state.show_tutorial

    st.divider()
    dept = st.selectbox("🎓 Department", list(DEPARTMENT_PROMPTS.keys()))
    mode = st.radio("📥 Input Mode", ["✏️ Text / Code Query", "📷 Scan Handwritten Notes"])
    diff_val = st.select_slider(
        "📶 Difficulty",
        options=[0, 1, 2],
        value=1,
        format_func=lambda x: ["🟢 Basic", "🟡 Intermediate", "🔴 Advanced"][x],
    )

    st.divider()
    st.markdown("**⚡ Quick Topics**")
    for topic in EXAMPLE_TOPICS[dept]:
        if st.button(topic, key=f"ex_{topic}"):
            st.session_state.prefill = topic
            st.session_state.followup_thread = []

    st.divider()
    st.markdown("**🕘 Session History**")
    if st.session_state.history:
        for i, (q, tp, mc) in enumerate(reversed(st.session_state.history)):
            label = q if len(q) <= 36 else q[:36] + "…"
            if st.button(f"↩ {label}", key=f"hist_{i}"):
                st.session_state.last_result = (q, tp, mc)
                st.session_state.followup_thread = []
        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.session_state.last_result = None
            st.session_state.followup_thread = []
            st.rerun()
    else:
        st.caption("No queries yet.")

    st.divider()
    st.caption("HackOPhobia 2026 · Aagni AI")

# ── TUTORIAL PANEL ─────────────────────────────────────────────────────────────
if st.session_state.show_tutorial:
    st.markdown("""
<div style='background:linear-gradient(135deg,#1a1a2e,#12121f);border:1px solid #3b82f644;
     border-radius:16px;padding:1.6rem 2rem;margin-bottom:1.5rem;
     box-shadow:0 4px 32px rgba(59,130,246,0.1)'>

<div style='text-align:center;margin-bottom:1.2rem'>
  <span style='font-size:2rem'>📖</span>
  <h2 style='color:#60a5fa;margin:0.3rem 0;font-size:1.4rem'>How to Use Aagni AI</h2>
  <p style='color:#64748b;font-size:0.88rem'>Your personal exam prep architect</p>
</div>

<div class='tut-step'><span class='tut-num'>1</span><strong style='color:#93c5fd'>Pick your Department</strong> — Choose CSE/IT, BEEE/ECE, Mechanical, or General from the sidebar. This tailors every explanation to your subject.</div>
<div class='tut-step'><span class='tut-num'>2</span><strong style='color:#93c5fd'>Set Difficulty</strong> — Use the 🟢/🟡/🔴 slider. Basic for quick revision, Advanced for deep exam prep.</div>
<div class='tut-step'><span class='tut-num'>3</span><strong style='color:#93c5fd'>Enter your Topic</strong> — Type any MST topic, paste code, or use a ⚡ Quick Topic button. You can also upload a photo of handwritten notes.</div>
<div class='tut-step'><span class='tut-num'>4</span><strong style='color:#93c5fd'>Click 🏗 Build Logic Architecture</strong> — Aagni AI generates a structured breakdown + flowchart.</div>
<div class='tut-step'><span class='tut-num'>5</span><strong style='color:#93c5fd'>Interact with the Flowchart</strong> — Scroll to zoom, drag to pan, use ＋ / － buttons, or hit ⊡ to fit the diagram perfectly in frame.</div>
<div class='tut-step'><span class='tut-num'>6</span><strong style='color:#93c5fd'>Ask Follow-ups</strong> — Use the 💬 chat below the result to ask deeper questions. Aagni remembers the context.</div>
<div class='tut-step'><span class='tut-num'>7</span><strong style='color:#93c5fd'>Download & Share</strong> — Save the breakdown as Markdown, download the diagram, or copy the 🔗 shareable link for classmates.</div>

<div style='margin-top:1.2rem;text-align:center'>
  <span class='feature-pill'>💡 Pro tip: Be specific!</span>
  <span class='feature-pill'>✏️ "Explain Dijkstra for weighted graphs" beats "Dijkstra"</span>
</div>
</div>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("<h1 class='title-text'>🔥 Aagni AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Your AI-powered exam blueprint architect</p>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>⚡ Chandigarh University · MST & Final Exam Prep · HackOPhobia 2026</p>", unsafe_allow_html=True)

# ── FEATURE PILLS ROW ──────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-bottom:1.5rem'>
  <span class='feature-pill'>🧠 AI Breakdown</span>
  <span class='feature-pill'>📊 Zoomable Flowchart</span>
  <span class='feature-pill'>💬 Follow-up Chat</span>
  <span class='feature-pill'>📷 Handwritten Notes</span>
  <span class='feature-pill'>⬇️ Export</span>
  <span class='feature-pill'>🔗 Share</span>
</div>
""", unsafe_allow_html=True)

# ── INPUT ──────────────────────────────────────────────────────────────────────
query_content: list = []
current_query: str = ""

if "✏️" in mode:
    user_input = st.text_area(
        "✏️ Paste your code or MST topic:",
        value=st.session_state.prefill,
        placeholder="e.g. 'BEEE Transformer Phasor Diagram Logic'  or  paste a code snippet…",
        height=150,
        key="text_input",
    )
    if st.session_state.prefill and user_input == st.session_state.prefill:
        st.session_state.prefill = ""
    if user_input.strip():
        if len(user_input) > MAX_INPUT_CHARS:
            st.warning(f"⚠️ Input trimmed to {MAX_INPUT_CHARS} characters.")
        current_query = user_input.strip()[:MAX_INPUT_CHARS]
        query_content.append(current_query)
else:
    uploaded_file = st.file_uploader(
        "📷 Upload a photo of your handwritten notes / diagrams:",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="✅ Note scanned successfully", width=420)
        current_query = f"[Image: {uploaded_file.name}]"
        query_content.append(img)
        query_content.append(
            "Analyse these handwritten notes. Convert the core logic into a "
            "professional engineering breakdown and a Mermaid flowchart."
        )

generate_btn = st.button("🏗️  Build Logic Architecture", disabled=not query_content)

# ── GENERATION ─────────────────────────────────────────────────────────────────
if generate_btn and query_content:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<div class='skeleton' style='width:55%;height:22px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='skeleton' style='width:85%;height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='skeleton' style='width:70%;height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='skeleton' style='width:90%;height:16px'></div>", unsafe_allow_html=True)

    with st.spinner("🚀 Aagni is architecting your blueprint…"):
        try:
            raw = call_gemini(query_content, build_system_prompt(dept, diff_val))
            text_part, mermaid_code = extract_mermaid(raw)
            if not mermaid_code:
                st.warning("⚠️ No flowchart returned. Try again — Gemini occasionally skips it.")
            st.session_state.last_result = (current_query, text_part, mermaid_code)
            st.session_state.followup_thread = []
            st.session_state.history.append((current_query, text_part, mermaid_code))
            if len(st.session_state.history) > 10:
                st.session_state.history.pop(0)
            st.session_state.total_blueprints += 1
        except Exception as exc:
            err = str(exc)
            if "429" in err or "quota" in err.lower():
                st.error("⚠️ **Rate limit hit.** Wait a moment and try again.")
            else:
                st.error(f"**API Error:** {exc}")
            st.session_state.last_result = None
    placeholder.empty()

# ── OUTPUT ─────────────────────────────────────────────────────────────────────
if st.session_state.last_result:
    query, text_part, mermaid_code = st.session_state.last_result
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("<div class='output-card'>", unsafe_allow_html=True)
        st.markdown("### 📝 Engineering Breakdown")
        st.markdown(text_part)
        st.download_button(
            label="⬇️ Download as Markdown",
            data=f"# {query}\n\n{text_part}",
            file_name="aagni_blueprint.md",
            mime="text/markdown",
        )
        link = make_shareable_link(query)
        st.text_input("🔗 Shareable link", value=link, help="Copy and share with classmates")

        st.markdown("**Was this helpful?**")
        fb1, fb2, _ = st.columns([1, 1, 6])
        with fb1:
            if st.button("👍", key="fb_up"):
                st.session_state.feedback[query] = "up"
        with fb2:
            if st.button("👎", key="fb_down"):
                st.session_state.feedback[query] = "down"
        fb = st.session_state.feedback.get(query)
        if fb == "up":   st.caption("✅ Glad it helped!")
        elif fb == "down": st.caption("📝 Thanks! Try rephrasing your topic for better results.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='output-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Logic Visualisation")
        st.caption("🖱 Scroll to zoom · Drag to pan · Use toolbar buttons · ⊡ to fit")
        if mermaid_code:
            render_mermaid_zoomable(mermaid_code, height=520)
            with st.expander("🔍 View / Download Mermaid source"):
                st.code(sanitize_mermaid(mermaid_code), language="mermaid")
                st.download_button(
                    label="⬇️ Download .mmd",
                    data=sanitize_mermaid(mermaid_code),
                    file_name="aagni_diagram.mmd",
                    mime="text/plain",
                )
        else:
            st.info("No flowchart generated. Click **Build Logic Architecture** again.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── FOLLOW-UP CHAT ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 💬 Ask a Follow-up")
    st.caption(f"💡 Context: *{query[:90]}{'…' if len(query) > 90 else ''}*")

    for msg in st.session_state.followup_thread:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>🧑‍🎓 {msg['text']}</div>", unsafe_allow_html=True)
        else:
            ai_text, ai_mermaid = extract_mermaid(msg["text"])
            st.markdown(f"<div class='chat-ai'>🔥 {ai_text}</div>", unsafe_allow_html=True)
            if ai_mermaid:
                render_mermaid_zoomable(ai_mermaid, height=320)

    followup_input = st.text_input(
        "Your question:",
        placeholder="e.g. 'What is the difference between step-up and step-down transformer?'",
        key="followup_input",
    )
    followup_btn = st.button("💬 Ask", disabled=not followup_input.strip())

    if followup_btn and followup_input.strip():
        context_parts = [f"Original topic: {query}\n\nBlueprint:\n{text_part}"]
        for msg in st.session_state.followup_thread:
            role_label = "Student" if msg["role"] == "user" else "Aagni AI"
            context_parts.append(f"{role_label}: {msg['text']}")
        context_parts.append(f"Student: {followup_input.strip()}")
        with st.spinner("🤔 Thinking…"):
            try:
                ai_reply = call_gemini(["\n\n".join(context_parts)], FOLLOWUP_SYSTEM_PROMPT)
                st.session_state.followup_thread.append({"role": "user", "text": followup_input.strip()})
                st.session_state.followup_thread.append({"role": "ai",   "text": ai_reply})
                st.rerun()
            except Exception as exc:
                st.error(f"**Follow-up error:** {exc}")

    if st.session_state.followup_thread:
        if st.button("🗑 Clear chat"):
            st.session_state.followup_thread = []
            st.rerun()

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;color:#475569;font-size:0.82rem;padding:0.5rem 0'>
  🔥 <strong style='color:#60a5fa'>Aagni AI</strong> · Built with Gemini API & Streamlit ·
  <span style='color:#a78bfa'>HackOPhobia 2026</span> · Chandigarh University
</div>
""", unsafe_allow_html=True)