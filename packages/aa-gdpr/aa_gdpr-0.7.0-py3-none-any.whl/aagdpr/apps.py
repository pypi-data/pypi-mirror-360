from django.apps import AppConfig

from . import __version__


class AagdprConfig(AppConfig):
    name = 'aagdpr'
    label = 'aagdpr'
    verbose_name = f'AA GDPR v{__version__}'
