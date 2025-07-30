from deepmerge import always_merger

from .defaults.view_defaults import meta_view_default_values
from ...core.dao.dao_orm import OrmDao
from ...data.models import MetaView, Meta, MetaFieldDomain


class OrmMeta:

    def __init__(self, entity, code):
        self.entity = entity
        self.dao = OrmDao(entity)
        self.code = code or 'default'


        # load_meta
        meta_dao = OrmDao('data.Meta')
        _meta = {"entity": entity}
        meta: Meta = meta_dao.search(_meta).first()
        if meta is None:
            _meta.update({"name": self.dao.model.name, 'saved': True})
            meta = meta_dao.save_one(_meta)
        self.meta = meta


        # load_view
        view_dao = OrmDao('data.MetaView')
        _view = {"code": self.code, "meta_id": meta.id}
        view: MetaView = view_dao.search(_view).first()
        if view is None:
            _view.update({"name": self.code.upper(), "saved": True})
            view = view_dao.save_one(_view)
            self.__init_view__(view)
        self.view = view

        # load_fields
        if view.metafield_set.count() == 0:
            field_dao = OrmDao('data.MetaField')
            _fields = self.dao.model.initial_fields(code)
            for _field in _fields:
                if _field['prop'] not in [ 'sort', 'create_time','modify_time','saved']:
                    _field.update({'view_id': view.id, "saved": True})
                    field_dao.save_one(_field)


    def get_view(self):
        _view = self.view.json()
        meta = self.meta.json()
        name, entity = meta['name'], meta['entity']
        fields = self.view.metafield_set.all().order_by('-sort')
        _fields = {
            field.prop: field.json(entity=entity, code=self.code, db='orm')
            for field in fields
            # if field.prop not in ['id', 'sort', 'create_time','modify_time','saved','pid','isLeaf']
        }
        _view.update({
            '$db': 'orm',
            '$entity': entity,
            '$code': self.code,
            '$meta_name': name,
            '$is_tree': self.dao.model.is_tree,
            '$fields': _fields
        })
        return _view

    def __init_view__(self, view: MetaView):
        default_view = meta_view_default_values.get(self.entity, {})
        default_values = default_view.get('__init__',{})
        code_values = default_view.get(self.code, {})
        values = always_merger.merge(default_values, code_values)
        if len(values) > 0:
            for key, value in values.items():
                setattr(view, key, value)
            view.save()