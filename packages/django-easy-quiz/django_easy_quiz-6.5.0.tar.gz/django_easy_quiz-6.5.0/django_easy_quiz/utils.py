# Standard Library
from random import shuffle

# Django
from django.contrib import messages
from django.forms import formset_factory
from django.utils.translation import gettext as _

# Local application / specific library imports
from .forms import MoreInfoQuizForm


def admin_error_min_max_conclusion(request, min, max, clue):
    text = _(f"Error: {min} (min value) > {max} (max value). Description: {clue}")
    messages.set_level(request, messages.ERROR)
    messages.error(request, text, extra_tags="easy_quiz_error")


def admin_error_lacks_answer(request, question, nb_answers):
    text = _(
        f'Error: question "{question}" lacks {4-nb_answers} answer(s) (answer text or nb of points).'
    )
    messages.set_level(request, messages.ERROR)
    messages.error(request, text, extra_tags="easy_quiz_error")


def get_quiz_and_formset(QuizType, FormType, pk):
    quiz = QuizType.objects.get(id=int(pk))
    initial_data = []

    try:
        questions = quiz.interpretationquizquestion_set.all().order_by("id")
        for question in questions:
            answers = []
            if question.answer_1 is not (None or ""):
                answers.append({"label": question.answer_1, "id": 1, "symbol": "■"})
            if question.answer_2 is not (None or ""):
                answers.append({"label": question.answer_2, "id": 2, "symbol": "▲"})
            if question.answer_3 is not (None or ""):
                answers.append({"label": question.answer_3, "id": 3, "symbol": "◆"})
            if question.answer_4 is not (None or ""):
                answers.append({"label": question.answer_4, "id": 4, "symbol": "●"})
            if quiz.answers_random:
                shuffle(answers)
            initial_data.append({"question": question, "answers": answers})

    except AttributeError:
        questions = quiz.weightedanswersquizquestion_set.all().order_by("id")
        for question in questions:
            answers = []
            if question.answer_1 is not (None or ""):
                answers.append({"label": question.answer_1, "id": 1})
            if question.answer_2 is not (None or ""):
                answers.append({"label": question.answer_2, "id": 2})
            if question.answer_3 is not (None or ""):
                answers.append({"label": question.answer_3, "id": 3})
            if question.answer_4 is not (None or ""):
                answers.append({"label": question.answer_4, "id": 4})
            if question.answer_5 is not (None or ""):
                answers.append({"label": question.answer_5, "id": 5})
            if question.answer_6 is not (None or ""):
                answers.append({"label": question.answer_6, "id": 6})
            if quiz.answers_random:
                shuffle(answers)
            initial_data.append({"question": question, "answers": answers})

    if quiz.questions_random:
        questions = questions.order_by("?")
    QuestionsFormSet = formset_factory(FormType, extra=0, can_delete=False)

    formset = QuestionsFormSet(initial=initial_data, prefix="questions")

    return quiz, formset


def get_more_info_quiz_formset(more_info_quiz):
    initial_data = []
    questions = more_info_quiz.moreinfoquestion_set.all()

    for question in questions:
        answers = [
            {"label": answer.answer, "id": answer.id}
            for answer in question.moreinfoanswer_set.all()
        ]
        initial_data.append({"question": question, "answers": answers})

    MoreInfoQuestionsFormSet = formset_factory(
        MoreInfoQuizForm, extra=0, can_delete=False
    )
    formset = MoreInfoQuestionsFormSet(initial=initial_data, prefix="questions")

    return formset
