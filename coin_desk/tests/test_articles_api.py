from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_desk.models import Article
from coin_desk.serializers import ArticleSerializer
from coin_desk.tests.factories import ArticleFactory
from coin_desk.tests.mixins import SHORT_TEXT


class TestArticleListAndRetrieve(APITestCase):
    def setUp(self):
        super().setUp()

        self.list_url = reverse('coin_desk:article-list')
        self.article_id = SHORT_TEXT.fuzz()

        self.retrieve_url = reverse(
            'coin_desk:article-detail',
            kwargs={'article_id': self.article_id},
        )
        self.not_found_retrieve_url = reverse(
            'coin_desk:article-detail',
            kwargs={'article_id': SHORT_TEXT.fuzz()},
        )

        ArticleFactory(id=self.article_id)
        ArticleFactory.create_batch(19)

        self.expected_fields = ArticleSerializer.Meta.fields
        self.queryset = Article.objects.all()

    def test_get_all_articles(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.queryset.count(), 20)

        for article in response.data:
            for field in self.expected_fields:
                self.assertIn(field, article)

    def test_get_a_single_article(self):
        response = self.client.get(self.retrieve_url)
        self.assertEqual(self.queryset.count(), 20)
        self.assertEqual(response.data.get('id'), self.article_id)
        self.assertEqual(len(response.data.get('snippet')), 150)

    def test_not_found_article(self):
        response = self.client.get(self.not_found_retrieve_url)
        self.assertEqual(self.queryset.count(), 20)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('detail'), "No Article matches the given query."
        )


class TestArticleEmptyState(APITestCase):
    def setUp(self):
        super().setUp()

        self.url = reverse('coin_desk:article-list')
        self.queryset = Article.objects.all()

    def test_no_artcle_in_db(self):
        response = self.client.get(self.url)
        self.assertEqual(self.queryset.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
