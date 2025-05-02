from django.urls import path
from .views import (
    CalculatorPage, CalendarPage,
    CoursesListView, CourseDetailView,
    AnalysesListView, KnowledgeBaseView
)
urlpatterns = [
    path('calculator/', CalculatorPage.as_view(), name='page_calculator'),
    path('calendar/',   CalendarPage.as_view(),   name='page_calendar'),
    path('courses/',    CoursesListView.as_view(), name='courses_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('analyses/',   AnalysesListView.as_view(),   name='analyses_list'),
    path('knowledge/',  KnowledgeBaseView.as_view(),  name='knowledge_base'),
]
