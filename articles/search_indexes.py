from haystack import indexes
from .models import Article

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='content')
    excerpt = indexes.CharField(model_attr='excerpt')
    created_at = indexes.DateTimeField(model_attr='created_at')
    
    def get_model(self):
        return Article
    
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status='published')
