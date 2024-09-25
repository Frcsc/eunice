from django.db import models


class Article(models.Model):
    id = models.CharField(max_length=512, primary_key=True, editable=False)
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=264)
    published_at = models.DateTimeField()
    content = models.TextField()
    url = models.URLField(unique=True)
    tags = models.JSONField(default=list)

    @property
    def snippet(self):
        return self.content[:150]

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
