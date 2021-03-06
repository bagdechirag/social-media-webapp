from django import forms
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()

# interchange the fields to see what happens further

class UserProfileform(forms.ModelForm):
    location = forms.CharField(required=False)
    bio = forms.CharField(required=False)
    class Meta:
        model = User
        fields = ['first_name','last_name','email']

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    class Meta:
        model = Profile
        fields = ['location','bio']

class UserBasicForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    location = forms.CharField(required=False)
    bio = forms.CharField(required=False)
