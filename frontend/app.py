"""
Nexus Research AI  -  Enterprise RAG Pipeline (n8n + ChromaDB + Gemini)
Dynamic Streamlit UI with two themes: Gotham (Batman) and Web-Verse (Spider-Man)
"""

import os
import sys
import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st
from dotenv import load_dotenv

# --- PATH SETUP FOR MODULAR BACKEND ---
# Python ko root folder ka rasta batane ke liye
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- REAL BACKEND IMPORTS ---
from backend.llm_engine import query_assistant
from backend.database import add_to_knowledge_base

load_dotenv()

# ----------------------------------------------------------------------------
# CONFIG 
# ----------------------------------------------------------------------------
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")
MODEL_LABEL = "Gemini 3.8"
REQUEST_TIMEOUT = 300

st.set_page_config(page_title="Nexus AI | Research", page_icon="🦇", layout="wide")

# ----------------------------------------------------------------------------
# THEMES
# ----------------------------------------------------------------------------
THEMES = {
    "🦇 Gotham": {
        "key": "bat",
        "p": "#FFD60A", "p_rgb": "255,214,10",
        "s": "#8A8F98", "bg": "#05060a", "bg2": "#0d0f16",
        "emoji": "🦇", "user_avatar": "🕵️", "ai_avatar": "🦇",
        "tag": "Gotham never sleeps. Neither does your knowledge base.",
        "empty": "The signal is lit. Drop a target URL in the sidebar to begin.",
    },
    "🕷️ Web-Verse": {
        "key": "spider",
        "p": "#FF2D3F", "p_rgb": "255,45,63",
        "s": "#2F6BFF", "bg": "#050814", "bg2": "#0b1022",
        "emoji": "🕷️", "user_avatar": "🧑‍🔬", "ai_avatar": "🕷️",
        "tag": "With great data comes great responsibility.",
        "empty": "Your web is ready. Drop a target URL in the sidebar to start spinning.",
    },
}

with st.sidebar:
    theme_name = st.radio("Theme", list(THEMES.keys()), horizontal=True, key="theme")
T = THEMES[theme_name]

# ----------------------------------------------------------------------------
# STATE
# ----------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("sid", str(uuid.uuid4()))
ss.setdefault("messages", [])
ss.setdefault("sources", [])
ss.setdefault("queries", 0)

def h(s: str) -> str:
    """Flatten html so markdown never treats indentation as a code block."""
    return "".join(line.strip() for line in s.strip().splitlines())

# ----------------------------------------------------------------------------
# CSS (Aapka custom Cyberpunk UI)
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;500;600&display=swap');

:root{
  --p:%P%; --p-rgb:%PRGB%; --s:%S%; --bg:%BG%; --bg2:%BG2%;
  --txt:#E8EAF0; --muted:#8b90a0;
}
html, body, [class*="css"], .stMarkdown, p, label, input, textarea, button{
  font-family:'Barlow',sans-serif !important;
}
.stApp{
  background:
    radial-gradient(1200px 600px at 80% -10%, rgba(var(--p-rgb),.14), transparent 60%),
    radial-gradient(900px 500px at -10% 110%, rgba(var(--p-rgb),.08), transparent 60%),
    var(--bg);
  color:var(--txt);
}
.stApp::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    linear-gradient(rgba(var(--p-rgb),.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(var(--p-rgb),.05) 1px, transparent 1px);
  background-size:48px 48px;
  mask-image:radial-gradient(ellipse at center, #000 30%, transparent 80%);
  animation:gridmove 14s linear infinite;
}
@keyframes gridmove{ to{ background-position:48px 48px, 48px 48px; } }

#MainMenu, footer{ visibility:hidden; }
header[data-testid="stHeader"]{ background:transparent; }

.particles{ position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden; }
.particles span{
  position:absolute; bottom:-20px; width:3px; height:3px; border-radius:50%;
  background:var(--p); box-shadow:0 0 10px var(--p); opacity:0;
  animation:rise linear infinite;
}
@keyframes rise{
  0%{ transform:translateY(0); opacity:0; }
  10%{ opacity:.8; }
  100%{ transform:translateY(-110vh) translateX(30px); opacity:0; }
}

section[data-testid="stSidebar"]{
  background:linear-gradient(180deg, var(--bg2), var(--bg));
  border-right:1px solid rgba(var(--p-rgb),.25);
  box-shadow:0 0 40px rgba(var(--p-rgb),.08);
}
section[data-testid="stSidebar"] hr{ border-color:rgba(var(--p-rgb),.18); }

.stButton>button{
  position:relative; overflow:hidden; width:100%;
  background:linear-gradient(135deg, var(--p), %PDARK%);
  color:#06070b; font-weight:700; letter-spacing:.4px;
  border:none; border-radius:10px; padding:.6rem 1rem;
  box-shadow:0 0 0 rgba(var(--p-rgb),0);
  transition:transform .15s ease, box-shadow .25s ease;
}
.stButton>button:hover{
  transform:translateY(-2px);
  box-shadow:0 8px 28px rgba(var(--p-rgb),.45);
  color:#000;
}
.stButton>button::after{
  content:""; position:absolute; top:0; left:-120%; width:60%; height:100%;
  background:linear-gradient(100deg, transparent, rgba(255,255,255,.55), transparent);
  transform:skewX(-20deg);
}
.stButton>button:hover::after{ left:140%; transition:left .7s ease; }
.stButton>button:active{ transform:scale(.97); }

.stTextInput input{
  background:rgba(255,255,255,.04) !important; color:var(--txt) !important;
  border:1px solid rgba(var(--p-rgb),.25) !important; border-radius:10px !important;
  transition:border .2s, box-shadow .2s;
}
.stTextInput input:focus{
  border-color:var(--p) !important; box-shadow:0 0 0 3px rgba(var(--p-rgb),.2) !important;
}
[data-testid="stChatInput"]{
  background:rgba(255,255,255,.04); border:1px solid rgba(var(--p-rgb),.4);
  border-radius:14px; animation:pulseborder 3s ease-in-out infinite;
}
@keyframes pulseborder{
  0%,100%{ box-shadow:0 0 0 rgba(var(--p-rgb),0); }
  50%{ box-shadow:0 0 22px rgba(var(--p-rgb),.35); }
}
[data-testid="stExpander"]{
  background:rgba(255,255,255,.03); border:1px solid rgba(var(--p-rgb),.2) !important; border-radius:10px;
}

[data-testid="stChatMessage"]{
  background:linear-gradient(135deg, rgba(255,255,255,.05), rgba(255,255,255,.015));
  border:1px solid rgba(var(--p-rgb),.18); border-left:3px solid var(--p);
  border-radius:12px; backdrop-filter:blur(6px);
}

.hero{ position:relative; z-index:1; padding:8px 0 18px; }
.glitch{
  font-family:'Bebas Neue',sans-serif !important; font-size:64px; letter-spacing:6px;
  color:var(--txt); position:relative; display:inline-block; line-height:1;
  text-shadow:0 0 24px rgba(var(--p-rgb),.55);
}
.glitch::before, .glitch::after{
  content:attr(data-text); position:absolute; left:0; top:0; width:100%; overflow:hidden;
}
.glitch::before{ color:var(--p); transform:translate(2px,0); clip-path:inset(0 0 60% 0); animation:gl1 4.5s infinite steps(1); }
.glitch::after{ color:var(--s); transform:translate(-2px,0); clip-path:inset(60% 0 0 0); animation:gl2 4.5s infinite steps(1); }
@keyframes gl1{ 0%,92%,100%{ transform:translate(0,0); } 93%{ transform:translate(4px,-2px);} 95%{ transform:translate(-3px,1px);} 97%{ transform:translate(2px,0);} }
@keyframes gl2{ 0%,90%,100%{ transform:translate(0,0); } 91%{ transform:translate(-4px,2px);} 94%{ transform:translate(3px,-1px);} 96%{ transform:translate(-2px,0);} }
.tagline{ color:var(--muted); font-size:16px; margin-top:6px; }
.chips{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
.chip{
  display:inline-flex; align-items:center; gap:8px; padding:5px 12px; border-radius:999px;
  background:rgba(var(--p-rgb),.08); border:1px solid rgba(var(--p-rgb),.3);
  font-size:13px; color:var(--txt);
}
.dot{ width:8px; height:8px; border-radius:50%; background:#2dd36f; box-shadow:0 0 8px #2dd36f; animation:blink 1.6s infinite; }
@keyframes blink{ 50%{ opacity:.3; } }

.stats{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:18px 0; position:relative; z-index:1; }
.stat{
  padding:14px 18px; border-radius:12px; background:rgba(255,255,255,.035);
  border:1px solid rgba(var(--p-rgb),.2);
}
.stat b{ font-family:'Bebas Neue',sans-serif; font-size:36px; letter-spacing:2px; color:var(--p); display:block; line-height:1.05; }
.stat small{ color:var(--muted); }

.empty{
  position:relative; z-index:1; margin-top:40px; padding:46px 20px; text-align:center;
  border:1px dashed rgba(var(--p-rgb),.35); border-radius:16px; background:rgba(255,255,255,.02);
}
.empty .big{ font-size:64px; animation:float 3.2s ease-in-out infinite; filter:drop-shadow(0 0 18px rgba(var(--p-rgb),.7)); }
@keyframes float{ 50%{ transform:translateY(-10px); } }

.proc{
  position:relative; z-index:1; display:grid; grid-template-columns:170px 1fr; gap:26px; align-items:center;
  padding:22px 26px; border-radius:16px; overflow:hidden;
  background:linear-gradient(135deg, rgba(var(--p-rgb),.08), rgba(0,0,0,.35));
  border:1px solid rgba(var(--p-rgb),.4); box-shadow:0 0 40px rgba(var(--p-rgb),.15);
}
.proc::after{
  content:""; position:absolute; left:0; right:0; height:70px; top:-70px; pointer-events:none;
  background:linear-gradient(180deg, transparent, rgba(var(--p-rgb),.16), transparent);
  animation:scan 2.6s linear infinite;
}
@keyframes scan{ to{ top:110%; } }
.radar{
  position:relative; width:150px; height:150px; border-radius:50%;
  border:2px solid rgba(var(--p-rgb),.7);
  background:repeating-radial-gradient(circle, transparent 0 17px, rgba(var(--p-rgb),.22) 18px 19px);
  box-shadow:0 0 30px rgba(var(--p-rgb),.4), inset 0 0 30px rgba(var(--p-rgb),.2);
}
.radar::before{
  content:""; position:absolute; inset:0; border-radius:50%;
  background:conic-gradient(from 0deg, rgba(var(--p-rgb),.65), transparent 35%);
  animation:spin 2s linear infinite;
}
.radar::after{
  content:""; position:absolute; inset:0; border-radius:50%;
  background:
    linear-gradient(rgba(var(--p-rgb),.35),rgba(var(--p-rgb),.35)) center/1px 100% no-repeat,
    linear-gradient(rgba(var(--p-rgb),.35),rgba(var(--p-rgb),.35)) center/100% 1px no-repeat;
}
.radar .core{
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-size:46px; z-index:2; animation:corepulse 1.4s ease-in-out infinite;
  filter:drop-shadow(0 0 14px rgba(var(--p-rgb),.9));
}
@keyframes spin{ to{ transform:rotate(360deg); } }
@keyframes corepulse{ 50%{ transform:scale(1.18); } }
.proc h3{ font-family:'Bebas Neue',sans-serif !important; letter-spacing:3px; font-size:28px; margin:0 0 2px; color:var(--p); }
.proc .sub{ color:var(--muted); font-size:14px; margin-bottom:12px; }
.bar{ height:6px; border-radius:6px; background:rgba(255,255,255,.08); overflow:hidden; margin-bottom:14px; }
.bar i{
  display:block; height:100%; border-radius:6px; transition:width .6s ease;
  background:linear-gradient(90deg, var(--s), var(--p), var(--s)); background-size:200% 100%;
  animation:shimmer 1.2s linear infinite;
}
@keyframes shimmer{ to{ background-position:-200% 0; } }
.steps{ display:grid; gap:7px; }
.step{ display:flex; align-items:center; gap:12px; font-size:15px; color:var(--muted); transition:color .3s; }
.step .ic{
  width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
  border:1px solid rgba(255,255,255,.2); font-size:12px;
}
.step.done{ color:var(--txt); }
.step.done .ic{ background:var(--p); border-color:var(--p); color:#000; font-weight:800; }
.step.active{ color:var(--p); font-weight:600; }
.step.active .ic{ border:2px solid transparent; border-top-color:var(--p); border-right-color:var(--p); animation:spin .7s linear infinite; }
.step.active::after{ content:"…"; animation:blink 1s infinite; }
.compact{ grid-template-columns:100px 1fr; padding:14px 18px; }
.compact .radar{ width:90px; height:90px; }
.compact .radar .core{ font-size:30px; }
.compact h3{ font-size:22px; }

.ok{
  position:relative; z-index:1; padding:14px 18px; border-radius:12px; color:var(--txt);
  background:rgba(45,211,111,.1); border:1px solid rgba(45,211,111,.5);
  animation:pop .5s cubic-bezier(.2,1.4,.4,1);
}
@keyframes pop{ from{ transform:scale(.9); opacity:0; } to{ transform:scale(1); opacity:1; } }

.srcchip{
  display:block; margin:5px 0; padding:6px 10px; font-size:12.5px; border-radius:8px;
  background:rgba(var(--p-rgb),.08); border:1px solid rgba(var(--p-rgb),.22);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.arch{ font-size:13px; line-height:1.9; color:var(--txt); }
.arch b{ color:var(--p); }

@media (max-width:760px){
  .glitch{ font-size:40px; } .stats{ grid-template-columns:1fr; } .proc{ grid-template-columns:1fr; justify-items:center; }
}
@media (prefers-reduced-motion:reduce){
  *{ animation:none !important; transition:none !important; }
}
</style>
"""

def darken(hex_color: str, f: float = 0.72) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))

st.markdown(
    CSS.replace("%PRGB%", T["p_rgb"]).replace("%PDARK%", darken(T["p"]))
    .replace("%P%", T["p"]).replace("%S%", T["s"])
    .replace("%BG2%", T["bg2"]).replace("%BG%", T["bg"]),
    unsafe_allow_html=True,
)

# floating particles
random.seed(7)
spans = "".join(
    f'<span style="left:{random.randint(0, 100)}%;animation-duration:{random.randint(9, 20)}s;'
    f'animation-delay:{random.randint(0, 12)}s"></span>'
    for _ in range(22)
)
st.markdown(f'<div class="particles">{spans}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# REAL BACKEND INTEGRATION HELPERS
# ----------------------------------------------------------------------------
def loader_html(title, sub, stages, active, compact=False, done_all=False):
    n = len(stages)
    done_count = n if done_all else active
    pct = int((done_count + (0 if done_all else 0.5)) / n * 100)
    rows = ""
    for i, label in enumerate(stages):
        cls = "done" if (done_all or i < active) else ("active" if i == active else "")
        icon = "✓" if cls == "done" else ""
        rows += f'<div class="step {cls}"><span class="ic">{icon}</span>{label}</div>'
    return h(f"""
    <div class="proc {'compact' if compact else ''}">
      <div class="radar"><div class="core">{T['emoji']}</div></div>
      <div>
        <h3>{title}</h3>
        <div class="sub">{sub}</div>
        <div class="bar"><i style="width:{min(pct, 100)}%"></i></div>
        <div class="steps">{rows}</div>
      </div>
    </div>
    """)

def run_with_animation(slot, title, sub, stages, fn, step_seconds=1.6, compact=False):
    """Run fn() in a thread while advancing the animated pipeline."""
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn)
        i, last_render, t0 = 0, -1, time.time()
        while not fut.done():
            i = min(int((time.time() - t0) / step_seconds), len(stages) - 1)
            if i != last_render:
                slot.markdown(loader_html(title, sub, stages, i, compact), unsafe_allow_html=True)
                last_render = i
            time.sleep(0.15)
        result = fut.result()
    slot.markdown(loader_html(title, sub, stages, len(stages), compact, done_all=True), unsafe_allow_html=True)
    time.sleep(0.5)
    return result

# ---- REAL N8N DATA INGESTION LOGIC ----
def call_ingest(url):
    if not N8N_WEBHOOK_URL:
        return False, "N8N_WEBHOOK_URL missing in .env"
    try:
        response = requests.post(N8N_WEBHOOK_URL, json={"url": url}, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            n8n_data = response.json()
            raw_text = n8n_data.get("text", "")
            
            if isinstance(raw_text, list):
                scraped_text = " ".join([str(item) for item in raw_text if item])
            else:
                scraped_text = str(raw_text)
            
            if scraped_text.strip():
                chunk_size = 1000
                text_chunks = [scraped_text[i:i+chunk_size] for i in range(0, len(scraped_text), chunk_size)]
                urls = [url] * len(text_chunks)
                
                # Saving to local ChromaDB
                add_to_knowledge_base(text_chunks, urls)
                return True, "Data securely vectorized and embedded into ChromaDB."
            else:
                return False, "n8n returned empty data. Check HTML Extract node."
        else:
            return False, f"HTTP Error {response.status_code} from n8n."
    except Exception as e: 
        return False, f"Ingestion connection failed: {e}"

# ---- REAL GEMINI RAG QUERY LOGIC ----
def call_chat(question):
    try:
        # Fetching real answer from our backend
        answer = query_assistant(question)
        return True, answer
    except Exception as e:
        return False, f"System Error: {e}"

def typewriter(slot, text):
    words = text.split(" ")
    delay = min(0.03, 3.0 / max(len(words), 1))
    out = ""
    for w in words:
        out += w + " "
        slot.markdown(out + "▌")
        time.sleep(delay)
    slot.markdown(text)

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"## {T['emoji']} Data Ingestion Node")
    st.divider()
    url = st.text_input("Target website URL", placeholder="https://en.wikipedia.org/wiki/...")
    ingest_clicked = st.button("🚀  Process & inject to vector DB")

    if ss.sources:
        st.markdown("**Loaded sources**")
        st.markdown("".join(f'<span class="srcchip">🔗 {s}</span>' for s in ss.sources[-5:]), unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️  Clear context memory"):
        ss.messages, ss.queries, ss.sid = [], 0, str(uuid.uuid4())
        st.toast("Memory wiped. Fresh session started.", icon="🧹")
        st.rerun()

    with st.expander("⚙️  System architecture"):
        st.markdown(
            h(f"""
            <div class="arch">
            <b>Streamlit</b> UI<br>↓ webhook<br>
            <b>n8n</b> workflow (scrape · clean · chunk)<br>↓<br>
            <b>{MODEL_LABEL}</b> embeddings<br>↓<br>
            <b>ChromaDB</b> vector store<br>↓<br>
            <b>{MODEL_LABEL}</b> agent + session memory
            </div>
            """),
            unsafe_allow_html=True,
        )
    mode = "LIVE" if N8N_WEBHOOK_URL else "DISCONNECTED"
    st.caption(f"Status: {mode}  ·  Session {ss.sid[:8]}")

# ----------------------------------------------------------------------------
# HERO + STATS
# ----------------------------------------------------------------------------
st.markdown(
    h(f"""
    <div class="hero">
      <div class="glitch" data-text="NEXUS RESEARCH AI">NEXUS RESEARCH AI</div>
      <div class="tagline">{T['tag']}</div>
      <div class="chips">
        <span class="chip"><span class="dot"></span>n8n online</span>
        <span class="chip"><span class="dot"></span>ChromaDB connected</span>
        <span class="chip"><span class="dot"></span>{MODEL_LABEL} ready</span>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><b>{len(ss.sources)}</b><small>Sources in vector DB</small></div>
      <div class="stat"><b>{ss.queries}</b><small>Queries answered</small></div>
      <div class="stat"><b>{len(ss.messages)}</b><small>Messages in memory</small></div>
    </div>
    """),
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# INGEST FLOW
# ----------------------------------------------------------------------------
if ingest_clicked:
    if not url.strip().startswith("http"):
        st.toast("Enter a valid URL starting with http(s)://", icon="⚠️")
    else:
        slot = st.empty()
        ok, msg = run_with_animation(
            slot,
            "INGESTING TARGET",
            url.strip(),
            ["Infiltrating target URL", "Extracting and cleaning content", "Chunking the knowledge",
             f"Embedding with {MODEL_LABEL}", "Sealing vectors into ChromaDB"],
            lambda: call_ingest(url.strip()),
            step_seconds=1.8,
        )
        if ok:
            ss.sources.append(url.strip())
            slot.markdown(f'<div class="ok">✅ <b>Source locked in.</b> {msg} Ask your first question below.</div>',
                          unsafe_allow_html=True)
            st.balloons() if T["key"] == "spider" else st.snow()
        else:
            slot.error(msg)

# ----------------------------------------------------------------------------
# CHAT
# ----------------------------------------------------------------------------
if not ss.messages and not ingest_clicked:
    st.markdown(
        f'<div class="empty"><div class="big">{T["emoji"]}</div>'
        f'<h3 style="margin:10px 0 4px">Awaiting target</h3><div style="color:var(--muted)">{T["empty"]}</div></div>',
        unsafe_allow_html=True,
    )

for m in ss.messages:
    with st.chat_message(m["role"], avatar=T["user_avatar"] if m["role"] == "user" else T["ai_avatar"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Query the vectorized knowledge base..."):
    ss.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=T["user_avatar"]):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=T["ai_avatar"]):
        slot = st.empty()
        
        # Real animation followed by real backend response
        ok, answer = run_with_animation(
            slot,
            "ANALYZING",
            "Searching your knowledge base",
            ["Recalling session memory", "Similarity search in ChromaDB", f"{MODEL_LABEL} reasoning",
             "Composing answer"],
            lambda: call_chat(prompt),
            step_seconds=1.3,
            compact=True,
        )
        if ok:
            typewriter(slot, answer)
            ss.queries += 1
        else:
            slot.error(answer)
            
    ss.messages.append({"role": "assistant", "content": answer})
    st.rerun()