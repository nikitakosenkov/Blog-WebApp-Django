from django.forms import *
from .models import Comment

class EmailPostForm(forms.Form):
    name = CharField(max_length=25, required=False, widget=TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'Name'}))
    email = EmailField(required=False, widget=TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'E-Mail'}))
    to = EmailField(required=True, widget=TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'To (E-Mail)'}))
    comments = CharField(required=False,
                               widget=Textarea(attrs={"class": "form-control mb-1", 'placeholder': 'Comments'}))


class CommentForm(ModelForm):
    name = CharField(required=True,
                           widget=TextInput(attrs={"class": "form-control", 'placeholder': 'Name'}))
    email = EmailField(required=False,
                             widget=EmailInput(attrs={"class": "form-control", 'placeholder': 'Email'}))
    body = CharField(required=True, widget=Textarea(attrs={"class": "form-control", 'placeholder': 'Write your comment...'}))

    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):
    query = CharField(required=False, widget=TextInput(attrs={'placeholder': "let's see...", "class": "form-control mb-1"}))