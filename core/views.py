from datetime import datetime, timedelta
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView
from django.shortcuts import get_object_or_404
from .models import Drug, IntakeDuration, DecayFormula
from .models import (
    User, Subscription,
    DrugGroup, Drug, SideEffect,
    DrugSideEffect, IntakeDuration,
    DrugCompatibility, EtherType,
    ReceptionMethod, DrugReception,
    DrugInfo, DecayFormula,
    Course, CourseDose, BloodAnalysis
)
from .serializers import (
    UserSerializer, SubscriptionSerializer,
    DrugGroupSerializer, DrugSerializer,
    SideEffectSerializer, DrugSideEffectSerializer,
    IntakeDurationSerializer, DrugCompatibilitySerializer,
    EtherTypeSerializer, ReceptionMethodSerializer,
    DrugReceptionSerializer, DrugInfoSerializer,
    DecayFormulaSerializer,
    CourseSerializer, CourseDoseSerializer, BloodAnalysisSerializer
)

from .utils import compute_concentration
from .services import regenerate_course_schedule  # вынесите логику в отдельный модуль


class CalculatorAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        doses = []
        for item in data.get('doses', []):
            drug = Drug.objects.get(pk=item['drug_id'])
            dt = datetime.fromisoformat(item['datetime'])
            doses.append((dt, float(item['amount'])))
        half = float(drug.info.half_life_hours)
        start = min(dt for dt, _ in doses)
        end = max(dt for dt, _ in doses) + timedelta(hours=half*5)
        timeline = compute_concentration(doses, half, start, end, step_minutes=int(data.get('step_minutes',60)))
        return Response([{'time':p['time'].isoformat(),'conc':p['conc']} for p in timeline])

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

class DrugGroupViewSet(viewsets.ModelViewSet):
    queryset = DrugGroup.objects.all()
    serializer_class = DrugGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class DrugViewSet(viewsets.ModelViewSet):
    queryset = Drug.objects.all().order_by('sort')
    serializer_class = DrugSerializer
    permission_classes = [permissions.IsAuthenticated]

class SideEffectViewSet(viewsets.ModelViewSet):
    queryset = SideEffect.objects.all()
    serializer_class = SideEffectSerializer
    permission_classes = [permissions.IsAuthenticated]

class DrugSideEffectViewSet(viewsets.ModelViewSet):
    queryset = DrugSideEffect.objects.all()
    serializer_class = DrugSideEffectSerializer
    permission_classes = [permissions.IsAuthenticated]

class IntakeDurationViewSet(viewsets.ModelViewSet):
    queryset = IntakeDuration.objects.all()
    serializer_class = IntakeDurationSerializer
    permission_classes = [permissions.IsAuthenticated]

class DrugCompatibilityViewSet(viewsets.ModelViewSet):
    queryset = DrugCompatibility.objects.all()
    serializer_class = DrugCompatibilitySerializer
    permission_classes = [permissions.IsAuthenticated]

class EtherTypeViewSet(viewsets.ModelViewSet):
    queryset = EtherType.objects.all()
    serializer_class = EtherTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReceptionMethodViewSet(viewsets.ModelViewSet):
    queryset = ReceptionMethod.objects.all()
    serializer_class = ReceptionMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

class DrugReceptionViewSet(viewsets.ModelViewSet):
    queryset = DrugReception.objects.all()
    serializer_class = DrugReceptionSerializer
    permission_classes = [permissions.IsAuthenticated]

class DrugInfoViewSet(viewsets.ModelViewSet):
    queryset = DrugInfo.objects.all()
    serializer_class = DrugInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

class DecayFormulaViewSet(viewsets.ModelViewSet):
    """
    Позволяет получить формулу распада.
    Если указан GET-параметр ?drug=<id>, то фильтруем по drug_id.
    """
    # <<------ Добавляем этот атрибут
    queryset = DecayFormula.objects.all()
    serializer_class = DecayFormulaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        drug_id = self.request.query_params.get('drug')
        if drug_id is not None:
            qs = qs.filter(drug_id=drug_id)
        return qs

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(user__isnull=False)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        course = serializer.save()
        regenerate_course_schedule(course)

    def perform_update(self, serializer):
        course = serializer.save()
        regenerate_course_schedule(course)

class CourseDoseViewSet(viewsets.ModelViewSet):
    queryset = CourseDose.objects.all()
    serializer_class = CourseDoseSerializer

    def perform_update(self, serializer):
        # Сохраняем изменения времени приёма и пересчитываем концентрацию курса
        dose = serializer.save()
        dose.course.recalc_concentration()
    permission_classes = [permissions.IsAuthenticated]

class BloodAnalysisViewSet(viewsets.ModelViewSet):
    queryset = BloodAnalysis.objects.all().order_by('-analysis_date')
    serializer_class = BloodAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
def drug_list(request):
    """Список всех препаратов для выпадающего списка."""
    drugs = list(Drug.objects.values('id', 'name'))
    return JsonResponse(drugs, safe=False)

def drug_dosage(request, pk):
    """Рекомендованные длительности приёма для выбранного препарата."""
    try:
        intake = IntakeDuration.objects.get(drug_id=pk)
        data = {
            'min': intake.min_duration_days,
            'rec': intake.rec_duration_days,
            'max': intake.max_duration_days,
        }
    except IntakeDuration.DoesNotExist:
        data = {}
    return JsonResponse(data)
    
    
# Frontend views
class CourseCreateView(TemplateView):
    template_name = 'core/course_form.html'

class CourseDetailView(TemplateView):
    template_name = 'core/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=kwargs['pk'], user=self.request.user)
        doses = CourseDose.objects.filter(schedule__course=course).order_by('intake_dt')
        context.update({
            'course': course,
            'doses': doses,
            'concentration_data': course.concentration_cache or [],
        })
        return context
class CourseListView(ListView):
    model = Course
    template_name = 'core/courses.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user).order_by('-created_at')