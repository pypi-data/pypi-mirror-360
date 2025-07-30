# Django
from django.views.generic import FormView

# Project
from django_easy_quiz.forms import WeightedAnswersQuizForm
from django_easy_quiz.models import (
    MoreInfoAnswer,
    MoreInfoQuestion,
    SavedQuiz,
    WeightedAnswersQuiz,
    WeightedAnswersQuizConclusion,
)
from django_easy_quiz.settings import (
    GATHER_STATISTICS,
    GATHER_STATISTICS_DURING_QUIZ,
    RELAUNCH_BUTTON,
    SAVE_PDF,
    SAVE_QUIZZES_RESULTS,
)
from django_easy_quiz.utils import get_more_info_quiz_formset, get_quiz_and_formset


class WeightedAnswersQuizView(FormView):
    form_class = WeightedAnswersQuizForm
    model = WeightedAnswersQuiz
    template_name = "django_easy_quiz/weighted_answers_form.html"

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz, formset = get_quiz_and_formset(
            WeightedAnswersQuiz,
            WeightedAnswersQuizForm,
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
                more_info_quiz_formset = get_more_info_quiz_formset(quiz.more_info_quiz)
                context["more_info_quiz"] = more_info_quiz_formset
                context["more_info_quiz_after_main_quiz"] = True

        if GATHER_STATISTICS_DURING_QUIZ and "more_info_quiz" in context:
            context["more_info_quiz_after_main_quiz"] = False

        context["quiz"] = quiz
        context["formset"] = formset
        return context

    def handle_first_post_request(self, request, form, *args, **kwargs):
        if form.is_valid():
            context = self.get_context_data()

            quiz = WeightedAnswersQuiz.objects.get(id=int(kwargs["pk"]))
            total_points = 0
            final_quiz = []

            for input in form.data:
                answers = []
                if input.startswith("question_"):
                    question = quiz.weightedanswersquizquestion_set.get(
                        id=input.split("_")[1]
                    )
                    answers_ids = [int(id) for id in form.data.getlist(input)]
                    if 1 in answers_ids:
                        answers.append(question.answer_1)
                        total_points += question.points_answer_1
                    if 2 in answers_ids:
                        answers.append(question.answer_2)
                        total_points += question.points_answer_2
                    if 3 in answers_ids:
                        answers.append(question.answer_3)
                        total_points += question.points_answer_3
                    if 4 in answers_ids:
                        answers.append(question.answer_4)
                        total_points += question.points_answer_4
                    if 5 in answers_ids:
                        answers.append(question.answer_5)
                        total_points += question.points_answer_5
                    if 6 in answers_ids:
                        answers.append(question.answer_6)
                        total_points += question.points_answer_6
                    final_quiz.append({"question": question, "answers": answers})
            conclusion = WeightedAnswersQuizConclusion.objects.filter(
                min_points__lte=total_points, max_points__gte=total_points, quiz=quiz
            )
            if conclusion.exists():
                conclusion = conclusion[0]
            else:
                conclusion = WeightedAnswersQuizConclusion()

            conclusion.points = total_points
            context["conclusion"] = conclusion
            context["final_quiz"] = final_quiz
            context["relaunch_button"] = RELAUNCH_BUTTON

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
                    question = MoreInfoQuestion.objects.get(id=question_id)
                    if not question.answer_is_txt and answer.isdigit():
                        answer_object = MoreInfoAnswer.objects.get(id=answer).answer
                    else:
                        answer_object = answer
                    more_info_quiz_answers.append(
                        {"question": question.label, "answer": answer_object}
                    )

            if "saved_quiz" in request.POST and request.POST["saved_quiz"].isdigit():
                for question in final_quiz:
                    question["question"] = question["question"].toJson()
                saved_quiz = SavedQuiz.objects.get(id=request.POST["saved_quiz"])
                saved_quiz.quiz_ended = True
                saved_quiz.weighted_answers_quiz = quiz
                saved_quiz.conclusion = {
                    "points": conclusion.points,
                    "description": conclusion.description,
                }
                saved_quiz.answers = final_quiz
                saved_quiz.more_infos = more_info_quiz_answers
                saved_quiz.save()

                context["saved_quiz_id"] = saved_quiz.id

            if SAVE_PDF and "saved_quiz_id" in context:
                context["weasyprint_download_uuid"] = saved_quiz.uuid

            return self.render_to_response(context)
        return self.form_invalid(form)

    def handle_second_post_request(self, request, form, *args, **kwargs):
        context = self.get_context_data()
        if "saved_quiz" in request.POST and request.POST["saved_quiz"].isdigit():
            saved_quiz = SavedQuiz.objects.get(id=request.POST["saved_quiz"])

            context["quiz"] = saved_quiz.weighted_answers_quiz
            context["final_quiz"] = saved_quiz.answers
            context["conclusion"] = saved_quiz.conclusion
            context["relaunch_button"] = RELAUNCH_BUTTON

            answers = []
            for question in form.data:
                answer_object = None
                question_id = (
                    question.split("_")[2]
                    if question.startswith("more_question_")
                    else ""
                )
                if question_id.isdigit():
                    answer = form.data[question]
                    question = MoreInfoQuestion.objects.get(id=question_id)
                    if not question.answer_is_txt and answer.isdigit():
                        answer_object = MoreInfoAnswer.objects.get(id=answer).answer
                    else:
                        answer_object = answer
                    answers.append(
                        {"question": question.label, "answer": answer_object}
                    )

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
        return self.handle_first_post_request(request, form, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if "question" not in request.GET:
            return super().get(request, *args, **kwargs)

        context = self.get_context_data()
        quiz = WeightedAnswersQuiz.objects.get(id=int(kwargs["pk"]))
        questions_url = request.GET.getlist("question")
        quiz_context = []
        total_points = 0
        for question in questions_url:
            answers_objects = []
            answers = [int(id) for id in question.split(".")[1:]]
            question = quiz.weightedanswersquizquestion_set.get(
                id=int(question.split(".")[0])
            )
            if 1 in answers:
                total_points += question.points_answer_1
                answers_objects.append(question.answer_1)
            if 2 in answers:
                total_points += question.points_answer_2
                answers_objects.append(question.answer_2)
            if 3 in answers:
                total_points += question.points_answer_3
                answers_objects.append(question.answer_3)
            if 4 in answers:
                total_points += question.points_answer_4
                answers_objects.append(question.answer_4)
            if 5 in answers:
                total_points += question.points_answer_5
                answers_objects.append(question.answer_5)
            if 6 in answers:
                total_points += question.points_answer_6
                answers_objects.append(question.answer_6)

            quiz_context.append({"question": question, "answers": answers_objects})

        quiz.points = total_points
        quiz.conclusion_description = WeightedAnswersQuizConclusion.objects.filter(
            min_points__lte=total_points, max_points__gte=total_points, quiz=quiz
        )[0].description
        context["quiz"] = quiz
        context["quiz_answers"] = quiz_context

        return self.render_to_response(context)
