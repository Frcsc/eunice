from unittest.mock import patch

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

from coin_desk.models import Article
from coin_desk.tests.factories import IDUrlFactory, ItemFactory
from coin_desk.tests.mixins import SHORT_TEXT


@patch(
    'coin_desk.management.commands.scrap_coin_desk.Command.fetch_article_urls_and_ids'
)
@patch('coin_desk.management.commands.scrap_coin_desk.Command.fetch_articles_details')
class TestCoindeskScrapingCommand(TestCase):
    def setUp(self):
        super().setUp()
        self.valid_urls_and_ids = IDUrlFactory.create_batch(20)
        self.articles_details = [
            ItemFactory(id=detail.get('_id'), url=detail.get('url'))
            for detail in self.valid_urls_and_ids
        ]

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_handle_with_twenty_clean_articles(
        self, mock_fetch_articles_details, mock_fetch_article_urls_and_ids
    ):
        mock_fetch_article_urls_and_ids.return_value = self.valid_urls_and_ids
        mock_fetch_articles_details.return_value = self.articles_details

        call_command('scrap_coin_desk')

        mock_fetch_article_urls_and_ids.assert_called_once()
        mock_fetch_articles_details.assert_called_once_with(
            mock_fetch_article_urls_and_ids.return_value
        )
        self.assertEqual(Article.objects.count(), 20)

    def test_no_duplicate_in_database(
        self, mock_fetch_articles_details, mock_fetch_article_urls_and_ids
    ):
        duplicate_id = SHORT_TEXT.fuzz()
        url_and_ids = IDUrlFactory.create_batch(15)
        three_duplicates = IDUrlFactory.create_batch(3, _id=duplicate_id)

        for duplicate in three_duplicates:
            url_and_ids.append(duplicate)

        articles_details = [
            ItemFactory(id=detail.get('_id'), url=detail.get('url'))
            for detail in url_and_ids
        ]

        mock_fetch_article_urls_and_ids.return_value = url_and_ids
        mock_fetch_articles_details.return_value = articles_details

        call_command('scrap_coin_desk')

        self.assertEqual(Article.objects.count(), 16)


class TestCoinDeskScraperNoneGetArticlesResponse(TestCase):
    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_no_urls_and_id_returned(self):
        with patch(
            'coin_desk.management.commands.scrap_coin_desk.Command.get_articles',
            return_value={},
        ) as mock_fetch_get_articles:

            call_command('scrap_coin_desk')
            mock_fetch_get_articles.assert_called_with(1, 40)
            self.assertEqual(Article.objects.count(), 0)


class TestCoinDeskScraperNoneForUrlAndIdResponse(TestCase):
    def test_no_urls_and_id_returned(self):
        with patch(
            'coin_desk.management.commands.scrap_coin_desk.Command.fetch_article_urls_and_ids',
            return_value=[],
        ) as mock_fetch_article_urls_and_ids:
            call_command('scrap_coin_desk')
            mock_fetch_article_urls_and_ids.assert_called_once()
            self.assertEqual(Article.objects.count(), 0)


class TestCoinDeskScraperBadArticleSection(TestCase):
    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_bad_section_markets(self):
        with patch(
            'coin_desk.management.commands.scrap_coin_desk.Command.map_section',
            return_value={
                "_id": SHORT_TEXT.fuzz(),
                "url": f"/markets/{SHORT_TEXT.fuzz()}",
            },
        ) as mock_bad_article_section:
            call_command('scrap_coin_desk')
            mock_bad_article_section.assert_called()
            self.assertEqual(Article.objects.count(), 0)

    def test_bad_section_learn(self):
        with patch(
            'coin_desk.management.commands.scrap_coin_desk.Command.map_section',
            return_value={
                "_id": SHORT_TEXT.fuzz(),
                "url": f"/learn/{SHORT_TEXT.fuzz()}",
            },
        ) as mock_bad_article_section:
            call_command('scrap_coin_desk')
            mock_bad_article_section.assert_called()

            self.assertEqual(Article.objects.count(), 0)

    def test_bad_section_consensus_magazine(self):
        with patch(
            'coin_desk.management.commands.scrap_coin_desk.Command.map_section',
            return_value={
                "_id": SHORT_TEXT.fuzz(),
                "url": f"/consensus-magazine/{SHORT_TEXT.fuzz()}",
            },
        ) as mock_bad_article_section:
            call_command('scrap_coin_desk')
            mock_bad_article_section.assert_called()
            self.assertEqual(Article.objects.count(), 0)


@patch(
    'coin_desk.management.commands.scrap_coin_desk.Command.fetch_article_urls_and_ids'
)
@patch('coin_desk.management.commands.scrap_coin_desk.Command.get_item_details')
class TestCoinDeskScraperBadArticleItemsDetails(TestCase):
    def setUp(self):
        super().setUp()
        self.valid_urls_and_ids = IDUrlFactory.create_batch(20)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_bad_details(self, mock_get_item_details, mock_fetch_article_urls_and_ids):
        mock_fetch_article_urls_and_ids.return_value = self.valid_urls_and_ids
        mock_get_item_details.return_value = None, None, None, None

        call_command('scrap_coin_desk')

        for url in mock_fetch_article_urls_and_ids.return_value:
            mock_fetch_article_urls_and_ids.called_with(url.get('url'))

        self.assertEqual(Article.objects.count(), 0)
