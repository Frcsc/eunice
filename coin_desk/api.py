from rest_framework import generics

from coin_desk.models import Article
from coin_desk.serializers import ArticleSerializer


class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_url_kwarg = 'article_id'
