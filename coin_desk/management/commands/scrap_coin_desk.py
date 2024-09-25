from django.core.management.base import BaseCommand

from coin_desk.mixins import CoinDeskScrapper
from coin_desk.models import Article
from eunice.settings import COIN_DESK_BASE_URL

REQUIRED_ARTICLE_NUM = 20


class Command(BaseCommand, CoinDeskScrapper):
    def fetch_article_urls_and_ids(self):
        valid_urls_and_ids = []
        count = 0
        page_num = 1
        page_size = 40
        seen_article_ids = set()

        while count < REQUIRED_ARTICLE_NUM:

            raw_articles = self.get_articles(page_num, page_size)

            if not raw_articles:
                self.stdout.write(
                    self.style.WARNING('No more articles found in the API')
                )
                break

            for raw_article in raw_articles:

                article_id = raw_article.get('_id')
                partial_url = raw_article.get('url')

                if not article_id or not partial_url:
                    continue

                if (
                    self.map_section(partial_url) is not None
                    or article_id in seen_article_ids
                ):
                    continue

                valid_urls_and_ids.append(
                    {"_id": article_id, "url": f"{COIN_DESK_BASE_URL}{partial_url}"}
                )

                seen_article_ids.add(article_id)

                count += 1

                if count >= REQUIRED_ARTICLE_NUM:
                    break

            page_num += 1
        return valid_urls_and_ids

    def fetch_articles_details(self, items):
        detailed_article_fields = []
        for item in items:
            try:
                title, author, published_at, content, tags = self.get_item_details(
                    item.get('url')
                )
                if (
                    not title
                    or not author
                    or not published_at
                    or not content
                    or not tags
                ):
                    continue

                detailed_article_fields.append(
                    {
                        "id": item.get('_id'),
                        'title': title,
                        'url': item.get('url'),
                        'author': author,
                        'published_at': published_at,
                        'content': content,
                        'tags': tags,
                    }
                )
            except Exception:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error fetching details for article {item.get('_id')}"
                    )
                )

        return detailed_article_fields

    def save_articles(self, articles):
        for article in articles:
            obj, created = Article.objects.update_or_create(
                id=article.get('id'),
                defaults={
                    'title': article.get('title'),
                    'author': article.get('author'),
                    'published_at': article.get('published_at'),
                    'content': article.get('content'),
                    'url': article.get('url'),
                    'tags': article.get('tags'),
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} article with ID: {obj.id}"))

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting CoinDesk article scraping..."))

        article_urls_and_ids = self.fetch_article_urls_and_ids()

        if not article_urls_and_ids:
            self.stdout.write(self.style.WARNING("No valid urls and ids. Exiting..."))
            return

        articles_and_their_details = self.fetch_articles_details(article_urls_and_ids)

        if not articles_and_their_details:
            self.stdout.write(
                self.style.WARNING(
                    "No valid articles and their details found. Exiting..."
                )
            )
            return

        self.save_articles(articles_and_their_details)
