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
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PhoneNumberViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents phone number
    """
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CallViewSet(generics.CreateAPIView):
    """
    This endpoint Register Calls to be billed 
    """
    serializer_class = CallSerializer


class CallView(views.APIView):
    """
    This endpoint presents Registered Call 
    """

    def get(self, request, pk):
        """
        GET Call Register By id
        :param request: 
        :param pk: 
        :return: JSON 
        """
        logger.debug('Request Call', extra={'id': pk})
        call = Call.objects.get(id=pk)
        if call is None:
            return HttpResponseNotFound()

        data = {
            'id': call.id,
            'destination': call.fk_destination_phone_number.formatted(),
            'origin': call.fk_origin_phone_number.formatted(),
            'type': Call.TYPE_START,
            'timestamp': call.started_at,
            'call_identifier': call.call_code,
        }
        logger.debug(call.started_at)
        serializer = CallSerializer(data=data)
        if serializer.is_valid():
            result = serializer.data
            return Response(result)
        else:
            logger.error(serializer._errors)
            logger.error('Invalid Serializer Data')
            return HttpResponseForbidden({'error': 'Invalid Call Data'})


def index(request):

    origin_area = '11'
    origin_phone_number = '972577063'

    destination_area = '11'
    destination_phone_number = '996465321'

    origin = get_number_object(origin_area, origin_phone_number)
    destination = get_number_object(destination_area, destination_phone_number)

    call_code = 'test_function'
    started_at = timezone.now()
    sleep(2)
    ended_at = timezone.now()
    logger.debug('Registering Call', extra={
        'call_code': call_code,
        'action': 'create'
    })
    c = Call(
        started_at=started_at,
        call_code=call_code,
        fk_origin_phone_number=origin,
        fk_destination_phone_number=destination,
        ended_at=ended_at,
    )
    c.save()
    id_call = c.id
    logger.debug('Registered Call', extra={
        'id_call': id_call,
    })

    return HttpResponse("Registered Call {}".format(id_call))
