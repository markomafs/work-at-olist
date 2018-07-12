from rest_framework import serializers
from .models import PhoneNumber, Call
from .services import BillingService
import logging

logger = logging.getLogger(__name__)


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = (
            'id',
            'phone_number',
            'created_at',
            'updated_at',
        )


class CallSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    origin = serializers.IntegerField(
        min_value=PhoneNumber.MIN_PHONE, max_value=PhoneNumber.MAX_PHONE,
        allow_null=True, required=False
    )
    destination = serializers.IntegerField(
        min_value=PhoneNumber.MIN_PHONE, max_value=PhoneNumber.MAX_PHONE,
        allow_null=True, required=False
    )
    type = serializers.ChoiceField(choices=Call.TYPE_CHOICES)
    timestamp = serializers.DateTimeField()
    call_code = serializers.CharField(max_length=200)

    def create(self, validated_data):
        logger.debug('Creating Validated Data', extra=validated_data)

        call_id = validated_data['id']
        try:
            Call.objects.get(id=call_id)
            logger.warning('Call Already Exists', extra={'id': call_id})
            return validated_data
        except Call.DoesNotExist:
            pass

        origin = PhoneNumber.get_instance(validated_data['origin'])
        destination = PhoneNumber.get_instance(validated_data['destination'])
        call = Call(
            id=call_id,
            fk_origin_phone_number=origin,
            fk_destination_phone_number=destination,
            started_at=validated_data['timestamp'],
            call_code=validated_data['call_code'],
        )
        call.save()
        validated_data['id'] = call.id
        return validated_data

    def update(self, instance, validated_data):
        call_id = validated_data['id']
        call = Call.objects.get(id=call_id)
        logger.debug('Updating Call', extra={'call': call.id})

        if validated_data['timestamp'] > call.started_at:
            logger.debug('Valid Value', extra={
                'field': 'ended_at',
                'entity':  'Call',
                'value': validated_data['timestamp']
            })

            call.ended_at = validated_data['timestamp']
            call.save()
            logger.debug('Call Saved')
            BillingService().create_billings(call)
        else:
            logger.warning('Received a Invalid Value', extra={
                'field': 'ended_at',
                'entity':  'Call',
                'value': validated_data['timestamp']
            })
        return instance
