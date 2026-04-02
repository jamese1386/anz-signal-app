import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="ANZ Signal", layout="wide")

# -----------------------------
# PAGE STYLING
# -----------------------------
st.markdown(
    """
    <style>
        .main {
            background-color: #f6f8fb;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .hero {
            background: linear-gradient(135deg, #0b1f33 0%, #14395b 100%);
            padding: 1.4rem 1.6rem;
            border-radius: 18px;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        }
        .hero h1 {
            margin: 0;
            font-size: 2rem;
        }
        .hero p {
            margin: 0.35rem 0 0 0;
            color: #d9e4ef;
            font-size: 0.98rem;
        }
        .section-card {
            background: white;
            padding: 1rem 1rem 0.5rem 1rem;
            border-radius: 16px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
            border: 1px solid #e7edf3;
            margin-bottom: 1rem;
        }
        .insight-box {
            background: #eef4fa;
            padding: 0.9rem 1rem;
            border-radius: 12px;
            border-left: 5px solid #14395b;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .stMetric {
            background: white;
            border: 1px solid #e7edf3;
            padding: 0.5rem;
            border-radius: 14px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# MOCK DATA
# -----------------------------
clients_data = [
    {
        "client": "Southern Export Co",
        "industry": "Agribusiness",
        "relationship_manager": "R. Dykes",
        "fx_pair": "NZD/USD",
        "fx_exposure_nzd": 8_500_000,
        "debt_nzd": 12_000_000,
        "rate_sensitivity": "High",
        "risk_level": "High",
        "region": "South Island",
    },
    {
        "client": "Pacific Imports Ltd",
        "industry": "Retail",
        "relationship_manager": "J. Morgan",
        "fx_pair": "NZD/AUD",
        "fx_exposure_nzd": 4_200_000,
        "debt_nzd": 7_000_000,
        "rate_sensitivity": "Medium",
        "risk_level": "Medium",
        "region": "North Island",
    },
    {
        "client": "Harbour Infrastructure Group",
        "industry": "Infrastructure",
        "relationship_manager": "R. Dykes",
        "fx_pair": "NZD/USD",
        "fx_exposure_nzd": 15_000_000,
        "debt_nzd": 25_000_000,
        "rate_sensitivity": "High",
        "risk_level": "High",
        "region": "Upper North Island",
    },
    {
        "client": "Kiwi Consumer Brands",
        "industry": "Consumer Goods",
        "relationship_manager": "S. Patel",
        "fx_pair": "NZD/CNY",
        "fx_exposure_nzd": 3_000_000,
        "debt_nzd": 4_000_000,
        "rate_sensitivity": "Low",
        "risk_level": "Low",
        "region": "North Island",
    },
    {
        "client": "Tasman Food Group",
        "industry": "Food & Beverage",
        "relationship_manager": "A. Chen",
        "fx_pair": "NZD/USD",
        "fx_exposure_nzd": 6_300_000,
        "debt_nzd": 9_500_000,
        "rate_sensitivity": "Medium",
        "risk_level": "Medium",
        "region": "South Island",
    },
    {
        "client": "Southern Logistics Network",
        "industry": "Transport",
        "relationship_manager": "R. Dykes",
        "fx_pair": "NZD/AUD",
        "fx_exposure_nzd": 5_400_000,
        "debt_nzd": 11_200_000,
        "rate_sensitivity": "High",
        "risk_level": "Medium",
        "region": "South Island",
    },
]

market_data = [
    {"instrument": "NZD/USD", "price": 0.6021, "daily_change_pct": -1.3},
    {"instrument": "NZD/AUD", "price": 0.9215, "daily_change_pct": 0.6},
    {"instrument": "NZD/CNY", "price": 4.3600, "daily_change_pct": -0.9},
    {"instrument": "2Y Swap", "price": 4.82, "daily_change_pct": 0.18},
    {"instrument": "10Y Swap", "price": 5.07, "daily_change_pct": 0.10},
]

events_data = [
    {
        "event": "US inflation came in above expectations",
        "category": "Macro",
        "severity": "High",
        "likely_market_effect": "USD strengthens, NZD/USD weakens, rates stay elevated",
    },
    {
        "event": "China manufacturing data softened",
        "category": "Macro",
        "severity": "Medium",
        "likely_market_effect": "Pressure on NZD/CNY-sensitive trade flows",
    },
    {
        "event": "RBNZ signalled caution on future cuts",
        "category": "Central Bank",
        "severity": "Medium",
        "likely_market_effect": "NZ interest rates may remain higher for longer",
    },
]

clients_df = pd.DataFrame(clients_data)
market_df = pd.DataFrame(market_data)
events_df = pd.DataFrame(events_data)

# -----------------------------
# SYNTHETIC HISTORY FOR CHARTS
# -----------------------------
np.random.seed(7)


def build_history(base_price: float, days: int = 30, drift: float = 0.0, noise: float = 0.006) -> pd.DataFrame:
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days)
    returns = np.random.normal(loc=drift, scale=noise, size=days)
    prices = [base_price]
    for r in returns[1:]:
        prices.append(prices[-1] * (1 + r))
    return pd.DataFrame({"date": dates, "price": prices})


history_map = {
    "NZD/USD": build_history(0.6021, drift=-0.0002, noise=0.008),
    "NZD/AUD": build_history(0.9215, drift=0.0001, noise=0.004),
    "NZD/CNY": build_history(4.3600, drift=-0.0001, noise=0.005),
    "2Y Swap": build_history(4.82, drift=0.0003, noise=0.003),
    "10Y Swap": build_history(5.07, drift=0.0002, noise=0.0025),
}

# -----------------------------
# HELPERS
# -----------------------------

def risk_score(row: pd.Series) -> int:
    risk_points = {"Low": 1, "Medium": 2, "High": 3}[row["risk_level"]]
    rate_points = {"Low": 1, "Medium": 2, "High": 3}[row["rate_sensitivity"]]
    exposure_points = 3 if row["fx_exposure_nzd"] >= 10_000_000 else 2 if row["fx_exposure_nzd"] >= 5_000_000 else 1
    return risk_points + rate_points + exposure_points


def generate_alerts(clients: pd.DataFrame, market: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    alerts = []
    market_lookup = {row["instrument"]: row for _, row in market.iterrows()}

    for _, client in clients.iterrows():
        fx_pair = client["fx_pair"]
        exposure = client["fx_exposure_nzd"]
        risk = client["risk_level"]
        rate_sensitivity = client["rate_sensitivity"]

        if fx_pair in market_lookup:
            move = market_lookup[fx_pair]["daily_change_pct"]
            if abs(move) >= 0.8:
                est_value_move = exposure * (abs(move) / 100)
                direction_text = f"{fx_pair} fell {abs(move):.1f}% today" if move < 0 else f"{fx_pair} rose {abs(move):.1f}% today"
                suggestion = "Review hedge position"
                if fx_pair == "NZD/USD":
                    suggestion = "Consider forward FX hedge"
                elif fx_pair == "NZD/AUD":
                    suggestion = "Check natural hedge or short-dated cover"
                elif fx_pair == "NZD/CNY":
                    suggestion = "Review supplier timing and hedge options"

                alerts.append(
                    {
                        "client": client["client"],
                        "alert_type": "FX Move",
                        "priority": risk,
                        "message": f"{direction_text}; estimated exposure impact ≈ NZD {est_value_move:,.0f}",
                        "suggested_action": suggestion,
                    }
                )

        two_year_change = market_lookup.get("2Y Swap", {}).get("daily_change_pct", 0)
        if rate_sensitivity == "High" and two_year_change >= 0.15:
            alerts.append(
                {
                    "client": client["client"],
                    "alert_type": "Rates",
                    "priority": "High",
                    "message": f"Short-end rates moved higher; debt exposure ≈ NZD {client['debt_nzd']:,.0f}",
                    "suggested_action": "Discuss fixed/floating debt mix",
                }
            )

    for _, event in events.iterrows():
        if event["severity"] == "High":
            impacted_clients = clients[clients["fx_pair"] == "NZD/USD"]["client"].tolist()
            for name in impacted_clients:
                alerts.append(
                    {
                        "client": name,
                        "alert_type": "Macro Event",
                        "priority": "High",
                        "message": event["event"],
                        "suggested_action": "Prepare proactive client call",
                    }
                )

    alerts_df = pd.DataFrame(alerts)
    if not alerts_df.empty:
        order = {"High": 0, "Medium": 1, "Low": 2}
        alerts_df["priority_rank"] = alerts_df["priority"].map(order)
        alerts_df = alerts_df.sort_values(["priority_rank", "client"]).drop(columns="priority_rank")
    return alerts_df


def plain_english(alert_row: pd.Series) -> str:
    return (
        f"For {alert_row['client']}, this signal suggests a meaningful change in financial exposure. "
        f"The issue is: {alert_row['message']}. "
        f"A sensible next step would be to {alert_row['suggested_action'].lower()}."
    )


clients_df["risk_score"] = clients_df.apply(risk_score, axis=1)
alerts_df = generate_alerts(clients_df, market_df, events_df)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("ANZ Signal")
st.sidebar.caption("Institutional Intelligence Dashboard")

selected_pairs = st.sidebar.multiselect(
    "Currency Pair",
    options=sorted(clients_df["fx_pair"].unique().tolist()),
    default=sorted(clients_df["fx_pair"].unique().tolist()),
)

selected_risks = st.sidebar.multiselect(
    "Risk Level",
    options=["High", "Medium", "Low"],
    default=["High", "Medium", "Low"],
)

selected_region = st.sidebar.multiselect(
    "Region",
    options=sorted(clients_df["region"].unique().tolist()),
    default=sorted(clients_df["region"].unique().tolist()),
)

filtered_clients = clients_df[
    clients_df["fx_pair"].isin(selected_pairs)
    & clients_df["risk_level"].isin(selected_risks)
    & clients_df["region"].isin(selected_region)
]

filtered_alerts = alerts_df[alerts_df["client"].isin(filtered_clients["client"])] if not alerts_df.empty else alerts_df

# -----------------------------
# HERO
# -----------------------------
st.markdown(
    f"""
    <div class='hero'>
        <h1>ANZ Signal</h1>
        <p>Proactive institutional insights across client exposures, market movements, and relationship actions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Clients Tracked", len(filtered_clients))
col2.metric("FX Exposure", f"NZD {filtered_clients['fx_exposure_nzd'].sum():,.0f}")
col3.metric("Debt Exposure", f"NZD {filtered_clients['debt_nzd'].sum():,.0f}")
col4.metric("Active Alerts", len(filtered_alerts))

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Executive Snapshot")
summary_text = "Highest concentration remains in NZD/USD-linked clients, with rate-sensitive balance sheets creating a strong case for proactive outreach and hedge review."
st.markdown(f"<div class='insight-box'>{summary_text}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# TOP CHARTS
# -----------------------------
left, right = st.columns(2)

with left:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Client FX Exposure")
    fig, ax = plt.subplots(figsize=(8, 4))
    exposure_chart = filtered_clients.sort_values("fx_exposure_nzd", ascending=True)
    ax.barh(exposure_chart["client"], exposure_chart["fx_exposure_nzd"])
    ax.set_xlabel("NZD Exposure")
    ax.set_ylabel("Client")
    ax.set_title("Exposure by Client")
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Exposure by Currency Pair")
    fig, ax = plt.subplots(figsize=(8, 4))
    pair_totals = filtered_clients.groupby("fx_pair", as_index=False)["fx_exposure_nzd"].sum()
    ax.bar(pair_totals["fx_pair"], pair_totals["fx_exposure_nzd"])
    ax.set_xlabel("FX Pair")
    ax.set_ylabel("NZD Exposure")
    ax.set_title("Total Exposure by Pair")
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Portfolio View",
    "Client Drilldown",
    "Markets & Events",
    "Relationship Manager Mode",
])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Risk Score by Client")
        fig, ax = plt.subplots(figsize=(8, 4))
        risk_chart = filtered_clients.sort_values("risk_score", ascending=True)
        ax.barh(risk_chart["client"], risk_chart["risk_score"])
        ax.set_xlabel("Risk Score")
        ax.set_ylabel("Client")
        ax.set_title("Priority Ranking")
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Debt vs FX Exposure")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(filtered_clients["debt_nzd"], filtered_clients["fx_exposure_nzd"])
        for _, row in filtered_clients.iterrows():
            ax.annotate(row["client"], (row["debt_nzd"], row["fx_exposure_nzd"]), fontsize=8)
        ax.set_xlabel("Debt (NZD)")
        ax.set_ylabel("FX Exposure (NZD)")
        ax.set_title("Balance Sheet Sensitivity")
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Portfolio Table")
    st.dataframe(
        filtered_clients[[
            "client",
            "industry",
            "relationship_manager",
            "region",
            "fx_pair",
            "fx_exposure_nzd",
            "debt_nzd",
            "rate_sensitivity",
            "risk_level",
            "risk_score",
        ]],
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Client Drilldown")

    selected_client = st.selectbox("Select a client", filtered_clients["client"].tolist())
    client_row = filtered_clients[filtered_clients["client"] == selected_client].iloc[0]

    a, b, c, d = st.columns(4)
    a.metric("FX Pair", client_row["fx_pair"])
    b.metric("FX Exposure", f"NZD {client_row['fx_exposure_nzd']:,.0f}")
    c.metric("Debt", f"NZD {client_row['debt_nzd']:,.0f}")
    d.metric("Risk Score", int(client_row["risk_score"]))

    st.write(f"**Industry:** {client_row['industry']}")
    st.write(f"**Relationship Manager:** {client_row['relationship_manager']}")
    st.write(f"**Region:** {client_row['region']}")
    st.write(f"**Risk Level:** {client_row['risk_level']}")
    st.write(f"**Rate Sensitivity:** {client_row['rate_sensitivity']}")

    fig, ax = plt.subplots(figsize=(9, 4))
    pair_history = history_map[client_row["fx_pair"]]
    ax.plot(pair_history["date"], pair_history["price"])
    ax.set_title(f"30-Day Trend: {client_row['fx_pair']}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.markdown(
        f"<div class='insight-box'>{client_row['client']} is most exposed to {client_row['fx_pair']} movements. Current balance sheet mix suggests priority monitoring for treasury and relationship teams.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Market Dashboard")
        selected_instrument = st.selectbox("Select an instrument", market_df["instrument"].tolist())
        row = market_df[market_df["instrument"] == selected_instrument].iloc[0]
        st.metric("Current Price", row["price"], delta=f"{row['daily_change_pct']}% today")
        st.dataframe(market_df, use_container_width=True)

        fig, ax = plt.subplots(figsize=(8, 4))
        hist = history_map[selected_instrument]
        ax.plot(hist["date"], hist["price"])
        ax.set_title(f"30-Day Trend: {selected_instrument}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Event Impact Engine")
        st.dataframe(events_df, use_container_width=True)
        chosen_event = st.selectbox("Choose an event", events_df["event"].tolist())
        event_row = events_df[events_df["event"] == chosen_event].iloc[0]

        st.write(f"**Category:** {event_row['category']}")
        st.write(f"**Severity:** {event_row['severity']}")
        st.write(f"**Likely Market Effect:** {event_row['likely_market_effect']}")

        impacted = []
        if "USD" in event_row["likely_market_effect"]:
            impacted = filtered_clients[filtered_clients["fx_pair"] == "NZD/USD"]["client"].tolist()
        elif "NZD/CNY" in event_row["likely_market_effect"]:
            impacted = filtered_clients[filtered_clients["fx_pair"] == "NZD/CNY"]["client"].tolist()

        if impacted:
            st.warning("Likely impacted clients:")
            for name in impacted:
                st.write(f"- {name}")
        else:
            st.success("No directly mapped client exposure found in this prototype.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Triggered Alerts")
    if filtered_alerts.empty:
        st.success("No alerts triggered.")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        priority_counts = filtered_alerts["priority"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
        ax.bar(priority_counts.index, priority_counts.values)
        ax.set_xlabel("Priority")
        ax.set_ylabel("Number of Alerts")
        ax.set_title("Alert Mix")
        st.pyplot(fig)
        st.dataframe(filtered_alerts, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Relationship Manager Mode")
    if filtered_alerts.empty:
        st.info("No current alerts to explain.")
    else:
        selected_alert_idx = st.number_input(
            "Choose alert row number",
            min_value=0,
            max_value=max(len(filtered_alerts.reset_index(drop=True)) - 1, 0),
            value=0,
            step=1,
        )
        alert_row = filtered_alerts.reset_index(drop=True).iloc[selected_alert_idx]
        st.write("### Plain-English Client Explanation")
        st.info(plain_english(alert_row))

        st.write("### Suggested Relationship Talking Point")
        st.write(
            f"{alert_row['client']} may be affected by current market conditions. "
            f"We should {alert_row['suggested_action'].lower()} and contact them proactively."
        )

        st.write("### Action Card")
        st.success(
            f"Priority: {alert_row['priority']} | Type: {alert_row['alert_type']}\n\n"
            f"Issue: {alert_row['message']}\n\n"
            f"Action: {alert_row['suggested_action']}"
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
