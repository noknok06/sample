from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm

User = get_user_model()

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    position = forms.CharField(max_length=100, label=_('Position'), required=False)
    phone_number = forms.CharField(max_length=20, label=_('Phone Number'), required=False)
    
    def save(self, request):
        # Save the user using the parent class save method
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.position = self.cleaned_data['position']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'position', 
            'phone_number', 'profile_picture'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'hidden'}),
        }

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['role']