from django.db import models
from dateutil import parser

# Create your models here.
class Target(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class CrossPlatformProfile(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField()
    bio = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} on {self.platform.name}"

class Profile(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="profiles")
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="profiles")
    
    # Basic identity
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Visuals
    profile_image_url = models.URLField(blank=True, null=True)
    profile_banner_url = models.URLField(blank=True, null=True)
    
    # Metrics
    followers = models.PositiveIntegerField(blank=True, null=True)
    following = models.PositiveIntegerField(blank=True, null=True)
    tweet_count = models.PositiveIntegerField(blank=True, null=True)
    listed_count = models.PositiveIntegerField(blank=True, null=True)
    like_count = models.PositiveIntegerField(blank=True, null=True)
    media_count = models.PositiveIntegerField(blank=True, null=True)
    
    # Account info
    verified = models.BooleanField(default=False)
    most_recent_tweet_id = models.CharField(max_length=50, blank=True, null=True)
    pinned_tweet_id = models.CharField(max_length=50, blank=True, null=True)
    protected = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("platform", "username")
        ordering = ["-followers", "-tweet_count"]

    def __str__(self):
        return f"{self.username} on {self.platform.name}"
    
    # Populate fields helper
    def populate_from_data(self, data: dict):
        self.display_name = data.get("name")
        self.url = data.get("url") or f"https://x.com/{data.get('username')}"
        self.bio = data.get("description")
        self.profile_image_url = data.get("profile_image_url")
        self.profile_banner_url = data.get("profile_banner_url")

        # Metrics
        public_metrics = data.get("public_metrics", {})
        self.followers = int(public_metrics.get("followers_count", 0) or 0)
        self.following = int(public_metrics.get("following_count", 0) or 0)
        self.tweet_count = int(public_metrics.get("tweet_count", 0) or 0)
        self.listed_count = int(public_metrics.get("listed_count", 0) or 0)
        self.like_count = int(public_metrics.get("like_count", 0) or 0)
        self.media_count = int(public_metrics.get("media_count", 0) or 0)

        # Account info
        self.verified = data.get("verified", False)
        self.most_recent_tweet_id = data.get("most_recent_tweet_id")
        self.pinned_tweet_id = data.get("pinned_tweet_id")
        self.protected = data.get("protected", False)
        self.location = data.get("location")

        # Account creation date
        created_at_str = data.get("created_at")
        if created_at_str:
            self.created_at = parser.isoparse(created_at_str)

        return self

class Post(models.Model):
    # profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    username = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField()
    text = models.TextField()
    text_analysis = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField()
    lang = models.CharField(max_length=10, blank=True, null=True)
    reply_settings = models.CharField(max_length=50, blank=True, null=True)
    possibly_sensitive = models.BooleanField(default=False)
    edit_history_tweet_ids = models.JSONField(blank=True, null=True)
    referenced_tweets = models.JSONField(blank=True, null=True)
    entities = models.JSONField(blank=True, null=True)

    # Metrics
    retweet_count = models.PositiveIntegerField(blank=True, null=True)
    reply_count = models.PositiveIntegerField(blank=True, null=True)
    like_count = models.PositiveIntegerField(blank=True, null=True)
    quote_count = models.PositiveIntegerField(blank=True, null=True)
    bookmark_count = models.PositiveIntegerField(blank=True, null=True)
    impression_count = models.PositiveIntegerField(blank=True, null=True)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-like_count"]

    def __str__(self):
        return f"{self.username}: {self.text[:50]}…"

    def populate_from_data(self, data: dict, username: str):   
        """
        Populate the Post instance from X/Twitter API JSON.
        """
        self.username = username
        self.text = data.get("text")
        self.text_analysis = data.get("text_analysis")
        self.lang = data.get("lang")
        self.reply_settings = data.get("reply_settings")
        self.possibly_sensitive = data.get("possibly_sensitive", False)
        self.edit_history_tweet_ids = data.get("edit_history_tweet_ids")
        self.referenced_tweets = data.get("referenced_tweets")
        self.entities = data.get("entities")

        metrics = data.get("public_metrics", {})
        self.retweet_count = metrics.get("retweet_count")
        self.reply_count = metrics.get("reply_count")
        self.like_count = metrics.get("like_count")
        self.quote_count = metrics.get("quote_count")
        self.bookmark_count = metrics.get("bookmark_count")
        self.impression_count = metrics.get("impression_count")

        created_at_str = data.get("created_at")
        if created_at_str:
            try:
                self.date = parser.isoparse(created_at_str)
            except Exception:
                self.date = None

class RawJSONData(models.Model):
    data = models.TextField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Raw data  {self.fetched_at}"
