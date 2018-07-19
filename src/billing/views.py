from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PhoneNumberSerializer, CallSerializer
from .models import PhoneNumber, Call, Billing

import logging

logger = logging.getLogger(__name__)


class PhoneNumberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Phone Number resource.
    
    retrieve:
    Return the given phone number

    list:
    Return a list of all the existing phone numbers.
    """
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    lookup_field = 'phone_number'

    @action(detail=True)
    def billings(self, request, phone_number=None):
        """
        Return Billings for existing phone number
        """
        phone = self.get_object()
        month = request.GET.get('month')
        year = request.GET.get('year')
        try:
            year, month = Billing.get_valid_report_date(year=year, month=month)
        except Exception:
            raise Http404

        billing_summary = Billing.summarized_data(phone.id, year, month)

        if billing_summary is None:
            return Response()

        billing_detail = Billing.detailed_data(phone.id, year, month)

        return Response({
            'summary': billing_summary,
            'detail': billing_detail,
        })


class CallDetailViewSet(generics.UpdateAPIView):
    """
    This endpoint Register End of a Call
    """
    serializer_class = CallSerializer

    def get_queryset(self):
        return Call.objects.all()


class CallViewSet(generics.CreateAPIView):
    """
    This endpoint Register Calls to be billed 
    """
    serializer_class = CallSerializer


class WelcomeView(APIView):
    """
    This endpoint is the Welcome Home to address Swagger Docs URI
    """
    def get(self, request):
        site = get_current_site(request)
        return Response({
            'name': 'Callcenter Billing',
            'author': 'Marco Souza',
            'description': 'Microservice to Handle Billing of Registered Calls',
            'api-doc': site.domain + '/swagger/',
            'repository': 'https://github.com/markomafs/work-at-olist/'
        })
