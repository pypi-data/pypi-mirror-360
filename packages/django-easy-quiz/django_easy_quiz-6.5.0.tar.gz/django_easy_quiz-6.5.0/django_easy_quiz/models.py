# Standard Library
from uuid import uuid4

# Django
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

# Third party
from ckeditor_uploader.fields import RichTextUploadingField

# Quiz


class Quiz(models.Model):
    name = models.CharField(_("Quiz name"), max_length=1024)
    questions_random = models.BooleanField(
        default=False,
        verbose_name=_("Random questions"),
        help_text=_("Questions will be shown on random order."),
    )
    answers_random = models.BooleanField(
        default=False,
        verbose_name=_("Random answers"),
        help_text=_("Answers will be shown on random order."),
    )
    create_date = models.DateTimeField(auto_now_add=True)
    description = RichTextUploadingField()
    more_info_quiz = models.ForeignKey(
        "MoreInfoQuiz",
        default=None,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_("Will display this 'more info quiz' at the end of the main quiz."),
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        abstract = True


class WeightedAnswersQuiz(Quiz):
    show_score_summary = models.BooleanField(
        default=True, verbose_name=_("Show score in summary")
    )

    class Meta:
        verbose_name = _("Weighted Answers Quiz")
        verbose_name_plural = _("Weighted Answers Quizzes")

    def get_absolute_url(self):
        return reverse("weighted_answers_quiz", kwargs={"pk": self.pk})


class InterpretationQuiz(Quiz):
    conclusion_max_1 = RichTextUploadingField(
        verbose_name=_("Conclusion for max of ■:")
    )
    conclusion_max_2 = RichTextUploadingField(
        verbose_name=_("Conclusion for max of ▲:")
    )
    conclusion_max_3 = RichTextUploadingField(
        verbose_name=_("Conclusion for max of ◆:")
    )
    conclusion_max_4 = RichTextUploadingField(
        verbose_name=_("Conclusion for max of ●:")
    )

    class Meta:
        verbose_name = _("Interpretation Quiz")
        verbose_name_plural = _("Interpretation Quizzes")

    def get_absolute_url(self):
        return reverse("interpretation_quiz", kwargs={"pk": self.pk})


# Questions


class Question(models.Model):
    label = models.CharField(_("Question"), max_length=1024)

    class Meta:
        abstract = True


class WeightedAnswersQuizQuestion(Question):
    quiz = models.ForeignKey(WeightedAnswersQuiz, on_delete=models.CASCADE)
    label = models.CharField(verbose_name=_("Question"), max_length=1024)
    multiple_answers = models.BooleanField(
        default=False, verbose_name=_("More than one answer possible")
    )

    answer_1 = RichTextUploadingField(verbose_name=_("Answer 1"))
    points_answer_1 = models.IntegerField(verbose_name=_("Points for answer 1"))
    answer_2 = RichTextUploadingField(verbose_name=_("Answer 2"), null=True, blank=True)
    points_answer_2 = models.IntegerField(
        verbose_name=_("Points for answer 2"), null=True, blank=True
    )
    answer_3 = RichTextUploadingField(verbose_name=_("Answer 3"), null=True, blank=True)
    points_answer_3 = models.IntegerField(
        verbose_name=_("Points for answer 3"), null=True, blank=True
    )
    answer_4 = RichTextUploadingField(verbose_name=_("Answer 4"), null=True, blank=True)
    points_answer_4 = models.IntegerField(
        verbose_name=_("Points for answer 4"), null=True, blank=True
    )
    answer_5 = RichTextUploadingField(verbose_name=_("Answer 5"), null=True, blank=True)
    points_answer_5 = models.IntegerField(
        verbose_name=_("Points for answer 5"), null=True, blank=True
    )
    answer_6 = RichTextUploadingField(verbose_name=_("Answer 6"), null=True, blank=True)
    points_answer_6 = models.IntegerField(
        verbose_name=_("Points for answer 6"), null=True, blank=True
    )
    answer_7 = RichTextUploadingField(verbose_name=_("Answer 7"), null=True, blank=True)
    points_answer_7 = models.IntegerField(
        verbose_name=_("Points for answer 7"), null=True, blank=True
    )
    answer_8 = RichTextUploadingField(verbose_name=_("Answer 8"), null=True, blank=True)
    points_answer_8 = models.IntegerField(
        verbose_name=_("Points for answer 8"), null=True, blank=True
    )
    answer_9 = RichTextUploadingField(verbose_name=_("Answer 9"), null=True, blank=True)
    points_answer_9 = models.IntegerField(
        verbose_name=_("Points for answer 9"), null=True, blank=True
    )
    answer_10 = RichTextUploadingField(
        verbose_name=_("Answer 10"), null=True, blank=True
    )
    points_answer_10 = models.IntegerField(
        verbose_name=_("Points for answer 10"), null=True, blank=True
    )

    def __str__(self):
        quiz_name = ""
        # if self.quiz is not None:
        #     quiz_name = _("[in quizz ") + self.quiz.name + "] "
        return f"{quiz_name}{self.label}"

    def toJson(self):
        return {
            "label": self.label,
            "multiple_answers": self.multiple_answers,
            "answer_1": self.answer_1,
            "answer_2": self.answer_2,
            "answer_3": self.answer_3,
            "answer_4": self.answer_4,
            "answer_5": self.answer_5,
            "answer_6": self.answer_6,
            "points_answer_1": self.points_answer_1,
            "points_answer_2": self.points_answer_2,
            "points_answer_3": self.points_answer_3,
            "points_answer_4": self.points_answer_4,
            "points_answer_5": self.points_answer_5,
            "points_answer_6": self.points_answer_6,
        }

    class Meta:
        verbose_name = _("Weighted Answers Quiz Question")
        verbose_name_plural = _("Weighted Answers Quiz Questions")


class InterpretationQuizQuestion(Question):
    quiz = models.ForeignKey(InterpretationQuiz, on_delete=models.CASCADE)
    label = models.CharField(verbose_name=_("Question"), max_length=1024)

    answer_1 = RichTextUploadingField(verbose_name=_("Answer 1 (■)"))
    answer_2 = RichTextUploadingField(
        verbose_name=_("Answer 2 (▲)"), null=True, blank=True
    )
    answer_3 = RichTextUploadingField(
        verbose_name=_("Answer 3 (◆)"), null=True, blank=True
    )
    answer_4 = RichTextUploadingField(
        verbose_name=_("Answer 4 (●)"), null=True, blank=True
    )

    def __str__(self):
        quiz_name = ""
        # if self.quiz is not None:
        #     quiz_name = _("[in quizz ") + self.quiz.name + "] "
        return f"{quiz_name}{self.label}"

    def toJson(self):
        return {
            "label": self.label,
            "answer_1": f"■ - {self.answer_1}",
            "answer_2": f"▲ - {self.answer_2}",
            "answer_3": f"◆ - {self.answer_3}",
            "answer_4": f"● - {self.answer_4}",
        }

    class Meta:
        verbose_name = _("Interpretation Quiz Question")
        verbose_name_plural = _("Interpretation Quiz Questions")


# Answers


class Answer(models.Model):
    answer = RichTextUploadingField()

    def __str__(self):
        return _(f"Answer #{self.id}")

    class Meta:
        abstract = True


INTERPRETATION_QUESTION_CHOICES = (
    ("1", "■"),
    ("2", "▲"),
    ("3", "◆"),
    ("4", "●"),
)

# Conclusions/results


class QuizConclusion(models.Model):
    description = RichTextUploadingField()

    class Meta:
        abstract = True


class WeightedAnswersQuizConclusion(QuizConclusion):
    quiz = models.ForeignKey(WeightedAnswersQuiz, on_delete=models.CASCADE)
    min_points = models.IntegerField(_("Min amount of points (included)"))
    max_points = models.IntegerField(_("Max amount of points (included)"))

    def __str__(self):
        return _("Weighted Answers Quiz Conclusion") + " #" + str(self.id)

    class Meta:
        verbose_name = _("Weighted Answers Quiz Conclusion")
        verbose_name_plural = _("Weighted Answers Quiz Conclusions")


# Djangocms Plugins


class BasePlugin(models.Model):
    LEVEL_1 = "h1"
    LEVEL_2 = "h2"
    LEVEL_3 = "h3"
    LEVEL_4 = "h4"
    LEVEL_5 = "h5"
    LEVEL_6 = "h6"
    TITLE_LEVEL = [
        (LEVEL_1, _("Title level 1 (<h1>)")),
        (LEVEL_2, _("Title level 2 (<h2>)")),
        (LEVEL_3, _("Title level 3 (<h3>)")),
        (LEVEL_4, _("Title level 4 (<h4>)")),
        (LEVEL_5, _("Title level 5 (<h5>)")),
        (LEVEL_6, _("Title level 6 (<h6>)")),
    ]

    title_level = models.CharField(
        choices=TITLE_LEVEL, max_length=4, help_text=_("Title level")
    )
    short_description = models.CharField(
        _("Short description"),
        max_length=1024,
        null=True,
        blank=True,
    )
    button_text = models.CharField(
        _("Button text"),
        max_length=1024,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class SavedQuiz(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False)
    quiz_type = models.CharField(max_length=255)
    started_quiz = models.DateTimeField(auto_now_add=True)
    quiz_ended = models.BooleanField(default=False)
    answers = models.JSONField(default=dict)
    weighted_answers_quiz = models.ForeignKey(
        WeightedAnswersQuiz, null=True, blank=True, on_delete=models.PROTECT
    )
    interpretation_quiz = models.ForeignKey(
        InterpretationQuiz, null=True, blank=True, on_delete=models.PROTECT
    )
    interpretation_max_symbol = models.CharField(max_length=32, null=True, blank=True)
    conclusion = models.JSONField(default=dict)
    more_infos = models.JSONField(default=dict)

    class Meta:
        verbose_name = _("Saved Quiz")
        verbose_name_plural = _("Saved Quizzes")


class MoreInfoQuiz(models.Model):
    name = models.CharField(
        max_length=255, help_text=_("Will be displayed below the results.")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("More-Info Quiz")
        verbose_name_plural = _("More-Info Quizzes")


class MoreInfoQuestion(models.Model):
    label = models.CharField(max_length=255)
    quiz = models.ForeignKey(MoreInfoQuiz, on_delete=models.PROTECT)
    is_required = models.BooleanField(
        default=False, help_text=_("Is this question required?")
    )
    answer_is_txt = models.BooleanField(
        default=False,
        help_text=_(
            "Check this parameter to allow plain text answers instead of pre-defined answers."
        ),
    )
    answer_is_list = models.BooleanField(
        default=False,
        help_text=_(
            "Check this parameter to display a big list of answers using a select input and not radio buttons."
        ),
    )

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("More-Info Question")
        verbose_name_plural = _("More-Info Questions")


class MoreInfoAnswer(models.Model):
    question = models.ForeignKey(MoreInfoQuestion, on_delete=models.PROTECT)
    answer = models.CharField(max_length=512)

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name = _("More-Info Answer")
        verbose_name_plural = _("More-Info Answers")


try:
    # Third party
    from cms.models.pluginmodel import CMSPlugin

    class WeightedAnswersPlugin(BasePlugin, CMSPlugin):
        quiz = models.ForeignKey(
            WeightedAnswersQuiz, on_delete=models.SET_NULL, null=True
        )

        class Meta:
            verbose_name = _("Weighted Answers Quiz")
            verbose_name_plural = _("Weighted Answers Quizzes")

    class InterpretationPlugin(BasePlugin, CMSPlugin):
        quiz = models.ForeignKey(
            InterpretationQuiz, on_delete=models.SET_NULL, null=True
        )

        class Meta:
            verbose_name = _("Interpretation Quiz")
            verbose_name_plural = _("Interpretation Quizzes")

except ImportError:
    ...
