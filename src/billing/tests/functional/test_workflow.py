import json

from django.test import client
from django.urls import reverse
from datetime import datetime
from rest_framework import status
import pytest

http = client.Client()

# Billing Calculation Data
fields = "call_id, source, destination, code, start, end, billing_amount"
cases = [
    (1, '11987654321', '1123456789', '1', datetime(2017, 7, 12, 3, 20, 10),
     datetime(2017, 7, 12, 3, 30, 10), "R$ 0,36"),
    (2, '11987654321', '1123456789', '2', datetime(2017, 7, 13, 8, 2, 17),
     datetime(2017, 7, 13, 9, 2, 17), "R$ 5,76"),
    (3, '11987654321', '1123456789', '3', datetime(2017, 7, 14, 22, 10, 9),
     datetime(2017, 7, 14, 22, 12, 9), "R$ 0,36"),
    (4, '11987654321', '1123456789', '4', datetime(2017, 7, 15, 10, 0, 1),
     datetime(2017, 7, 15, 10, 59, 59), "R$ 5,67"),
    (5, '11987654321', '1123456789', '5', datetime(2017, 7, 10, 10, 0, 1),
     datetime(2017, 7, 11, 10, 59, 59), "R$ 92,07"),
]


def build_start_request(call_id, source, destination, code, timestamp):
    request = {
        'id': call_id,
        'source': source,
        'destination': destination,
        'timestamp': str(timestamp),
        'type': 'start',
        'call_code': code
    }
    return request


def build_end_request(call_id, code, timestamp):
    request = {
        'id': call_id,
        'timestamp': str(timestamp),
        'type': 'end',
        'call_code': code
    }
    return request


@pytest.mark.parametrize(
    fields,
    cases
)
@pytest.mark.django_db()
def test_calculate_and_billing_one_call(
        call_id, source, destination, code, start, end, billing_amount):
    request = build_start_request(call_id, source, destination, code, start)
    response = http.post(path=reverse('call-create'), data=request)
    assert status.is_success(response.status_code)

    request = build_end_request(call_id, code, end)
    response = http.put(
        path=reverse('call-detail', kwargs={'pk': call_id}),
        data=json.dumps(request),
        content_type='application/json'
    )
    assert status.is_success(response.status_code)

    response = http.get(
        reverse('phonenumber-billing', kwargs={'phone_number': source}),
        data={'year': end.year, 'month': end.month},
    )
    assert status.is_success(response.status_code)

    body = json.loads(response.content)
    assert body['summary']['amount'] == billing_amount

    # Testing Empty Billing
    response = http.get(
        reverse('phonenumber-billing', kwargs={'phone_number': source}),
        data={'year': end.year-1, 'month': end.month},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.content.decode('UTF-8')
    assert '{"detail":"Billing Not Found"}' == body


@pytest.mark.parametrize(
    fields,
    cases
)
@pytest.mark.django_db()
def test_calculate_and_billing_one_call_with_wrong_order(
        call_id, source, destination, code, start, end, billing_amount):
    request = build_end_request(call_id, code, end)
    response = http.post(path=reverse('call-create'), data=request)
    assert status.is_success(response.status_code)

    request = build_start_request(call_id, source, destination, code, start)
    response = http.post(path=reverse('call-create'), data=request)
    assert status.is_success(response.status_code)

    response = http.get(
        reverse('phonenumber-billing', kwargs={'phone_number': source}),
        data={'year': end.year, 'month': end.month},
    )
    assert status.is_success(response.status_code)

    body = json.loads(response.content)
    assert body['summary']['amount'] == billing_amount


@pytest.mark.parametrize(
    fields,
    cases
)
@pytest.mark.django_db()
def test_calculate_and_billing_one_call_using_post_only(
        call_id, source, destination, code, start, end, billing_amount):

    request = build_start_request(call_id, source, destination, code, start)
    response = http.post(path=reverse('call-create'), data=request)
    assert status.is_success(response.status_code)

    request = build_end_request(call_id, code, end)
    response = http.post(path=reverse('call-create'), data=request)
    assert status.is_success(response.status_code)

    response = http.get(
        reverse('phonenumber-billing', kwargs={'phone_number': source}),
        data={'year': end.year, 'month': end.month},
    )
    assert status.is_success(response.status_code)

    body = json.loads(response.content)
    assert body['summary']['amount'] == billing_amount


@pytest.mark.parametrize(
    fields,
    cases
)
@pytest.mark.django_db()
def test_invalid_billing_data(
        call_id, source, destination, code, start, end, billing_amount):

    request = build_start_request(call_id, source, destination, code, start)
    response = http.post(path=reverse('call-create'), data=request)
    assert status.is_success(response.status_code)

    date = datetime.today()
    response = http.get(
        reverse('phonenumber-billing', kwargs={'phone_number': source}),
        data={'year': date.year, 'month': date.month},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_home():
    response = http.get(path='/')
    assert status.is_success(response.status_code)
