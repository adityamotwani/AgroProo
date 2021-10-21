from django.apps import apps
from rest_framework import serializers
Farmer = apps.get_model('home', 'Farmer')
Wholesaler = apps.get_model('home', 'Wholesaler')
Crop = apps.get_model('home', 'Crop')
Notification = apps.get_model('home', 'Notification')


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Farmer
        fields = '__all__'

class WholesalerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Wholesaler
        fields = '__all__'

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model= Crop
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model= Notification
        fields = '__all__'