from rest_framework import serializers
from users.models import User

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'description']
        extra_kwargs = {
            field: {'read_only': True} for field in fields
        }