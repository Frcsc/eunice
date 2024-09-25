from django.contrib import admin

from coin_desk.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'published_at', 'url']


admin.site.register(Article, ArticleAdmin)
