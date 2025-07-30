# apps.py
import os
from django.apps import AppConfig




class ValarDataConfig(AppConfig):
    name='src.valar.data'
    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from src.valar.core.meta.init_meta_frame import init_meta_frame
            init_meta_frame()