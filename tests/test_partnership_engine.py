import unittest

import pandas as pd

from partnership_engine import (
    DEFAULT_CONFIG,
    build_runtime_config,
    classify_partnership_archetype,
    evaluate_partnership,
    normalize_weights,
    rank_partnerships,
    validate_partnership_dataframe,
)


class PartnershipIntelligenceEngineTests(unittest.TestCase):

    def setUp(self):

        self.operational_partnership = {
            "company": "Gulf Trade Partners",
            "partner": "PortLink Logistics",
            "country": "UAE",
            "region": "MENA",
            "industry": "Logistics & Trade",
            "partner_type": "Operational Partner",
            "strategic_goal": "Improve cross-border trade execution",
            "market_overlap": "high",
            "deal_value_usd": 500000,
            "relationship_signal": "warm",
            "execution_complexity": "medium",
        }

        self.channel_partnership = {
            "company": "Continental Foods",
            "partner": "Andes Retail Network",
            "country": "Colombia",
            "region": "LATAM",
            "industry": "Agribusiness",
            "partner_type": "Distributor",
            "strategic_goal": "Expand regional distribution",
            "market_overlap": "high",
            "deal_value_usd": 220000,
            "relationship_signal": "hot",
            "execution_complexity": "medium",
        }

        self.low_priority_partnership = {
            "company": "Example Company",
            "partner": "Example Partner",
            "country": "Canada",
            "region": "NA",
            "industry": "Other",
            "partner_type": "Other",
            "strategic_goal": "Explore future collaboration",
            "market_overlap": "low",
            "deal_value_usd": 50000,
            "relationship_signal": "cold",
            "execution_complexity": "high",
        }

    def test_operational_partnership_default_score(self):

        result = evaluate_partnership(
            self.operational_partnership
        )

        self.assertEqual(
            result["partnership_fit_score"],
            89.2,
        )

        self.assertEqual(
            result["fit_tier"],
            "Strategic Fit",
        )

        self.assertEqual(
            result["priority_level"],
            "High",
        )

    def test_operational_partner_is_classified_correctly(self):

        archetype = classify_partnership_archetype(
            "Operational Partner",
            "Improve cross-border trade execution",
        )

        self.assertEqual(
            archetype,
            "Operational Partnership",
        )

    def test_distributor_is_channel_partnership(self):

        archetype = classify_partnership_archetype(
            "Distributor",
            "Expand regional distribution",
        )

        self.assertEqual(
            archetype,
            "Channel Partnership",
        )

    def test_priority_changes_when_strategic_threshold_changes(self):

        config = build_runtime_config(
            strategic_fit_threshold=90,
            promising_fit_threshold=65,
            exploratory_fit_threshold=50,
        )

        result = evaluate_partnership(
            self.operational_partnership,
            config=config,
        )

        self.assertEqual(
            result["partnership_fit_score"],
            89.2,
        )

        self.assertEqual(
            result["fit_tier"],
            "Promising Fit",
        )

        self.assertEqual(
            result["priority_level"],
            "Medium",
        )

    def test_priority_returns_to_high_with_default_threshold(self):

        config = build_runtime_config(
            strategic_fit_threshold=80,
            promising_fit_threshold=65,
            exploratory_fit_threshold=50,
        )

        result = evaluate_partnership(
            self.operational_partnership,
            config=config,
        )

        self.assertEqual(
            result["fit_tier"],
            "Strategic Fit",
        )

        self.assertEqual(
            result["priority_level"],
            "High",
        )

    def test_weights_are_normalized_to_one(self):

        weights = {
            "region_fit": 15,
            "industry_alignment": 15,
            "market_access": 20,
            "relationship_strength": 15,
            "opportunity_value": 15,
            "partner_type_fit": 10,
            "execution_feasibility": 10,
        }

        normalized = normalize_weights(
            weights
        )

        self.assertAlmostEqual(
            sum(
                normalized.values()
            ),
            1.0,
            places=6,
        )

    def test_non_100_weight_total_is_normalized(self):

        weights = {
            "region_fit": 30,
            "industry_alignment": 10,
            "market_access": 30,
            "relationship_strength": 10,
            "opportunity_value": 10,
            "partner_type_fit": 5,
            "execution_feasibility": 5,
        }

        normalized = normalize_weights(
            weights
        )

        self.assertAlmostEqual(
            sum(
                normalized.values()
            ),
            1.0,
            places=6,
        )

        self.assertAlmostEqual(
            normalized[
                "region_fit"
            ],
            0.30,
            places=6,
        )

    def test_all_zero_weights_raise_error(self):

        weights = {
            "region_fit": 0,
            "industry_alignment": 0,
            "market_access": 0,
            "relationship_strength": 0,
            "opportunity_value": 0,
            "partner_type_fit": 0,
            "execution_feasibility": 0,
        }

        with self.assertRaises(
            ValueError
        ):
            normalize_weights(
                weights
            )

    def test_invalid_threshold_order_raises_error(self):

        with self.assertRaises(
            ValueError
        ):
            build_runtime_config(
                strategic_fit_threshold=60,
                promising_fit_threshold=70,
                exploratory_fit_threshold=50,
            )

    def test_score_breakdown_contains_all_dimensions(self):

        result = evaluate_partnership(
            self.operational_partnership
        )

        raw_scores = result[
            "score_breakdown"
        ][
            "raw_scores"
        ]

        expected_dimensions = {
            "region_fit",
            "industry_alignment",
            "market_access",
            "relationship_strength",
            "opportunity_value",
            "partner_type_fit",
            "execution_feasibility",
        }

        self.assertEqual(
            set(
                raw_scores.keys()
            ),
            expected_dimensions,
        )

    def test_score_rationale_is_generated(self):

        result = evaluate_partnership(
            self.operational_partnership
        )

        rationale = result[
            "score_rationale"
        ]

        self.assertIn(
            "Region Fit",
            rationale,
        )

        self.assertIn(
            "Market Access",
            rationale,
        )

        self.assertIn(
            "Execution Feasibility",
            rationale,
        )

    def test_operational_model_is_recommended(self):

        result = evaluate_partnership(
            self.operational_partnership
        )

        recommendation = result[
            "recommended_partnership_model"
        ].lower()

        self.assertIn(
            "operational",
            recommendation,
        )

    def test_outreach_handoff_contains_partnership_context(self):

        result = evaluate_partnership(
            self.operational_partnership
        )

        handoff = result[
            "outreach_handoff_context"
        ]

        self.assertIn(
            "PortLink Logistics",
            handoff,
        )

        self.assertIn(
            "Operational Partnership",
            handoff,
        )

        self.assertIn(
            "High",
            handoff,
        )

    def test_partnership_thesis_is_marked_as_hypothesis(self):

        result = evaluate_partnership(
            self.operational_partnership
        )

        thesis = result[
            "partnership_thesis"
        ].lower()

        self.assertIn(
            "hypothesis to validate",
            thesis,
        )

    def test_weak_opportunity_is_not_high_priority(self):

        result = evaluate_partnership(
            self.low_priority_partnership
        )

        self.assertNotEqual(
            result[
                "priority_level"
            ],
            "High",
        )

    def test_pipeline_is_ranked_by_score(self):

        dataframe = pd.DataFrame(
            [
                self.low_priority_partnership,
                self.operational_partnership,
                self.channel_partnership,
            ]
        )

        ranked = rank_partnerships(
            dataframe
        )

        scores = ranked[
            "partnership_fit_score"
        ].tolist()

        self.assertEqual(
            scores,
            sorted(
                scores,
                reverse=True,
            ),
        )

    def test_operational_partnership_ranks_above_low_fit(self):

        dataframe = pd.DataFrame(
            [
                self.low_priority_partnership,
                self.operational_partnership,
            ]
        )

        ranked = rank_partnerships(
            dataframe
        )

        self.assertEqual(
            ranked.iloc[
                0
            ][
                "partner"
            ],
            "PortLink Logistics",
        )

    def test_valid_dataframe_has_no_missing_fields(self):

        dataframe = pd.DataFrame(
            [
                self.operational_partnership
            ]
        )

        missing = validate_partnership_dataframe(
            dataframe
        )

        self.assertEqual(
            missing,
            [],
        )

    def test_missing_partner_field_is_detected(self):

        invalid = dict(
            self.operational_partnership
        )

        invalid.pop(
            "partner"
        )

        dataframe = pd.DataFrame(
            [
                invalid
            ]
        )

        missing = validate_partnership_dataframe(
            dataframe
        )

        self.assertTrue(
            any(
                "partner" in item
                for item in missing
            )
        )

    def test_alternative_input_columns_are_supported(self):

        dataframe = pd.DataFrame(
            [
                {
                    "company_name": "Source Company",
                    "partner_name": "Target Partner",
                    "country": "Italy",
                    "region": "EU",
                    "industry": "Renewable Energy",
                    "partner_type": "Channel Partner",
                    "strategic_goal": "Expand distribution",
                    "market_overlap": "high",
                    "estimated_deal_value_usd": 200000,
                    "engagement_signal": "warm",
                }
            ]
        )

        ranked = rank_partnerships(
            dataframe
        )

        self.assertEqual(
            ranked.iloc[
                0
            ][
                "company"
            ],
            "Source Company",
        )

        self.assertEqual(
            ranked.iloc[
                0
            ][
                "partner"
            ],
            "Target Partner",
        )

    def test_default_weights_total_one(self):

        self.assertAlmostEqual(
            sum(
                DEFAULT_CONFIG[
                    "weights"
                ].values()
            ),
            1.0,
            places=6,
        )


if __name__ == "__main__":
    unittest.main()
