from django.urls import path

from coin_desk import api

app_name = 'coin_desk'


urlpatterns = [
    path('articles', api.ArticleListView.as_view(), name='article-list'),
    path(
        'articles/<str:article_id>',
        api.ArticleDetailView.as_view(),
        name='article-detail',
    ),
]
