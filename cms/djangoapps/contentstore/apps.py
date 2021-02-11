"""
Contentstore Application Configuration

Above-modulestore level signal handlers are connected here.
"""


from django.apps import AppConfig


class ContentstoreConfig(AppConfig):
    """
    Application Configuration for Contentstore.
    """
    name = u'cms.djangoapps.contentstore'

    def ready(self):
        """
        Connect handlers to signals.
        """
