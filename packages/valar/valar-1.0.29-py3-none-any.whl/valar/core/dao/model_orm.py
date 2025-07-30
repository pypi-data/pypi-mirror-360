import copy

from bson import ObjectId
from bson.errors import InvalidId
from deepmerge import always_merger
from django.db.models import ManyToOneRel, ForeignKey, ManyToManyRel, ManyToManyField, OneToOneField, OneToOneRel
from django.db.models import QuerySet
from django.db.models import Manager
from django.db.models.fields.files import FieldFile
from django.forms import FileField

from .engine_minio import MinioEngine
from .utils_orm import OrmUtils
from ..meta.defaults.field_keys_default import meta_field_key_defaults
from ..meta.defaults.field_values_default import meta_field_value_defaults
from ..meta.field_orm import OrmField
from ..valar_models import VModel, VTree
from ...data.models import MetaFieldDomain


class OrmModel:

    def __init__(self, mod, entity):
        self.entity = entity
        self.model = mod
        meta = getattr(mod, '_meta')
        self.name = meta.verbose_name
        self.is_tree = issubclass(mod, VTree)
        self.manager: Manager = mod.objects
        fields = meta.get_fields()
        mapping = {}
        for f in fields:
            field = OrmField(entity, f, self.is_tree)
            mapping[field.prop] = field
        self.mapping = mapping
        self.minio = MinioEngine()
        self.bucket_name = self.minio.get_bucket_name(entity)

    @staticmethod
    def object_id(_id):
        try:
            return int(_id)
        except TypeError:
            return None


    def props(self, domain=None):
        array = []
        for prop in self.mapping:
            field: OrmField = self.mapping[prop]
            if field.domain == domain or domain is None:
                array.append(prop)
        return array



    def initial_fields(self, code):
        props = self.props()
        default_keys = meta_field_key_defaults.get(self.entity,{})
        method, array = default_keys.get(code, ('omit',[]))
        def fun(prop): return prop not in array if method == 'omit' else prop in array
        props = [prop for prop in props if fun(prop)]

        default_values = meta_field_value_defaults.get(self.entity, {})
        init_values = default_values.get('__init__', {})
        code_values = default_values.get(code, {})
        default_fields = always_merger.merge(init_values, code_values)

        values = MetaFieldDomain.objects.all().values('name', 'default__code', 'align')
        meta_frame = {
            vs['name']: {
                "tool": vs['default__code'],
                "align": vs['align'],
            }
            for vs in values
        }
        fields = []
        for prop in props:
            field = self.get_field(prop)
            field_json = field.json()
            frame = copy.deepcopy(meta_frame.get(field.domain, {}))
            refer = field_json['refer']
            if refer['isTree'] and frame.get('tool') == 'select' :
                frame['tool'] = 'tree'
            elif self.is_tree and prop =='icon':
                frame['tool'] = 'icon'
            field_json.update(frame)
            default_field = default_fields.get(prop, {})
            always_merger.merge(field_json, default_field)
            fields.append(field_json)
        fields.reverse()
        return fields

    def get_field(self, prop)->OrmField:
        return self.mapping[prop]

    def detach_item(self, item):
        _id = item.get('id')
        if _id:
            del item['id']
        simple_item = {}
        complex_item = {}
        for prop in item:
            field = self.get_field(prop)
            value = item.get(prop)
            if field.domain in ['ManyToOneRel', 'ManyToManyField', 'ManyToManyRel', 'OneToOneRel', 'OneToOneField','FileField']:
                complex_item[prop] = value
            else:
                simple_item[prop] = value
        return self.object_id(_id), simple_item, complex_item

    def get_file_paths(self, query_set: QuerySet):
        props = self.props('FileField')
        items = query_set.values(*props)
        array = []
        for item in items:
            array += [i for i in item.values() if i]
        return array

    def remove_files(self, query_set: QuerySet):
        paths = self.get_file_paths(query_set)
        for path in paths:
            self.minio.remove_path(path)

    def save_complex_field(self, complex_item, bean):
        for prop in complex_item:
            value = complex_item[prop]
            field = self.get_field(prop).model_field
            clazz = type(field)
            if clazz == ManyToManyField:
                m2m = getattr(bean, prop)
                m2m.clear()
                m2m.add(*value)
            elif clazz == ManyToOneRel:
                getattr(bean, field.get_accessor_name()).clear()
                remote_model: VModel = field.related_model
                new_set: QuerySet = remote_model.objects.filter(id__in=value)
                remote_field: ForeignKey = field.remote_field
                k = remote_field.get_attname()
                new_set.update(**{k: bean.id})
            elif clazz == ManyToManyRel:
                getattr(bean, field.get_accessor_name()).clear()
                remote_model: VModel = field.related_model
                remote_items: QuerySet = remote_model.objects.filter(id__in=value)
                remote_field: ManyToManyField = field.remote_field
                remote_field_prop = remote_field.get_attname()
                for _bean in remote_items:
                    bean_set = getattr(_bean, remote_field_prop)
                    bean_set.add(bean)
            elif clazz == OneToOneRel:
                remote_model: VModel = field.related_model
                remote_field: OneToOneField = field.remote_field
                remote_field_prop = remote_field.get_attname()
                _bean = remote_model.objects.get(id=value)
                __bean = remote_model.objects.filter(**{remote_field_prop: bean.id}).first()
                if __bean:
                    setattr(__bean, remote_field_prop, None)
                    __bean.save()
                setattr(_bean, remote_field_prop, bean.id)
                _bean.save()
            elif clazz == OneToOneField:
                __bean = field.model.objects.filter(**{prop: value}).first()
                if __bean:
                    setattr(__bean, prop, None)
                    __bean.save()
                setattr(bean, prop, value)
            elif clazz == FileField:
                file_name, _bytes = value
                field_file: FieldFile = getattr(bean, prop)
                if field_file:
                    path = field_file.name
                    self.minio.remove_path(path)
                object_name = self.minio.get_object_name(bean.id, prop, file_name)
                path = self.minio.upload(self.bucket_name, object_name, _bytes) if _bytes else None
                setattr(bean, prop, path)




    def to_dict(self, query_set: QuerySet, code=None):
        # query_set = query_set.filter(saved=True)
        utils = OrmUtils()
        orm_fields = self.mapping.values()
        # 简单字段取值
        simple_props = [field.prop for field in orm_fields if field.domain not in utils.referred_domains]
        custom_props = utils.custom_props(self.entity, code)
        results = list(query_set.filter().values(*[*simple_props, *custom_props]))
        utils.date_values(orm_fields, results)
        # 关系型字段取值
        mapping = { row['id']: row for row in results}
        referred_fields = [field for field in orm_fields if field.domain in utils.referred_domains]
        pks = mapping.keys()
        for field in referred_fields:
            manager: Manager = query_set.model.objects
            qs = manager.filter(id__in=pks)
            utils.linkage(field, qs, mapping)
        return results

