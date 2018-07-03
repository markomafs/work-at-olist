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
    origin = serializers.CharField(max_length=15, allow_null=True,
                                   required=False)
    destination = serializers.CharField(max_length=15, allow_null=True,
                                        required=False)
    type = serializers.ChoiceField(choices=Call.TYPE_CHOICES)
    timestamp = serializers.DateTimeField()
    call_identifier = serializers.CharField(max_length=200)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
