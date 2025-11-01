# app.py
# fx-991MS-inspired Scientific Calculator (Streamlit)
# Theme: classic grey + green display, dark keys, Exact CASIO SHIFT behaviour

import streamlit as st
import math
import re
from math import factorial

# ---------- Page ----------
st.set_page_config(page_title="Casio fx-991MS - Streamlit", page_icon="🧮", layout="wide")

# ---------- Session state init ----------
if "expr" not in st.session_state: st.session_state.expr = ""
if "ans" not in st.session_state: st.session_state.ans = ""
if "memory" not in st.session_state: st.session_state.memory = 0.0
if "angle_mode" not in st.session_state: st.session_state.angle_mode = "DEG"  # DEG default like physical calc
if "shift" not in st.session_state: st.session_state.shift = False
if "keyboard" not in st.session_state: st.session_state.keyboard = ""
if "eval_on_enter" not in st.session_state: st.session_state.eval_on_enter = True

# ---------- CSS (fx-991MS grey + green display) ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700&family=Inter:wght@300;400;600&display=swap');
    :root{
      --bg:#ececec;
      --panel:#d7d7d7;
      --key:#9aa0a6;
      --key-dark:#7f8489;
      --display-bg:#031006;
      --display-text:#a6ffcc;
      --muted:#333;
    }
    body { background: linear-gradient(180deg,#f2f3f5,#e6e8ea); color: #111; font-family: Inter, sans-serif; }
    .calculator { max-width: 980px; margin: 20px auto; }
    .card { background: linear-gradient(180deg,#cfcfcf,#bfbfbf); border-radius: 14px; padding: 18px; box-shadow: 0 8px 30px rgba(0,0,0,0.15); border:1px solid rgba(0,0,0,0.06); }
    .brand { font-family: Orbitron, monospace; color:#264653; font-weight:700; letter-spacing:2px; font-size:20px; text-align:center; margin-bottom:6px; }
    .model { text-align:center; color: #37474F; margin-bottom:12px; font-size:13px; }

    /* Display row - two equal blocks responsive */
    .display-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:10px; }
    .display-block {
      flex:1 1 48%;
      background: linear-gradient(180deg,#05110a,#021007);
      border-radius:10px;
      padding: 12px 14px;
      min-height:72px;
      color: var(--display-text);
      text-align:right;
      font-family: 'Orbitron', monospace;
      font-size:28px;
      border: 2px solid rgba(0,0,0,0.2);
      box-shadow: inset 0 -6px 14px rgba(0,0,0,0.45);
      display:flex; align-items:center; justify-content:flex-end; word-break:break-all;
    }
    .display-sub { color:#42504f; font-size:13px; text-align:right; margin-bottom:10px; }

    /* Buttons */
    .keys { display:grid; gap:8px; }
    .grid-6 { grid-template-columns: repeat(6, 1fr); display:grid; gap:8px; }
    .grid-4 { grid-template-columns: repeat(4, 1fr); display:grid; gap:8px; }
    .stButton>button {
      background: linear-gradient(180deg,var(--key),var(--key-dark));
      color: #fff;
      border-radius:8px;
      height:54px;
      border:1px solid rgba(0,0,0,0.15);
      font-weight:700;
      font-size:16px;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.15); }
    .btn-shift { background: linear-gradient(180deg,#f4d35e,#e6b800) !important; color: #111 !important; }
    .btn-ac { background: linear-gradient(180deg,#b34a4a,#8b2e2e) !important; color:#fff !important; }
    .btn-eq { background: linear-gradient(180deg,#2e8b57,#1b6a40) !important; color:#fff !important; font-weight:800; }
    .small-note { font-size:12px; color:#2f3a36; margin-top:8px; text-align:center; }

    /* tighten streamlit vertical spacing */
    [data-testid="stVerticalBlock"] > div { gap:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Safe math environment ----------
def _sin(x):
    x = float(x)
    return math.sin(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.sin(x)

def _cos(x):
    x = float(x)
    return math.cos(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.cos(x)

def _tan(x):
    x = float(x)
    return math.tan(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.tan(x)

def _asin(x):
    r = math.asin(float(x))
    return math.degrees(r) if st.session_state.angle_mode == "DEG" else r

def _acos(x):
    r = math.acos(float(x))
    return math.degrees(r) if st.session_state.angle_mode == "DEG" else r

def _atan(x):
    r = math.atan(float(x))
    return math.degrees(r) if st.session_state.angle_mode == "DEG" else r

SAFE = {
    "pi": math.pi, "e": math.e,
    "sin": _sin, "cos": _cos, "tan": _tan,
    "asin": _asin, "acos": _acos, "atan": _atan,
    "sqrt": math.sqrt, "ln": math.log, "log": math.log10,
    "abs": abs, "pow": pow, "factorial": factorial, "exp": math.exp
}

def replace_factorials(expr: str) -> str:
    # 5! -> factorial(5), (expr)! -> factorial(expr)
    expr = re.sub(r"(\d+(?:\.\d+)?)!", r"factorial(\1)", expr)
    expr = re.sub(r"(\))!", r"factorial\1", expr)
    return expr

def safe_eval(expr: str):
    expr = expr.replace("^", "**")
    expr = expr.replace("×", "*").replace("÷", "/")
    expr = replace_factorials(expr)
    return eval(expr, {"__builtins__": None}, SAFE)

# ---------- Helpers ----------
def append_token(tok: str):
    # only update expr here; keyboard input will sync separately
    st.session_state.expr = (st.session_state.expr or "") + str(tok)

def evaluate_expr():
    expr = (st.session_state.expr or "").strip()
    if not expr:
        return
    try:
        res = safe_eval(expr)
        # format display: if integer-like show int
        if isinstance(res, float) and abs(res - round(res)) < 1e-10:
            res = int(round(res))
        st.session_state.ans = str(res)
        st.session_state.expr = str(res)
    except ZeroDivisionError:
        st.session_state.ans = "Error: /0"
    except Exception:
        st.session_state.ans = "Error"

# text_input handler - sync keyboard to expr, optionally evaluate on Enter
def on_text_submit():
    # streamlit calls on Enter (submit) or when text_input loses focus after change
    st.session_state.expr = st.session_state.keyboard or ""
    # If user wants auto-eval on Enter, evaluate:
    if st.session_state.eval_on_enter:
        evaluate_expr()

# ---------- Layout ----------
st.markdown('<div class="calculator">', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="brand">CASIO</div><div class="model">fx-991MS — Scientific Calculator (inspired)</div>', unsafe_allow_html=True)

# keyboard input field (user types here). Press Enter to submit (and evaluate if eval_on_enter True)
st.text_input("Type here (press Enter to submit)", key="keyboard", on_change=on_text_submit, label_visibility="visible")

# display: two equal blocks (input left, result right)
st.markdown('<div class="display-row">', unsafe_allow_html=True)
st.markdown(f'<div class="display-block" id="display_input">{st.session_state.expr or "&nbsp;"}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-block" id="display_result">{st.session_state.ans or "&nbsp;"}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div class="display-sub">Angle: {st.session_state.angle_mode} &nbsp;&nbsp; Memory: {st.session_state.memory} &nbsp;&nbsp; SHIFT: {"ON" if st.session_state.shift else "OFF"}</div>', unsafe_allow_html=True)

# ---------- Buttons (unique keys) ----------
# layout similar to fx-991MS grouping but simplified for screen
buttons = [
    ["SHIFT", "ALPHA", "MODE", "DEL", "AC", "ANS"],
    ["sin", "cos", "tan", "ln", "log", "√"],
    ["(", ")", "^", "EXP", "×", "÷"],
    ["7", "8", "9", "-", "π", "e"],
    ["4", "5", "6", "+", "!", "Ans"],
    ["1", "2", "3", "x^2", "x^3", "%"],
    ["0", ".", "+/-", "=", "", ""],
]

# render buttons grid with 6 columns per row
for row_idx, row in enumerate(buttons):
    cols = st.columns(len(row))
    for col_idx, label in enumerate(row):
        if not label:
            cols[col_idx].markdown("")  # empty slot
            continue
        # style classes for special buttons
        btn_kwargs = {}
        # unique key: include row and col indices
        key = f"btn_r{row_idx}_c{col_idx}_{label}"
        if label == "SHIFT":
            # yellowish like physical
            if cols[col_idx].button(label, key=key):
                st.session_state.shift = True
        elif label == "AC":
            if cols[col_idx].button(label, key=key):
                st.session_state.expr = ""
                st.session_state.ans = ""
        elif label == "DEL":
            if cols[col_idx].button(label, key=key):
                st.session_state.expr = (st.session_state.expr or "")[:-1]
        elif label == "=":
            if cols[col_idx].button(label, key=key):
                evaluate_expr()
        elif label == "ALPHA":
            # decorative in this build (could be implemented later)
            if cols[col_idx].button(label, key=key):
                # toggling alpha for visuals only
                st.session_state.alpha = not st.session_state.get("alpha", False)
        else:
            # normal calculator buttons with SHIFT-aware alternate for trig and sqrt etc.
            if cols[col_idx].button(label, key=key):
                # SHIFT functional behaviour: pressing SHIFT then a key uses alternate function, then auto-reset SHIFT
                if st.session_state.shift:
                    # mapping for alternate functions when SHIFT is active
                    alt_map = {
                        "sin": "asin(", "cos": "acos(", "tan": "atan(", "ln": "exp(", "log": "10**(", "√": "sqrt(",
                        "x^2": "**2", "x^3": "**3"
                    }
                    tok = alt_map.get(label)
                    if tok:
                        append_token(tok)
                    else:
                        # if no alt mapping, just append normal label
                        append_token(label)
                    st.session_state.shift = False
                else:
                    # normal behavior
                    # map display labels to expression tokens
                    token_map = {
                        "×": "*", "÷": "/", "x^2": "**2", "x^3": "**3", "π": "pi", "Ans": st.session_state.ans or "",
                        "+/-": "-", "%": "/100"
                    }
                    if label in token_map:
                        append_token(token_map[label])
                    elif label == "π" or label == "pi":
                        append_token("pi")
                    elif label == "e":
                        append_token("e")
                    elif label == "√":
                        append_token("sqrt(")
                    elif label == "!":
                        append_token("!")
                    elif label == "EXP":
                        append_token("exp(")
                    elif label == "+/-":
                        # toggle sign of current expression (simple heuristic)
                        expr = st.session_state.expr or ""
                        if expr.startswith("-"):
                            st.session_state.expr = expr[1:]
                        else:
                            st.session_state.expr = "-" + expr
                    else:
                        append_token(label)

# ---------- Side actions: Memory & mode ----------
st.markdown('<div style="margin-top:10px; padding-top:8px; border-top:1px solid rgba(0,0,0,0.08)">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
if c1.button("M+ (add last)", key="mem_add"):
    try:
        st.session_state.memory += float(st.session_state.ans)
    except Exception:
        pass
if c2.button("M- (sub last)", key="mem_sub"):
    try:
        st.session_state.memory -= float(st.session_state.ans)
    except Exception:
        pass
if c3.button("MR (recall)", key="mem_rec"):
    st.session_state.expr = (st.session_state.expr or "") + str(st.session_state.memory)
if c4.button("MC (clear)", key="mem_clear"):
    st.session_state.memory = 0.0

# mode toggle for DEG / RAD
m1, m2 = st.columns(2)
if m1.button("Mode: DEG", key="mode_deg"):
    st.session_state.angle_mode = "DEG"
if m2.button("Mode: RAD", key="mode_rad"):
    st.session_state.angle_mode = "RAD"

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Tip: type in the box above; press Enter or "=" to evaluate. SHIFT is exact-CASIO: press SHIFT then a key for its alternate function.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
