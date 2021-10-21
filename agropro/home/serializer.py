from django.db.models import fields
from django.apps import apps
from rest_framework import serializers
from .models import Farmer, Wholesaler
import uuid
from django.conf import settings
from django.core.mail import send_mail


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Farmer
        fields = '__all__'

class WholesalerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Wholesaler
        fields = '__all__'
