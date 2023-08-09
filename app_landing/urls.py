from django.conf.urls.static import static
from django.urls import path

from app_landing.views import MainView
from sunrise_project import settings

urlpatterns = [
    path('', MainView.as_view(), name='main'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
