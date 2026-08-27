# BRPI Research Demonstrator: Django Model-Build Proposal

**Project status:** Conceptual research demonstrator—not a validated diagnostic device  
**Prepared:** 25 August 2026  
**Working title:** BRPI Research Demonstrator  
**Underlying concept:** Bivariate Reflux Probability Instrument (BRPI)

## 1. Purpose

Build a web-based research demonstrator showing how GERD symptom frequency and intensity can be retained as separate dimensions rather than converted into additive questionnaire points. The application should make the manuscript's proposed workflow tangible, support usability evaluation, and provide a foundation for future prospective research.

The first release must **not** diagnose GERD, recommend treatment, or claim that its probability estimates are clinically validated. It should be presented as an interactive methodological demonstration using fictional or non-identifiable data and explicitly illustrative coefficients.

## 2. Intended users

- Researchers evaluating the BRPI concept.
- Clinicians reviewing the proposed interface and workflow.
- Patients or members of the public participating in supervised usability testing.
- Study administrators managing questionnaire and model versions.

The public demonstration must not invite users to rely on the result for healthcare decisions.

## 3. Core safety statement

Display the following message prominently on the landing page, questionnaire, and report:

> **Research prototype—not for clinical diagnosis or treatment.** BRPI has not yet been trained or validated in patient cohorts. The displayed probabilities and thresholds are illustrative. This application must not delay urgent assessment, endoscopy, reflux monitoring, cardiac evaluation, or other clinically indicated care.

Require users to acknowledge this statement before beginning an interactive assessment.

## 4. Recommended technical architecture

### 4.1 Backend

- Python 3.12 or a later version supported by the selected Django release.
- **Django 5.2 LTS** for stability and extended security support.
- PostgreSQL in deployed research environments.
- SQLite only for local development and demonstration installations.
- Django templates for server-rendered pages.
- Django forms for validation and accessibility.
- A small JSON API may be added for interactive plots, but a separate REST framework is unnecessary for the minimum viable product.

### 4.2 Frontend

- Responsive HTML5 and accessible form controls.
- Bootstrap 5 or a similarly lightweight design system.
- Vanilla JavaScript or HTMX for conditional questions and plot updates.
- Plotly.js or Chart.js for probability gauges, curves, and bivariate surfaces.
- No single-page-application framework is required initially.

### 4.3 Deployment

- Environment variables for secrets and deployment configuration.
- Gunicorn or another production WSGI/ASGI server behind a TLS-enabled reverse proxy.
- Static-file collection and secure production settings.
- Docker support is desirable but not required for the first local prototype.
- No analytics, advertising scripts, or third-party patient-tracking services.

## 5. Proposed Django project structure

```text
brpi_demo/
├── manage.py
├── config/                 # settings, URLs, ASGI/WSGI
├── core/                   # landing page, acknowledgements, shared templates
├── questionnaire/          # item definitions, forms, safety screen, responses
├── assessment/             # workflow, validation, calculation orchestration
├── model_registry/         # versioned model specifications and engines
├── reports/                # result page, plots, printable report
├── research_admin/         # exports, study configuration, audit review
├── templates/
├── static/
├── tests/
└── docs/
```

Keep mathematical calculation code independent of Django views and database models. The same calculation engine should be testable from Python without starting a web server.

## 6. Required user workflow

### Step 1: Landing page

- Explain the BRPI concept in plain language.
- Distinguish frequency from intensity.
- Display the research-only warning.
- Offer two entry modes:
  - **Paper example:** automatically load the fictional case from the manuscript.
  - **Interactive exploration:** enter fictional or demonstration responses.

### Step 2: Intended-use and consent screen

- Confirm age 18 years or older for interface testing.
- Confirm that the tool is not being used for urgent clinical decision-making.
- Record acknowledgement of the research disclaimer.
- If research data are retained, present the approved study information and consent language. Do not imply that clicking a generic disclaimer constitutes research consent.

### Step 3: Safety screen

Ask about:

- dysphagia;
- odynophagia;
- gastrointestinal bleeding or black stool;
- unexplained weight loss;
- persistent vomiting;
- known anemia;
- abdominal or neck mass;
- concerning chest pain or symptoms requiring cardiac assessment.

If any safety item is positive:

1. stop the probability calculation;
2. display a neutral safety message advising prompt professional assessment;
3. do not estimate or display a GERD probability;
4. record `safety_override=True` in the session result;
5. never describe the override as a GERD prediction.

### Step 4: Seven-day symptom questionnaire

Collect the following separately:

| Domain | Field | Range or options |
|---|---|---|
| Heartburn | symptomatic days | 0–7 |
| Heartburn | episodes | non-negative integer, optional |
| Heartburn | intensity | 0–10 with anchors |
| Regurgitation | symptomatic days | 0–7 |
| Regurgitation | episodes | non-negative integer, optional |
| Regurgitation | intensity | 0–10 with anchors |
| Nocturnal reflux | nights | 0–7 |
| Postprandial association | none/sometimes/most episodes | ordinal |
| Supine or bending association | none/sometimes/often | ordinal |
| Epigastric pain | days and intensity | 0–7; 0–10 |
| Nausea | days and intensity | 0–7; 0–10 |
| Response certainty | typical-week certainty | 0–100% |
| Context | PPI/acid blocker use | yes/no/details |
| Context | prior GERD evidence | yes/no/uncertain |
| Context | BMI, pregnancy, major comorbidity | optional research fields |

Every intensity control must display anchors:

- 0: none;
- 3: noticeable without activity limitation;
- 5: interferes with usual activity;
- 7: marked limitation;
- 10: worst imaginable.

### Step 5: Review responses

- Present all inputs in a readable summary.
- Allow correction before calculation.
- Repeat that the calculation is illustrative.

### Step 6: Generate demonstration report

The report should contain:

- safety-screen status;
- model name and version;
- illustrative probability, when calculation is permitted;
- clearly labelled demonstration action zone;
- main positive and negative mathematical contributors;
- statement that contributors are associations within an illustrative equation, not causes;
- response-certainty value;
- patient-specific frequency curve;
- optional bivariate frequency–intensity surface;
- printable PDF or print-friendly HTML;
- timestamp and unique non-identifying session code.

## 7. Versioned model engine

Define a stable interface such as:

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Protocol


@dataclass(frozen=True)
class PredictionResult:
    probability: Decimal | None
    zone: str
    safety_override: bool
    contributors: Mapping[str, Decimal]
    model_name: str
    model_version: str
    uncertainty_lower: Decimal | None = None
    uncertainty_upper: Decimal | None = None
    uncertainty_method: str | None = None


class BRPIModel(Protocol):
    name: str
    version: str

    def predict(self, inputs: Mapping[str, float | int | bool]) -> PredictionResult:
        ...
```

Views must call this interface rather than containing coefficients or diagnostic logic. Model specifications should be immutable after release. A changed coefficient, threshold, or feature definition requires a new version.

## 8. Illustrative model for the prototype

Implement the exact manuscript demonstration equation as `IllustrativeLogisticModelV1`:

```text
eta = -6.60
      + 0.30 * HF
      + 0.20 * HI
      + 0.35 * RF
      + 0.24 * RI
      + 0.045 * HF * HI
      + 0.055 * RF * RI
      + 0.18 * N
      + 0.25 * P
      + 0.20 * S
      - 0.10 * E

probability = 1 / (1 + exp(-eta))
```

Definitions:

- `HF`: heartburn days, 0–7;
- `HI`: heartburn intensity, 0–10;
- `RF`: regurgitation days, 0–7;
- `RI`: regurgitation intensity, 0–10;
- `N`: nocturnal symptom nights, 0–7;
- `P`: postprandial association, coded 0 or 1 for the manuscript example;
- `S`: supine/bending association, coded 0 or 1 for the manuscript example;
- `E`: epigastric-pain days, 0–7.

These coefficients must be stored with metadata stating:

```text
validation_status = "illustrative_only"
clinical_use_permitted = false
training_dataset = null
calibration_dataset = null
```

### Demonstration zones

To reproduce the manuscript graphic only:

- below 0.20: low demonstration zone;
- 0.20 to below 0.80: indeterminate demonstration zone;
- 0.80 or above: high demonstration zone.

Every zone label must include “demonstration” or “illustrative.” These are not clinical cutoffs.

### Uncertainty

Do not calculate a confidence or credible interval from the illustrative logistic equation. In interactive mode, display:

> A statistically valid uncertainty interval is unavailable because this demonstration model has not been fitted to patient data.

The paper-example mode may reproduce the manuscript's fixed example interval of 0.74–0.94, but it must be labelled as a prewritten illustration rather than a calculated posterior interval.

## 9. Paper-example acceptance test

For the fictional manuscript case:

```text
HF=5, HI=6, RF=4, RI=5, N=2, P=1, S=1, E=1
```

the application must produce approximately:

```text
eta = 1.86
probability = 0.8653, displayed as 0.87
zone = high-probability demonstration zone
```

This should be implemented as an automated unit test.

## 10. Explainability design

For the illustrative model, calculate each equation term separately and rank its absolute contribution. Example terms include:

- heartburn frequency;
- heartburn intensity;
- heartburn frequency–intensity interaction;
- regurgitation frequency;
- regurgitation intensity;
- regurgitation interaction;
- nocturnal symptoms;
- postprandial association;
- positional association;
- epigastric-pain term.

Use wording such as:

> In this illustrative equation, frequent regurgitation and moderate-to-high intensity increased the displayed value most strongly.

Do not use causal wording such as “regurgitation caused the risk.”

## 11. Visualizations

### Required

1. Probability gauge from 0 to 1 with the three illustrative zones.
2. Patient-specific curve varying heartburn days from 0 to 7 while holding other responses fixed.
3. Marker showing the entered heartburn frequency.

### Optional

4. Regurgitation-specific curve.
5. Bivariate surface with days on one axis, intensity on the second, and illustrative probability on the third.
6. Two-dimensional response grid with an uncertainty ellipse reflecting response certainty.

Plots must include “Illustrative—not clinically validated” within or immediately below the graphic.

## 12. Suggested database models

### `QuestionnaireVersion`

- name;
- semantic version;
- status: draft/frozen/retired;
- item-definition JSON;
- created timestamp;
- frozen timestamp.

### `ModelVersion`

- name;
- semantic version;
- model class path;
- coefficient JSON or signed model artifact reference;
- predictor definitions;
- action-zone metadata;
- validation status;
- clinical-use flag;
- checksum;
- created and activated timestamps.

### `AssessmentSession`

- random UUID;
- mode: paper example/interactive/research;
- questionnaire version;
- model version;
- started and completed timestamps;
- disclaimer acknowledged;
- consent record, when applicable;
- completion status;
- no directly identifying information by default.

### `SafetyResponse`

- assessment session;
- one Boolean per safety item;
- optional non-identifying comment;
- override triggered;
- timestamp.

### `SymptomResponse`

- assessment session;
- item code;
- numeric or categorical value;
- unit;
- missing/unsure flag;
- response certainty;
- timestamp.

### `AssessmentResult`

- session;
- safety override;
- probability, nullable;
- zone;
- contributor JSON;
- uncertainty bounds, nullable;
- uncertainty method, nullable;
- full model-output JSON;
- generated timestamp.

### `AuditEvent`

- actor or anonymous session code;
- event type;
- object identifier;
- model and questionnaire versions;
- timestamp;
- minimal metadata without raw health information where possible.

## 13. Research-data boundaries

### Demonstration mode

- Do not retain responses after the session unless the user explicitly downloads a local report.
- Do not collect name, date of birth, email, telephone number, IP-derived location, or medical-record number.
- Mark sample data as synthetic.

### Approved research mode

- Enable only after ethics approval and a finalized protocol.
- Use coded participant identifiers.
- Store the re-identification key separately from the application database.
- Apply role-based access, encryption in transit, encrypted backups, retention rules, and documented data export.
- Maintain a data dictionary and provenance for every variable.

## 14. Security and privacy requirements

- Use Django's CSRF protection, secure session cookies, clickjacking protection, and automatic HTML escaping.
- Enforce HTTPS in deployed environments.
- Keep `DEBUG=False` in production.
- Store `SECRET_KEY` and database credentials in environment variables or a secrets manager.
- Apply least-privilege database credentials.
- Rate-limit public submission endpoints.
- Validate all ranges on both client and server.
- Never deserialize untrusted model objects.
- Log model versions and errors without logging raw questionnaire responses unnecessarily.
- Run Django's deployment checks before release.
- Define a breach-response and backup-restoration procedure before collecting research data.

## 15. Accessibility and human factors

- Meet WCAG 2.2 AA where feasible.
- Support keyboard-only navigation and screen readers.
- Do not rely on colour alone for zone meaning.
- Provide plain-language definitions of heartburn and regurgitation.
- Display units beside every numeric field.
- Provide “unsure” and “not applicable” where methodologically appropriate.
- Test on mobile, tablet, desktop, and printable paper-like layouts.
- Preserve responses when validation errors occur.
- Plan Chinese-language development through cognitive testing and cultural adaptation, not literal translation alone.

## 16. Administrative functions

The Django admin or a restricted research dashboard should allow authorized staff to:

- inspect questionnaire and model versions;
- freeze a questionnaire version;
- activate or retire a model version;
- view non-identifying session summaries;
- export research data as CSV with a data dictionary;
- inspect safety-override frequency;
- review calculation and application errors;
- verify model-artifact checksums.

Do not permit administrators to edit coefficients inside an already frozen model version.

## 17. Testing requirements

### Unit tests

- all field ranges and missing-value rules;
- safety override prevents prediction;
- exact paper-example calculation;
- zone boundary behavior at 0.20 and 0.80;
- stable contributor calculations;
- model-version immutability;
- no uncertainty interval for interactive illustrative predictions.

### Integration tests

- complete paper-example workflow;
- interactive workflow;
- positive safety-screen workflow;
- correction on review page;
- printable report;
- anonymous session expiration;
- research export permissions.

### Security tests

- unauthorized access to research administration;
- CSRF protection;
- range manipulation through direct POST requests;
- session isolation;
- production configuration checks.

### Usability tests

- comprehension of symptom definitions;
- ability to distinguish frequency from intensity;
- comprehension of the research disclaimer;
- recognition that alarm symptoms stop the calculation;
- comprehension of probability versus diagnosis;
- interpretation of the patient-specific curve.

## 18. Minimum viable product acceptance criteria

The MVP is complete when:

1. A user can select paper-example or interactive mode.
2. The safety screen always precedes symptom calculation.
3. Any positive safety response prevents probability output.
4. All questionnaire fields are validated server-side.
5. The paper example returns 0.87 using the manuscript equation.
6. Interactive results are labelled illustrative on every relevant page and printout.
7. No invented statistical uncertainty interval is displayed.
8. A patient-specific frequency curve is generated correctly.
9. Model and questionnaire versions are visible in the report.
10. Automated tests pass.
11. No personally identifying data are required in demonstration mode.
12. Production deployment checks pass before any hosted release.

## 19. Development phases

### Phase 1: Static demonstrator

- Landing page and disclaimer.
- Paper-example questionnaire and report.
- Exact illustrative equation.
- Probability gauge and patient curve.
- No persistent database responses.

### Phase 2: Interactive prototype

- Validated user-entered fictional responses.
- Safety override.
- Dynamic plots and contributor explanation.
- Print-friendly report.
- Versioned questionnaire and model metadata.

### Phase 3: Usability-research platform

- Ethics-approved consent workflow.
- Coded participant sessions.
- Research database and exports.
- Completion-time and missingness metrics.
- Optional randomized interface variants.

### Phase 4: Prospective model-development platform

- Reference-standard outcome capture or import.
- Locked analysis dataset.
- Separate statistical-training pipeline outside the production web process.
- Import of signed, versioned fitted-model artifacts.
- Internal validation and calibration reports.

### Phase 5: Externally validated clinical research software

- Temporal and geographic validation.
- Subgroup calibration assessment.
- Decision-curve analysis.
- Clinical-impact study.
- Formal regulatory and quality-management assessment before any diagnostic or treatment claim.

## 20. Explicitly out of scope for the first build

- Clinical diagnosis.
- Treatment or medication recommendations.
- A claim that BRPI is superior to GerdQ, RDQ, endoscopy, or reflux monitoring.
- Automated model retraining.
- Electronic health-record integration.
- Storage of identifiable patient records.
- A chatbot that interprets free-text symptoms.
- Replacement of clinician judgment or urgent-care pathways.
- Use of the illustrative interval as if statistically estimated.

## 21. Future fitted-model interface

When prospective data become available, model development should occur in a separate reproducible analysis repository. The web application should receive a frozen model artifact containing:

- predictor schema and units;
- missing-data policy;
- fitted coefficients or spline basis parameters;
- posterior samples or uncertainty representation;
- calibration parameters;
- intended population and exclusions;
- training and validation dataset identifiers;
- performance summary;
- model card;
- artifact checksum and approval record.

The application should reject an artifact if its predictor schema, checksum, or software compatibility version is invalid.

## 22. Standards and governance to consult

- TRIPOD+AI for transparent reporting of prediction-model development and validation.
- PROBAST or the applicable current extension for risk-of-bias assessment.
- STARD for diagnostic-accuracy study reporting.
- SPIRIT-AI and CONSORT-AI if the software is evaluated prospectively as an intervention.
- Applicable privacy, medical-device, clinical-research, and cybersecurity requirements in every deployment jurisdiction.
- FDA Clinical Decision Support Software guidance when considering US clinical use or diagnostic claims.

This proposal is a technical and research plan, not legal or regulatory advice.

## 23. Ready-to-paste prompt for an AI coding agent

> Build a Django 5.2 LTS project named `brpi_demo` from the attached BRPI Research Demonstrator specification. Implement only Phase 1 and Phase 2. The product is a research prototype and must never claim to diagnose or treat GERD. Use server-rendered Django templates, Django forms, Bootstrap 5, and minimal vanilla JavaScript or HTMX. Keep the calculation engine independent of Django views and implement a versioned `IllustrativeLogisticModelV1` using the exact equation in the specification. A positive alarm-feature response must stop calculation and display a safety message. Provide paper-example and interactive modes, a review page, an illustrative report, a probability gauge, a patient-specific heartburn-frequency curve, a print-friendly report, and complete automated tests. Do not collect personally identifying data. Do not fabricate an uncertainty interval for interactive predictions. Include setup instructions, environment-variable configuration, sample data, migrations, accessibility labels, security settings, and a README. Work incrementally: first show the proposed file tree and data models, then scaffold the project, implement tests before or alongside each feature, run the test suite, and report any assumptions.

## 24. Manuscript integration after prototype development

After a working prototype exists, add a short manuscript subsection titled **“BRPI research demonstrator”**. It should describe:

- the demonstrator's purpose as an implementation and usability artifact;
- its research-only status;
- the safety override;
- separation of the interface from the versioned prediction engine;
- reproducibility of the manuscript example;
- planned usability outcomes;
- the distinction between a software demonstration and a validated clinical prediction model.

Avoid presenting screenshots or software availability claims until the application and archived version actually exist.