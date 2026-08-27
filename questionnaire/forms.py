from django import forms

from questionnaire.constants import ASSOCIATION_MAP, INTENSITY_ANCHORS, SAFETY_ITEMS


class ConsentForm(forms.Form):
    age_confirmed = forms.BooleanField(
        label="I confirm that I am 18 years of age or older (interface testing).",
        required=True,
    )
    not_urgent_care = forms.BooleanField(
        label=(
            "I confirm that I am not using this tool for urgent clinical "
            "decision-making or to replace professional medical care."
        ),
        required=True,
    )
    disclaimer_acknowledged = forms.BooleanField(
        label=(
            "I have read and understand that this is a research prototype "
            "and must not be used for diagnosis or treatment."
        ),
        required=True,
    )


class SafetyScreenForm(forms.Form):
    """Alarm-feature screen. Any Yes stops probability calculation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, label in SAFETY_ITEMS:
            self.fields[key] = forms.ChoiceField(
                label=label,
                choices=[("no", "No"), ("yes", "Yes")],
                widget=forms.RadioSelect,
                required=True,
            )
        self.fields["comment"] = forms.CharField(
            label="Optional non-identifying comment",
            required=False,
            widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        )

    def any_positive(self) -> bool:
        return any(self.cleaned_data.get(key) == "yes" for key, _ in SAFETY_ITEMS)


def _days_field(label: str) -> forms.IntegerField:
    return forms.IntegerField(
        label=label,
        min_value=0,
        max_value=7,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 7}),
    )


def _intensity_field(label: str) -> forms.IntegerField:
    help_parts = "; ".join(f"{v}: {t.split('—', 1)[1].strip()}" for v, t in INTENSITY_ANCHORS)
    return forms.IntegerField(
        label=label,
        min_value=0,
        max_value=10,
        help_text=f"Anchors — {help_parts}",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 10}),
    )


class SymptomQuestionnaireForm(forms.Form):
    heartburn_days = _days_field("Heartburn — symptomatic days in the past 7 days")
    heartburn_episodes = forms.IntegerField(
        label="Heartburn — number of episodes (optional)",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )
    heartburn_intensity = _intensity_field("Heartburn — typical intensity (0–10)")

    regurgitation_days = _days_field("Regurgitation — symptomatic days in the past 7 days")
    regurgitation_episodes = forms.IntegerField(
        label="Regurgitation — number of episodes (optional)",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )
    regurgitation_intensity = _intensity_field("Regurgitation — typical intensity (0–10)")

    nocturnal_nights = _days_field("Nocturnal reflux — nights affected (0–7)")

    postprandial = forms.ChoiceField(
        label="Postprandial association",
        choices=[
            ("none", "None"),
            ("sometimes", "Sometimes"),
            ("most", "Most episodes"),
        ],
        widget=forms.RadioSelect,
    )
    supine_bending = forms.ChoiceField(
        label="Supine or bending association",
        choices=[
            ("none", "None"),
            ("sometimes", "Sometimes"),
            ("often", "Often"),
        ],
        widget=forms.RadioSelect,
    )

    epigastric_days = _days_field("Epigastric pain — days (0–7)")
    epigastric_intensity = _intensity_field("Epigastric pain — intensity (0–10)")

    nausea_days = _days_field("Nausea — days (0–7)")
    nausea_intensity = _intensity_field("Nausea — intensity (0–10)")

    response_certainty = forms.IntegerField(
        label="How certain are you that this reflects a typical week? (0–100%)",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100}),
    )

    ppi_use = forms.ChoiceField(
        label="Current PPI / acid-blocker use",
        choices=[("no", "No"), ("yes", "Yes"), ("unsure", "Unsure")],
        widget=forms.RadioSelect,
    )
    ppi_details = forms.CharField(
        label="PPI / acid-blocker details (optional, non-identifying)",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    prior_gerd_evidence = forms.ChoiceField(
        label="Prior GERD evidence (endoscopy, pH monitoring, etc.)",
        choices=[
            ("no", "No"),
            ("yes", "Yes"),
            ("uncertain", "Uncertain"),
        ],
        widget=forms.RadioSelect,
    )
    bmi = forms.CharField(
        label="BMI (optional research field)",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    pregnancy = forms.ChoiceField(
        label="Pregnancy (optional research field)",
        choices=[("no", "No"), ("yes", "Yes"), ("na", "Not applicable / prefer not to say")],
        required=False,
        initial="na",
        widget=forms.RadioSelect,
    )
    major_comorbidity = forms.CharField(
        label="Major comorbidity notes (optional, non-identifying)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    )

    def to_model_inputs(self) -> dict[str, float | int]:
        data = self.cleaned_data
        return {
            "HF": int(data["heartburn_days"]),
            "HI": int(data["heartburn_intensity"]),
            "RF": int(data["regurgitation_days"]),
            "RI": int(data["regurgitation_intensity"]),
            "N": int(data["nocturnal_nights"]),
            "P": ASSOCIATION_MAP[data["postprandial"]],
            "S": ASSOCIATION_MAP[data["supine_bending"]],
            "E": int(data["epigastric_days"]),
        }
