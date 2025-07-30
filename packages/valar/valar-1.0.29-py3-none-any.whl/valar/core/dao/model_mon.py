from bson import ObjectId
from bson.errors import InvalidId
from pymongo.synchronous.collection import Collection


class MonModel:

    def __init__(self, database, entity):
        self.entity = entity
        self.name = entity.replace('.', '_')
        self.manager: Collection = database[self.name]

    @staticmethod
    def object_id(_id):
        try:
            return ObjectId(_id)
        except(InvalidId, TypeError):
            return None

    def detach_item(self, item):
        _id = item.get('id')
        if _id:
            del item['id']
        return self.object_id(_id), item