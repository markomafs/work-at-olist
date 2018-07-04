from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'phone', views.PhoneNumberViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^call/(?P<pk>[0-9]+)$', views.CallView.as_view()),
    url(r'call', views.CallViewSet.as_view()),
]
