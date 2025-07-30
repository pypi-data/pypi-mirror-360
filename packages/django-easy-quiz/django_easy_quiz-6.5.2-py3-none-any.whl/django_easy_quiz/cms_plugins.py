# Django
from django.utils.translation import gettext as _

try:
    # Third party
    from cms.plugin_base import CMSPluginBase
    from cms.plugin_pool import plugin_pool

    # Local application / specific library imports
    from .models import InterpretationPlugin, WeightedAnswersPlugin

    @plugin_pool.register_plugin
    class WeightedAnswersPluginPublisher(CMSPluginBase):
        module = _("Quiz")
        name = _("Weighted Answers Quiz")
        model = WeightedAnswersPlugin
        render_template = "django_easy_quiz/weighted_answers_plugin.html"

        allow_children = False

        def render(self, context, instance, placeholder):
            context.update({"instance": instance})
            return context

    @plugin_pool.register_plugin
    class InterpretationPluginPublisher(CMSPluginBase):
        module = _("Quiz")
        name = _("Interpretation Quiz")
        model = InterpretationPlugin
        render_template = "django_easy_quiz/interpretation_plugin.html"
        allow_children = False

        def render(self, context, instance, placeholder):
            context.update({"instance": instance})
            return context

except ImportError:
    ...
