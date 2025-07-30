from pymongo.results import InsertOneResult
from pymongo.synchronous.cursor import Cursor

from .engine import DaoEngine
from .model_mon import MonModel
from .query_mon import MonQuery
from ..dao_abstract import AbstractDao


class MonDao(AbstractDao):
    def __init__(self, entity):
        self.entity = entity
        engine = DaoEngine().mon
        self.model:MonModel = engine.get_model(entity)
        self.objects = self.model.manager

    def get_model(self):
        return self.model

    def save_one(self, item):
        oid, item = self.model.detach_item(item)
        if oid:
            self.objects.update_one({'_id': oid}, {'$set': item})
        else:
            bean: InsertOneResult = self.objects.insert_one(item)
            oid = bean.inserted_id
            self.objects.update_one({'_id': oid}, {'$set': {'sort': str(oid)}})
        return self.objects.find_one({'_id': oid})

    def delete_one(self, _id):
        oid = self.model.object_id(_id)
        flag = False
        if oid:
            self.objects.delete_one({'_id': oid})
            flag = True
        return flag

    def find_one(self, _id):
        oid = self.model.object_id(_id)
        return self.objects.find_one({'_id': oid}) if oid else None

    def find(self, conditions=None, orders=None, size=0, page=1):
        query = MonQuery(conditions, orders)
        skip = (page - 1) * size
        total = self.objects.count_documents(query.finder)
        cursor = self.objects.find(query.finder, query.orders).skip(skip)
        if size:
            cursor = cursor.limit(size)
        return cursor, total

    def update(self, template, conditions):
        if template and len(template.keys()):
            oid, item = self.model.detach_item(template)
            query = MonQuery(conditions)
            self.objects.update_many(query.finder, {'$set': item})
            return True
        return False

    def delete(self, conditions):
        query = MonQuery(conditions)
        self.objects.delete_many(query.finder)

    def transform(self, o, code=None):
        if isinstance(o, Cursor):
            return [__to_item__(doc) for doc in o]
        else:
            return __to_item__(o)

    def tree(self, root, conditions=None):
        pass


def __to_item__(o):
    o['id'] = str(o['_id'])
    del o['_id']
    return o