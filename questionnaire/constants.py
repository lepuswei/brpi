SAFETY_DISCLAIMER = (
    "Research prototype—not for clinical diagnosis or treatment. "
    "BRPI has not yet been trained or validated in patient cohorts. "
    "The displayed probabilities and thresholds are illustrative. "
    "This application must not delay urgent assessment, endoscopy, "
    "reflux monitoring, cardiac evaluation, or other clinically indicated care."
)

SAFETY_ITEMS = [
    ("dysphagia", "Difficulty swallowing (dysphagia)"),
    ("odynophagia", "Painful swallowing (odynophagia)"),
    ("gi_bleeding", "Gastrointestinal bleeding or black stool"),
    ("weight_loss", "Unexplained weight loss"),
    ("persistent_vomiting", "Persistent vomiting"),
    ("anemia", "Known anemia"),
    ("mass", "Abdominal or neck mass"),
    ("chest_pain", "Concerning chest pain or symptoms that may need cardiac assessment"),
]

INTENSITY_ANCHORS = [
    (0, "0 — none"),
    (3, "3 — noticeable without activity limitation"),
    (5, "5 — interferes with usual activity"),
    (7, "7 — marked limitation"),
    (10, "10 — worst imaginable"),
]

PAPER_EXAMPLE_SYMPTOMS = {
    "heartburn_days": 5,
    "heartburn_episodes": 8,
    "heartburn_intensity": 6,
    "regurgitation_days": 4,
    "regurgitation_episodes": 5,
    "regurgitation_intensity": 5,
    "nocturnal_nights": 2,
    "postprandial": "most",
    "supine_bending": "often",
    "epigastric_days": 1,
    "epigastric_intensity": 3,
    "nausea_days": 0,
    "nausea_intensity": 0,
    "response_certainty": 80,
    "ppi_use": "no",
    "ppi_details": "",
    "prior_gerd_evidence": "uncertain",
    "bmi": "",
    "pregnancy": "no",
    "major_comorbidity": "",
}

# Binary coding for illustrative equation (manuscript-style 0/1).
ASSOCIATION_MAP = {
    "none": 0,
    "sometimes": 1,
    "most": 1,
    "often": 1,
}
