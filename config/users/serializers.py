from rest_framework import serializers

from users.models import User

class TempUserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'description']
        extra_kwargs = {
            field: {'read_only': True} for field in fields
        }
        
class GoogleLoginRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField()     
        
class GoogleRegisterRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField()
    description = serializers.CharField()       
        

class KakaoLoginRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField()

class KakaoRegisterRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField()
    description = serializers.CharField()
