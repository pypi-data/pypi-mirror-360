from django.apps import apps

from .model_orm import OrmModel
from ..valar_models import VModel


class OrmEngine:

    def __init__(self):
        mapping = {}
        for model in apps.get_models():
            if issubclass(model, VModel):
                path, name = model.__module__, model.__name__
                prefix = 'src.valar.' if path.startswith('src') else 'valar.'
                app = path.replace('.models', '').replace(prefix, '')
                entity = '%s.%s' % (app, name)
                mapping[entity] = model
        self.mapping = mapping

    def get_mapping(self)->dict:
        return self.mapping

    def get_model(self,entity)->OrmModel:
        mod = self.mapping.get(entity)
        return OrmModel(mod, entity)
