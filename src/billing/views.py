from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled, \
    SwaggerAutoSchema, FieldInspector
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.decorators import action, api_view
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

    filter_month = openapi.Parameter(
        'month',
        openapi.IN_QUERY,
        description="filter month Billing",
        type=openapi.TYPE_NUMBER
    )
    filter_year = openapi.Parameter(
        'year',
        openapi.IN_QUERY,
        description="filter year Billing",
        type=openapi.TYPE_NUMBER,
    )
    success_response = '''
    {
        "summary": {
            "amount": "R$ 1,00", 
            "source": "11987654321", 
            "call_time": "1h0m0s"
        }, 
        "detail": [
            {
                "amount": "R$ 1,00", 
                "destination": "11297654321", 
                "call_start": "2018-06-02T07:19:38.558894Z", 
                "call_end": "2018-06-02T08:19:38.558894Z", 
                "call_time": "1h0m0s" 
            }
        ]
    }
    '''

    @swagger_auto_schema(
        method='get',
        operation_description="Billing for existing phone number",
        responses={200: success_response, 404: '{"detail": "Message"}'},
        field_inspectors=[],
        manual_parameters=[filter_month, filter_year],
    )
    @action(detail=True)
    def billing(self, request, phone_number=None):
        phone = self.get_object()
        month = request.GET.get('month')
        year = request.GET.get('year')
        try:
            year, month = Billing.get_valid_report_date(year=year, month=month)
        except Exception as err:
            logger.exception('Invalid Filter Date', extra={
                'error': err.__str__(),
                'month': month,
                'year': year,
                'phone': phone_number,
            })

            raise NotFound("Invalid Filter", code=status.HTTP_404_NOT_FOUND)

        billing_summary = Billing.summarized_data(phone.id, year, month)

        if billing_summary is None:
            logger.warning('Billing Not Found', extra={
                'month': month,
                'year': year,
                'phone': phone_number,
            })
            raise NotFound("Billing Not Found", code=status.HTTP_404_NOT_FOUND)

        billing_detail = Billing.detailed_data(phone.id, year, month)

        return Response({
            'summary': billing_summary,
            'detail': billing_detail,
        })


class CallViewSet(generics.CreateAPIView):
    """
    This endpoint Register Calls to be billed 
    """
    serializer_class = CallSerializer


class WelcomeView(APIView):
    """
    This endpoint is the Welcome Home to address Swagger Docs URI
    """
    swagger_schema = None

    def get(self, request):
        site = get_current_site(request)
        return Response({
            'name': 'Callcenter Billing',
            'author': 'Marco Souza',
            'description': 'Microservice to Handle Billing of Registered Calls',
            'api-doc': site.domain + '/swagger/',
            'repository': 'https://github.com/markomafs/work-at-olist/'
        })
