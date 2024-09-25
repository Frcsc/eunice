import factory

from coin_desk.models import Article
from coin_desk.tests.mixins import DATE_TIME, LONG_TEXT, SHORT_TEXT


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    id = SHORT_TEXT
    title = SHORT_TEXT
    author = SHORT_TEXT
    published_at = DATE_TIME
    content = LONG_TEXT
    url = factory.LazyAttribute(lambda obj: f"http:coindeak.com/{obj.id}/{obj.title}")
    tags = factory.LazyFunction(lambda: ["finance", "opinion", "crypto"])


class ItemFactory(factory.Factory):
    class Meta:
        model = dict

    id = SHORT_TEXT
    title = SHORT_TEXT
    author = SHORT_TEXT
    published_at = DATE_TIME
    content = LONG_TEXT
    section = SHORT_TEXT
    tags = factory.LazyFunction(lambda: ["finance", "opinion", "crypto"])
    url = factory.LazyAttribute(lambda obj: f"/{obj.section}/{obj._id}/{obj.title}")


class IDUrlFactory(factory.Factory):
    class Meta:
        model = dict

    _id = SHORT_TEXT
    section = SHORT_TEXT
    url = factory.LazyAttribute(
        lambda obj: f"/{obj.section}/{obj._id}/{SHORT_TEXT.fuzz()}"
    )
