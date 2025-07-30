# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EasyQuizConfig(AppConfig):
    name = "django_easy_quiz"
    verbose_name = _("Easy Quiz")
