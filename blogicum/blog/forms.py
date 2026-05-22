from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%d.%m.%Y %H:%M',
                attrs={'type': 'datetime'},
            ),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        exclude = ('author', 'post', 'is_published')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = (
            'is_staff',
            'groups',
            'user_permissions',
            'is_active',
            'is_superuser',
            'last_login',
            'date_joined',
            'username',
            'password',
        )
