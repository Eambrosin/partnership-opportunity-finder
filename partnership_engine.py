from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Optional

import pandas as pd


# ============================================================
# DEFAULT CONFIGURATION
# ============================================================

DEFAULT_CONFIG: Dict[str, Any] = {
    "weights": {
        "region_fit": 0.15,
        "industry_alignment": 0.15,
        "market_access": 0.20,
        "relationship_strength": 0.15,
        "opportunity_value": 0.15,
        "partner_type_fit": 0.10,
        "execution_feasibility": 0.10,
    },

    "region_scores": {
        "LATAM": 90,
        "MENA": 95,
        "EU": 75,
        "NA": 70,
        "APAC": 65,
        "AFRICA": 80,
    },

    "industry_scores": {
        "Renewable Energy": 95,
        "Agribusiness": 90,
        "Logistics & Trade": 90,
        "Fintech": 85,
        "Real Estate": 75,
        "Government / Public Sector": 85,
        "Other": 50,
    },

    "market_overlap_scores": {
        "high": 100,
        "medium": 70,
        "low": 40,
    },

    "relationship_scores": {
        "hot": 100,
        "warm": 70,
        "cold": 35,
    },

    "partner_type_scores": {
        "channel partner": 100,
        "distributor": 100,
        "reseller": 95,
        "strategic alliance": 95,
        "technology partner": 90,
        "institutional partner": 90,
        "government partner": 90,
        "market entry partner": 95,
        "commercial representative": 85,
        "referral partner": 80,
        "consulting partner": 70,
        "other": 60,
    },

    "execution_complexity_scores": {
        "low": 100,
        "medium": 70,
        "high": 40,
    },

    "deal_value_target_usd": 500_000,

    "tier_thresholds": {
        "strategic_fit": 80,
        "promising_fit": 65,
        "exploratory_fit": 50,
    },
}


# ============================================================
# INPUT COMPATIBILITY
# ============================================================

REQUIRED_FIELD_ALTERNATIVES = {
    "company": [
        "company",
        "company_name",
    ],

    "partner": [
        "partner",
        "partner_name",
    ],

    "country": [
        "country",
    ],

    "region": [
        "region",
    ],

    "industry": [
        "industry",
    ],

    "partner_type": [
        "partner_type",
    ],

    "strategic_goal": [
        "strategic_goal",
    ],

    "market_overlap": [
        "market_overlap",
    ],

    "deal_value_usd": [
        "deal_value_usd",
        "estimated_deal_value_usd",
        "partnership_value_usd",
    ],

    "relationship_signal": [
        "relationship_signal",
        "engagement_signal",
    ],
}


# ============================================================
# CONFIGURATION HELPERS
# ============================================================

def load_partnership_config() -> Dict[str, Any]:
    return deepcopy(DEFAULT_CONFIG)


def normalize_weights(
    weights: Mapping[str, float],
) -> Dict[str, float]:

    cleaned = {
        key: max(float(value), 0.0)
        for key, value in weights.items()
    }

    total = sum(cleaned.values())

    if total <= 0:
        raise ValueError(
            "At least one scoring weight must be greater than zero."
        )

    return {
        key: value / total
        for key, value in cleaned.items()
    }


def build_runtime_config(
    *,
    base_config: Optional[Mapping[str, Any]] = None,
    preferred_regions: Optional[Iterable[str]] = None,
    preferred_industries: Optional[Iterable[str]] = None,
    preferred_partner_types: Optional[Iterable[str]] = None,
    weights: Optional[Mapping[str, float]] = None,
    deal_value_target_usd: Optional[float] = None,
    strategic_fit_threshold: Optional[float] = None,
    promising_fit_threshold: Optional[float] = None,
    exploratory_fit_threshold: Optional[float] = None,
) -> Dict[str, Any]:

    config = deepcopy(
        dict(base_config)
        if base_config is not None
        else DEFAULT_CONFIG
    )

    if preferred_regions:

        for region in preferred_regions:
            config["region_scores"][str(region)] = 100

    if preferred_industries:

        for industry in preferred_industries:
            config["industry_scores"][str(industry)] = 100

    if preferred_partner_types:

        for partner_type in preferred_partner_types:
            config["partner_type_scores"][
                str(partner_type).strip().lower()
            ] = 100

    if weights is not None:

        config["weights"] = normalize_weights(
            weights
        )

    else:

        config["weights"] = normalize_weights(
            config["weights"]
        )

    if deal_value_target_usd is not None:

        target = float(
            deal_value_target_usd
        )

        if target <= 0:

            raise ValueError(
                "deal_value_target_usd must be greater than zero."
            )

        config["deal_value_target_usd"] = target

    thresholds = deepcopy(
        config["tier_thresholds"]
    )

    if strategic_fit_threshold is not None:

        thresholds["strategic_fit"] = float(
            strategic_fit_threshold
        )

    if promising_fit_threshold is not None:

        thresholds["promising_fit"] = float(
            promising_fit_threshold
        )

    if exploratory_fit_threshold is not None:

        thresholds["exploratory_fit"] = float(
            exploratory_fit_threshold
        )

    if not (
        thresholds["strategic_fit"]
        > thresholds["promising_fit"]
        > thresholds["exploratory_fit"]
    ):

        raise ValueError(
            "Tier thresholds must satisfy "
            "Strategic Fit > Promising Fit > Exploratory Fit."
        )

    config["tier_thresholds"] = thresholds

    return config


# ============================================================
# NORMALIZATION
# ============================================================

def _first_value(
    row: Mapping[str, Any],
    keys: Iterable[str],
    default: Any = "",
) -> Any:

    for key in keys:

        value = row.get(
            key
        )

        if value is None:
            continue

        try:

            if pd.isna(
                value
            ):
                continue

        except Exception:
            pass

        if str(
            value
        ).strip():

            return value

    return default


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        if value is None:
            return float(
                default
            )

        try:

            if pd.isna(
                value
            ):
                return float(
                    default
                )

        except Exception:
            pass

        return float(
            value
        )

    except Exception:

        return float(
            default
        )


def _normalized_key(
    value: Any,
) -> str:

    return str(
        value or ""
    ).strip().lower()


def validate_partnership_dataframe(
    dataframe: pd.DataFrame,
) -> list[str]:

    missing = []

    columns = set(
        dataframe.columns
    )

    for (
        logical_name,
        alternatives,
    ) in REQUIRED_FIELD_ALTERNATIVES.items():

        if not any(
            column in columns
            for column in alternatives
        ):

            missing.append(
                f"{logical_name} "
                f"({' or '.join(alternatives)})"
            )

    return missing


def normalize_partnership(
    row: Mapping[str, Any],
) -> Dict[str, Any]:

    return {

        "company": str(
            _first_value(
                row,
                [
                    "company",
                    "company_name",
                ],
                "Unknown Company",
            )
        ).strip(),

        "partner": str(
            _first_value(
                row,
                [
                    "partner",
                    "partner_name",
                ],
                "Unknown Partner",
            )
        ).strip(),

        "contact_name": str(
            _first_value(
                row,
                [
                    "contact_name",
                    "partner_contact",
                ],
                "",
            )
        ).strip(),

        "country": str(
            _first_value(
                row,
                [
                    "country",
                ],
                "",
            )
        ).strip(),

        "region": str(
            _first_value(
                row,
                [
                    "region",
                ],
                "",
            )
        ).strip(),

        "industry": str(
            _first_value(
                row,
                [
                    "industry",
                ],
                "Other",
            )
        ).strip(),

        "partner_type": str(
            _first_value(
                row,
                [
                    "partner_type",
                ],
                "Other",
            )
        ).strip(),

        "strategic_goal": str(
            _first_value(
                row,
                [
                    "strategic_goal",
                ],
                "Explore a mutually relevant commercial opportunity",
            )
        ).strip(),

        "market_overlap": _normalized_key(
            _first_value(
                row,
                [
                    "market_overlap",
                ],
                "medium",
            )
        ),

        "deal_value_usd": _safe_float(
            _first_value(
                row,
                [
                    "deal_value_usd",
                    "estimated_deal_value_usd",
                    "partnership_value_usd",
                ],
                0,
            )
        ),

        "relationship_signal": _normalized_key(
            _first_value(
                row,
                [
                    "relationship_signal",
                    "engagement_signal",
                ],
                "cold",
            )
        ),

        "execution_complexity": _normalized_key(
            _first_value(
                row,
                [
                    "execution_complexity",
                ],
                "medium",
            )
        ),

        "source_score": _first_value(
            row,
            [
                "score",
                "commercial_score",
            ],
            None,
        ),

        "source_tier": str(
            _first_value(
                row,
                [
                    "tier",
                    "priority_tier",
                ],
                "",
            )
        ).strip(),

        "source_recommended_action": str(
            _first_value(
                row,
                [
                    "recommended_action",
                ],
                "",
            )
        ).strip(),

        "source_score_rationale": str(
            _first_value(
                row,
                [
                    "score_rationale",
                ],
                "",
            )
        ).strip(),
    }


# ============================================================
# SCORING HELPERS
# ============================================================

def _lookup_score(
    value: Any,
    mapping: Mapping[str, float],
    default: float,
) -> float:

    normalized_mapping = {

        _normalized_key(
            key
        ): float(
            score
        )

        for key, score
        in mapping.items()
    }

    return round(

        normalized_mapping.get(
            _normalized_key(
                value
            ),
            float(
                default
            ),
        ),

        1,
    )


def score_opportunity_value(
    value: float,
    target_value: float,
) -> float:

    if target_value <= 0:

        return 0.0

    score = (
        max(
            float(
                value
            ),
            0.0,
        )
        / target_value
    ) * 100

    return round(
        min(
            score,
            100.0,
        ),
        1,
    )


# ============================================================
# EXPLAINABLE PARTNERSHIP SCORING
# ============================================================

def score_components(
    partnership: Mapping[str, Any],
    config: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:

    active_config = build_runtime_config(
        base_config=(
            config
            if config is not None
            else DEFAULT_CONFIG
        )
    )

    normalized = normalize_partnership(
        partnership
    )

    raw_scores = {

        "region_fit": _lookup_score(
            normalized["region"],
            active_config[
                "region_scores"
            ],
            55,
        ),

        "industry_alignment": _lookup_score(
            normalized["industry"],
            active_config[
                "industry_scores"
            ],
            50,
        ),

        "market_access": _lookup_score(
            normalized[
                "market_overlap"
            ],
            active_config[
                "market_overlap_scores"
            ],
            40,
        ),

        "relationship_strength": _lookup_score(
            normalized[
                "relationship_signal"
            ],
            active_config[
                "relationship_scores"
            ],
            35,
        ),

        "opportunity_value": score_opportunity_value(
            normalized[
                "deal_value_usd"
            ],
            active_config[
                "deal_value_target_usd"
            ],
        ),

        "partner_type_fit": _lookup_score(
            normalized[
                "partner_type"
            ],
            active_config[
                "partner_type_scores"
            ],
            60,
        ),

        "execution_feasibility": _lookup_score(
            normalized[
                "execution_complexity"
            ],
            active_config[
                "execution_complexity_scores"
            ],
            70,
        ),
    }

    weights = active_config[
        "weights"
    ]

    weighted_contributions = {

        component: round(
            raw_scores[
                component
            ]
            * weights[
                component
            ],
            2,
        )

        for component
        in weights
    }

    total_score = round(

        sum(
            weighted_contributions.values()
        ),

        1,
    )

    return {

        "raw_scores": (
            raw_scores
        ),

        "weighted_contributions": (
            weighted_contributions
        ),

        "weights": (
            weights
        ),

        "total_score": (
            total_score
        ),

        "deal_value_target_usd": (
            active_config[
                "deal_value_target_usd"
            ]
        ),
    }


# ============================================================
# FIT TIERS
# ============================================================

def partnership_tier(
    score: float,
    config: Optional[Mapping[str, Any]] = None,
) -> str:

    active_config = build_runtime_config(
        base_config=(
            config
            if config is not None
            else DEFAULT_CONFIG
        )
    )

    thresholds = active_config[
        "tier_thresholds"
    ]

    if score >= thresholds[
        "strategic_fit"
    ]:

        return "Strategic Fit"

    if score >= thresholds[
        "promising_fit"
    ]:

        return "Promising Fit"

    if score >= thresholds[
        "exploratory_fit"
    ]:

        return "Exploratory Fit"

    return "Low Fit"


def priority_level(
    score: float,
) -> str:

    if score >= 80:
        return "High"

    if score >= 60:
        return "Medium"

    return "Low"


# ============================================================
# PARTNERSHIP ARCHETYPES
# ============================================================

def classify_partnership_archetype(
    partner_type: str,
    strategic_goal: str = "",
) -> str:

    text = (
        f"{partner_type} "
        f"{strategic_goal}"
    ).lower()

    if any(
        keyword in text
        for keyword in [
            "distributor",
            "reseller",
            "channel",
        ]
    ):

        return "Channel Partnership"

    if any(
        keyword in text
        for keyword in [
            "technology",
            "integration",
            "platform",
            "software",
        ]
    ):

        return "Technology Alliance"

    if any(
        keyword in text
        for keyword in [
            "government",
            "institutional",
            "public sector",
        ]
    ):

        return "Institutional Partnership"

    if any(
        keyword in text
        for keyword in [
            "referral",
            "introducer",
            "introduction",
        ]
    ):

        return "Referral Partnership"

    if any(
        keyword in text
        for keyword in [
            "market entry",
            "representative",
            "local partner",
            "market access",
            "expansion",
        ]
    ):

        return "Market Access Partnership"

    return "Strategic Alliance"


def recommended_partnership_model(
    archetype: str,
) -> str:

    mapping = {

        "Channel Partnership": (
            "Evaluate reseller, distribution "
            "or co-selling structure."
        ),

        "Technology Alliance": (
            "Evaluate integration, co-solution "
            "or joint GTM structure."
        ),

        "Institutional Partnership": (
            "Evaluate institutional collaboration, "
            "program partnership or structured B2G engagement."
        ),

        "Referral Partnership": (
            "Evaluate referral, introduction "
            "or lead-sharing structure."
        ),

        "Market Access Partnership": (
            "Evaluate local representation, "
            "market-entry support, distribution "
            "or commercial access model."
        ),

        "Strategic Alliance": (
            "Evaluate a strategic alliance "
            "or joint commercial initiative based "
            "on complementary capabilities."
        ),
    }

    return mapping.get(
        archetype,
        mapping[
            "Strategic Alliance"
        ],
    )


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def recommended_action(
    partnership: Mapping[str, Any],
    score: float,
) -> str:

    normalized = normalize_partnership(
        partnership
    )

    relationship = normalized[
        "relationship_signal"
    ]

    if (
        score >= 80
        and relationship == "hot"
    ):

        return (
            "Schedule an executive discovery call "
            "and prepare a joint value hypothesis."
        )

    if score >= 80:

        return (
            "Prioritize targeted partner research, "
            "identify the strongest introduction path "
            "and propose a strategic discovery call."
        )

    if (
        score >= 60
        and relationship
        in {
            "hot",
            "warm",
        }
    ):

        return (
            "Send a targeted partnership introduction "
            "and validate mutual priorities, commercial "
            "value and decision context."
        )

    if score >= 60:

        return (
            "Develop a partnership hypothesis, "
            "validate strategic relevance and build "
            "relationship momentum before proposing "
            "a formal partnership motion."
        )

    if score >= 50:

        return (
            "Validate strategic fit and value exchange "
            "before allocating significant partnership "
            "development resources."
        )

    return (
        "Keep the opportunity in nurture and monitor "
        "for stronger timing, relationship signals "
        "or strategic relevance."
    )


# ============================================================
# STRATEGIC INTERPRETATION
# ============================================================

def strategic_interpretation(
    partnership: Mapping[str, Any],
    score: float,
    archetype: str,
) -> str:

    normalized = normalize_partnership(
        partnership
    )

    signals = []

    if normalized[
        "market_overlap"
    ] == "high":

        signals.append(
            "strong market overlap"
        )

    if normalized[
        "relationship_signal"
    ] == "hot":

        signals.append(
            "strong relationship momentum"
        )

    elif normalized[
        "relationship_signal"
    ] == "warm":

        signals.append(
            "an existing relationship signal"
        )

    if normalized[
        "execution_complexity"
    ] == "low":

        signals.append(
            "relatively favorable execution conditions"
        )

    if score >= 80:

        strength = "strong"

    elif score >= 65:

        strength = "promising"

    elif score >= 50:

        strength = "exploratory"

    else:

        strength = "limited"

    signal_text = (

        ", ".join(
            signals
        )

        if signals

        else (
            "a mixed set of commercial signals"
        )
    )

    return (
        f"This opportunity shows {strength} "
        f"partnership potential with {signal_text}. "
        f"The current partnership archetype is "
        f"{archetype}. "
        f"The commercial team should validate "
        f"the value exchange, decision context "
        f"and practical partnership motion "
        f"before commitment."
    )


# ============================================================
# EXPANSION POTENTIAL
# ============================================================

def expansion_potential(
    partnership: Mapping[str, Any],
) -> str:

    normalized = normalize_partnership(
        partnership
    )

    region = normalized[
        "region"
    ]

    partner_type = normalized[
        "partner_type"
    ]

    if region:

        return (
            f"The opportunity may support commercial "
            f"access or expansion in {region}, "
            f"particularly if the "
            f"{partner_type.lower()} relationship "
            f"can provide relevant market access, "
            f"credibility or execution support. "
            f"This should be validated before treating "
            f"expansion potential as confirmed."
        )

    return (
        "Expansion potential cannot be assessed "
        "confidently from the available regional data "
        "and should be validated through discovery."
    )


# ============================================================
# PARTNERSHIP THESIS
# ============================================================

def partnership_thesis(
    partnership: Mapping[str, Any],
    archetype: str,
) -> str:

    normalized = normalize_partnership(
        partnership
    )

    return (
        f"Hypothesis to validate: "
        f"{normalized['company']} and "
        f"{normalized['partner']} may have a relevant "
        f"{archetype.lower()} opportunity around the "
        f"objective to "
        f"{normalized['strategic_goal'].lower()}. "
        f"The estimated commercial value is "
        f"USD {normalized['deal_value_usd']:,.0f}, "
        f"subject to validation."
    )


# ============================================================
# EXPLAINABILITY
# ============================================================

def score_rationale(
    components: Mapping[str, Any],
) -> str:

    labels = {

        "region_fit": (
            "Region Fit"
        ),

        "industry_alignment": (
            "Industry Alignment"
        ),

        "market_access": (
            "Market Access"
        ),

        "relationship_strength": (
            "Relationship Strength"
        ),

        "opportunity_value": (
            "Opportunity Value"
        ),

        "partner_type_fit": (
            "Partner Type Fit"
        ),

        "execution_feasibility": (
            "Execution Feasibility"
        ),
    }

    parts = []

    for (
        key,
        raw_score,
    ) in components[
        "raw_scores"
    ].items():

        weight = components[
            "weights"
        ][
            key
        ]

        contribution = components[
            "weighted_contributions"
        ][
            key
        ]

        parts.append(

            f"{labels[key]}: "
            f"{raw_score:.1f}/100 × "
            f"{weight * 100:.0f}% = "
            f"{contribution:.1f}"
        )

    return " | ".join(
        parts
    )


# ============================================================
# OUTREACH HANDOFF
# ============================================================

def outreach_handoff_context(
    partnership: Mapping[str, Any],
    score: float,
    tier: str,
    action: str,
    archetype: str,
) -> str:

    normalized = normalize_partnership(
        partnership
    )

    return (
        f"Partnership opportunity: "
        f"{normalized['company']} + "
        f"{normalized['partner']}. "
        f"Archetype: {archetype}. "
        f"Partnership score: {score:.1f}. "
        f"Tier: {tier}. "
        f"Relationship signal: "
        f"{normalized['relationship_signal']}. "
        f"Recommended internal action: "
        f"{action}"
    )


# ============================================================
# SINGLE PARTNERSHIP EVALUATION
# ============================================================

def evaluate_partnership(
    partnership: Mapping[str, Any],
    config: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:

    normalized = normalize_partnership(
        partnership
    )

    components = score_components(
        normalized,
        config=config,
    )

    score = components[
        "total_score"
    ]

    tier = partnership_tier(
        score,
        config=config,
    )

    priority = priority_level(
        score
    )

    archetype = classify_partnership_archetype(
        normalized[
            "partner_type"
        ],
        normalized[
            "strategic_goal"
        ],
    )

    partnership_model = (
        recommended_partnership_model(
            archetype
        )
    )

    action = recommended_action(
        normalized,
        score,
    )

    interpretation = (
        strategic_interpretation(
            normalized,
            score,
            archetype,
        )
    )

    expansion = (
        expansion_potential(
            normalized
        )
    )

    thesis = (
        partnership_thesis(
            normalized,
            archetype,
        )
    )

    rationale = (
        score_rationale(
            components
        )
    )

    handoff = (
        outreach_handoff_context(
            normalized,
            score,
            tier,
            action,
            archetype,
        )
    )

    return {

        **normalized,

        "partnership_fit_score": (
            score
        ),

        "fit_tier": (
            tier
        ),

        "priority_level": (
            priority
        ),

        "partnership_archetype": (
            archetype
        ),

        "recommended_partnership_model": (
            partnership_model
        ),

        "recommended_action": (
            action
        ),

        "strategic_interpretation": (
            interpretation
        ),

        "expansion_potential": (
            expansion
        ),

        "partnership_thesis": (
            thesis
        ),

        "score_rationale": (
            rationale
        ),

        "score_breakdown": (
            components
        ),

        "outreach_handoff_context": (
            handoff
        ),
    }


# ============================================================
# PIPELINE RANKING
# ============================================================

def rank_partnerships(
    dataframe: pd.DataFrame,
    config: Optional[Mapping[str, Any]] = None,
) -> pd.DataFrame:

    missing = (
        validate_partnership_dataframe(
            dataframe
        )
    )

    if missing:

        raise ValueError(
            "Missing required partnership fields: "
            + ", ".join(
                missing
            )
        )

    records = [

        evaluate_partnership(
            row.to_dict(),
            config=config,
        )

        for _, row
        in dataframe.iterrows()
    ]

    ranked = pd.DataFrame(
        records
    )

    if ranked.empty:

        return ranked

    ranked = ranked.sort_values(

        by=[
            "partnership_fit_score",
            "deal_value_usd",
        ],

        ascending=[
            False,
            False,
        ],

    ).reset_index(
        drop=True
    )

    return ranked
