{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww28900\viewh18100\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # ANZ Signal - Improved Streamlit MVP\
# Run with:\
#   pip install streamlit pandas numpy matplotlib\
#   streamlit run anz_signal_streamlit_app.py\
\
import streamlit as st\
import pandas as pd\
import numpy as np\
import matplotlib.pyplot as plt\
from datetime import datetime\
\
st.set_page_config(page_title="ANZ Signal", layout="wide")\
\
# -------------------------------------------------\
# MOCK DATA\
# -------------------------------------------------\
clients_data = [\
    \{\
        "client": "Southern Export Co",\
        "industry": "Agribusiness",\
        "fx_pair": "NZD/USD",\
        "fx_exposure_nzd": 8_500_000,\
        "rate_sensitivity": "High",\
        "debt_nzd": 12_000_000,\
        "risk_level": "High",\
    \},\
    \{\
        "client": "Pacific Imports Ltd",\
        "industry": "Retail",\
        "fx_pair": "NZD/AUD",\
        "fx_exposure_nzd": 4_200_000,\
        "rate_sensitivity": "Medium",\
        "debt_nzd": 7_000_000,\
        "risk_level": "Medium",\
    \},\
    \{\
        "client": "Harbour Infrastructure Group",\
        "industry": "Infrastructure",\
        "fx_pair": "NZD/USD",\
        "fx_exposure_nzd": 15_000_000,\
        "rate_sensitivity": "High",\
        "debt_nzd": 25_000_000,\
        "risk_level": "High",\
    \},\
    \{\
        "client": "Kiwi Consumer Brands",\
        "industry": "Consumer Goods",\
        "fx_pair": "NZD/CNY",\
        "fx_exposure_nzd": 3_000_000,\
        "rate_sensitivity": "Low",\
        "debt_nzd": 4_000_000,\
        "risk_level": "Low",\
    \},\
    \{\
        "client": "Tasman Food Group",\
        "industry": "Food & Beverage",\
        "fx_pair": "NZD/USD",\
        "fx_exposure_nzd": 6_300_000,\
        "rate_sensitivity": "Medium",\
        "debt_nzd": 9_500_000,\
        "risk_level": "Medium",\
    \},\
]\
\
market_data = [\
    \{"instrument": "NZD/USD", "price": 0.6021, "daily_change_pct": -1.3\},\
    \{"instrument": "NZD/AUD", "price": 0.9215, "daily_change_pct": 0.6\},\
    \{"instrument": "NZD/CNY", "price": 4.3600, "daily_change_pct": -0.9\},\
    \{"instrument": "2Y Swap", "price": 4.82, "daily_change_pct": 0.18\},\
    \{"instrument": "10Y Swap", "price": 5.07, "daily_change_pct": 0.10\},\
]\
\
events_data = [\
    \{\
        "event": "US inflation came in above expectations",\
        "category": "Macro",\
        "severity": "High",\
        "likely_market_effect": "USD strengthens, NZD/USD weakens, rates stay elevated",\
    \},\
    \{\
        "event": "China manufacturing data softened",\
        "category": "Macro",\
        "severity": "Medium",\
        "likely_market_effect": "Pressure on NZD/CNY-sensitive trade flows",\
    \},\
    \{\
        "event": "RBNZ signalled caution on future cuts",\
        "category": "Central Bank",\
        "severity": "Medium",\
        "likely_market_effect": "NZ interest rates may remain higher for longer",\
    \},\
]\
\
clients_df = pd.DataFrame(clients_data)\
market_df = pd.DataFrame(market_data)\
events_df = pd.DataFrame(events_data)\
\
# -------------------------------------------------\
# SYNTHETIC PRICE HISTORY FOR CHARTS\
# -------------------------------------------------\
np.random.seed(7)\
\
\
def build_history(base_price: float, days: int = 30, drift: float = 0.0, noise: float = 0.006) -> pd.DataFrame:\
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days)\
    rets = np.random.normal(loc=drift, scale=noise, size=days)\
    prices = [base_price]\
    for r in rets[1:]:\
        prices.append(prices[-1] * (1 + r))\
    return pd.DataFrame(\{"date": dates, "price": prices\})\
\
\
history_map = \{\
    "NZD/USD": build_history(0.6021, drift=-0.0002, noise=0.008),\
    "NZD/AUD": build_history(0.9215, drift=0.0001, noise=0.004),\
    "NZD/CNY": build_history(4.3600, drift=-0.0001, noise=0.005),\
    "2Y Swap": build_history(4.82, drift=0.0003, noise=0.003),\
    "10Y Swap": build_history(5.07, drift=0.0002, noise=0.0025),\
\}\
\
# -------------------------------------------------\
# HELPERS\
# -------------------------------------------------\
\
def generate_alerts(clients: pd.DataFrame, market: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:\
    alerts = []\
    market_lookup = \{row["instrument"]: row for _, row in market.iterrows()\}\
\
    for _, client in clients.iterrows():\
        fx_pair = client["fx_pair"]\
        exposure = client["fx_exposure_nzd"]\
        risk = client["risk_level"]\
        rate_sensitivity = client["rate_sensitivity"]\
\
        if fx_pair in market_lookup:\
            move = market_lookup[fx_pair]["daily_change_pct"]\
            est_value_move = exposure * (abs(move) / 100)\
\
            if abs(move) >= 0.8:\
                if move < 0:\
                    direction_text = f"\{fx_pair\} fell \{abs(move):.1f\}% today"\
                else:\
                    direction_text = f"\{fx_pair\} rose \{abs(move):.1f\}% today"\
\
                suggestion = "Review hedge position"\
                if fx_pair == "NZD/USD":\
                    suggestion = "Consider forward FX hedge"\
                elif fx_pair == "NZD/AUD":\
                    suggestion = "Check natural hedge or short-dated cover"\
                elif fx_pair == "NZD/CNY":\
                    suggestion = "Review supplier timing and hedge options"\
\
                alerts.append(\
                    \{\
                        "client": client["client"],\
                        "alert_type": "FX Move",\
                        "priority": risk,\
                        "message": f"\{direction_text\}; estimated exposure impact \uc0\u8776  NZD \{est_value_move:,.0f\}",\
                        "suggested_action": suggestion,\
                    \}\
                )\
\
        two_year_swap_change = market_lookup.get("2Y Swap", \{\}).get("daily_change_pct", 0)\
        if rate_sensitivity == "High" and two_year_swap_change >= 0.15:\
            alerts.append(\
                \{\
                    "client": client["client"],\
                    "alert_type": "Rates",\
                    "priority": "High",\
                    "message": f"Short-end rates moved higher; debt exposure \uc0\u8776  NZD \{client['debt_nzd']:,.0f\}",\
                    "suggested_action": "Discuss fixed/floating debt mix",\
                \}\
            )\
\
    for _, event in events.iterrows():\
        if event["severity"] == "High":\
            impacted_clients = clients[clients["fx_pair"] == "NZD/USD"]["client"].tolist()\
            for name in impacted_clients:\
                alerts.append(\
                    \{\
                        "client": name,\
                        "alert_type": "Macro Event",\
                        "priority": "High",\
                        "message": event["event"],\
                        "suggested_action": "Prepare proactive client call",\
                    \}\
                )\
\
    order = \{"High": 0, "Medium": 1, "Low": 2\}\
    alerts_df = pd.DataFrame(alerts)\
    if not alerts_df.empty:\
        alerts_df["priority_rank"] = alerts_df["priority"].map(order)\
        alerts_df = alerts_df.sort_values(["priority_rank", "client"]).drop(columns="priority_rank")\
    return alerts_df\
\
\
\
def explain_in_plain_english(alert_row: pd.Series) -> str:\
    return (\
        f"For \{alert_row['client']\}, this signal suggests a meaningful change in financial exposure. "\
        f"The issue is: \{alert_row['message']\}. "\
        f"A practical next step would be to \{alert_row['suggested_action'].lower()\}."\
    )\
\
\
\
def risk_score(row: pd.Series) -> int:\
    risk_points = \{"Low": 1, "Medium": 2, "High": 3\}[row["risk_level"]]\
    rate_points = \{"Low": 1, "Medium": 2, "High": 3\}[row["rate_sensitivity"]]\
    exposure_points = 3 if row["fx_exposure_nzd"] >= 10_000_000 else 2 if row["fx_exposure_nzd"] >= 5_000_000 else 1\
    return risk_points + rate_points + exposure_points\
\
\
clients_df["risk_score"] = clients_df.apply(risk_score, axis=1)\
alerts_df = generate_alerts(clients_df, market_df, events_df)\
\
# -------------------------------------------------\
# SIDEBAR\
# -------------------------------------------------\
st.sidebar.title("ANZ Signal")\
st.sidebar.caption("Institutional intelligence dashboard")\
selected_pairs = st.sidebar.multiselect(\
    "Filter FX pairs",\
    options=sorted(clients_df["fx_pair"].unique().tolist()),\
    default=sorted(clients_df["fx_pair"].unique().tolist()),\
)\
selected_risks = st.sidebar.multiselect(\
    "Filter risk levels",\
    options=["High", "Medium", "Low"],\
    default=["High", "Medium", "Low"],\
)\
\
filtered_clients = clients_df[\
    clients_df["fx_pair"].isin(selected_pairs) & clients_df["risk_level"].isin(selected_risks)\
]\
filtered_alerts = alerts_df[alerts_df["client"].isin(filtered_clients["client"])] if not alerts_df.empty else alerts_df\
\
# -------------------------------------------------\
# HEADER\
# -------------------------------------------------\
st.title("ANZ Signal")\
st.caption("Prototype for proactive institutional banking insights")\
\
m1, m2, m3, m4 = st.columns(4)\
m1.metric("Clients Tracked", len(filtered_clients))\
m2.metric("FX Exposure", f"NZD \{filtered_clients['fx_exposure_nzd'].sum():,.0f\}")\
m3.metric("Debt Exposure", f"NZD \{filtered_clients['debt_nzd'].sum():,.0f\}")\
m4.metric("Active Alerts", len(filtered_alerts))\
\
st.markdown("---")\
\
# -------------------------------------------------\
# TOP CHARTS\
# -------------------------------------------------\
left, right = st.columns(2)\
\
with left:\
    st.subheader("Client FX Exposure")\
    fig, ax = plt.subplots(figsize=(8, 4))\
    exposure_chart = filtered_clients.sort_values("fx_exposure_nzd", ascending=True)\
    ax.barh(exposure_chart["client"], exposure_chart["fx_exposure_nzd"])\
    ax.set_xlabel("NZD Exposure")\
    ax.set_ylabel("Client")\
    ax.set_title("Exposure by Client")\
    st.pyplot(fig)\
\
with right:\
    st.subheader("Exposure by Currency Pair")\
    fig, ax = plt.subplots(figsize=(8, 4))\
    pair_totals = filtered_clients.groupby("fx_pair", as_index=False)["fx_exposure_nzd"].sum()\
    ax.bar(pair_totals["fx_pair"], pair_totals["fx_exposure_nzd"])\
    ax.set_xlabel("FX Pair")\
    ax.set_ylabel("NZD Exposure")\
    ax.set_title("Total Exposure by FX Pair")\
    st.pyplot(fig)\
\
st.markdown("---")\
\
tab1, tab2, tab3, tab4, tab5 = st.tabs([\
    "Overview",\
    "Client Drilldown",\
    "Markets",\
    "Events & Alerts",\
    "Relationship Manager Mode",\
])\
\
# -------------------------------------------------\
# TAB 1 - OVERVIEW\
# -------------------------------------------------\
with tab1:\
    c1, c2 = st.columns(2)\
\
    with c1:\
        st.subheader("Risk Score by Client")\
        fig, ax = plt.subplots(figsize=(8, 4))\
        risk_chart = filtered_clients.sort_values("risk_score", ascending=True)\
        ax.barh(risk_chart["client"], risk_chart["risk_score"])\
        ax.set_xlabel("Risk Score")\
        ax.set_ylabel("Client")\
        ax.set_title("Who Needs Attention Most")\
        st.pyplot(fig)\
\
    with c2:\
        st.subheader("Debt vs FX Exposure")\
        fig, ax = plt.subplots(figsize=(8, 4))\
        ax.scatter(filtered_clients["debt_nzd"], filtered_clients["fx_exposure_nzd"])\
        for _, row in filtered_clients.iterrows():\
            ax.annotate(row["client"], (row["debt_nzd"], row["fx_exposure_nzd"]), fontsize=8)\
        ax.set_xlabel("Debt (NZD)")\
        ax.set_ylabel("FX Exposure (NZD)")\
        ax.set_title("Balance Sheet Sensitivity Snapshot")\
        st.pyplot(fig)\
\
    st.subheader("Client Table")\
    st.dataframe(\
        filtered_clients[[\
            "client", "industry", "fx_pair", "fx_exposure_nzd", "debt_nzd", "rate_sensitivity", "risk_level", "risk_score"\
        ]],\
        use_container_width=True,\
    )\
\
# -------------------------------------------------\
# TAB 2 - CLIENT DRILLDOWN\
# -------------------------------------------------\
with tab2:\
    st.subheader("Client Drilldown")\
    selected_client = st.selectbox("Select a client", filtered_clients["client"].tolist())\
    client_row = filtered_clients[filtered_clients["client"] == selected_client].iloc[0]\
\
    a, b, c, d = st.columns(4)\
    a.metric("FX Pair", client_row["fx_pair"])\
    b.metric("FX Exposure", f"NZD \{client_row['fx_exposure_nzd']:,.0f\}")\
    c.metric("Debt", f"NZD \{client_row['debt_nzd']:,.0f\}")\
    d.metric("Risk Score", int(client_row["risk_score"]))\
\
    st.write(f"**Industry:** \{client_row['industry']\}")\
    st.write(f"**Risk Level:** \{client_row['risk_level']\}")\
    st.write(f"**Rate Sensitivity:** \{client_row['rate_sensitivity']\}")\
\
    fig, ax = plt.subplots(figsize=(9, 4))\
    pair_history = history_map[client_row["fx_pair"]]\
    ax.plot(pair_history["date"], pair_history["price"])\
    ax.set_title(f"30-Day Trend: \{client_row['fx_pair']\}")\
    ax.set_xlabel("Date")\
    ax.set_ylabel("Price")\
    plt.xticks(rotation=45)\
    st.pyplot(fig)\
\
    st.info(\
        f"\{client_row['client']\} is primarily exposed to \{client_row['fx_pair']\} movements. "\
        f"This client has \{client_row['risk_level'].lower()\} overall risk and \{client_row['rate_sensitivity'].lower()\} rate sensitivity."\
    )\
\
# -------------------------------------------------\
# TAB 3 - MARKETS\
# -------------------------------------------------\
with tab3:\
    st.subheader("Market Dashboard")\
    selected_instrument = st.selectbox("Select an instrument", market_df["instrument"].tolist())\
\
    i1, i2 = st.columns([1, 2])\
    with i1:\
        row = market_df[market_df["instrument"] == selected_instrument].iloc[0]\
        st.metric("Current Price", row["price"], delta=f"\{row['daily_change_pct']\}% today")\
        st.dataframe(market_df, use_container_width=True)\
\
    with i2:\
        fig, ax = plt.subplots(figsize=(9, 4))\
        hist = history_map[selected_instrument]\
        ax.plot(hist["date"], hist["price"])\
        ax.set_title(f"30-Day Price Trend: \{selected_instrument\}")\
        ax.set_xlabel("Date")\
        ax.set_ylabel("Price")\
        plt.xticks(rotation=45)\
        st.pyplot(fig)\
\
    st.write("### Quick Market Read")\
    for _, row in market_df.iterrows():\
        direction = "up" if row["daily_change_pct"] > 0 else "down"\
        st.write(f"- \{row['instrument']\} is \{direction\} \{abs(row['daily_change_pct']):.2f\}% today")\
\
# -------------------------------------------------\
# TAB 4 - EVENTS & ALERTS\
# -------------------------------------------------\
with tab4:\
    st.subheader("Event Impact Engine")\
    st.dataframe(events_df, use_container_width=True)\
\
    event_choice = st.selectbox("Choose an event to assess", events_df["event"].tolist())\
    event_row = events_df[events_df["event"] == event_choice].iloc[0]\
\
    st.write(f"**Category:** \{event_row['category']\}")\
    st.write(f"**Severity:** \{event_row['severity']\}")\
    st.write(f"**Likely Market Effect:** \{event_row['likely_market_effect']\}")\
\
    impacted = []\
    if "USD" in event_row["likely_market_effect"]:\
        impacted = filtered_clients[filtered_clients["fx_pair"] == "NZD/USD"]["client"].tolist()\
    elif "NZD/CNY" in event_row["likely_market_effect"]:\
        impacted = filtered_clients[filtered_clients["fx_pair"] == "NZD/CNY"]["client"].tolist()\
\
    if impacted:\
        st.warning("Likely impacted clients:")\
        for name in impacted:\
            st.write(f"- \{name\}")\
    else:\
        st.success("No directly mapped client exposure found in this prototype.")\
\
    st.subheader("Triggered Alerts")\
    if filtered_alerts.empty:\
        st.success("No alerts triggered.")\
    else:\
        fig, ax = plt.subplots(figsize=(8, 4))\
        priority_counts = filtered_alerts["priority"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)\
        ax.bar(priority_counts.index, priority_counts.values)\
        ax.set_xlabel("Priority")\
        ax.set_ylabel("Number of Alerts")\
        ax.set_title("Alert Mix")\
        st.pyplot(fig)\
\
        st.dataframe(filtered_alerts, use_container_width=True)\
\
# -------------------------------------------------\
# TAB 5 - RELATIONSHIP MANAGER MODE\
# -------------------------------------------------\
with tab5:\
    st.subheader("Relationship Manager Mode")\
    if filtered_alerts.empty:\
        st.info("No current alerts to explain.")\
    else:\
        selected_alert_idx = st.number_input(\
            "Choose alert row number",\
            min_value=0,\
            max_value=max(len(filtered_alerts.reset_index(drop=True)) - 1, 0),\
            value=0,\
            step=1,\
        )\
        alert_row = filtered_alerts.reset_index(drop=True).iloc[selected_alert_idx]\
\
        st.write("### Plain-English Explanation")\
        st.info(explain_in_plain_english(alert_row))\
\
        st.write("### Suggested Talking Point")\
        st.write(\
            f"\{alert_row['client']\} may be affected by current market conditions. "\
            f"We should \{alert_row['suggested_action'].lower()\} and contact them proactively."\
        )\
\
        st.write("### Recommended Action Card")\
        st.success(\
            f"Priority: \{alert_row['priority']\} | Type: \{alert_row['alert_type']\}\\n\\n"\
            f"Issue: \{alert_row['message']\}\\n\\n"\
            f"Action: \{alert_row['suggested_action']\}"\
        )\
\
st.markdown("---")\
st.caption(f"Prototype generated at \{datetime.now().strftime('%Y-%m-%d %H:%M:%S')\}")\
}