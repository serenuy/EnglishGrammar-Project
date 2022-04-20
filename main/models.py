from django.db import models
from django.contrib.auth.models import User

# Create your models/attributes here.

class Collection(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collection", null=True)
	text = models.TextField(max_length=1000, default='',)
