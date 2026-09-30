from django.urls import path

from . import views

app_name = "onlinecourse"

urlpatterns = [
    path("submit/<int:course_id>/", views.submit, name="submit"),
    path(
        "exam-result/<int:course_id>/",
        views.show_exam_result,
        name="show_exam_result",
    ),
]
