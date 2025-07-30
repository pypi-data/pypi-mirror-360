# Django
from django.conf import settings
from django.urls import path
from django.utils.translation import gettext_lazy as _

# Local application / specific library imports
from .views.interpretation import InterpretationQuizView
from .views.misc import DisplayPdfView
from .views.weightedanswers import WeightedAnswersQuizView

urlpatterns = [
    path(
        _("weighted-answers/<int:pk>/"),
        WeightedAnswersQuizView.as_view(),
        name="weighted_answers_quiz",
    ),
    path(
        _("interpretation/<int:pk>/"),
        InterpretationQuizView.as_view(),
        name="interpretation_quiz",
    ),
]

if getattr(settings, "DJANGO_EASY_QUIZ_SAVE_PDF", False):
    urlpatterns += [
        path(
            "pdf/<uuid:identifier>", DisplayPdfView.as_view(), name="quiz_download_pdf"
        ),
    ]
