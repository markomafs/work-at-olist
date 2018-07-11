from django.utils import timezone
from django.http import (
    HttpResponse, HttpResponseForbidden, HttpResponseNotFound,
    HttpResponseBadRequest
)
from rest_framework import permissions, renderers, views, viewsets, generics

from rest_framework.decorators import action
from rest_framework.response import Response
from time import sleep

from .serializers import PhoneNumberSerializer, CallSerializer
from .models import PhoneNumber, Call

import logging

logger = logging.getLogger(__name__)


class PhoneNumberViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents phone number
    """
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CallDetailViewSet(generics.UpdateAPIView):
    serializer_class = CallSerializer

    def get_queryset(self):
        return Call.objects.all()


class CallViewSet(generics.CreateAPIView):
    """
    This endpoint Register Calls to be billed 
    """
    serializer_class = CallSerializer
