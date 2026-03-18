from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import datetime

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
    
class TelegramScrapeSerializer(serializers.Serializer):
    target = serializers.CharField(required=True)
    message_limit = serializers.IntegerField(required=False, default=25, min_value=1)
    user_limit = serializers.IntegerField(required=False, default=50, min_value=1)
    # keyword = serializers.CharField(required=False, allow_blank=True)
    include_users = serializers.BooleanField(required=False, default=True)
    join_before_scrape = serializers.BooleanField(required=False, default=False)
    since = serializers.DateTimeField(required=False)

    keyword_groups = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    custom_keywords = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    def validate_since(self, value):
        if value and value > datetime.now(value.tzinfo):
            raise serializers.ValidationError("`since` cannot be in the future.")
        return value