import json

from django.test import client
from django.urls import reverse
from datetime import datetime
from rest_framework import status
import pytest

http = client.Client()


@pytest.mark.parametrize(
    "call_id, origin, destination, code, start, end, billing_amount ",
    [
        (1, '11987654321', '1123456789', '1', datetime(2017, 7, 12, 3, 20, 10), datetime(2017, 7, 12, 3, 30, 10), 0),
        (2, '11987654321', '1123456789', '2', datetime(2017, 7, 13, 8, 2, 17), datetime(2017, 7, 13, 9, 2, 17), 5.4),
        (3, '11987654321', '1123456789', '3', datetime(2017, 7, 14, 22, 10, 9), datetime(2017, 7, 14, 22, 12, 9), 0 ),
        (4, '11987654321', '1123456789', '4', datetime(2017, 7, 15, 10, 0, 1), datetime(2017, 7, 15, 10, 59, 59), 5.31),
    ]
)
@pytest.mark.django_db()
def test_calculate_and_billing_one_call(
        call_id, origin, destination, code, start, end, billing_amount):
    request = {
        'id': call_id,
        'origin': origin,
        'destination': destination,
        'timestamp': str(start),
        'type': 'start',
        'call_code': code
    }
    response = http.post(path=reverse('call-create'), data=request)
    assert status.is_success(response.status_code)

    request = {
        'id': call_id,
        'origin': origin,
        'destination': destination,
        'timestamp': str(end),
        'type': 'end',
        'call_code': code
    }
    response = http.put(
        path=reverse('call-detail', kwargs={'pk': call_id}),
        data=json.dumps(request),
        content_type='application/json'
    )
    assert status.is_success(response.status_code)

    response = http.get(
        reverse('phonenumber-billings', kwargs={'phone_number': origin}),
        data={'year': end.year, 'month': end.month},
    )
    assert status.is_success(response.status_code)

    body = json.loads(response.content)
    assert body['summary']['amount'] == billing_amount
