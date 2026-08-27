from django.shortcuts import redirect, render
from django.views import View

from assessment.services import get_assessment, safety_summary
from questionnaire.constants import SAFETY_DISCLAIMER


class ReportView(View):
    template_name = "reports/report.html"

    def get(self, request):
        data = get_assessment(request.session)
        if not data or not data.get("result"):
            return redirect("core:landing")
        result = data["result"]
        return render(
            request,
            self.template_name,
            {
                "disclaimer": SAFETY_DISCLAIMER,
                "assessment": data,
                "result": result,
                "safety_rows": safety_summary(data.get("safety") or {}),
                "print_mode": request.GET.get("print") == "1",
            },
        )


class PrintReportView(View):
    def get(self, request):
        return redirect("/report/?print=1")
