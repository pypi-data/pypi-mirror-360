# Django
from django.conf import settings
from django.utils.translation import gettext_lazy as _

GATHER_STATISTICS_DURING_QUIZ = getattr(
    settings, "DJANGO_EASY_QUIZ_GATHER_STATISTICS_DURING_QUIZ", False
)

SAVE_QUIZZES_RESULTS = getattr(settings, "DJANGO_EASY_QUIZ_SAVE_QUIZZES_RESULTS", False)

GATHER_STATISTICS = getattr(settings, "DJANGO_EASY_QUIZ_GATHER_STATISTICS", False)

SAVE_PDF = getattr(settings, "DJANGO_EASY_QUIZ_SAVE_PDF", False)

RELAUNCH_BUTTON = getattr(settings, "DJANGO_EASY_QUIZ_RELAUNCH_BUTTON", False)

PDF_FILE_NAME = getattr(
    settings, "DJANGO_EASY_QUIZ_PDF_FILE_NAME", _("quiz_summary.pdf")
)

PDF_LOGO = getattr(settings, "DJANGO_EASY_QUIZ_PDF_LOGO", "logo.png")
