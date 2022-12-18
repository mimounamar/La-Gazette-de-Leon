from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from gazette_backend.models import LostPasswordToken, Edition, Article


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "groups"]


class LostPasswordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostPasswordToken
        fields = ["username", "token"]


class EditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        fields = ["id", "title", "status", "done", "correction", "redaction"]


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "status", "label", "redactor_1", "redactor_2", "full_names", "corrector", "content", "edition"]
