from django import forms
from .models import Collection
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

# I did not implement a upload .txt as input because I could not figure that one out.

class NewInput(forms.Form):
	text = forms.CharField(label='Input', max_length=1000, required=False)

class RegisterForm(UserCreationForm):
	email = forms.EmailField()
	first_name = forms.CharField(max_length=100)
	last_name = forms.CharField(max_length=100)

	class Meta:
		model = User
		fields = ["first_name", "last_name",  "username", "email", "password1", "password2"]