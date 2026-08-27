from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from assessment.services import (
    clear_assessment,
    compute_result,
    get_assessment,
    save_assessment,
    start_assessment,
    symptom_summary,
)
from questionnaire.constants import PAPER_EXAMPLE_SYMPTOMS, SAFETY_DISCLAIMER
from questionnaire.forms import ConsentForm, SafetyScreenForm, SymptomQuestionnaireForm


def _require_assessment(request, *, min_step: str | None = None):
    data = get_assessment(request.session)
    if not data:
        messages.warning(request, "Please start from the landing page.")
        return None, redirect("core:landing")
    return data, None


class StartAssessmentView(View):
    def post(self, request):
        mode = request.POST.get("mode", "interactive")
        if mode not in {"paper_example", "interactive"}:
            mode = "interactive"
        clear_assessment(request.session)
        start_assessment(request.session, mode=mode)
        return redirect("assessment:consent")


class ResetAssessmentView(View):
    """Clear the current demonstration session and return to the landing page."""

    def post(self, request):
        clear_assessment(request.session)
        messages.info(
            request,
            "Questionnaire reset. You can start again with the illustrative reference case or an interactive session.",
        )
        return redirect("core:landing")

    def get(self, request):
        # Allow link-style reset as well (bookmark / reviewer convenience).
        return self.post(request)


class ConsentView(View):
    template_name = "assessment/consent.html"

    def get(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        form = ConsentForm(initial=data.get("consent") or None)
        return render(
            request,
            self.template_name,
            {"form": form, "disclaimer": SAFETY_DISCLAIMER, "assessment": data},
        )

    def post(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        form = ConsentForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form, "disclaimer": SAFETY_DISCLAIMER, "assessment": data},
            )
        data["consent"] = form.cleaned_data
        data["disclaimer_acknowledged"] = True
        data["step"] = "safety"
        save_assessment(request.session, data)
        return redirect("assessment:safety")


class SafetyView(View):
    template_name = "assessment/safety.html"

    def get(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        if not data.get("disclaimer_acknowledged"):
            return redirect("assessment:consent")
        form = SafetyScreenForm(initial=data.get("safety") or None)
        return render(
            request,
            self.template_name,
            {"form": form, "disclaimer": SAFETY_DISCLAIMER, "assessment": data},
        )

    def post(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        form = SafetyScreenForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form, "disclaimer": SAFETY_DISCLAIMER, "assessment": data},
            )
        data["safety"] = form.cleaned_data
        data["safety_override"] = form.any_positive()
        data["step"] = "safety_stop" if data["safety_override"] else "questionnaire"
        save_assessment(request.session, data)
        if data["safety_override"]:
            data["result"] = compute_result(data)
            data["completed_at"] = data["result"]["generated_at"]
            data["step"] = "complete"
            save_assessment(request.session, data)
            return redirect("reports:report")
        return redirect("assessment:questionnaire")


class QuestionnaireView(View):
    template_name = "assessment/questionnaire.html"

    def get(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        if not data.get("disclaimer_acknowledged"):
            return redirect("assessment:consent")
        if data.get("safety_override"):
            return redirect("reports:report")
        if not data.get("safety"):
            return redirect("assessment:safety")

        initial = data.get("symptoms") or (
            PAPER_EXAMPLE_SYMPTOMS if data.get("mode") == "paper_example" else None
        )
        form = SymptomQuestionnaireForm(initial=initial)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "disclaimer": SAFETY_DISCLAIMER,
                "assessment": data,
                "readonly_paper": data.get("mode") == "paper_example",
            },
        )

    def post(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        if data.get("safety_override"):
            return redirect("reports:report")

        form = SymptomQuestionnaireForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "disclaimer": SAFETY_DISCLAIMER,
                    "assessment": data,
                    "readonly_paper": False,
                },
            )
        data["symptoms"] = form.cleaned_data
        data["model_inputs"] = form.to_model_inputs()
        data["step"] = "review"
        save_assessment(request.session, data)
        return redirect("assessment:review")


class ReviewView(View):
    template_name = "assessment/review.html"

    def get(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        if not data.get("symptoms"):
            return redirect("assessment:questionnaire")
        return render(
            request,
            self.template_name,
            {
                "disclaimer": SAFETY_DISCLAIMER,
                "assessment": data,
                "symptom_rows": symptom_summary(data.get("symptoms") or {}),
            },
        )

    def post(self, request):
        data, err = _require_assessment(request)
        if err:
            return err
        action = request.POST.get("action", "calculate")
        if action == "edit":
            return redirect("assessment:questionnaire")
        data["result"] = compute_result(data)
        data["completed_at"] = data["result"]["generated_at"]
        data["step"] = "complete"
        save_assessment(request.session, data)
        return redirect("reports:report")
