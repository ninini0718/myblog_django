from django import forms
from .models import Comment
from django.core.exceptions import ValidationError
from core.utils import SENSITIVE_WORDS

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content','image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '写下你的评论...',
            }),
        }
        labels = {
            'content': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': '写下你的评论...',
        })
