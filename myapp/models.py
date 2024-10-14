# facebook_ads/models.py
from django.contrib.auth.models import User
from django.db import models

class FacebookAccessToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
