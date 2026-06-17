import os
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="AI Partnership Opportunity Finder",
    page_icon="🤝",
    layout="wide",
)

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


REGION_SCORES = {
    "LATAM": 90,
    "MENA": 95,
    "EU": 75,
    "NA": 70,
    "APAC": 65,
    "AFRICA": 80,
}

INDUSTRY_SCORES = {
    "Renewable Energy": 95,
    "Agribusiness": 90,
    "Logistics & Trade": 90,
    "Fintech": 85,
    "Real Estate": 75,
    "Other": 50,
}

OVERLAP_SCORES = {
    "high": 100,
    "medium": 70,
    "low": 40,
}

RELATIONSHIP_SCORES = {
    "hot": 100,
    "warm": 70,
    "cold": 35,
}


def format_money(value):
    try:
        return f"${float(value):,.0f}"
    except Exception:
        return str(value)


def score_deal_value(value, max_value):
    if max_value == 0:
        return 0
    return round((value / max_value) * 100, 1)


def score_partnership(row, max_deal_value):
    region_score = REGION_SCORES.get(row["region"], 55)
    industry_score = INDUSTRY_SCORES.get(row["industry"], 50)
    overlap_score = OVERLAP_SCORES.get(str(row["market_overlap"]).lower(), 40)
    relationship_score = RELATIONSHIP_SCORES.get(str(row["relationship_signal"]).lower(), 35)
    deal_score = score_deal_value(row["deal_value_usd"], max_deal_value)

    total = (
        region_score * 0.20
        + industry_score * 0.20
        + overlap_score * 0.25
        + relationship_score * 0.20
        + deal_score * 0.15
    )

    return round(total, 1)


def fit_tier(score):
    if score >= 80:
        return "Strategic Fit"
    if score >= 60:
        return "Potential Fit"
    return "Low Fit"


def priority_level(score):
    if score >= 80:
        return "High"
    if score >= 60:
        return "Medium"
    return "Low"


def strategic_fit(row):
    return (
        f"{row['company']} and {row['partner']} show a {row['fit_tier'].lower()} based on "
        f"{row['industry']} alignment, {row['market_overlap']} market overlap and a "
        f"{row['relationship_signal']} relationship signal."
    )


def expansion_potential(row):
    if row["region"] in ["MENA", "LATAM", "AFRICA"]:
        return (
            f"This opportunity may support expansion across {row['region']}, especially through "
            f"{row['partner_type'].lower()} collaboration and market access."
        )
    return (
        f"This opportunity may support selective market expansion or commercial access in {row['region']}."
    )


def synergy_analysis(row):
    return (
        f"The partnership can create value by connecting {row['company']}'s commercial objective "
        f"with {row['partner']}'s role as a {row['partner_type'].lower()}."
    )


def partnership_thesis(row):
    return (
        f"Partnership thesis: {row['company']} should explore collaboration with {row['partner']} to "
        f"{str(row['strategic_goal']).lower()}, with potential opportunity value of "
        f"{format_money(row['deal_value_usd'])}."
    )


def intro_strategy(row):
    if row["priority_level"] == "High":
        return "Prioritize executive introduction and propose a strategic discovery call."
    if row["priority_level"] == "Medium":
        return "Start with a targeted intro message and validate mutual priorities."
    return "Keep in nurture and monitor for stronger timing or relationship signal."


def ai_partnership_insight(row):
    signals = []

    if row["partnership_fit_score"] >= 80:
        signals.append("strong strategic alignment")
    if str(row["market_overlap"]).lower() == "high":
        signals.append("high market overlap")
    if str(row["relationship_signal"]).lower() == "hot":
        signals.append("strong relationship momentum")
    if row["region"] in ["MENA", "LATAM", "AFRICA"]:
        signals.append("meaningful international expansion potential")

    signal_text = ", ".join(signals) if signals else "moderate strategic alignment with selective commercial upside"

    return (
        f"This partnership shows {signal_text}. "
        f"The recommended approach is to validate executive-level alignment, assess commercial synergies, "
        f"and define a clear partnership motion around {str(row['strategic_goal']).lower()}."
    )


def next_best_action(row):
    if row["priority_level"] == "High":
        return "Schedule an executive discovery call and prepare a joint value hypothesis."
    if row["priority_level"] == "Medium":
        return "Send a targeted introduction and validate market timing, decision-makers and mutual priorities."
    return "Keep the opportunity in nurture and monitor for improved timing, signal strength or market relevance."


def render_card(title, content, icon="📌"):
    st.markdown(f"### {icon} {title}")
    st.markdown(
        f"""
<div style="
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
    background-color: #ffffff;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    white-space: pre-wrap;
    line-height: 1.6;
">{str(content).strip()}</div>
        """,
        unsafe_allow_html=True,
    )


st.title("🤝 AI Partnership Opportunity Finder")
st.caption(
    "Identify, score and prioritize strategic partnership opportunities for "
    "Business Development, Partnerships, GTM and International Expansion teams."
)

uploaded = st.file_uploader("Upload Partnerships CSV", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    df = pd.read_csv("data/sample_partnerships.csv")

required_columns = [
    "company",
    "partner",
    "country",
    "region",
    "industry",
    "partner_type",
    "strategic_goal",
    "market_overlap",
    "deal_value_usd",
    "relationship_signal",
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error("Missing columns in CSV: " + ", ".join(missing_columns))
    st.stop()

df["deal_value_usd"] = pd.to_numeric(df["deal_value_usd"], errors="coerce").fillna(0)

max_deal_value = df["deal_value_usd"].max()

df["partnership_fit_score"] = df.apply(lambda row: score_partnership(row, max_deal_value), axis=1)
df["fit_tier"] = df["partnership_fit_score"].apply(fit_tier)
df["priority_level"] = df["partnership_fit_score"].apply(priority_level)

df["strategic_fit"] = df.apply(strategic_fit, axis=1)
df["expansion_potential"] = df.apply(expansion_potential, axis=1)
df["synergy_analysis"] = df.apply(synergy_analysis, axis=1)
df["partnership_thesis"] = df.apply(partnership_thesis, axis=1)
df["recommended_intro_strategy"] = df.apply(intro_strategy, axis=1)
df["ai_partnership_insight"] = df.apply(ai_partnership_insight, axis=1)
df["next_best_action"] = df.apply(next_best_action, axis=1)

df = df.sort_values("partnership_fit_score", ascending=False).reset_index(drop=True)

st.subheader("📊 Executive Partnership Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Opportunities", len(df))
col2.metric("Pipeline Value", f"${df['deal_value_usd'].sum():,.0f}")
col3.metric("Avg Fit Score", round(df["partnership_fit_score"].mean(), 1))
col4.metric("High Priority", len(df[df["priority_level"] == "High"]))

st.divider()

st.subheader("👔 Executive Partnership Dashboard")

top_fit = df.iloc[0]
top_revenue = df.sort_values("deal_value_usd", ascending=False).iloc[0]
top_expansion = df[df["region"].isin(["MENA", "LATAM", "AFRICA"])].sort_values(
    "partnership_fit_score", ascending=False
)

if len(top_expansion) > 0:
    top_expansion_row = top_expansion.iloc[0]
else:
    top_expansion_row = top_fit

dash_col_1, dash_col_2, dash_col_3 = st.columns(3)

with dash_col_1:
    st.metric(
        "Top Strategic Fit",
        f"{top_fit['company']} + {top_fit['partner']}",
        f"Score {top_fit['partnership_fit_score']}",
    )
    st.metric(
        "Top Revenue Opportunity",
        f"{top_revenue['company']} + {top_revenue['partner']}",
        format_money(top_revenue["deal_value_usd"]),
    )

with dash_col_2:
    st.metric(
        "Top Expansion Opportunity",
        f"{top_expansion_row['company']} + {top_expansion_row['partner']}",
        top_expansion_row["region"],
    )
    st.metric("Strategic Fit Opportunities", len(df[df["fit_tier"] == "Strategic Fit"]))

with dash_col_3:
    st.metric(
        "Hot Relationship Signals",
        len(df[df["relationship_signal"].astype(str).str.lower() == "hot"]),
    )
    st.metric(
        "High Market Overlap",
        len(df[df["market_overlap"].astype(str).str.lower() == "high"]),
    )

st.markdown("#### Executive Interpretation")
st.write(
    f"The strongest partnership opportunity is **{top_fit['company']} + {top_fit['partner']}**, "
    f"with a fit score of **{top_fit['partnership_fit_score']}**."
)
st.write(
    f"The largest revenue opportunity is **{top_revenue['company']} + {top_revenue['partner']}**, "
    f"with an estimated value of **{format_money(top_revenue['deal_value_usd'])}**."
)

st.divider()

st.subheader("🔥 Opportunity Heatmap")

heatmap_fig = px.scatter(
    df,
    x="deal_value_usd",
    y="partnership_fit_score",
    size="deal_value_usd",
    color="priority_level",
    hover_name="partner",
    hover_data=["company", "region", "industry", "partner_type"],
    labels={
        "deal_value_usd": "Deal Value USD",
        "partnership_fit_score": "Partnership Fit Score",
        "priority_level": "Priority Level",
    },
    title="Partnership Fit vs Deal Value",
)

st.plotly_chart(heatmap_fig, use_container_width=True, config=PLOTLY_CONFIG)

st.divider()

st.subheader("🌍 Regional Expansion Dashboard")

regional_df = (
    df.groupby("region", as_index=False)
    .agg(
        total_pipeline_value=("deal_value_usd", "sum"),
        avg_fit_score=("partnership_fit_score", "mean"),
        opportunities=("company", "count"),
    )
    .sort_values("total_pipeline_value", ascending=False)
)

regional_fig = px.bar(
    regional_df,
    x="region",
    y="total_pipeline_value",
    text="total_pipeline_value",
    hover_data=["avg_fit_score", "opportunities"],
    labels={
        "region": "Region",
        "total_pipeline_value": "Total Pipeline Value",
        "avg_fit_score": "Average Fit Score",
        "opportunities": "Opportunities",
    },
    title="Pipeline Value by Region",
)

st.plotly_chart(regional_fig, use_container_width=True, config=PLOTLY_CONFIG)

st.divider()

st.subheader("🤝 Partner Portfolio Analysis")

partner_type_df = (
    df.groupby("partner_type", as_index=False)
    .agg(
        opportunities=("company", "count"),
        pipeline_value=("deal_value_usd", "sum"),
    )
    .sort_values("pipeline_value", ascending=False)
)

portfolio_fig = px.pie(
    partner_type_df,
    names="partner_type",
    values="pipeline_value",
    title="Pipeline Value by Partner Type",
)

st.plotly_chart(portfolio_fig, use_container_width=True, config=PLOTLY_CONFIG)

st.divider()

st.subheader("🏆 Executive Recommendation Center")

top_3 = df.head(3)

for index, row in top_3.iterrows():
    render_card(
        f"#{index + 1} {row['company']} + {row['partner']}",
        (
            f"Score: {row['partnership_fit_score']}\n"
            f"Priority: {row['priority_level']}\n"
            f"Value: {format_money(row['deal_value_usd'])}\n\n"
            f"{row['ai_partnership_insight']}\n\n"
            f"Next Best Action: {row['next_best_action']}"
        ),
        "🏆",
    )

st.divider()

st.subheader("🎯 Partnership Prioritization Engine")

display_columns = [
    "company",
    "partner",
    "country",
    "region",
    "industry",
    "partner_type",
    "deal_value_usd",
    "market_overlap",
    "relationship_signal",
    "partnership_fit_score",
    "fit_tier",
    "priority_level",
    "recommended_intro_strategy",
    "next_best_action",
]

st.dataframe(df[display_columns], width="stretch")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Partnership Opportunities CSV",
    csv,
    "partnership_opportunities_ranked.csv",
    "text/csv",
)

os.makedirs("exports", exist_ok=True)
df.to_csv("exports/partnership_opportunities_ranked.csv", index=False)

st.divider()

st.subheader("🧩 Partnership Intelligence Workspace")

selected_option = st.selectbox(
    "Select a partnership opportunity",
    [f"{row['company']} + {row['partner']}" for _, row in df.iterrows()],
)

selected_row = df[(df["company"] + " + " + df["partner"]) == selected_option].iloc[0]

profile_col_1, profile_col_2, profile_col_3 = st.columns(3)

with profile_col_1:
    st.markdown("#### 🏢 Company Profile")
    st.write(f"**Company:** {selected_row['company']}")
    st.write(f"**Partner:** {selected_row['partner']}")
    st.write(f"**Country:** {selected_row['country']}")
    st.write(f"**Region:** {selected_row['region']}")

with profile_col_2:
    st.markdown("#### 💼 Partnership Context")
    st.write(f"**Industry:** {selected_row['industry']}")
    st.write(f"**Partner Type:** {selected_row['partner_type']}")
    st.write(f"**Strategic Goal:** {selected_row['strategic_goal']}")
    st.write(f"**Deal Value:** {format_money(selected_row['deal_value_usd'])}")

with profile_col_3:
    st.markdown("#### 🚀 Fit Assessment")
    st.write(f"**Fit Score:** {selected_row['partnership_fit_score']}")
    st.write(f"**Fit Tier:** {selected_row['fit_tier']}")
    st.write(f"**Priority:** {selected_row['priority_level']}")
    st.write(f"**Relationship Signal:** {selected_row['relationship_signal']}")

st.divider()

intelligence_col_1, intelligence_col_2 = st.columns(2)

with intelligence_col_1:
    render_card("Strategic Fit", selected_row["strategic_fit"], "🎯")
    render_card("Synergy Analysis", selected_row["synergy_analysis"], "🔗")
    render_card("Recommended Intro Strategy", selected_row["recommended_intro_strategy"], "📨")

with intelligence_col_2:
    render_card("Expansion Potential", selected_row["expansion_potential"], "🌍")
    render_card("Partnership Thesis", selected_row["partnership_thesis"], "🤝")
    render_card("AI Partnership Insight", selected_row["ai_partnership_insight"], "🧠")
    render_card("Next Best Action", selected_row["next_best_action"], "🚀")

output_text = f"""Partnership Opportunity Brief

Company: {selected_row['company']}
Partner: {selected_row['partner']}
Country: {selected_row['country']}
Region: {selected_row['region']}
Industry: {selected_row['industry']}
Partner Type: {selected_row['partner_type']}
Strategic Goal: {selected_row['strategic_goal']}
Deal Value: {format_money(selected_row['deal_value_usd'])}
Fit Score: {selected_row['partnership_fit_score']}
Fit Tier: {selected_row['fit_tier']}
Priority: {selected_row['priority_level']}

Strategic Fit:
{selected_row['strategic_fit']}

Expansion Potential:
{selected_row['expansion_potential']}

Synergy Analysis:
{selected_row['synergy_analysis']}

Partnership Thesis:
{selected_row['partnership_thesis']}

Recommended Intro Strategy:
{selected_row['recommended_intro_strategy']}

AI Partnership Insight:
{selected_row['ai_partnership_insight']}

Next Best Action:
{selected_row['next_best_action']}
"""

safe_name = (
    f"{selected_row['company']}_{selected_row['partner']}"
    .lower()
    .replace(" ", "_")
    .replace("/", "_")
)

brief_path = f"exports/{safe_name}_partnership_brief.txt"

with open(brief_path, "w", encoding="utf-8") as f:
    f.write(output_text)

st.success(f"Partnership brief saved to {brief_path}")

st.download_button(
    "⬇ Download Partnership Brief",
    output_text,
    file_name=f"{safe_name}_partnership_brief.txt",
    mime="text/plain",
)