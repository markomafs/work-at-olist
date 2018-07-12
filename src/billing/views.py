from django.http import Http404
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import PhoneNumberSerializer, CallSerializer
from .models import PhoneNumber, Call, Billing
from django.db.models import Sum
from datetime import date, timedelta

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
    def calls(self, request, phone_number=None):
        """
        Return Calls for existing phone number
        """
        phone = self.get_object()
        calls = Call.objects.filter(fk_origin_phone_number=phone.id).all()
        return Response([
            {
                'start': call.started_at,
                'end': call.ended_at
            } for call in calls
        ])

    @action(detail=True)
    def billings(self, request, phone_number=None):
        """
        Return Billings for existing phone number
        """
        def get_filters(request):
            valid_date = date.today().replace(day=1) - timedelta(days=1)
            month = int(request.GET.get('month'))
            year = int(request.GET.get('year'))
            if month and year:
                if date(year=year, month=month, day=1) > valid_date:
                    raise Http404
            else:
                month = valid_date.month
                year = valid_date.year
            return year, month

        phone = self.get_object()
        year, month = get_filters(request)
        billing_summary = Billing.objects.all().select_related(
            'fk_call__fk_origin_phone_number'
        ).values(
            'fk_call__fk_origin_phone_number__phone_number',
        ).filter(
            fk_call__fk_origin_phone_number_id=phone.id,
            year__exact=year,
            month__exact=month,
        ).annotate(
            Sum('amount'),
            Sum('hours'),
            Sum('minutes'),
            Sum('seconds'),
        )

        bill_detail = Billing.objects.all().select_related(
            'fk_call__fk_origin_phone_number'
        ).values(
            'fk_call__fk_origin_phone_number__phone_number',
            'fk_call__fk_destination_phone_number__phone_number',
            'fk_call__started_at',
            'fk_call__ended_at',
        ).filter(
            fk_call__fk_origin_phone_number_id=phone.id,
            year__exact=year,
            month__exact=month,
        ).annotate(
            Sum('amount'),
            Sum('hours'),
            Sum('minutes'),
            Sum('seconds'),
        )
        return Response({
            'summary': billing_summary,
            'detail': bill_detail,
        })


class CallDetailViewSet(generics.UpdateAPIView):
    serializer_class = CallSerializer

    def get_queryset(self):
        return Call.objects.all()


class CallViewSet(generics.CreateAPIView):
    """
    This endpoint Register Calls to be billed 
    """
    serializer_class = CallSerializer
