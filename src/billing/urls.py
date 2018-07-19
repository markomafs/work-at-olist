from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'phone', views.PhoneNumberViewSet)

urlpatterns = [
    url('^$', views.WelcomeView.as_view(), name='home'),
    url(r'^', include(router.urls)),
    url(r'^call/(?P<pk>[0-9]+)$', views.CallDetailViewSet.as_view(), name='call-detail'),
    url(r'^call$', views.CallViewSet.as_view(), name='call-create'),
]
