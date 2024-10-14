# auth_app/serializers.py

from rest_framework import serializers

class AdAccountSerializer(serializers.Serializer):
    account_id = serializers.CharField()
    id = serializers.CharField()