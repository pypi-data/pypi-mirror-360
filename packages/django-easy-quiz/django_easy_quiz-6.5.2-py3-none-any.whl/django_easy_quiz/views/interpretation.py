# Django
from django.views.generic import FormView

# Project
from django_easy_quiz.forms import InterpretationQuizForm
from django_easy_quiz.models import (
    INTERPRETATION_QUESTION_CHOICES,
    InterpretationQuiz,
    MoreInfoAnswer,
    MoreInfoQuestion,
    SavedQuiz,
)
from django_easy_quiz.settings import (
    GATHER_STATISTICS,
    GATHER_STATISTICS_DURING_QUIZ,
    PDF_FILE_NAME,
    RELAUNCH_BUTTON,
    SAVE_PDF,
    SAVE_QUIZZES_RESULTS,
)
from django_easy_quiz.utils import get_more_info_quiz_formset, get_quiz_and_formset


class InterpretationQuizView(FormView):
    form_class = InterpretationQuizForm
    model = InterpretationQuiz
    template_name = "django_easy_quiz/interpretation_form.html"

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz, formset = get_quiz_and_formset(
            InterpretationQuiz,
            InterpretationQuizForm,
            self.kwargs["pk"],
        )

        if SAVE_QUIZZES_RESULTS:
            if (
                "saved_quiz" not in self.request.POST
                or not self.request.POST["saved_quiz"].isdigit()
            ):
                saved_quiz_id = SavedQuiz.objects.create(
                    quiz_type=str(quiz),
                    quiz_ended=False,
                ).id
                context["saved_quiz_id"] = saved_quiz_id

        if GATHER_STATISTICS:
            if quiz.more_info_quiz is not None:
                context["more_info_quiz"] = quiz.more_info_quiz

        context["quiz"] = quiz
        context["formset"] = formset
        context["pdf_file_name"] = PDF_FILE_NAME

        return context

    def handle_first_post_request(self, request, form, *args, **kwargs):
        if form.is_valid():
            context = self.get_context_data()

            answers = []  # noqa: FURB138
            for input in form.data:
                if "question_" in input:
                    # question_id = input.split("_")[1]
                    # answer_id = int(form.data[input])
                    # store position in INTERPRETATION_QUESTION_CHOICES:
                    answers.append(int(form.data[input]))
            quiz = InterpretationQuiz.objects.get(id=int(kwargs["pk"]))

            # return conclusion equal to max answers in INTERPRETATION_QUESTION_CHOICES (1=■, 2=▲, 3=◆, 4=●)
            # TODO: check for equality ?
            max_occurrences = max(answers, key=answers.count)
            context["symbol"] = INTERPRETATION_QUESTION_CHOICES[max_occurrences - 1][1]
            if max_occurrences == 1:
                context["conclusion"] = quiz.conclusion_max_1
            if max_occurrences == 2:
                context["conclusion"] = quiz.conclusion_max_2
            if max_occurrences == 3:
                context["conclusion"] = quiz.conclusion_max_3
            if max_occurrences == 4:
                context["conclusion"] = quiz.conclusion_max_4

            final_quiz = []
            questions = quiz.interpretationquizquestion_set.all()
            index = 0
            for question in questions:
                final_quiz.append(
                    {
                        "question": question.toJson(),
                        "answer": getattr(question, f"answer_{answers[index]}", ""),
                    }
                )
                index += 1

            # we might already have data for more_info_quiz here, so treat it here too
            more_info_quiz_answers = []
            for question in form.data:
                answer_object = None
                question_id = (
                    question.split("_")[2]
                    if question.startswith("more_question_")
                    else ""
                )
                if question_id.isdigit():
                    answer = form.data[question]
                    question = MoreInfoQuestion.objects.get(id=question_id).label
                    if answer.isdigit():
                        answer_object = MoreInfoAnswer.objects.get(id=answer).answer
                    else:
                        answer_object = answer
                    more_info_quiz_answers.append(
                        {"question": question, "answer": answer_object}
                    )

            if "saved_quiz" in request.POST and request.POST["saved_quiz"].isdigit():
                saved_quiz = SavedQuiz.objects.get(id=request.POST["saved_quiz"])
                saved_quiz.quiz_ended = True
                saved_quiz.interpretation_quiz = quiz
                saved_quiz.interpretation_max_symbol = context["symbol"]
                saved_quiz.answers = final_quiz
                saved_quiz.conclusion = context["conclusion"]
                saved_quiz.answers = final_quiz
                saved_quiz.more_infos = more_info_quiz_answers
                saved_quiz.save()

                context["saved_quiz_id"] = saved_quiz.id

                if GATHER_STATISTICS:
                    if quiz.more_info_quiz is not None:
                        formset = get_more_info_quiz_formset(quiz.more_info_quiz)
                        context["more_info_quiz"] = formset
                        context["more_info_quiz_after_main_quiz"] = True

            if GATHER_STATISTICS_DURING_QUIZ and "more_info_quiz" in context:
                context["more_info_quiz_after_main_quiz"] = False

            if SAVE_PDF and "saved_quiz_id" in context:
                context["weasyprint_download_uuid"] = saved_quiz.uuid

            context["relaunch_button"] = RELAUNCH_BUTTON

            return self.render_to_response(context)
        return self.form_invalid(form)

    def handle_second_post_request(self, request, form, *args, **kwargs):
        context = self.get_context_data()
        if "saved_quiz" in request.POST and request.POST["saved_quiz"].isdigit():
            saved_quiz = SavedQuiz.objects.get(id=request.POST["saved_quiz"])
            context["quiz"] = saved_quiz.interpretation_quiz
            context["final_quiz"] = saved_quiz.answers
            context["conclusion"] = saved_quiz.conclusion
            context["relaunch_button"] = RELAUNCH_BUTTON
            context["symbol"] = saved_quiz.interpretation_max_symbol
            context["saved_quiz_id"] = saved_quiz.id
            if SAVE_PDF and "saved_quiz_id" in context:
                context["weasyprint_download_uuid"] = saved_quiz.uuid

            answers = []
            for question in form.data:
                answer_object = None
                question_id = question.split("_")[2] if "question_" in question else ""
                if question_id.isdigit():
                    answer = form.data[question]
                    question = MoreInfoQuestion.objects.get(id=question_id).label
                    if answer.isdigit():
                        answer_object = MoreInfoAnswer.objects.get(id=answer).answer
                    else:
                        answer_object = answer
                    answers.append({"question": question, "answer": answer_object})

            saved_quiz.more_infos = answers
            saved_quiz.save()

        if SAVE_PDF and saved_quiz:
            context["weasyprint_download_uuid"] = saved_quiz.uuid

        context[
            "more_info_quiz"
        ] = False  # do not keep the form: do not try to display fields in template anymore
        context["thank_you"] = True  # thanks the person for the more_info quiz

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if not GATHER_STATISTICS_DURING_QUIZ:
            if "quiz_type" in form.data and form.data["quiz_type"] == "more_info":
                return self.handle_second_post_request(request, form, *args, **kwargs)
            return self.handle_first_post_request(request, form, *args, **kwargs)

        self.handle_first_post_request(request, form, *args, **kwargs)
