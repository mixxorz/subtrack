from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


class Subscription(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    extra_data = JSONField()

    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='subscriptions')

    @property
    def url(self):
        return 'https://www.youtube.com/channel/{}'.format(self.id)

    def __str__(self):
        return self.title
