from django.conf import settings

DEFAULT_SETTINGS = {
    'LOCALBITCOINS_API_KEY': '',
    'LOCALBITCOINS_API_SECRET': '',
}

for k, v in DEFAULT_SETTINGS.iteritems():
    if not hasattr(settings, k):
        setattr(settings, k, v)
