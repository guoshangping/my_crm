from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class MyskyConfig(AppConfig):
    name = 'mysky'

    def ready(self):
        autodiscover_modules('mysky')
