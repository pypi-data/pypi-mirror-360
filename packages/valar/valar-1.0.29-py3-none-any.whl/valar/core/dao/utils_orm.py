from django.db.models import QuerySet

from ..valar_models import VModel
from ...core.meta.field_orm import OrmField
from ...data.models import MetaField


class OrmUtils:
    def __init__(self):
        self.multiple_domains = ['ManyToOneRel', 'ManyToManyField', 'ManyToManyRel']
        self.referred_domains = [*self.multiple_domains, 'OneToOneRel', 'OneToOneField', 'ForeignKey']
        self.omit_field_props = ['create_time', 'modify_time', 'saved', 'sort']
        self.data_props_formatting = {'DateField': '%Y-%m-%d', 'DateTimeField': '%Y-%m-%d %H:%M:%S', 'TimeField': '%H:%M:%S'}


    @staticmethod
    def json(bean: VModel):
        pass

    @staticmethod
    def custom_props(entity, code='default'):
        field_set = MetaField.objects.filter(view__code=code, view__meta__entity=entity, domain='Custom').values('prop')
        return [item['prop'] for item in field_set if item['prop']]


    def linkage(self, field, query_set: QuerySet, mapping):
        model_field = field.model_field
        prop = model_field.name
        multiple = field.domain in self.multiple_domains

        # 获取级联关系的键索引
        ref_prop = f'{prop}__id'
        edges = query_set.exclude(**{f'{ref_prop}__isnull': True}).values('id', ref_prop)
        if multiple:
            related_primary_keys = set()
            results_mapping = {}
            for edge in edges:
                _id, rid = edge['id'], edge[ref_prop]
                related_primary_keys.add(rid)
                array = results_mapping.get(_id, [])
                array.append(rid)
                results_mapping[_id] = array
        else:
            results_mapping = {row['id']: row[ref_prop] for row in edges if row[ref_prop]}
            related_primary_keys = set(results_mapping.values())

        # 获取级联关系从属方的数据
        related_model = model_field.related_model
        related_fields = related_model._meta.get_fields()
        related_props = self.__get_related_props__(related_fields)
        related_values = list(related_model.objects.filter(id__in=related_primary_keys).values(*related_props))
        self.date_values(related_fields, related_values)
        related_mapping = {item['id']: item for item in related_values}

        # 将从属方的数据绑定在主数据上
        for _id in mapping:
            row = mapping[_id]
            if multiple:
                keys = results_mapping.get(_id, [])
                items = [related_mapping[pid] for pid in keys]
                row[prop] = keys
                row[f'{prop}_set'] = items
            else:
                key = results_mapping.get(_id)
                item = related_mapping.get(key) if key else None
                row[prop] = item
                row[f'{prop}_id'] = key

    def __get_related_props__(self,fields):
        def fun(field): return type(field).__name__ not in self.referred_domains and field.name not in self.omit_field_props
        return [field.name for field in fields if fun(field)]

    def date_values(self, fields, values):
        date_props_mapping = {}
        for field in fields:
            if isinstance(field, OrmField):
                prop = field.prop
                domain = field.domain
            else:
                prop = field.name
                domain = type(field).__name__
            if domain in self.data_props_formatting.keys():
                date_props_mapping[prop] = self.data_props_formatting[domain]
        for row in values:
            for prop, formating in date_props_mapping.items():
                if row.get(prop):
                    row[prop] = row[prop].strftime(formating)