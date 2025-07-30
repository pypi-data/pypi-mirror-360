import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class ChannelMapping:
    def __init__(self):
        root = settings.ROOT_URLCONF
        module = importlib.import_module(root)
        name = 'channel_mapping'
        if hasattr(module, name):
            self.mapping: dict = getattr(module, name)
        else:
            raise ImproperlyConfigured("%r has no attribute %r" % (root, name))

    def get_handler(self, handler):
        method = self.mapping.get(handler)
        if method is None:
            raise ImproperlyConfigured("Cannot find handler - %r" % handler)
        return method

