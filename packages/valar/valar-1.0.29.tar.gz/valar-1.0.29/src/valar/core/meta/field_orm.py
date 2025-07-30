from deepmerge import always_merger
from django.db.models import ManyToOneRel, ForeignKey, ManyToManyRel, ManyToManyField,OneToOneField,OneToOneRel
from django.db.models import IntegerField, BooleanField, FloatField,TextField, CharField
from django.db.models import FileField, JSONField
from django.db.models import DateTimeField, TimeField, DateField

from src.valar.core.valar_models import VTree


class OrmField:

    def __init__(self, entity, field, is_tree):
        self.entity = entity
        self.model_field = field
        self.is_tree = is_tree
        self.not_null = not field.null
        self.clazz = type(field)
        self.multiple = self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel]

        self.prop = self.__prop__()
        self.domain = self.__domain__()
        self.model = self.__model__()
        self.label = self.__label__()
        self.column_width = self.__column_width__()
        self.refer = self.__refer__()
        self.align = self.___align__()
        self.format = self.__formating__()





    def json(self):
        _field = {
            "prop": self.prop,
            "label": self.label,
            "name": self.label,
            "domain": self.domain,
            "refer": self.refer,
            "format": self.format,
            "not_null": self.not_null,
            "align": self.align,
            "column_width": self.column_width,
        }
        if self.is_tree:
            if self.prop in ['pid', 'isLeaf']:
                # _field['hide_on_table'] = True
                _field['hide_on_form'] = True
                _field['hide_on_form_branch'] = True
                _field['hide_on_form_leaf'] = True
            elif self.prop in ['icon']:
                _field['tool'] = 'icon'
        return _field


    def __column_width__(self):
        if self.clazz in [BooleanField, FileField, JSONField]:
            return 100
        elif self.clazz in [DateField, DateTimeField, TimeField]:
            return 120
        return 0

    def __label__(self):
        return self.model._meta.verbose_name \
            if self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel, OneToOneRel, OneToOneField] \
            else self.model_field.verbose_name


    def __model__(self):
        return self.model_field.related_model \
            if self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel, OneToOneRel, OneToOneField, ForeignKey] \
            else None


    def __domain__(self):
        return self.clazz.__name__ \
            if self.clazz in [ManyToOneRel, ManyToManyField, ManyToManyRel ,OneToOneRel, OneToOneField] \
            else self.model_field.get_internal_type()

    def __prop__(self):
        return self.model_field.name + "_id" \
            if self.clazz in [ForeignKey,OneToOneRel, OneToOneField] \
            else self.model_field.name


    def ___align__(self):
        if self.clazz in [FloatField, IntegerField]:
            return 'right'
        elif self.clazz in [BooleanField, FileField, JSONField, DateField, DateTimeField, TimeField]:
            return 'center'
        return 'left'

    def __refer__(self):
        refer = {
            "entity": None,
            "value": "id", "label": 'name', "display": "id",
            "multiple": self.multiple, "strict": False, "remote": False,
            "includes": {}, "excludes": {},
            "root": 0, "isTree": False
        }
        if self.model:
            module, name = self.model.__module__, self.model.__name__
            refer['entity'] = '%s.%s' % (module.replace('.models', '').split('.')[-1], name)
            refer['isTree'] = issubclass(self.model, VTree)
        return refer

    def __formating__(self):
        _format = {
            # 文本
            "maxlength": 0,
            "type": 'text',

            # 数值
            "min": None,
            "max": None,
            "step": 1,
            "precision": None,
            "step_strictly": False,

            # 日期
            "frequency": "date",

            # 文件
            "maximum": 5,
            "accept": [],
            "width": 800,
            "height": 0,
            "file_name_field":None,
            "locked": False,

            #集合
            "set": {}
        }
        if self.clazz == CharField:
            _format['maxlength'] = self.model_field.max_length
        if self.clazz == TextField:
            _format['type'] = "textarea"
        elif self.clazz == DateTimeField:
            _format['frequency'] = "datetime"
        elif self.clazz == IntegerField:
            _format['precision'] = 0
            _format['step_strictly'] = True
        return _format



