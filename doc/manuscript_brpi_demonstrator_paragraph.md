# BRPI research demonstrator (manuscript draft text)

Suggested subsection title: **BRPI research demonstrator**

Suggested figure placement: after this paragraph (or at the end of the Methods / Software subsection).

---

## Manuscript paragraph (copy-ready)

To make the proposed bivariate workflow tangible for method discussion and usability evaluation, we implemented a web-based **BRPI research demonstrator** (Django 5.2) that presents frequency and intensity as separate questionnaire dimensions, applies an explicit safety/alarm-feature gate before any calculation, and returns an illustrative probability from a versioned prediction engine that is kept independent of the user interface. In demonstration mode the application does not collect personally identifying information; responses are held only for the interactive session. Any positive safety response stops probability estimation and displays a neutral prompt for professional assessment rather than a GERD prediction. For the fictional manuscript case (HF = 5, HI = 6, RF = 4, RI = 5, N = 2, P = 1, S = 1, E = 1), the demonstrator reproduces the illustrative logistic output (η ≈ 1.86; probability ≈ 0.87) and labels the corresponding high-probability *demonstration* zone, together with ranked equation contributors and a patient-specific heartburn-frequency curve generated while other inputs are held fixed (**Figure X**). The software is an implementation and communication artifact only: coefficients remain illustrative, interactive sessions do not fabricate statistical uncertainty intervals, and the demonstrator is not a validated clinical prediction model or diagnostic device.

---

## Figure legends

**Figure X. BRPI research demonstrator.**  
**(A)** Landing page of the research prototype, offering paper-example and interactive exploration modes and displaying the required research-only disclaimer.  
**(B)** Illustrative paper-example output: probability with demonstration zones (panel A of the report graphic) and the patient-specific heartburn-frequency curve with the entered frequency marked (panel B). Zones at 0.20 and 0.80 and the prewritten 0.74–0.94 interval are illustrative only and are not clinically validated cutoffs or calculated confidence intervals.

Alternative single-panel legend if only the report graphic is used:

**Figure X. Illustrative output of the BRPI research demonstrator for the fictional manuscript case.**  
(A) Probability on the demonstration action-zone scale. (B) Heartburn days varied from 0 to 7 with other responses fixed; diamond/marker indicates the entered frequency (HF = 5). Labels emphasise research-only, non-validated status.

---

## Files for the journal/production team

| File | Content |
|---|---|
| `doc/figures/figure_brpi_demonstrator_landing.png` | Landing-page screenshot (UI overview) |
| `doc/figures/figure_brpi_demonstrator_report.svg` | Paper-example probability + frequency curve (vector) |

Suggested composite for submission: place the landing screenshot above or beside the SVG report graphic as panels A and B of a single multi-panel figure.
