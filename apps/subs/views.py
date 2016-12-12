from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
import requests

from .models import Subscription, SubscriptionLog


class Error(Exception):
    pass


class GoogleAPIError(Error):

    def __init__(self, error):
        self.code = error['code']
        self.message = error['message']
        self.error = error

    def __str__(self):
        return ('{}: {}'.format(self.code, self.message))


def fetch_subscriptions(token):
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'part': 'snippet', 'mine': True, 'maxResults': 50}
    url = 'https://www.googleapis.com/youtube/v3/subscriptions'

    res = requests.get(url, params=params, headers=headers)

    if res.status_code != 200:
        raise GoogleAPIError(res.json()['error'])

    channels = [x['snippet'] for x in res.json()['items']]

    # Pagination
    while res.json().get('nextPageToken', False):
        params['pageToken'] = res.json()['nextPageToken']
        res = requests.get(url, params=params, headers=headers)

        for item in res.json()['items']:
            channels.append(item['snippet'])

    return channels


class SubscriptionListView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super(SubscriptionListView, self).get_context_data(**kwargs)
        context['channels'] = self.request.user.subscriptions.all()
        context['sub_log'] = self.request.user.subscription_logs.order_by('created_at').last()  # noqa
        return context


subscription_list_view = SubscriptionListView.as_view()


class SubscriptionFetchView(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request):
        user = self.request.user
        provider = user.socialaccount_set.get(provider='google')
        token = provider.socialtoken_set.first().token
        try:
            channels = fetch_subscriptions(token)
        except GoogleAPIError as e:
            messages.error(self.request, 'Error {}'.format(str(e)))
            return redirect(reverse('subs'))

        current_subs = list(user.subscriptions.all())
        fetched_subs = []
        added_subs = []
        removed_subs = []

        for channel in channels:
            sub, created = Subscription.objects.get_or_create(
                id=channel['resourceId']['channelId'],
                defaults={
                    'title': channel['title'],
                    'extra_data': channel,
                },
            )

            fetched_subs.append(sub)

        for sub in fetched_subs:
            if sub not in current_subs:
                user.subscriptions.add(sub)
                user.save()
                added_subs.append(sub)

        for sub in current_subs:
            if sub not in fetched_subs:
                user.subscriptions.remove(sub)
                user.save()
                removed_subs.append(sub)

        sub_log = SubscriptionLog.objects.create(user=user)
        sub_log.subscriptions_added.add(*added_subs)
        sub_log.subscriptions_removed.add(*removed_subs)
        sub_log.save()

        return redirect(reverse('subs'))


subscription_fetch_view = SubscriptionFetchView.as_view()
