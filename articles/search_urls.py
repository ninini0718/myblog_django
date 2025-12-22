from django.urls import path
from haystack.views import SearchView

app_name = 'search'

urlpatterns = [
    path('', SearchView(template='articles/search.html'), name='haystack_search'),
]
