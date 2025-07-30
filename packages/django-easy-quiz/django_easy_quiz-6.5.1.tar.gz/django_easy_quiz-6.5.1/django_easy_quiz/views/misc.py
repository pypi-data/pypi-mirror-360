# Standard Library
from io import BytesIO

# Django
from django.http import FileResponse
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic

# Project
from django_easy_quiz.models import SavedQuiz
from django_easy_quiz.settings import PDF_LOGO


class DisplayPdfView(generic.detail.BaseDetailView):
    def get(self, request, identifier=None, *args, **kwargs):
        # Third party
        from weasyprint import HTML

        try:
            fname = request.GET["name"] + ".pdf"
        except MultiValueDictKeyError:
            fname = "document.pdf"

        saved_quiz = SavedQuiz.objects.filter(uuid=identifier).first()

        quiz_type = (
            "interpretation_quiz"
            if saved_quiz.interpretation_quiz
            else "weighed_answers_quiz"
        )
        final_quiz = saved_quiz.answers
        conclusion = saved_quiz.conclusion

        rendered = render_to_string(
            "django_easy_quiz/quiz_pdf.html",
            {
                "logo": PDF_LOGO,
                "quiz_type": quiz_type,
                "final_quiz": final_quiz,
                "conclusion": conclusion,
            },
        )
        html = HTML(string=rendered, base_url=request.build_absolute_uri())
        content = BytesIO(html.write_pdf())
        response = FileResponse(content, content_type="application/pdf")
        response["Content-Disposition"] = "filename={}".format(fname)
        response["Content-Length"] = content.getbuffer().nbytes
        return response
