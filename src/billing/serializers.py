from rest_framework import serializers
from .models import PhoneNumber, Call
from .services import BillingService
import logging

logger = logging.getLogger(__name__)


class PhoneNumberSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='phonenumber-detail',
        lookup_field='phone_number',
    )
    billing_url = serializers.HyperlinkedIdentityField(
        view_name='phonenumber-billings',
        lookup_field='phone_number',
    )

    class Meta:
        model = PhoneNumber
        fields = (
            'id',
            'phone_number',
            'created_at',
            'updated_at',
            'url',
            'billing_url'
        )


class CallSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    source = serializers.IntegerField(
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

        call, created = Call.objects.get_or_create(id=call_id)

        if created is False and validated_data['type'] == Call.TYPE_END:
            self.update(call, validated_data)

        logger.warning('Call Already Exists', extra={'id': call_id})

        if validated_data['type'] == Call.TYPE_END:
            call.ended_at = validated_data['timestamp']
            call.call_code = validated_data['call_code']
            call.save()
        else:
            source = PhoneNumber.get_instance(validated_data['source'])
            destination = PhoneNumber.get_instance(
                validated_data['destination'])

            call.fk_source_phone_number = source
            call.fk_destination_phone_number = destination
            call.started_at = validated_data['timestamp']
            call.call_code = validated_data['call_code']

            call.save()
            if call.ended_at is not None:
                BillingService().create_billings(call)

        return validated_data

    def update(self, instance, validated_data):
        logger.debug('Updating Call', extra={'call': instance.id})

        if validated_data['timestamp'] > instance.started_at:
            logger.debug('Valid Value', extra={
                'field': 'ended_at',
                'entity':  'Call',
                'value': validated_data['timestamp']
            })

            instance.ended_at = validated_data['timestamp']
            instance.save()
            logger.debug('Call Saved')
            BillingService().create_billings(instance)
        else:
            logger.warning('Received a Invalid Value', extra={
                'field': 'ended_at',
                'entity':  'Call',
                'value': validated_data['timestamp']
            })
        return instance
