from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # API core
    path('api/', include('core.urls')),

    # JWT-endpoints
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # Frontend-страницы
    path('', include(('frontend.urls', 'frontend'), namespace='frontend')),

    # Стандартный Django-auth (login/logout)
    path('accounts/', include('django.contrib.auth.urls')),
]
