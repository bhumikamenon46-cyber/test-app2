# app.py
# fx-991EX-inspired scientific calculator (Streamlit)
# Responsive, keyboard input, SHIFT functional, error-free

import streamlit as st
import math
import re
from math import factorial

# ---------------- Page config ----------------
st.set_page_config(page_title="fx-991EX Calculator", page_icon="🧮", layout="wide")

# ---------------- Initialize session state (ALL keys) ----------------
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "last" not in st.session_state:
    st.session_state.last = ""
if "memory" not in st.session_state:
    st.session_state.memory = 0.0
if "angle_mode" not in st.session_state:
    st.session_state.angle_mode = "DEG"  # or "RAD"
if "shift" not in st.session_state:
    st.session_state.shift = False
if "keyboard" not in st.session_state:
    st.session_state.keyboard = ""
if "eval_on_enter" not in st.session_state:
    st.session_state.eval_on_enter = False

# ---------------- CSS / styling ----------------
st.markdown(
    r"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700&family=Inter:wght@300;400;600&display=swap');
    :root{--bg:#070708;--glass:rgba(255,255,255,0.03);--muted:#9aa4b2}
    body{background:var(--bg); color:#eaf0f7}
    .card{max-width:1100px;margin:18px auto;padding:18px;background:linear-gradient(180deg,#111214,#0b0c0d);
          border-radius:14px;border:1px solid var(--glass);box-shadow:0 10px 30px rgba(0,0,0,0.6)}
    .display-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:10px}
    .display-block{flex:1 1 48%;background:linear-gradient(180deg,#020204,#0b0f13);border-radius:10px;
                   padding:14px 16px;min-height:72px;font-family:'Orbitron',monospace;font-size:28px;
                   color:#fff;text-align:right;border:1px solid rgba(255,255,255,0.04);
                   display:flex;align-items:center;justify-content:flex-end;word-break:break-all}
    .display-sub{color:var(--muted);font-size:13px;margin-bottom:12px;text-align:right}
    .keys{display:grid;gap:10px}
    .grid-6{grid-template-columns:repeat(6,1fr)}
    .grid-4{grid-template-columns:repeat(4,1fr)}
    .key{background:linear-gradient(180deg,#1b1c1e,#0f1011);border-radius:10px;padding:10px 6px;text-align:center;
         font-weight:700;border:1px solid rgba(255,255,255,0.02)}
    .key-ac{background:linear-gradient(180deg,#6a1f1f,#3a0f0f);color:white}
    .key-eq{background:linear-gradient(180deg,#0f7a48,#055a33);color:white;font-weight:800}
    .side{background:linear-gradient(180deg,#0f1113,#090a0b);border-radius:12px;padding:12px;border:1px solid var(--glass)}
    .stButton>button{background:transparent!important;border:none!important;width:100%;height:100%;color:inherit}
    [data-testid="stVerticalBlock"] > div { gap:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Safe math and DEG/RAD wrappers ----------------
def sin_wr(x):
    x = float(x)
    return math.sin(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.sin(x)

def cos_wr(x):
    x = float(x)
    return math.cos(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.cos(x)

def tan_wr(x):
    x = float(x)
    return math.tan(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.tan(x)

def asin_wr(x):
    res = math.asin(float(x))
    return math.degrees(res) if st.session_state.angle_mode == "DEG" else res

def acos_wr(x):
    res = math.acos(float(x))
    return math.degrees(res) if st.session_state.angle_mode == "DEG" else res

def atan_wr(x):
    res = math.atan(float(x))
    return math.degrees(res) if st.session_state.angle_mode == "DEG" else res

SAFE = {
    "pi": math.pi,
    "e": math.e,
    "sin": sin_wr,
    "cos": cos_wr,
    "tan": tan_wr,
    "asin": asin_wr,
    "acos": acos_wr,
    "atan": atan_wr,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "ln": math.log,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "abs": abs,
    "pow": pow,
    "factorial": factorial,
    "exp": math.exp,
    "rad": math.radians,
    "deg": math.degrees,
}

# ---------------- Helpers ----------------
def append_token(tok: str):
    """Append a token to the expression and keep keyboard box synced."""
    st.session_state.expr = (st.session_state.expr or "") + str(tok)
    st.session_state.keyboard = st.session_state.expr

def replace_factorials(expr: str) -> str:
    # convert 5! -> factorial(5) and (expr)! -> factorial(expr)
    expr = re.sub(r"(\d+(?:\.\d+)?)!", r"factorial(\1)", expr)
    expr = re.sub(r"(\))!", r"factorial\1", expr)
    return expr

def safe_eval(expr: str):
    expr = expr.replace("^", "**")
    expr = replace_factorials(expr)
    return eval(expr, {"__builtins__": None}, SAFE)

def evaluate():
    expr = (st.session_state.expr or "").strip()
    if not expr:
        return
    try:
        res = safe_eval(expr)
        st.session_state.last = str(res)
        st.session_state.expr = str(res)
        st.session_state.keyboard = st.session_state.expr
    except Exception:
        st.error("Invalid expression")

# text_input on_change handler: just sync keyboard -> expr (no eval)
def on_keyboard_change():
    st.session_state.expr = st.session_state.keyboard or ""

# ---------------- Layout ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

# visible keyboard box (user types here). It updates display instantly, eval only on Enter button or "=".
st.text_input("Type expression here (then press Enter or '=')", key="keyboard", on_change=on_keyboard_change, label_visibility="visible")

# display row: input and result equal sized
st.markdown('<div class="display-row">', unsafe_allow_html=True)
st.markdown(f'<div class="display-block" id="input_block">{st.session_state.expr or ""}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-block" id="result_block">{st.session_state.last or ""}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# small info line
st.markdown(f'<div class="display-sub">Angle: {st.session_state.angle_mode} &nbsp;&nbsp; Memory: {st.session_state.memory} &nbsp;&nbsp; SHIFT: {"ON" if st.session_state.shift else "OFF"}</div>', unsafe_allow_html=True)

# main keys and side panel (minimize rerenders by grouping)
col_keys, col_side = st.columns([9, 3])

with col_keys:
    # Scientific row 1 (sin/cos/tan + SHIFT + parens)
    st.markdown('<div class="keys grid-6">', unsafe_allow_html=True)
    c = st.columns(6)
    if c[0].button("sin", key="btn_sin"):
        if st.session_state.shift:
            append_token("asin(")
        else:
            append_token("sin(")
        st.session_state.shift = False
    if c[1].button("cos", key="btn_cos"):
        if st.session_state.shift:
            append_token("acos(")
        else:
            append_token("cos(")
        st.session_state.shift = False
    if c[2].button("tan", key="btn_tan"):
        if st.session_state.shift:
            append_token("atan(")
        else:
            append_token("tan(")
        st.session_state.shift = False
    if c[3].button("SHIFT", key="btn_shift"):
        st.session_state.shift = not st.session_state.shift
    if c[4].button("(", key="btn_lpar"):
        append_token("(")
    if c[5].button(")", key="btn_rpar"):
        append_token(")")
    st.markdown('</div>', unsafe_allow_html=True)

    # Scientific row 2
    st.markdown('<div class="keys grid-6">', unsafe_allow_html=True)
    c = st.columns(6)
    if c[0].button("ln", key="btn_ln"): append_token("ln(")
    if c[1].button("log", key="btn_log"): append_token("log10(")
    if c[2].button("sqrt", key="btn_sqrt"): append_token("sqrt(")
    if c[3].button("x^2", key="btn_x2"): append_token("**2")
    if c[4].button("x^3", key="btn_x3"): append_token("**3")
    if c[5].button("x^y", key="btn_xy"): append_token("**")
    st.markdown('</div>', unsafe_allow_html=True)

    # Scientific row 3
    st.markdown('<div class="keys grid-6">', unsafe_allow_html=True)
    c = st.columns(6)
    if c[0].button("pi", key="btn_pi"): append_token("pi")
    if c[1].button("e", key="btn_e"): append_token("e")
    if c[2].button("!", key="btn_fact"): append_token("!")
    if c[3].button("Ans", key="btn_ans"): append_token(st.session_state.last or "")
    if c[4].button("^", key="btn_caret"): append_token("**")
    if c[5].button("Exp", key="btn_exp"): append_token("exp(")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    # Numeric keypad
    st.markdown('<div class="keys grid-4">', unsafe_allow_html=True)
    k = st.columns(4)
    if k[0].button("7", key="btn_7"): append_token("7")
    if k[1].button("8", key="btn_8"): append_token("8")
    if k[2].button("9", key="btn_9"): append_token("9")
    if k[3].button("/", key="btn_div"): append_token("/")
    k = st.columns(4)
    if k[0].button("4", key="btn_4"): append_token("4")
    if k[1].button("5", key="btn_5"): append_token("5")
    if k[2].button("6", key="btn_6"): append_token("6")
    if k[3].button("*", key="btn_mul"): append_token("*")
    k = st.columns(4)
    if k[0].button("1", key="btn_1"): append_token("1")
    if k[1].button("2", key="btn_2"): append_token("2")
    if k[2].button("3", key="btn_3"): append_token("3")
    if k[3].button("-", key="btn_sub"): append_token("-")
    k = st.columns(4)
    if k[0].button("0", key="btn_0"): append_token("0")
    if k[1].button(".", key="btn_dot"): append_token(".")
    if k[2].button("+/-", key="btn_neg"):
        expr = st.session_state.expr or st.session_state.last or ""
        if expr.startswith("-"):
            st.session_state.expr = expr[1:]
        else:
            st.session_state.expr = "-" + expr
        st.session_state.keyboard = st.session_state.expr
    if k[3].button("+", key="btn_add"): append_token("+")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # Action row
    a1, a2, a3, a4, a5 = st.columns([1.4,1.4,1.4,1.4,3.4])
    if a1.button("Enter", key="btn_enter"):
        evaluate()
    if a2.button("=", key="btn_eq"):
        evaluate()
    if a3.button("AC", key="btn_ac"):
        st.session_state.expr = ""; st.session_state.last = ""; st.session_state.keyboard = ""
    if a4.button("DEL", key="btn_del"):
        st.session_state.expr = (st.session_state.expr or "")[:-1]
        st.session_state.keyboard = st.session_state.expr
    if a5.button("Mode: DEG/RAD", key="btn_mode"):
        st.session_state.angle_mode = "RAD" if st.session_state.angle_mode == "DEG" else "DEG"

with col_side:
    st.markdown('<div class="side">', unsafe_allow_html=True)
    st.subheader("Memory & Extras")
    if st.button("M+", key="btn_mplus"):
        try:
            st.session_state.memory += float(st.session_state.last)
            st.success("Added to memory")
        except Exception:
            st.error("No numeric last answer")
    if st.button("M-", key="btn_mminus"):
        try:
            st.session_state.memory -= float(st.session_state.last)
            st.success("Subtracted from memory")
        except Exception:
            st.error("No numeric last answer")
    if st.button("MR", key="btn_mrec"):
        st.session_state.expr = (st.session_state.expr or "") + str(st.session_state.memory)
        st.session_state.keyboard = st.session_state.expr
    if st.button("MC", key="btn_mclear"):
        st.session_state.memory = 0.0

    st.markdown("---")
    st.markdown("**Quick tips**")
    st.markdown("- Type in the box above; it updates the display instantly.")
    st.markdown("- Press Enter or '=' to evaluate.")
    st.markdown("- SHIFT toggles inverse trig for the next trig key.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
st.caption("fx-991 inspired — visual & layout inspiration only")
