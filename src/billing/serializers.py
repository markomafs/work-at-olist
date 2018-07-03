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
    phone_number = serializers.CharField(max_length=15)
    type = serializers.ChoiceField(choices=Call.TYPE_CHOICES)
    # timestamp = serializers.DateTimeField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    # def create(self, validated_data):
    #     logger.debug('Create Call Validated Data', extra=validated_data)
    #     return None
    #
    # def update(self, instance, validated_data):
    #     instance.phone_number = validated_data.get('phone_number',
    #                                                instance.phone_number)
    #     instance.started_at = validated_data.get('timestamp',
    #                                              instance.started_at)
    #     type = validated_data.get('type')
    #     return instance

    #
    # class Meta:
    #     fields = (
    #         'id',
    #         'call_code',
    #         'started_at',
    #         'ended_at',
    #         'created_at',
    #         'updated_at',
    #         'phone_number',
    #         'type',
    #         'timestamp'
    #     )
