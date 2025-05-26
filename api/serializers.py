from rest_framework import serializers
from applications.models import Business


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'business_type', 'address', 'category', 'reference', 'registration_date', 'tin']
