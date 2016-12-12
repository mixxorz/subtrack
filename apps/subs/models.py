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


class SubscriptionLog(models.Model):
    subscriptions_added = models.ManyToManyField('subs.Subscription',
                                                 related_name='+')
    subscriptions_removed = models.ManyToManyField('subs.Subscription',
                                                   related_name='+')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='subscription_logs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {} added {} removed'.format(
            self.user,
            self.subscriptions_added.count(),
            self.subscriptions_removed.count()
        )
