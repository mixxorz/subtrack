from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

import requests


class SubscriptionsView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super(SubscriptionsView, self).get_context_data(**kwargs)

        provider = self.request.user.socialaccount_set.get(provider='google')
        token = provider.socialtoken_set.first().token

        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {'part': 'snippet', 'mine': True, 'maxResults': 50}
        url = 'https://www.googleapis.com/youtube/v3/subscriptions'

        res = requests.get(url, params=params, headers=headers)

        channels = []

        for item in res.json()['items']:
            channels.append(item['snippet']['title'])

        context['channels'] = channels

        return context


subscriptions_view = SubscriptionsView.as_view()
