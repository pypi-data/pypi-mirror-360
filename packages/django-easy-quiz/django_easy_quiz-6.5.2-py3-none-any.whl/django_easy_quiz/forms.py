# Django
from django import forms
from django.forms import ModelForm
from django.utils.safestring import mark_safe

# Local application / specific library imports
from .models import (
    InterpretationQuiz,
    InterpretationQuizQuestion,
    MoreInfoQuestion,
    MoreInfoQuiz,
    WeightedAnswersQuiz,
    WeightedAnswersQuizQuestion,
)


class PlainTextWidgetWithHiddenCopy(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self, "initial"):
            value = self.initial

        return mark_safe(
            (str(value) if value is not None else "-")
            + f"<input type='hidden' name='{name}' value='{value}'>"
        )


class InterpretationQuizForm(ModelForm):
    class Meta:
        model = InterpretationQuiz
        fields = [
            "questions",
        ]

    questions = forms.ModelMultipleChoiceField(
        queryset=InterpretationQuizQuestion.objects.all(),
        widget=PlainTextWidgetWithHiddenCopy,
        required=False,
    )


class WeightedAnswersQuizForm(ModelForm):
    class Meta:
        model = WeightedAnswersQuiz
        fields = [
            "questions",
        ]

    questions = forms.ModelMultipleChoiceField(
        queryset=WeightedAnswersQuizQuestion.objects.all(),
        widget=PlainTextWidgetWithHiddenCopy,
        required=False,
    )


class MoreInfoQuizForm(ModelForm):
    class Meta:
        model = MoreInfoQuiz
        fields = [
            "questions",
        ]

    questions = forms.ModelMultipleChoiceField(
        queryset=MoreInfoQuestion.objects.all(),
        widget=PlainTextWidgetWithHiddenCopy,
        required=False,
    )
