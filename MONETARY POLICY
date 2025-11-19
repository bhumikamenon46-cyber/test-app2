import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# -------------------------------------------
# PAGE CONFIG
# -------------------------------------------
st.set_page_config(
    page_title="RBI Monetary Policy Risk Dashboard",
    layout="wide",
    page_icon="📊"
)

# -------------------------------------------
# STYLING
# -------------------------------------------
st.markdown("""
<style>
body {
    background-color: #f7f7f7;
}
.big-title {
    font-size: 32px;
    font-weight: 800;
    padding-bottom: 10px;
}
.section-header {
    font-size: 22px;
    font-weight: 600;
    margin-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------
# GENERATE SYNTHETIC DATA
# -------------------------------------------
def generate_data():
    dates = pd.date_range("2015-01-01", periods=130, freq="M")

    df = pd.DataFrame({
        "date": dates,
        "gdp_index": 100 + np.random.normal(0, 2, len(dates)).cumsum(),
        "cpi": 4 + np.random.normal(0, 0.1, len(dates)).cumsum(),
        "unemployment": 7 - np.random.normal(0, 0.05, len(dates)).cumsum(),
        "credit_growth": 6 + np.random.normal(0, 0.2, len(dates)).cumsum(),
        "m2_growth": 8 + np.random.normal(0, 0.1, len(dates)).cumsum(),
        "stock_index": 900 + np.random.normal(0, 20, len(dates)).cumsum(),
        "yield_10y": 6.5 + np.random.normal(0, 0.05, len(dates)).cumsum(),
        "exchange_rate": 68 + np.random.normal(0, 0.2, len(dates)).cumsum(),
    })

    df.set_index("date", inplace=True)
    return df

df = generate_data()

# -------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------
st.sidebar.header("🔧 Controls")
interest_shock = st.sidebar.slider("Interest Rate Increase (bps)", 0, 300, 100)
liquidity_shock = st.sidebar.slider("Liquidity Increase (%)", 0.0, 10.0, 2.0)
inflation_shock = st.sidebar.slider("Inflation Increase (%)", 0.0, 5.0, 1.0)

# -------------------------------------------
# APPLY SHOCKS
# -------------------------------------------
def apply_interest_shock(df, shock):
    df = df.copy()
    df["yield_10y"] += shock / 100
    df["gdp_index"] *= (1 - shock / 500)
    df["credit_growth"] *= (1 - shock / 400)
    df["stock_index"] *= (1 - shock / 300)
    return df

def apply_liquidity_shock(df, shock):
    df = df.copy()
    df["m2_growth"] += shock
    df["credit_growth"] += shock * 0.5
    df["cpi"] += shock * 0.1
    df["stock_index"] *= (1 + shock * 0.03)
    return df

def apply_inflation_shock(df, shock):
    df = df.copy()
    df["cpi"] += shock
    df["yield_10y"] += shock * 0.5
    df["gdp_index"] *= (1 - shock / 200)
    df["stock_index"] *= (1 - shock / 250)
    return df

sc_interest = apply_interest_shock(df, interest_shock)
sc_liquidity = apply_liquidity_shock(df, liquidity_shock)
sc_inflation = apply_inflation_shock(df, inflation_shock)

# -------------------------------------------
# RISK SCORE (Simple, Clean Version)
# -------------------------------------------
def risk_score(base, sc):
    # percent change of latest point
    pct = ((sc.iloc[-1] - base.iloc[-1]) / (base.iloc[-1] + 1e-9)) * 100
    score = np.mean(np.abs(pct.values))  # average % deviation
    return min(100, round(score, 1))

score_interest = risk_score(df, sc_interest)
score_liquidity = risk_score(df, sc_liquidity)
score_inflation = risk_score(df, sc_inflation)

# -------------------------------------------
# TITLE
# -------------------------------------------
st.markdown("<div class='big-title'>📊 RBI Monetary Policy Risk Dashboard</div>", unsafe_allow_html=True)
st.write("This dashboard simulates monetary policy shocks and shows how macroeconomic indicators respond.")

# -------------------------------------------
# RISKOMETER GAUGES
# -------------------------------------------
col1, col2, col3 = st.columns(3)

def gauge(label, value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 33], "color": "lightgreen"},
                {"range": [33, 66], "color": "yellow"},
                {"range": [66, 100], "color": "red"},
            ],
        },
        title={"text": label}
    ))
    st.plotly_chart(fig, use_container_width=True)

with col1:
    gauge("Interest Rate Hike Risk", score_interest)
with col2:
    gauge("Liquidity Injection Risk", score_liquidity)
with col3:
    gauge("Inflation Shock Risk", score_inflation)

# -------------------------------------------
# TIME-SERIES VISUALIZATION
# -------------------------------------------
st.markdown("<div class='section-header'>📈 Indicator Comparison</div>", unsafe_allow_html=True)

indicator = st.selectbox("Choose Indicator", df.columns)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df[indicator], name="Baseline"))
fig.add_trace(go.Scatter(x=sc_interest.index, y=sc_interest[indicator], name="Interest Shock"))
fig.add_trace(go.Scatter(x=sc_liquidity.index, y=sc_liquidity[indicator], name="Liquidity Shock"))
fig.add_trace(go.Scatter(x=sc_inflation.index, y=sc_inflation[indicator], name="Inflation Shock"))
fig.update_layout(height=400)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------
# COMPARISON TABLE
# -------------------------------------------
st.markdown("<div class='section-header'>📊 Latest Values Comparison</div>", unsafe_allow_html=True)

latest = pd.DataFrame({
    "Baseline": df.iloc[-1],
    "Interest Shock": sc_interest.iloc[-1],
    "Liquidity Shock": sc_liquidity.iloc[-1],
    "Inflation Shock": sc_inflation.iloc[-1]
})

st.dataframe(latest.style.format("{:.2f}"))

