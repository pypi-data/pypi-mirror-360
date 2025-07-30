<div align="center">
    <img src="https://gitlab.com/kapt/open-source/django-easy-quiz/uploads/085c27d6a332b09a0931df378124270f/django-easy-quiz.png" alt="Django simple quiz" />
    <p><i>Create quizzes with ease!</i></p>
</div>


# Features

- Create quizzes!
  - **Weighted-answers quizzes** (up to 10 answers to choose from, conclusions are in categories by points count, like *"you have between 0 and 5 points"*, single (radio) OR multiple (checkboxes) answers per question!),
  - **Interpretation quizzes** (4 answers to choose from, conclusions are in categories by max symbols count, like *"you have a majority of ◆"*),
  - Admin option to choose to display random questions and/or answers!
  - Another admin option to display the nb of points (for weighted-answers quizzes)!
- Create django-cms plugins that redirect to your quizzes (quizzes are available through a special url, you cannot add quizzes as django cms plugin by default).
- (optional) Save quizzes data in your database (*started quizzes, finished quizzes, results*)
- (optional) Add general questions to the end of the quiz to gather more data! (*name, email, job, age range, [...]*)
- (optional) Let visitors download a pdf version of their results.
- (optional) Export data from saved quizzes.

### Warning!

*Do not use versions < 3.0.0, they are not production-ready and have a lot of problems.*

# Install

1. Install the package:
    ```sh
    python3 -m pip install django-easy-quiz
    ```
2. Add those apps to your `INSTALLED_APPS`:
    ```python
    "filer",
    "ckeditor",
    "ckeditor_uploader",  # for hosting images in your ckeditor view, see below for a ready-to-use config
    "ckeditor_filebrowser_filer",
    "import_export",
    "django_easy_quiz",
    ```
3. Add the `sessions` middleware in your settings if it's not already here:
    ```python
    MIDDLEWARE = (
        # [...]
        "django.contrib.sessions.middleware.SessionMiddleware",
        # [...]
    )
    ```
4. Add those urls in your `urls.py`:
    ```python
    # main app urls
    path("quiz/", include("django_easy_quiz.urls")),
    # ckeditor-related urls
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("filer/", include("filer.urls")),
    path("filebrowser_filer/", include("ckeditor_filebrowser_filer.urls")),
    path("filebrowser_filer/filer_", include("ckeditor_filebrowser_filer.urls")),  # only add this line if you're using django-ckeditor-filebrowser-filer from the develop branch or our fork on the "various-fixes" branch
    ```
5. Migrate
    ```sh
    python3 manage.py migrate
    ```
6. That's all folks!

# Signals

Want to do something when someone submit the quiz? Some signals are here, ready to be handled!

```python
@receiver(pre_save, sender=SavedQuiz)
def saved_quiz_more_infos_do_something(sender, signal, instance, **kwargs):
    ...
    # your code
```

# Config

## Ckeditor config

You will need to configure `django-ckeditor` in order to make it work in the quiz descriptions. Here's a ready-to-use config snippet that you can paste on your project's settings:

```python
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_THUMBNAIL_SIZE = (150, 150)
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_CONFIGS = {
  "default": {
    "language": "{{ language }}",
    "toolbar": "Simple",
    "toolbar_Simple": [
        ["Undo", "Redo"],
        ["Styles", "Format"],
        ["TextColor", "BGColor"],
        ["Subscript", "Superscript", "-", "RemoveFormat", "PasteText", "PasteFromWord", "FilerImage"],
        ["Link", "Unlink"],
        ["Source"],
    ],
    "autoParagraph": False,
    "colorButton_colors": "01b6ad,00b6ef,a0cd49,ffc01c,9d1a75,fff,000",
    "skin": "moono-lisa",
    "height": "100px",
    "extraPlugins": "filerimage",
    "removePlugins": "image"  # do not use the classic image plugin, use the one from django-ckeditor-filebrowser-filer
    "resize_enabled": True,
  }
}
```

*You can learn more about those config values and customize them values by having a look at the [django-ckeditor documentation](https://django-ckeditor.readthedocs.io/en/latest/#optional-customizing-ckeditor-editor).*

## Save quizzes in your database

Add `DJANGO_EASY_QUIZ_SAVE_QUIZZES_RESULTS=True` (default `False`) in your settings.

## Display 'more info' questions

Add `DJANGO_EASY_QUIZ_GATHER_STATISTICS=True` (default `False`) in your settings.

By default, the 'more info' question will be displayed on the summary page, after having answered the quiz.

If you want to display the 'more info' questions **during** the quiz, then set `DJANGO_EASY_QUIZ_GATHER_STATISTICS_DURING_QUIZ` to `True` in your settings (default `False`).

## Download pdf with infos on the quiz

Add `DJANGO_EASY_QUIZ_SAVE_PDF` (default `False`) in your settings.

*Only work if `DJANGO_EASY_QUIZ_SAVE_QUIZZES_RESULTS` is true. Requires weasyprint. Template to edit is in `django_easy_quiz/quiz_pdf.html`.*

You can update the pdf file name using `DJANGO_EASY_QUIZ_PDF_FILE_NAME` (default `_("quiz_summary.pdf")`).

You can also update the logo in the pdf using `DJANGO_EASY_QUIZ_PDF_LOGO` (default `logo.png`).

If you want to change more things in the pdf, you can create a file named `quiz_pdf.html` in `templates/django_easy_quiz` and update the html file (rendered to a pdf file using weasyprint).

## Add button "relaunch the quiz"

Add `DJANGO_EASY_QUIZ_RELAUNCH_BUTTON` (default `False`) in your settings.

