from datetime import timedelta

from django.utils import timezone
from factory import fuzzy

SHORT_TEXT = fuzzy.FuzzyText(length=56)
LONG_TEXT = fuzzy.FuzzyText(length=1000)
END_TIME = timezone.now()
START_TIME = END_TIME - timedelta(days=1)
VALID_CATEGORIES = [SHORT_TEXT.fuzz(), SHORT_TEXT.fuzz(), SHORT_TEXT.fuzz()]
DATE_TIME = fuzzy.FuzzyDateTime(start_dt=START_TIME, end_dt=END_TIME)
