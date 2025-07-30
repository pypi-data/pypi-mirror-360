# Django
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Third party
from import_export.admin import ExportActionModelAdmin

# Project
from django_easy_quiz.models import (
    InterpretationQuiz,
    InterpretationQuizQuestion,
    MoreInfoAnswer,
    MoreInfoQuestion,
    MoreInfoQuiz,
    SavedQuiz,
    WeightedAnswersQuiz,
    WeightedAnswersQuizConclusion,
    WeightedAnswersQuizQuestion,
)
from django_easy_quiz.settings import GATHER_STATISTICS
from django_easy_quiz.utils import (
    admin_error_lacks_answer,
    admin_error_min_max_conclusion,
)


def nb_of_questions(obj):
    try:
        return str(len(obj.weightedanswersquizquestion_set.all()))
    except AttributeError:
        return str(len(obj.interpretationquizquestion_set.all()))


class WeightedAnswersQuizConclusionAdminInline(admin.StackedInline):
    model = WeightedAnswersQuizConclusion
    extra = 1
    min_num = 1

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("min_points", "max_points"),
                    "description",
                ),
            },
        ),
    )


class WeightedAnswersQuizQuestionAdminInline(admin.StackedInline):
    model = WeightedAnswersQuizQuestion
    extra = 1
    min_num = 1
    question_number_count = 0
    readonly_fields = ("question_number",)

    fieldsets = (
        (
            None,
            {
                "fields": ("question_number", "label", "multiple_answers"),
            },
        ),
        (
            _("Answer 1"),
            {
                "fields": (
                    "answer_1",
                    "points_answer_1",
                ),
            },
        ),
        (
            _("Answer 2"),
            {
                "fields": (
                    "answer_2",
                    "points_answer_2",
                ),
            },
        ),
        (
            _("Answer 3"),
            {
                "fields": (
                    "answer_3",
                    "points_answer_3",
                ),
            },
        ),
        (
            _("Answer 4"),
            {
                "fields": (
                    "answer_4",
                    "points_answer_4",
                ),
            },
        ),
        (
            _("Answer 5"),
            {
                "fields": (
                    "answer_5",
                    "points_answer_5",
                ),
            },
        ),
        (
            _("Answer 6"),
            {
                "fields": (
                    "answer_6",
                    "points_answer_6",
                ),
            },
        ),
        (
            _("Answer 7"),
            {
                "fields": (
                    "answer_7",
                    "points_answer_7",
                ),
            },
        ),
        (
            _("Answer 8"),
            {
                "fields": (
                    "answer_8",
                    "points_answer_8",
                ),
            },
        ),
        (
            _("Answer 9"),
            {
                "fields": (
                    "answer_9",
                    "points_answer_9",
                ),
            },
        ),
        (
            _("Answer 10"),
            {
                "fields": (
                    "answer_10",
                    "points_answer_10",
                ),
            },
        ),
    )

    @admin.display(description="")
    def question_number(self, obj):
        self.question_number_count += 1
        return _("Question number") + " " + str(self.question_number_count)


@admin.register(WeightedAnswersQuiz)
class WeightedAnswersQuizAdmin(admin.ModelAdmin):
    if GATHER_STATISTICS:
        fieldsets = (
            (
                None,
                {
                    "fields": (
                        "name",
                        "questions_random",
                        "answers_random",
                        "show_score_summary",
                        "description",
                        "more_info_quiz",
                    ),
                },
            ),
        )
    else:
        fieldsets = (
            (
                None,
                {
                    "fields": (
                        "name",
                        "questions_random",
                        "answers_random",
                        "show_score_summary",
                        "description",
                    ),
                },
            ),
        )

    list_display = (
        "id",
        "name",
        nb_of_questions,
        "questions_random",
        "answers_random",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "questions_random",
        "answers_random",
        "create_date",
    )
    search_fields = ("name",)

    inlines = [
        WeightedAnswersQuizQuestionAdminInline,
        WeightedAnswersQuizConclusionAdminInline,
    ]

    def save_formset(self, request, form, formset, change):
        """
        Save formset, BUT we will launch some checks before:
            - check that no conclusion have min_points > max_points
            - check that all conclusions create only one (enclosed) number sequence and that the min(answers_points_sum) & max(answers_points_sum) are within its bounds
        """
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        # if checkbox "Delete" is ticked then delete questions
        for obj in formset.deleted_objects:
            obj.delete()

        # question formset is treated before conclusion, so in conclusion formset we can get the quiz, the questions, and the conclusion (using the formset.cleaned_data)
        if "WeightedAnswersQuizConclusionFormFormSet" in str(type(formset)):
            min_points_sum = 0
            max_points_sum = 0
            conclusions_combinations = []

            try:
                for question in (
                    formset[0]
                    .cleaned_data["quiz"]
                    .weightedanswersquizquestion_set.all()
                ):
                    all_points = [
                        question.points_answer_1,
                        question.points_answer_2,
                        question.points_answer_3
                        if question.points_answer_3 is not None
                        else 0,
                        question.points_answer_4
                        if question.points_answer_4 is not None
                        else 0,
                        question.points_answer_5
                        if question.points_answer_5 is not None
                        else 0,
                        question.points_answer_6
                        if question.points_answer_6 is not None
                        else 0,
                    ]

                    min_points_sum += min(all_points)
                    max_points_sum += max(all_points)
            except TypeError:
                nb_answers = 0
                if (
                    question.answer_1 is not (None or "")
                    and question.points_answer_1 is not None
                ):
                    nb_answers += 1
                if (
                    question.answer_2 is not (None or "")
                    and question.points_answer_2 is not None
                ):
                    nb_answers += 1
                if (
                    question.answer_3 is not (None or "")
                    and question.points_answer_3 is not None
                ):
                    nb_answers += 1
                if (
                    question.answer_4 is not (None or "")
                    and question.points_answer_4 is not None
                ):
                    nb_answers += 1
                if (
                    question.answer_5 is not (None or "")
                    and question.points_answer_5 is not None
                ):
                    nb_answers += 1
                if (
                    question.answer_6 is not (None or "")
                    and question.points_answer_6 is not None
                ):
                    nb_answers += 1
                admin_error_lacks_answer(request, question.label, nb_answers)

            for conclusion in formset.cleaned_data:
                if "min_points" in conclusion and "max_points" in conclusion:
                    if conclusion["min_points"] > conclusion["max_points"]:
                        # there is a problem, so we create a message with an extra tag using this function:
                        admin_error_min_max_conclusion(
                            request,
                            conclusion["min_points"],
                            conclusion["max_points"],
                            conclusion["description"],
                        )
                    conclusions_combinations.append(
                        [conclusion["min_points"], conclusion["max_points"]]
                    )
        # we need to save formset even if it have errors, because django needs its id somewhere later, and we don't want to make the user have to re-type the answers & conclusions
        formset.save_m2m()

    def response_add(self, request, obj, post_url_continue=None):
        """
        Method to get url to redirect after having created a new quiz:
            - Redirect to list view (using super) if there's no message with extra tag "easy_quiz_error".
            - Redirect to change view if a message with extra tag "easy_quiz_error" exist.
        """
        storage = messages.get_messages(request)
        for message in storage:
            if message.extra_tags == "easy_quiz_error":
                storage.used = False
                return HttpResponseRedirect(
                    reverse(
                        "admin:{}_{}_change".format(
                            obj._meta.app_label, obj._meta.model_name
                        ),
                        args=[obj.id],
                    )
                )
        storage.used = False
        return super().response_change(request, obj)

    def response_change(self, request, obj):
        """
        Method to get url to redirect after having modified a quiz:
            - Redirect to list view (using super) if there's no message with extra tag "easy_quiz_error".
            - Redirect to change view if a message with extra tag "easy_quiz_error" exist.
        """
        storage = messages.get_messages(request)
        for message in storage:
            if message.extra_tags == "easy_quiz_error":
                storage.used = False
                return HttpResponseRedirect(
                    reverse(
                        "admin:{}_{}_change".format(
                            obj._meta.app_label, obj._meta.model_name
                        ),
                        args=[obj.id],
                    )
                )
        storage.used = False

        return super().response_change(request, obj)


# InterpretationQuiz


class InterpretationQuizQuestionAdminInline(admin.StackedInline):
    model = InterpretationQuizQuestion
    extra = 1
    min_num = 1
    question_number_count = 0
    readonly_fields = ("question_number",)

    fieldsets = (
        (
            None,
            {
                "fields": (("question_number", "label"),),
                "description": _("Do not forget to write conclusions!"),
            },
        ),
        (
            _("Answer 1 (■)"),
            {
                "classes": ("collapse",),
                "fields": ("answer_1",),
            },
        ),
        (
            _("Answer 2 (▲)"),
            {
                "classes": ("collapse",),
                "fields": ("answer_2",),
            },
        ),
        (
            _("Answer 3 (◆)"),
            {
                "classes": ("collapse",),
                "fields": ("answer_3",),
            },
        ),
        (
            _("Answer 4 (●)"),
            {
                "classes": ("collapse",),
                "fields": ("answer_4",),
            },
        ),
    )

    @admin.display(description="")
    def question_number(self, obj):
        self.question_number_count += 1
        return _("Question number") + " " + str(self.question_number_count)


@admin.register(InterpretationQuiz)
class InterpretationQuizAdmin(admin.ModelAdmin):
    if GATHER_STATISTICS:
        fieldsets = (
            (
                None,
                {
                    "fields": (
                        "name",
                        "questions_random",
                        "answers_random",
                        "description",
                        "more_info_quiz",
                    ),
                },
            ),
            (
                _("Conclusions"),
                {
                    "classes": ("collapse",),
                    "fields": (
                        "conclusion_max_1",
                        "conclusion_max_2",
                        "conclusion_max_3",
                        "conclusion_max_4",
                    ),
                },
            ),
        )
    else:
        fieldsets = (
            (
                None,
                {
                    "fields": (
                        "name",
                        "questions_random",
                        "answers_random",
                        "description",
                    ),
                },
            ),
            (
                _("Conclusions"),
                {
                    "classes": ("collapse",),
                    "fields": (
                        "conclusion_max_1",
                        "conclusion_max_2",
                        "conclusion_max_3",
                        "conclusion_max_4",
                    ),
                },
            ),
        )

    list_display = (
        "id",
        "name",
        nb_of_questions,
        "questions_random",
        "answers_random",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "questions_random",
        "answers_random",
        "create_date",
    )
    search_fields = ("name",)

    inlines = [
        InterpretationQuizQuestionAdminInline,
    ]


# activate stats only if activated in settings (default = False)
if GATHER_STATISTICS:

    @admin.register(SavedQuiz)
    class SavedQuizAdmin(ExportActionModelAdmin, admin.ModelAdmin):
        def has_change_permission(self, request, obj=None):
            return False

        def has_add_permission(self, request, obj=None):
            return False

        readonly_fields = [field.name for field in SavedQuiz._meta.get_fields()]

        list_display = ("quiz_type", "quiz_ended", "uuid")

        fields = (
            "quiz_type",
            "quiz_ended",
            "answers_admin",
            "conclusion_points_admin",
            "conclusion_admin",
            "more_infos_admin",
        )

        @admin.display(description=_("Answers"))
        def answers_admin(self, obj):
            answers_txt = "<ul>"
            for answers in obj.answers:
                answers_txt += f"<li>{answers['question']['label']}<ul>"
                if "answers" in answers:  # weighted answers quiz
                    for answer in answers["answers"]:
                        answers_txt += f"<li>{strip_tags(answer)}</li>"
                else:
                    answers_txt += f"<li>{strip_tags(answers['question']['answer_1'])}</li><li>{strip_tags(answers['question']['answer_2'])}</li><li>{strip_tags(answers['question']['answer_3'])}</li><li>{strip_tags(answers['question']['answer_4'])}</li>"
                answers_txt += "</ul></li>"
            if answers_txt == "<ul>":
                answers_txt += f"<li>{_('No answer recorded for this quiz.')}</li>"
            answers_txt += "</ul>"
            return mark_safe(answers_txt)

        @admin.display(description=_("Points"))
        def conclusion_points_admin(self, obj):
            if "points" in obj.conclusion:  # weighted_answers quiz
                return obj.conclusion["points"]
            return ""  # interpretation quiz

        @admin.display(description=_("Conclusion"))
        def conclusion_admin(self, obj):
            if "description" in obj.conclusion:  # weighted_answers quiz
                return mark_safe(obj.conclusion["description"])
            return mark_safe(obj.conclusion)  # interpretation quiz

        @admin.display(description=_("More infos"))
        def more_infos_admin(self, obj):
            more_infos_txt = "<ul>"
            for question in obj.more_infos:
                more_infos_txt += f"<li>{question['question']}<ul>"
                more_infos_txt += f"<li>{question['answer']}</li>"
                more_infos_txt += "</ul></li>"
            return mark_safe(more_infos_txt)


# activate more info questions only if activated in settings (default = False)
if GATHER_STATISTICS:

    class MoreInfoAnswerAdminInline(admin.StackedInline):
        model = MoreInfoAnswer

    @admin.register(MoreInfoQuestion)
    class MoreInfoQuestionAdmin(admin.ModelAdmin):
        inlines = [
            MoreInfoAnswerAdminInline,
        ]

        readonly_fields = ("quiz",)

    class MoreInfoQuestionAdminInline(admin.StackedInline):
        model = MoreInfoQuestion
        show_change_link = True

    @admin.register(MoreInfoQuiz)
    class MoreInfoQuizAdmin(admin.ModelAdmin):
        fieldsets = (
            (
                None,
                {
                    "fields": (("name"),),
                },
            ),
            (
                None,
                {
                    "fields": [],
                    "description": _(
                        "Save your questions first, and then you will be able to update each question to add answers."
                    ),
                },
            ),
        )

        inlines = [
            MoreInfoQuestionAdminInline,
        ]
