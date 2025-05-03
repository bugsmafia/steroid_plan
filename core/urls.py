from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, SubscriptionViewSet,
    DrugGroupViewSet, DrugViewSet,
    SideEffectViewSet, DrugSideEffectViewSet,
    IntakeDurationViewSet, DrugCompatibilityViewSet,
    EtherTypeViewSet, ReceptionMethodViewSet,
    DrugReceptionViewSet, DrugInfoViewSet,
    DecayFormulaViewSet,
    CourseViewSet, CourseDoseViewSet, BloodAnalysisViewSet,
    CalculatorAPIView,
    drug_list, drug_dosage,
    CourseCreateView, CourseDetailView, CourseListView
)

app_name = 'core'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'drug-groups', DrugGroupViewSet)
router.register(r'drugs', DrugViewSet)
router.register(r'side-effects', SideEffectViewSet)
router.register(r'drug-side-effects', DrugSideEffectViewSet)
router.register(r'intake-durations', IntakeDurationViewSet)
router.register(r'drug-compatibility', DrugCompatibilityViewSet)
router.register(r'ether-types', EtherTypeViewSet)
router.register(r'reception-methods', ReceptionMethodViewSet)
router.register(r'drug-receptions', DrugReceptionViewSet)
router.register(r'drug-info', DrugInfoViewSet)
router.register(r'decay-formulas', DecayFormulaViewSet, basename='decay-formulas')
router.register(r'courses', CourseViewSet)
router.register(r'course-doses', CourseDoseViewSet)
router.register(r'blood-analyses', BloodAnalysisViewSet)

urlpatterns = [
    # API endpoints under /api/
    # path('api/', include(router.urls)),
    path('', include(router.urls)),
    path('api/calculator/', CalculatorAPIView.as_view(), name='calculator'),
    path('api/drugs-list/', drug_list, name='drugs_list'),
    path('api/drugs/', drug_list, name='drugs_list'),
    path('api/drugs/<int:pk>/dosage/', drug_dosage, name='drug_dosage'),
]
