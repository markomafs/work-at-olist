from django.http import HttpResponse
from django.utils import timezone
from .models import PhoneNumber, Call
from time import sleep
import logging

logger = logging.getLogger(__name__)


def index(request):

    def get_number_object(area, phone_number):
        phone_number, created = PhoneNumber.objects.get_or_create(
            area_code=area,
            phone_number=phone_number
        )
        if created is True:
            logger.debug('Created Phone Number', extra={
                'area_code': area,
                'phone_number': phone_number
            })
        return phone_number

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
