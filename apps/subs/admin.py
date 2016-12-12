from django.contrib import admin

from .models import Subscription, SubscriptionLog

admin.site.register(Subscription)
admin.site.register(SubscriptionLog)
