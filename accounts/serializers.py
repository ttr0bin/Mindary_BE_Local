from rest_framework import serializers
from .models import User
import re     

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'



"""
      < Kakao Login >
"""
class KakaoLoginRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField()

class KakaoRegisterRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField()
    nickname = serializers.CharField()



"""
      < Original Login >
"""
class OriginalRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'nickname', 'password']

    def validate_password(self, value):
        # 비밀번호가 8~12 자리 영소문자, 숫자, 특수문자 조합으로 이루어졌는지 검증합니다.
        if not re.match(r'^(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])[a-z\d!@#$%^&*]{8,12}$', value):
            raise serializers.ValidationError(
                "비밀번호는 8~12 자리의 영소문자, 숫자, 특수문자 조합이어야 합니다."
            )
        return value
    
    def create(self, validated_data):
        # create_user 메서드를 호출하여 새로운 사용자 생성
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password']
        )
        return user

# 이메일
class EmailVerificationSendSerializer(serializers.Serializer):
    email = serializers.EmailField()

# 이메일 인증 코드
class EmailVerificationCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)

