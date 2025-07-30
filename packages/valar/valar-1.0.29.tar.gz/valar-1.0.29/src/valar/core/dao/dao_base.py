from .dao_mon import MonDao
from .dao_orm import OrmDao
from ..dao_abstract import AbstractDao


class Dao(AbstractDao):

    def __init__(self, entity, db='orm'):
        self.entity = entity
        self.db = db
        self.dao: AbstractDao = OrmDao(entity) if db == 'orm' else MonDao(entity)

    def get_model(self):
        self.dao.get_model()

    def save_one(self, item):
        return self.dao.save_one(item)

    def delete_one(self, _id):
        return self.dao.delete_one(_id)

    def find_one(self, _id):
        return self.dao.find_one(_id)

    def find(self, conditions=None, orders=None, size=0, page=1):
        return self.dao.find(conditions, orders, size, page)

    def update(self, template, conditions):
        return self.dao.update(template, conditions)

    def delete(self, conditions):
        return self.dao.delete(conditions)

    def transform(self, o, code=None):
        return self.dao.transform(o)

    def tree(self, root, conditions=None):
        return self.dao.tree(root, conditions)



    # def values(self, props, conditions, orders=None):
    #     pass
    #
    # def group(self, props, conditions, orders=None):
    #     pass
    #
    # def count(self, props, conditions):
    #     pass

