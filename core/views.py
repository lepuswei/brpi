from django.shortcuts import render
from django.views import View

from questionnaire.constants import SAFETY_DISCLAIMER


class LandingView(View):
    def get(self, request):
        return render(
            request,
            "core/landing.html",
            {"disclaimer": SAFETY_DISCLAIMER},
        )


class AboutView(View):
    def get(self, request):
        return render(
            request,
            "core/about.html",
            {"disclaimer": SAFETY_DISCLAIMER},
        )
