from rest_framework import serializers
from .models import PhoneNumber, Call
import logging

logger = logging.getLogger(__name__)


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = (
            'id',
            'area_code',
            'phone_number',
            'created_at',
            'updated_at',
        )


class CallSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    origin = serializers.IntegerField(
        min_value=1000000000, max_value=99999999999, allow_null=True,
        required=False
    )
    destination = serializers.IntegerField(
        min_value=1000000000, max_value=99999999999, allow_null=True,
        required=False
    )
    type = serializers.ChoiceField(choices=Call.TYPE_CHOICES)
    timestamp = serializers.DateTimeField()
    call_identifier = serializers.CharField(max_length=200)

    def create(self, validated_data):
        logger.debug(validated_data)

        call_id = validated_data['id']
        try:
            Call.objects.get(id=call_id)
            return validated_data
        except Call.DoesNotExist:
            logger.debug('Call Does Not Exists', extra={'id': call_id})

        origin = PhoneNumber.get_instance(validated_data['origin'])
        destination = PhoneNumber.get_instance(validated_data['destination'])
        call = Call(
            id=call_id,
            fk_origin_phone_number=origin,
            fk_destination_phone_number=destination,
            started_at=validated_data['timestamp'],
            call_code=validated_data['call_identifier'],
        )
        call.save()
        validated_data['id'] = call.id
        return validated_data

    def update(self, instance, validated_data):
        id = validated_data['id']
        call = Call.objects.get(id=id)
        call.ended_at = validated_data['timestamp']
        pass
