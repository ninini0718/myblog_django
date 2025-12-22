from django import forms
from .models import Article, Category, Tag
from ckeditor.widgets import CKEditorWidget
class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(config_name='default'))
        
    class Meta:
        model = Article
        fields = ['title', 'content', 'excerpt', 'category', 'tags', 'status', 'image', 'is_top']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all()
