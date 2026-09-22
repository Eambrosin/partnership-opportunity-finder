import pandas as pd
import plotly.express as px
import streamlit as st

from partnership_engine import (
    DEFAULT_CONFIG,
    build_runtime_config,
    rank_partnerships,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Partnership Intelligence Platform",
    page_icon="🤝",
    layout="wide",
)

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}


# ============================================================
# HELPERS
# ============================================================

def format_money(value):
    try:
        return f"${float(value):,.0f}"
    except Exception:
        return str(value)


def unique_values(dataframe, column):
    if column not in dataframe.columns:
        return []

    return sorted(
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )


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
        ">
            {str(content).strip()}
        </div>
        """,
        unsafe_allow_html=True,
    )


def tier_to_outreach_tier(priority):
    mapping = {
        "High": "A",
        "Medium": "B",
        "Low": "C",
    }

    return mapping.get(
        str(priority),
        "C",
    )


def build_outreach_export(dataframe):
    outreach = pd.DataFrame()

    outreach["company_name"] = dataframe["partner"]
    outreach["contact_name"] = dataframe.get(
        "contact_name",
        "",
    )
    outreach["country"] = dataframe["country"]
    outreach["region"] = dataframe["region"]
    outreach["industry"] = dataframe["industry"]

    # Partnership datasets do not necessarily contain
    # employee count. Keep the field for downstream compatibility.
    outreach["company_size"] = ""

    outreach["estimated_deal_value_usd"] = dataframe[
        "deal_value_usd"
    ]

    outreach["engagement_signal"] = dataframe[
        "relationship_signal"
    ]

    outreach["score"] = dataframe[
        "partnership_fit_score"
    ]

    outreach["tier"] = dataframe[
        "priority_level"
    ].apply(
        tier_to_outreach_tier
    )

    outreach["recommended_action"] = dataframe[
        "recommended_action"
    ]

    outreach["score_rationale"] = dataframe[
        "score_rationale"
    ]

    outreach["partner_type"] = dataframe[
        "partner_type"
    ]

    outreach["partnership_archetype"] = dataframe[
        "partnership_archetype"
    ]

    outreach["source_company"] = dataframe[
        "company"
    ]

    outreach["strategic_goal"] = dataframe[
        "strategic_goal"
    ]

    return outreach


# ============================================================
# HEADER
# ============================================================

st.title("🤝 Partnership Intelligence Platform")

st.caption(
    "Configurable Partnership Scoring · Strategic Fit · "
    "Market Access · Partnership Archetypes · "
    "Commercial Prioritization · Outreach Handoff"
)

st.markdown(
    """
A practical Commercial Intelligence application designed to help
**Business Development, Partnerships, GTM and International Expansion teams**
identify, evaluate and prioritize strategic partnership opportunities.

The platform uses a deterministic and explainable scoring engine.

**The score is produced by structured commercial rules — not by AI.**
"""
)

st.info(
    "PARTNER stage of the Commercial Intelligence ecosystem: "
    "IDENTIFY → PRIORITIZE → ENGAGE → PARTNER → EXPAND"
)


# ============================================================
# DATA INPUT
# ============================================================

st.subheader("📂 Partnership Pipeline")

uploaded = st.file_uploader(
    "Upload Partnerships CSV",
    type=["csv"],
)

if uploaded is not None:

    try:
        source_df = pd.read_csv(
            uploaded
        )

        st.success(
            f"Loaded {len(source_df)} partnership opportunities."
        )

    except Exception as exc:

        st.error(
            f"Unable to read the uploaded CSV: {exc}"
        )

        st.stop()

else:

    try:
        source_df = pd.read_csv(
            "data/sample_partnerships.csv"
        )

        st.caption(
            "Using the demonstration partnership dataset."
        )

    except Exception as exc:

        st.error(
            "No uploaded CSV was provided and the sample dataset "
            f"could not be loaded: {exc}"
        )

        st.stop()


# ============================================================
# CONFIGURATION OPTIONS
# ============================================================

available_regions = unique_values(
    source_df,
    "region",
)

available_industries = unique_values(
    source_df,
    "industry",
)

available_partner_types = unique_values(
    source_df,
    "partner_type",
)


# ============================================================
# SIDEBAR — PARTNERSHIP MODEL
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Partnership Model"
    )

    st.caption(
        "Configure the commercial logic used to evaluate "
        "and prioritize partnership opportunities."
    )

    st.divider()

    st.subheader(
        "Strategic Preferences"
    )

    preferred_regions = st.multiselect(
        "Priority Regions",
        options=available_regions,
        default=[],
        help=(
            "Selected regions receive the strongest "
            "Region Fit score."
        ),
    )

    preferred_industries = st.multiselect(
        "Priority Industries",
        options=available_industries,
        default=[],
        help=(
            "Selected industries receive the strongest "
            "Industry Alignment score."
        ),
    )

    preferred_partner_types = st.multiselect(
        "Priority Partner Types",
        options=available_partner_types,
        default=[],
        help=(
            "Selected partner types receive the strongest "
            "Partner Type Fit score."
        ),
    )

    st.divider()

    st.subheader(
        "Commercial Value"
    )

    deal_value_target_usd = st.number_input(
        "Target Partnership Value (USD)",
        min_value=1_000,
        value=int(
            DEFAULT_CONFIG[
                "deal_value_target_usd"
            ]
        ),
        step=25_000,
        help=(
            "Opportunities reaching this value receive "
            "the maximum Opportunity Value score."
        ),
    )

    st.divider()

    st.subheader(
        "Scoring Priorities"
    )

    region_weight = st.slider(
        "Region Fit",
        min_value=0,
        max_value=40,
        value=int(
            DEFAULT_CONFIG["weights"][
                "region_fit"
            ]
            * 100
        ),
        step=5,
    )

    industry_weight = st.slider(
        "Industry Alignment",
        min_value=0,
        max_value=40,
        value=int(
            DEFAULT_CONFIG["weights"][
                "industry_alignment"
            ]
            * 100
        ),
        step=5,
    )

    market_access_weight = st.slider(
        "Market Access",
        min_value=0,
        max_value=40,
        value=int(
            DEFAULT_CONFIG["weights"][
                "market_access"
            ]
            * 100
        ),
        step=5,
    )

    relationship_weight = st.slider(
        "Relationship Strength",
        min_value=0,
        max_value=40,
        value=int(
            DEFAULT_CONFIG["weights"][
                "relationship_strength"
            ]
            * 100
        ),
        step=5,
    )

    value_weight = st.slider(
        "Opportunity Value",
        min_value=0,
        max_value=40,
        value=int(
            DEFAULT_CONFIG["weights"][
                "opportunity_value"
            ]
            * 100
        ),
        step=5,
    )

    partner_type_weight = st.slider(
        "Partner Type Fit",
        min_value=0,
        max_value=40,
        value=int(
            DEFAULT_CONFIG["weights"][
                "partner_type_fit"
            ]
            * 100
        ),
        step=5,
    )

    execution_weight = st.slider(
        "Execution Feasibility",
        min_value=0,
        max_value=40,
        value=int(
            DEFAULT_CONFIG["weights"][
                "execution_feasibility"
            ]
            * 100
        ),
        step=5,
    )

    raw_weight_total = (
        region_weight
        + industry_weight
        + market_access_weight
        + relationship_weight
        + value_weight
        + partner_type_weight
        + execution_weight
    )

    st.caption(
        f"Current raw weighting total: {raw_weight_total}%"
    )

    st.caption(
        "Weights are automatically normalized to 100% "
        "by the scoring engine."
    )

    st.divider()

    st.subheader(
        "Fit Thresholds"
    )

    strategic_fit_threshold = st.number_input(
        "Strategic Fit",
        min_value=1,
        max_value=100,
        value=int(
            DEFAULT_CONFIG[
                "tier_thresholds"
            ][
                "strategic_fit"
            ]
        ),
    )

    promising_fit_threshold = st.number_input(
        "Promising Fit",
        min_value=1,
        max_value=99,
        value=int(
            DEFAULT_CONFIG[
                "tier_thresholds"
            ][
                "promising_fit"
            ]
        ),
    )

    exploratory_fit_threshold = st.number_input(
        "Exploratory Fit",
        min_value=1,
        max_value=98,
        value=int(
            DEFAULT_CONFIG[
                "tier_thresholds"
            ][
                "exploratory_fit"
            ]
        ),
    )


# ============================================================
# BUILD ACTIVE CONFIGURATION
# ============================================================

weights = {
    "region_fit": (
        region_weight
        / 100
    ),
    "industry_alignment": (
        industry_weight
        / 100
    ),
    "market_access": (
        market_access_weight
        / 100
    ),
    "relationship_strength": (
        relationship_weight
        / 100
    ),
    "opportunity_value": (
        value_weight
        / 100
    ),
    "partner_type_fit": (
        partner_type_weight
        / 100
    ),
    "execution_feasibility": (
        execution_weight
        / 100
    ),
}


try:

    active_config = build_runtime_config(
        preferred_regions=preferred_regions,
        preferred_industries=preferred_industries,
        preferred_partner_types=preferred_partner_types,
        weights=weights,
        deal_value_target_usd=deal_value_target_usd,
        strategic_fit_threshold=strategic_fit_threshold,
        promising_fit_threshold=promising_fit_threshold,
        exploratory_fit_threshold=exploratory_fit_threshold,
    )

except ValueError as exc:

    st.error(
        str(exc)
    )

    st.stop()


# ============================================================
# RUN PARTNERSHIP INTELLIGENCE ENGINE
# ============================================================

try:

    df = rank_partnerships(
        source_df,
        config=active_config,
    )

except ValueError as exc:

    st.error(
        str(exc)
    )

    st.stop()

except Exception as exc:

    st.error(
        f"Unable to evaluate partnership pipeline: {exc}"
    )

    st.stop()


if df.empty:

    st.warning(
        "No partnership opportunities are available for analysis."
    )

    st.stop()


# ============================================================
# ACTIVE MODEL
# ============================================================

with st.expander(
    "🧠 Active Partnership Intelligence Model"
):

    weights_df = pd.DataFrame(
        [
            {
                "Dimension": "Region Fit",
                "Weight": (
                    active_config[
                        "weights"
                    ][
                        "region_fit"
                    ]
                    * 100
                ),
            },
            {
                "Dimension": "Industry Alignment",
                "Weight": (
                    active_config[
                        "weights"
                    ][
                        "industry_alignment"
                    ]
                    * 100
                ),
            },
            {
                "Dimension": "Market Access",
                "Weight": (
                    active_config[
                        "weights"
                    ][
                        "market_access"
                    ]
                    * 100
                ),
            },
            {
                "Dimension": "Relationship Strength",
                "Weight": (
                    active_config[
                        "weights"
                    ][
                        "relationship_strength"
                    ]
                    * 100
                ),
            },
            {
                "Dimension": "Opportunity Value",
                "Weight": (
                    active_config[
                        "weights"
                    ][
                        "opportunity_value"
                    ]
                    * 100
                ),
            },
            {
                "Dimension": "Partner Type Fit",
                "Weight": (
                    active_config[
                        "weights"
                    ][
                        "partner_type_fit"
                    ]
                    * 100
                ),
            },
            {
                "Dimension": "Execution Feasibility",
                "Weight": (
                    active_config[
                        "weights"
                    ][
                        "execution_feasibility"
                    ]
                    * 100
                ),
            },
        ]
    )

    weights_df["Weight"] = weights_df[
        "Weight"
    ].round(
        1
    )

    st.dataframe(
        weights_df,
        use_container_width=True,
        hide_index=True,
    )

    model_col_1, model_col_2, model_col_3 = st.columns(
        3
    )

    with model_col_1:

        st.write(
            "**Priority Regions:** "
            + (
                ", ".join(
                    preferred_regions
                )
                if preferred_regions
                else "Default model"
            )
        )

    with model_col_2:

        st.write(
            "**Priority Industries:** "
            + (
                ", ".join(
                    preferred_industries
                )
                if preferred_industries
                else "Default model"
            )
        )

    with model_col_3:

        st.write(
            "**Priority Partner Types:** "
            + (
                ", ".join(
                    preferred_partner_types
                )
                if preferred_partner_types
                else "Default model"
            )
        )

    st.write(
        f"**Target Partnership Value:** "
        f"{format_money(deal_value_target_usd)}"
    )

    st.write(
        "**Fit Thresholds:** "
        f"Strategic {strategic_fit_threshold}+ · "
        f"Promising {promising_fit_threshold}+ · "
        f"Exploratory {exploratory_fit_threshold}+"
    )


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

st.divider()

st.subheader(
    "📊 Executive Partnership Summary"
)

total_pipeline_value = df[
    "deal_value_usd"
].sum()

average_score = df[
    "partnership_fit_score"
].mean()

high_priority_count = len(
    df[
        df[
            "priority_level"
        ]
        == "High"
    ]
)

strategic_fit_count = len(
    df[
        df[
            "fit_tier"
        ]
        == "Strategic Fit"
    ]
)

summary_col_1, summary_col_2, summary_col_3, summary_col_4, summary_col_5 = st.columns(
    5
)

summary_col_1.metric(
    "Opportunities",
    len(df),
)

summary_col_2.metric(
    "Pipeline Value",
    format_money(
        total_pipeline_value
    ),
)

summary_col_3.metric(
    "Avg Partnership Score",
    round(
        average_score,
        1,
    ),
)

summary_col_4.metric(
    "Strategic Fit",
    strategic_fit_count,
)

summary_col_5.metric(
    "High Priority",
    high_priority_count,
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

st.divider()

st.subheader(
    "👔 Executive Partnership Dashboard"
)

top_fit = df.iloc[
    0
]

top_revenue = df.sort_values(
    "deal_value_usd",
    ascending=False,
).iloc[
    0
]

hot_relationships = df[
    df[
        "relationship_signal"
    ].astype(
        str
    ).str.lower()
    == "hot"
]

if not hot_relationships.empty:

    top_relationship = hot_relationships.sort_values(
        "partnership_fit_score",
        ascending=False,
    ).iloc[
        0
    ]

else:

    top_relationship = top_fit


market_access_df = df[
    df[
        "market_overlap"
    ].astype(
        str
    ).str.lower()
    == "high"
]

if not market_access_df.empty:

    top_market_access = market_access_df.sort_values(
        "partnership_fit_score",
        ascending=False,
    ).iloc[
        0
    ]

else:

    top_market_access = top_fit


dash_col_1, dash_col_2 = st.columns(
    2
)

with dash_col_1:

    render_card(
        "Top Strategic Fit",
        (
            f"{top_fit['company']} + {top_fit['partner']}\n\n"
            f"Score: {top_fit['partnership_fit_score']}\n"
            f"Tier: {top_fit['fit_tier']}\n"
            f"Archetype: {top_fit['partnership_archetype']}"
        ),
        "🏆",
    )

    render_card(
        "Top Relationship Opportunity",
        (
            f"{top_relationship['company']} + "
            f"{top_relationship['partner']}\n\n"
            f"Relationship Signal: "
            f"{top_relationship['relationship_signal']}\n"
            f"Score: "
            f"{top_relationship['partnership_fit_score']}"
        ),
        "🤝",
    )


with dash_col_2:

    render_card(
        "Top Revenue Opportunity",
        (
            f"{top_revenue['company']} + "
            f"{top_revenue['partner']}\n\n"
            f"Estimated Value: "
            f"{format_money(top_revenue['deal_value_usd'])}\n"
            f"Score: "
            f"{top_revenue['partnership_fit_score']}"
        ),
        "💰",
    )

    render_card(
        "Top Market Access Opportunity",
        (
            f"{top_market_access['company']} + "
            f"{top_market_access['partner']}\n\n"
            f"Region: {top_market_access['region']}\n"
            f"Partner Type: "
            f"{top_market_access['partner_type']}\n"
            f"Score: "
            f"{top_market_access['partnership_fit_score']}"
        ),
        "🌍",
    )


# ============================================================
# EXECUTIVE INTERPRETATION
# ============================================================

st.markdown(
    "### Executive Interpretation"
)

st.write(
    f"The highest-ranked partnership opportunity is "
    f"**{top_fit['company']} + {top_fit['partner']}**, "
    f"with a Partnership Intelligence score of "
    f"**{top_fit['partnership_fit_score']}** and classification "
    f"**{top_fit['fit_tier']}**."
)

st.write(
    f"The opportunity is currently classified as a "
    f"**{top_fit['partnership_archetype']}**."
)

st.write(
    f"Recommended next action: "
    f"**{top_fit['recommended_action']}**"
)


# ============================================================
# OPPORTUNITY MAP
# ============================================================

st.divider()

st.subheader(
    "🔥 Partnership Opportunity Map"
)

chart_df = df.copy()

chart_df[
    "_bubble_size"
] = chart_df[
    "deal_value_usd"
].clip(
    lower=1
)

heatmap_fig = px.scatter(
    chart_df,
    x="deal_value_usd",
    y="partnership_fit_score",
    size="_bubble_size",
    color="priority_level",
    hover_name="partner",
    hover_data=[
        "company",
        "region",
        "industry",
        "partner_type",
        "partnership_archetype",
        "fit_tier",
    ],
    labels={
        "deal_value_usd": "Estimated Partnership Value USD",
        "partnership_fit_score": "Partnership Intelligence Score",
        "priority_level": "Priority",
    },
    title="Partnership Score vs Commercial Value",
)

st.plotly_chart(
    heatmap_fig,
    use_container_width=True,
    config=PLOTLY_CONFIG,
)


# ============================================================
# REGIONAL INTELLIGENCE
# ============================================================

st.divider()

st.subheader(
    "🌍 Regional Partnership Intelligence"
)

regional_df = (
    df.groupby(
        "region",
        as_index=False,
    )
    .agg(
        total_pipeline_value=(
            "deal_value_usd",
            "sum",
        ),
        avg_fit_score=(
            "partnership_fit_score",
            "mean",
        ),
        opportunities=(
            "partner",
            "count",
        ),
    )
    .sort_values(
        "total_pipeline_value",
        ascending=False,
    )
)

regional_df[
    "avg_fit_score"
] = regional_df[
    "avg_fit_score"
].round(
    1
)

regional_fig = px.bar(
    regional_df,
    x="region",
    y="total_pipeline_value",
    text="total_pipeline_value",
    hover_data=[
        "avg_fit_score",
        "opportunities",
    ],
    labels={
        "region": "Region",
        "total_pipeline_value": "Partnership Pipeline Value",
        "avg_fit_score": "Average Partnership Score",
        "opportunities": "Opportunities",
    },
    title="Partnership Pipeline Value by Region",
)

st.plotly_chart(
    regional_fig,
    use_container_width=True,
    config=PLOTLY_CONFIG,
)


# ============================================================
# PARTNERSHIP ARCHETYPES
# ============================================================

st.divider()

st.subheader(
    "🧭 Partnership Archetype Analysis"
)

archetype_df = (
    df.groupby(
        "partnership_archetype",
        as_index=False,
    )
    .agg(
        opportunities=(
            "partner",
            "count",
        ),
        pipeline_value=(
            "deal_value_usd",
            "sum",
        ),
        average_score=(
            "partnership_fit_score",
            "mean",
        ),
    )
    .sort_values(
        "pipeline_value",
        ascending=False,
    )
)

archetype_df[
    "average_score"
] = archetype_df[
    "average_score"
].round(
    1
)

archetype_col_1, archetype_col_2 = st.columns(
    2
)

with archetype_col_1:

    archetype_fig = px.pie(
        archetype_df,
        names="partnership_archetype",
        values="pipeline_value",
        title="Pipeline Value by Partnership Archetype",
    )

    st.plotly_chart(
        archetype_fig,
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )


with archetype_col_2:

    st.dataframe(
        archetype_df.rename(
            columns={
                "partnership_archetype": "Archetype",
                "opportunities": "Opportunities",
                "pipeline_value": "Pipeline Value",
                "average_score": "Average Score",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# EXECUTIVE RECOMMENDATION CENTER
# ============================================================

st.divider()

st.subheader(
    "🏆 Executive Recommendation Center"
)

top_recommendations = df.head(
    min(
        5,
        len(df),
    )
)

for index, row in top_recommendations.iterrows():

    render_card(
        f"#{index + 1} "
        f"{row['company']} + "
        f"{row['partner']}",
        (
            f"Partnership Score: "
            f"{row['partnership_fit_score']}\n"
            f"Fit Tier: "
            f"{row['fit_tier']}\n"
            f"Priority: "
            f"{row['priority_level']}\n"
            f"Archetype: "
            f"{row['partnership_archetype']}\n"
            f"Estimated Value: "
            f"{format_money(row['deal_value_usd'])}\n\n"
            f"{row['strategic_interpretation']}\n\n"
            f"Recommended Model: "
            f"{row['recommended_partnership_model']}\n\n"
            f"Next Best Action: "
            f"{row['recommended_action']}"
        ),
        "🏆",
    )


# ============================================================
# PRIORITIZATION ENGINE
# ============================================================

st.divider()

st.subheader(
    "🎯 Partnership Prioritization Engine"
)

display_columns = [
    "company",
    "partner",
    "country",
    "region",
    "industry",
    "partner_type",
    "partnership_archetype",
    "deal_value_usd",
    "market_overlap",
    "relationship_signal",
    "execution_complexity",
    "partnership_fit_score",
    "fit_tier",
    "priority_level",
    "recommended_action",
]

available_display_columns = [
    column
    for column in display_columns
    if column in df.columns
]

st.dataframe(
    df[
        available_display_columns
    ],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# FULL PARTNERSHIP EXPORT
# ============================================================

export_columns = [
    "company",
    "partner",
    "contact_name",
    "country",
    "region",
    "industry",
    "partner_type",
    "strategic_goal",
    "market_overlap",
    "deal_value_usd",
    "relationship_signal",
    "execution_complexity",
    "partnership_fit_score",
    "fit_tier",
    "priority_level",
    "partnership_archetype",
    "recommended_partnership_model",
    "recommended_action",
    "strategic_interpretation",
    "expansion_potential",
    "partnership_thesis",
    "score_rationale",
    "outreach_handoff_context",
]

available_export_columns = [
    column
    for column in export_columns
    if column in df.columns
]

full_export_df = df[
    available_export_columns
].copy()

full_csv = full_export_df.to_csv(
    index=False
).encode(
    "utf-8"
)

st.download_button(
    "⬇ Download Ranked Partnership Pipeline",
    full_csv,
    file_name="partnership_intelligence_ranked.csv",
    mime="text/csv",
)


# ============================================================
# OUTREACH HANDOFF
# ============================================================

st.divider()

st.subheader(
    "🔗 Adaptive Outreach Intelligence Handoff"
)

st.write(
    "Partnership opportunities can be exported in a format designed "
    "for downstream commercial engagement."
)

st.markdown(
    """
```text
PARTNERSHIP INTELLIGENCE
        ↓
Partnership Score
        ↓
Priority
        ↓
Recommended Action
        ↓
OUTREACH HANDOFF
        ↓
Adaptive Cadence
        ↓
Channel Strategy
        ↓
Commercial Message
```
"""
)

outreach_df = build_outreach_export(
    df
)

outreach_csv = outreach_df.to_csv(
    index=False
).encode(
    "utf-8"
)

st.download_button(
    "📨 Export for Adaptive Outreach Intelligence",
    outreach_csv,
    file_name="partnership_outreach_handoff.csv",
    mime="text/csv",
)

with st.expander(
    "Preview Outreach Handoff"
):

    st.dataframe(
        outreach_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# PARTNERSHIP INTELLIGENCE WORKSPACE
# ============================================================

st.divider()

st.subheader(
    "🧩 Partnership Intelligence Workspace"
)

selection_map = {}

for index, row in df.iterrows():

    label = (
        f"{index + 1}. "
        f"{row['company']} + "
        f"{row['partner']}"
    )

    selection_map[
        label
    ] = index


selected_label = st.selectbox(
    "Select a partnership opportunity",
    list(
        selection_map.keys()
    ),
)

selected_index = selection_map[
    selected_label
]

selected_row = df.loc[
    selected_index
]


# ============================================================
# SELECTED OPPORTUNITY — PROFILE
# ============================================================

profile_col_1, profile_col_2, profile_col_3, profile_col_4 = st.columns(
    4
)

with profile_col_1:

    st.markdown(
        "#### 🏢 Company"
    )

    st.write(
        f"**Company:** "
        f"{selected_row['company']}"
    )

    st.write(
        f"**Partner:** "
        f"{selected_row['partner']}"
    )

    st.write(
        f"**Country:** "
        f"{selected_row['country']}"
    )

    st.write(
        f"**Region:** "
        f"{selected_row['region']}"
    )


with profile_col_2:

    st.markdown(
        "#### 💼 Partnership Context"
    )

    st.write(
        f"**Industry:** "
        f"{selected_row['industry']}"
    )

    st.write(
        f"**Partner Type:** "
        f"{selected_row['partner_type']}"
    )

    st.write(
        f"**Strategic Goal:** "
        f"{selected_row['strategic_goal']}"
    )

    st.write(
        f"**Value:** "
        f"{format_money(selected_row['deal_value_usd'])}"
    )


with profile_col_3:

    st.markdown(
        "#### 🎯 Fit Assessment"
    )

    st.write(
        f"**Score:** "
        f"{selected_row['partnership_fit_score']}"
    )

    st.write(
        f"**Fit Tier:** "
        f"{selected_row['fit_tier']}"
    )

    st.write(
        f"**Priority:** "
        f"{selected_row['priority_level']}"
    )

    st.write(
        f"**Relationship:** "
        f"{selected_row['relationship_signal']}"
    )


with profile_col_4:

    st.markdown(
        "#### 🧭 Partnership Model"
    )

    st.write(
        f"**Archetype:** "
        f"{selected_row['partnership_archetype']}"
    )

    st.write(
        f"**Market Overlap:** "
        f"{selected_row['market_overlap']}"
    )

    st.write(
        f"**Execution Complexity:** "
        f"{selected_row['execution_complexity']}"
    )


# ============================================================
# SCORE EXPLAINABILITY
# ============================================================

st.divider()

st.markdown(
    "### 🔎 Explainable Partnership Score"
)

score_breakdown = selected_row[
    "score_breakdown"
]

component_labels = {
    "region_fit": "Region Fit",
    "industry_alignment": "Industry Alignment",
    "market_access": "Market Access",
    "relationship_strength": "Relationship Strength",
    "opportunity_value": "Opportunity Value",
    "partner_type_fit": "Partner Type Fit",
    "execution_feasibility": "Execution Feasibility",
}

breakdown_rows = []

for component, raw_score in score_breakdown[
    "raw_scores"
].items():

    weight = score_breakdown[
        "weights"
    ][
        component
    ]

    contribution = score_breakdown[
        "weighted_contributions"
    ][
        component
    ]

    breakdown_rows.append(
        {
            "Component": component_labels.get(
                component,
                component,
            ),
            "Raw Score": round(
                raw_score,
                1,
            ),
            "Weight": f"{weight * 100:.1f}%",
            "Weighted Contribution": round(
                contribution,
                2,
            ),
        }
    )


breakdown_df = pd.DataFrame(
    breakdown_rows
)

st.dataframe(
    breakdown_df,
    use_container_width=True,
    hide_index=True,
)

st.markdown(
    f"### Final Partnership Intelligence Score: "
    f"**{selected_row['partnership_fit_score']} / 100**"
)

with st.expander(
    "Full Score Rationale"
):

    st.write(
        selected_row[
            "score_rationale"
        ]
    )


# ============================================================
# INTELLIGENCE CARDS
# ============================================================

st.divider()

intelligence_col_1, intelligence_col_2 = st.columns(
    2
)

with intelligence_col_1:

    render_card(
        "Strategic Interpretation",
        selected_row[
            "strategic_interpretation"
        ],
        "🎯",
    )

    render_card(
        "Partnership Archetype",
        (
            f"{selected_row['partnership_archetype']}\n\n"
            f"{selected_row['recommended_partnership_model']}"
        ),
        "🧭",
    )

    render_card(
        "Recommended Action",
        selected_row[
            "recommended_action"
        ],
        "🚀",
    )


with intelligence_col_2:

    render_card(
        "Expansion Potential",
        selected_row[
            "expansion_potential"
        ],
        "🌍",
    )

    render_card(
        "Partnership Thesis",
        selected_row[
            "partnership_thesis"
        ],
        "🤝",
    )

    render_card(
        "Outreach Handoff Context",
        selected_row[
            "outreach_handoff_context"
        ],
        "📨",
    )


# ============================================================
# PARTNERSHIP OPPORTUNITY BRIEF
# ============================================================

st.divider()

st.subheader(
    "📄 Partnership Opportunity Brief"
)

brief_text = f"""# Partnership Opportunity Brief

## Opportunity

Company: {selected_row['company']}
Partner: {selected_row['partner']}
Country: {selected_row['country']}
Region: {selected_row['region']}
Industry: {selected_row['industry']}
Partner Type: {selected_row['partner_type']}
Strategic Goal: {selected_row['strategic_goal']}

## Commercial Value

Estimated Partnership Value: {format_money(selected_row['deal_value_usd'])}

## Partnership Intelligence

Score: {selected_row['partnership_fit_score']}
Fit Tier: {selected_row['fit_tier']}
Priority: {selected_row['priority_level']}
Partnership Archetype: {selected_row['partnership_archetype']}
Relationship Signal: {selected_row['relationship_signal']}
Market Overlap: {selected_row['market_overlap']}
Execution Complexity: {selected_row['execution_complexity']}

## Strategic Interpretation

{selected_row['strategic_interpretation']}

## Partnership Thesis

{selected_row['partnership_thesis']}

## Expansion Potential

{selected_row['expansion_potential']}

## Recommended Partnership Model

{selected_row['recommended_partnership_model']}

## Recommended Next Action

{selected_row['recommended_action']}

## Explainable Score

{selected_row['score_rationale']}

## Outreach Handoff

{selected_row['outreach_handoff_context']}

---

Generated by the Partnership Intelligence Platform.
"""


safe_name = (
    f"{selected_row['company']}_"
    f"{selected_row['partner']}"
    .lower()
    .replace(
        " ",
        "_",
    )
    .replace(
        "/",
        "_",
    )
)

st.download_button(
    "⬇ Download Partnership Opportunity Brief",
    brief_text,
    file_name=f"{safe_name}_partnership_brief.md",
    mime="text/markdown",
)


# ============================================================
# ECOSYSTEM POSITIONING
# ============================================================

st.divider()

st.subheader(
    "🧠 Commercial Intelligence Ecosystem"
)

st.markdown(
    """
```text
IDENTIFY
Opportunity Discovery

        ↓

PRIORITIZE
Lead Qualification & Revenue Prioritization

        ↓

ENGAGE
Adaptive Outreach Intelligence

        ↓

PARTNER
Partnership Intelligence
← YOU ARE HERE

        ↓

EXPAND
Global Market Entry Intelligence
```
"""
)

st.caption(
    "The objective is to connect structured commercial logic "
    "across the complete Business Development lifecycle."
)
