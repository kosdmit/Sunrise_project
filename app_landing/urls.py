from django.conf.urls.static import static
from django.urls import path

from app_landing.views import MainView, OrderCreateView, ProjectListAPIView
from sunrise_project import settings

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('api/order_create/', OrderCreateView.as_view(), name='order_create'),
    path('api/projects/', ProjectListAPIView.as_view(), name='project_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
