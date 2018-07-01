from rest_framework import serializers
from .models import PhoneNumber


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
