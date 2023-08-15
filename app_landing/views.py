from django.views.generic import TemplateView

from app_landing.models import Project


# Create your views here.
class MainView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        featured_project = Project.objects.filter(is_featured=True, is_active=True).first()
        context['featured_project'] = featured_project

        projects = Project.objects.filter(is_featured=False, is_active=True)[:2]
        context['projects'] = projects

        return context
