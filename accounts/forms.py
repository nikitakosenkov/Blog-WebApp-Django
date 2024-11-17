from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Profile


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label='First Name', help_text='Enter your First Name', required=False,
                                 max_length=100, widget=forms.TextInput())
    last_name = forms.CharField(label='Last Name', help_text='Enter your Last Name', required=False,
                                max_length=100, widget=forms.TextInput())
    username = forms.CharField(label='Username', help_text='Enter your Username',
                               max_length=100, widget=forms.TextInput())
    email = forms.EmailField(label='E-mail', help_text='Enter your E-mail',
                             widget=forms.TextInput())
    password1 = forms.CharField(label='Password', help_text='Enter your Password',
                                max_length=50, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirm your Password', help_text='Confirm your Password',
                                max_length=50, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email=email)
            raise ValidationError(f'Entered email "{email}" already used in the database, please use another one')
        except User.DoesNotExist:
            return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fields Customization
        for field in self.fields.values():
            field.error_messages['required'] = f'The field "{field.label}" is required'
            field.widget.attrs.update({'class': 'form-control mb-1', 'placeholder': ''})


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'Username'}))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(
                                   attrs={"class": "form-control mb-1", 'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'Username'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control mb-1"}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))

    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
