from rest_framework import serializers
from django.contrib.auth.models import User

from api.models import Post, Profile, Platform

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        raw_data = request.data  

        platform, _ = Platform.objects.get_or_create(name="X")
        validated_data['platform'] = platform

        target = validated_data.get('target')
        username = validated_data.get('username')

        profile, _ = Profile.objects.update_or_create(
            platform=platform,
            username=username,
            defaults={'target': target}
        )

        profile.populate_from_data(raw_data)
        profile.save()

        return profile

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def create(self, validated_data):
        # Create user with hashed password
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", "")
        )
        return user