import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from eunice.settings import COIN_DESK_API


class CoinDeskScrapper:
    SECTION_MAP = ["learn", "markets", 'consensus-magazine']

    def format_time(self, data):
        try:
            date_str = data.replace('.', '')
            date_format = "%b %d, %Y at %I:%M %p UTC"
            parsed_date = datetime.strptime(date_str, date_format)
            return parsed_date.replace(tzinfo=ZoneInfo("UTC"))
        except ValueError:
            return None

    def map_section(self, partial_url):
        for key in self.SECTION_MAP:
            if partial_url.startswith(f"/{key}/"):
                return key
        return None

    def get_articles(self, page, size):

        query = f'{{"language":"en","size":{size},"page":{page},"format":"timeline"}}'

        try:
            response = requests.get(
                COIN_DESK_API,
                headers={'user-agent': f'{uuid.uuid4()}'},
                params={"query": query},
            )

            if response.status_code == 400:
                return {}

            return response.json().get('items')

        except RequestException:
            return {}

    def get_item_details(self, url):
        try:
            response = requests.get(url, headers={'user-agent': f'{uuid.uuid4()}'})
            soup = BeautifulSoup(response.content, 'html.parser')

            author = soup.find('div', class_='at-authors').get_text()
            title = soup.find('h1').get_text()
            raw_published_at = soup.find('div', class_='at-created').get_text()
            content = soup.find('div', class_='at-content-wrapper').get_text()
            tags = soup.find_all('a', class_='eJTFpe')

            published_at = self.format_time(raw_published_at)

            return (
                title.strip(),
                author.replace("By ", "").strip(),
                published_at,
                content.strip(),
                [i.get_text().strip() for i in tags],
            )
        except RequestException:
            return None, None, None, None, None
