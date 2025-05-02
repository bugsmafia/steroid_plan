# frontend/views.py
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Course, CourseDose, BloodAnalysis, Drug, DrugGroup

class CalculatorPage(LoginRequiredMixin, TemplateView):
    template_name = 'core/calculator.html'

class CalendarPage(LoginRequiredMixin, TemplateView):
    template_name = 'core/calendar.html'

class CoursesListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'core/courses.html'
    context_object_name = 'courses'

class CourseDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'core/course_detail.html'

class AnalysesListView(LoginRequiredMixin, ListView):
    model = BloodAnalysis
    template_name = 'core/analyses.html'
    context_object_name = 'analyses'

class KnowledgeBaseView(LoginRequiredMixin, TemplateView):
    template_name = 'core/knowledge.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['groups'] = DrugGroup.objects.all()
        return ctx