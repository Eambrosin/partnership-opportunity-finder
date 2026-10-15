# Route-to-Market & Partner Intelligence

### Partner Qualification | Market Access | Route-to-Market Readiness | Execution Feasibility

**Operational focus:** Route-to-Market & Partner Intelligence

[![Live App](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://partnership-opportunity-finder-eambrosin.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![Commercial Intelligence](https://img.shields.io/badge/Commercial%20Intelligence-PARTNER-8250df)
[![Python CI](https://github.com/Eambrosin/partnership-opportunity-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/Eambrosin/partnership-opportunity-finder/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/Release-v3.0.0-success)](https://github.com/Eambrosin/partnership-opportunity-finder/releases/tag/v3.0.0)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

A Commercial Intelligence application for evaluating, ranking and operationalizing distributors, sales agents, technical partners and other route-to-market relationships using transparent scoring, market-access signals and execution feasibility.

> **A strategically attractive partner is not automatically an executable partnership.**

A Commercial Mandate can be restored automatically from the shared private workspace or loaded as portable JSON to keep client, corridor, product, target market and commercial-objective context consistent with IDENTIFY, PRIORITIZE and ENGAGE.

**[Launch the live application](https://partnership-opportunity-finder-eambrosin.streamlit.app/)**

---

## Business Problem

Partnership decisions are often driven by reputation, introductions or broad strategic narratives without enough structure.

Typical problems include:

- unclear evaluation criteria
- overvaluing brand recognition
- weak visibility into market-access contribution
- execution complexity ignored during early-stage evaluation
- partnership models chosen before fit is understood
- inconsistent comparison across partner candidates
- no explicit next action after the evaluation

The platform turns partnership evaluation into an explainable decision workflow.

---


## Ambrosin Commercial Mandate Workspace

PARTNER is the route-to-market branch of the shared **Commercial Mandate Workspace**.

A saved mandate can be selected directly or opened from IDENTIFY / PRIORITIZE through an opaque **mandate_id**. After **Private Workspace Access** is granted, PARTNER restores the canonical client, corridor, product, target market and route-to-market context from the private Supabase-backed workspace.

Portable Commercial Mandate JSON remains available as a fallback / override.

When a mandate is active but no partner pipeline has been supplied, PARTNER **does not load demo partnerships into the live mandate**. It waits for a mandate-specific partner / route-to-market CSV.

Recommended progression:

```text
IDENTIFY / PRIORITIZE
        ↓
      PARTNER
        ↓
route-to-market due diligence
        ↓
      ENGAGE
        ↓
partner development / opportunity / reporting
```

---

## Partnership Workflow

```text
PARTNER CANDIDATE
        ↓
STRATEGIC FIT
        +
MARKET ACCESS
        +
RELATIONSHIP CONTEXT
        +
EXECUTION FEASIBILITY
        ↓
EXPLAINABLE SCORE
        ↓
PARTNERSHIP ARCHETYPE
        ↓
RECOMMENDED MODEL
        ↓
NEXT COMMERCIAL ACTION
```

The purpose is not to automate partnership decisions. It is to make commercial reasoning visible and comparable.

---

## Current Interface

The current live interface is organized around:

1. **Partnership Pipeline** — restore a saved Commercial Mandate, optionally load portable JSON and upload a mandate-specific partner CSV.
2. **Commercial Mandate Workspace** — keep client, corridor, product and counterparty focus visible throughout partner evaluation.
3. **Partnership Model** — configure priority regions, industries, partner types and scoring logic.
4. **Partner Ranking** — compare strategic fit, market access, relationship context and execution feasibility.
5. **Route-to-Market Due Diligence** — assess customer base, import capability, technical service, after-sales, installation, field service, financial capacity, management commitment and exclusivity conflicts.
6. **Execution Handoff** — move validated partner candidates into ENGAGE under the same mandate.

---

---

## Core Capabilities

- configurable partnership strategy
- explainable weighted scoring
- strategic-fit assessment
- regional / market-access context
- relationship-strength signals
- opportunity-value context
- execution-feasibility assessment
- partner-type fit
- commercial-priority classification
- partnership archetypes
- recommended partnership models
- next-best commercial action
- executive dashboard
- opportunity mapping
- partnership brief / handoff
- shared private Ambrosin Commercial Mandate Workspace
- automatic mandate restoration through `mandate_id`
- interactive Route-to-Market Due Diligence
- explicit due-diligence gap tracking
- CSV input compatibility
- automated tests and GitHub Actions CI
- full-history secret scanning

---

## Partnership Intelligence Model

The platform can evaluate dimensions such as:

**Region Fit**  
How relevant is the partner to the geographic strategy?

**Industry Alignment**  
Does the partner operate where the commercial proposition is strongest?

**Market Access**  
Can the partner unlock customers, channels, stakeholders or distribution?

**Relationship Strength**  
What level of existing access or credibility is already present?

**Opportunity Value**  
What commercial upside could the relationship create?

**Partner Type Fit**  
Does the organization fit the intended partnership motion?

**Execution Feasibility**  
Can both sides realistically operationalize the relationship?

Weights remain configurable so the model can reflect the partnership strategy rather than impose a universal formula.

---

## Route-to-Market Readiness

Beyond strategic fit, PARTNER can now evaluate practical route-to-market readiness using optional evidence around:

- geographic coverage
- relevant customer base
- technical-service capability
- after-sales capability
- installation / commissioning capability
- spare-parts capability
- field-service coverage
- industrial reference base
- import capability
- regulatory capability
- sales-force capability
- financial capacity
- management commitment
- pilot willingness
- exclusivity conflicts

When these fields are available, the app produces a separate **Route-to-Market Readiness** assessment and explicit due-diligence gaps.

This does not replace partner due diligence. It helps distinguish a commercially interesting partner from one that can realistically support execution.

---

## Interactive Due Diligence Workspace

The selected partner can be assessed directly inside the app using a Route-to-Market Due Diligence workspace.

The workspace captures evidence around:

- geographic coverage
- relevant customer base
- sales-force capability
- import capability
- financial capacity
- technical-service capability
- after-sales capability
- installation / commissioning capability
- spare-parts capability
- field-service coverage
- industrial reference base
- regulatory / market-entry capability
- management commitment
- pilot / market-development willingness
- competing representation or exclusivity conflicts

Unknown values remain outside the readiness score and are surfaced as explicit gaps.

The enriched partner record can be exported for continued validation or downstream engagement.

---

## Explainable Decision Logic

```text
CONFIGURED STRATEGY
      ↓
OBSERVED / PROVIDED PARTNER INPUTS
      ↓
WEIGHTED DIMENSIONS
      ↓
SCORE BREAKDOWN
      ↓
COMMERCIAL PRIORITY
      ↓
PARTNERSHIP MODEL
      ↓
NEXT ACTION
```

The score is a decision-support mechanism, not a substitute for due diligence or negotiation.

---

## Partnership Archetypes

Depending on the commercial context, the system can support archetypes such as:

- channel partnership
- market-access partnership
- referral partnership
- operational partnership
- technology alliance
- institutional partnership
- strategic alliance

The recommended archetype is intended to make the commercial hypothesis explicit before execution begins.

---

## From Evaluation to Execution

The output can be translated into:

- target partner shortlist
- initial outreach angle
- recommended relationship model
- due-diligence questions
- pilot structure
- governance requirements
- next commercial action

For deeper execution frameworks, see:

**[Business Development Frameworks & Playbooks](https://github.com/Eambrosin/bd-frameworks-and-playbooks)**

That repository includes a Partner Due Diligence Checklist, Distributor Selection Scorecard and market-entry execution playbooks.

---


## Architecture

```text
app.py
  ↓
commercial_mandate.py
  ↓
workspace_persistence.py / mandate_workspace.py
  ↓
partnership strategy configuration
  ↓
partnership_engine.py
  ↓
route-to-market readiness / due diligence
  ↓
explainable scoring + partner model
  ↓
ENGAGE handoff
```

The decision logic remains deterministic and inspectable. Shared cloud persistence restores the mandate context but does not replace partner-specific evidence or due diligence.

---

## Testing

The repository includes automated tests covering the partnership engine and scoring behavior.

Run locally:

```bash
python -m pytest -q
```

GitHub Actions runs CI on pushes and pull requests to `main`.

---

## Running Locally

```bash
git clone https://github.com/Eambrosin/partnership-opportunity-finder.git
cd partnership-opportunity-finder
pip install -r requirements.txt
streamlit run app.py
```

---


## Current Version

**v3.0.0 — Route-to-Market & Partner Intelligence**

Version 3.0 is the current stable release of PARTNER. It positions the application as the route-to-market and execution-readiness branch of the shared Commercial Mandate Workspace.

Key release capabilities include:

- shared private Commercial Mandate persistence
- automatic `mandate_id` restoration
- mandate-safe partner pipeline behavior
- no demo-data mixing in active mandates
- strategic-fit and market-access scoring
- Route-to-Market Readiness
- technical service / after-sales / import capability assessment
- financial capacity and management-commitment evidence
- exclusivity and competing-representation validation
- explicit due-diligence gaps
- direct ENGAGE handoff under the same mandate

**[View v3.0.0 Release](https://github.com/Eambrosin/partnership-opportunity-finder/releases/tag/v3.0.0)**  
[Release Notes](docs/RELEASE_NOTES_v3.0.0.md)

---

## Documentation

- [v3.0.0 Release Notes](docs/RELEASE_NOTES_v3.0.0.md)
- [Detailed Technical Reference](docs/TECHNICAL_REFERENCE.md)
- [Tests](tests/)
- [Commercial Intelligence Portfolio](https://github.com/Eambrosin)

---

## Limitations

This is a portfolio and strategic decision-support application.

It does not replace:

- partner due diligence
- legal review
- financial review
- contract negotiation
- regulatory validation
- management judgment

---

## Portfolio Context

This project is the **PARTNER / ROUTE-TO-MARKET** layer of the Commercial Intelligence portfolio:

```text
IDENTIFY / Partner Universe → PARTNER → ENGAGE
```

It operates alongside the account-development workflow:

```text
IDENTIFY → PRIORITIZE → ENGAGE
```

**IDENTIFY:** [Market Entry & Opportunity Intelligence](https://github.com/Eambrosin/opportunity-discovery-intelligence)  
**ENGAGE:** [Business Development Execution & Outreach](https://github.com/Eambrosin/outreach-sequence-generator)  
**Portfolio:** [github.com/Eambrosin](https://github.com/Eambrosin)

---

## Author

**Eduardo Ambrosin**  
International Business Development | Strategic Partnerships | GTM | Commercial Intelligence
