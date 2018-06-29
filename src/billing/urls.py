from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'phone', views.PhoneNumberViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
