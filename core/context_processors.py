from django.shortcuts import render


def safety_banner(request):
    from questionnaire.constants import SAFETY_DISCLAIMER

    return {"SAFETY_DISCLAIMER": SAFETY_DISCLAIMER}
