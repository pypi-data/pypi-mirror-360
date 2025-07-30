import datetime
from django.core.paginator import Paginator
from django.db.models import QuerySet

from .engine import DaoEngine
from .query_orm import OrmQuery
from ..dao_abstract import AbstractDao


class OrmDao(AbstractDao):
    def __init__(self, entity):
        self.entity = entity
        engine = DaoEngine().orm
        self.model = engine.get_model(entity)
        self.objects = self.model.manager

    def get_model(self):
        return self.model

    def save_one(self, item, with_id=False):
        oid, simple_item, complex_item  = self.model.detach_item(item)
        query_set = self.objects.filter(id=oid) if oid else []
        if len(query_set):
            simple_item['modify_time'] = datetime.datetime.now()
            query_set.update(**simple_item)
            bean = query_set.first()
        else:
            if with_id:
                bean = self.objects.create(**{**simple_item, "id": oid})
            else:
                bean = self.objects.create(**simple_item)
                bean.sort = bean.id
                bean.save()
        self.model.save_complex_field(complex_item, bean)
        bean.save()
        return bean

    def delete_one(self, _id):
        oid = self.model.object_id(_id)
        flag = False
        if oid:
            query_set = self.objects.filter(id=oid)
            self.model.remove_files(query_set)
            query_set.delete()
            flag = True
        return flag

    def find_one(self, _id):
        oid = self.model.object_id(_id)
        return self.objects.filter(id=oid).first() if oid else None



    def find(self, conditions=None, orders=None,size=0, page=1):
        query = OrmQuery(conditions, orders)
        query_set = self.objects.filter(query.includes).exclude(query.excludes).order_by(*query.orders)
        total = query_set.count()
        if size:
            paginator = Paginator(query_set, size)
            query_set = paginator.page(page).object_list
        return query_set, total

    def update(self, template, conditions):
        if template and len(template.keys()):
            oid, simple_item, complex_item = self.model.detach_item(template)
            query_set, total = self.find(conditions)
            query_set.update(**simple_item)
            return True
        return False

    def delete(self, conditions):
        query_set, total = self.find(conditions)
        # self.model.remove_files(query_set)
        query_set.delete()

    def transform(self, o, code=None):
        if isinstance(o, QuerySet):
            return self.model.to_dict(o, code)
        else:
            return o.full()

    def tree(self, root, conditions=None):
        all_set, _ = self.find()
        query = OrmQuery(conditions)
        if query.is_empty(conditions):
            return all_set
        values = all_set.values('id', 'pid')
        mapping = {item['id']: item['pid'] for item in values}
        results, _ = self.find(conditions)
        id_set = {root}
        for item in results:
            _id = item.id
            route = []
            while _id is not None:
                route.append(_id)
                _id = mapping.get(_id)
            if root in route:
                id_set.update(route)
        return all_set.filter(id__in=id_set).order_by('-sort')