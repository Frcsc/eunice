from rest_framework import serializers

from coin_desk.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article

        fields = ["id", "title", "published_at", "snippet", "url"]
