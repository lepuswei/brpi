from django.urls import path

from assessment import views

app_name = "assessment"

urlpatterns = [
    path("start/", views.StartAssessmentView.as_view(), name="start"),
    path("reset/", views.ResetAssessmentView.as_view(), name="reset"),
    path("consent/", views.ConsentView.as_view(), name="consent"),
    path("safety/", views.SafetyView.as_view(), name="safety"),
    path("questionnaire/", views.QuestionnaireView.as_view(), name="questionnaire"),
    path("review/", views.ReviewView.as_view(), name="review"),
]
