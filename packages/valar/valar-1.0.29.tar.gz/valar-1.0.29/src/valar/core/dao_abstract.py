from abc import ABC, abstractmethod

class AbstractDao(ABC):


    @abstractmethod
    def get_model(self):
        pass

    @abstractmethod
    def save_one(self, item):
        pass

    @abstractmethod
    def delete_one(self, _id):
        pass

    @abstractmethod
    def find_one(self, _id):
        pass

    @abstractmethod
    def find(self, conditions=None, orders=None, size=0, page=1):
        pass

    @abstractmethod
    def update(self, template, conditions):
        pass

    @abstractmethod
    def delete(self, conditions):
        pass

    @abstractmethod
    def transform(self, o, code=None):
        pass

    @abstractmethod
    def tree(self, root, conditions=None):
        pass

    def search(self, includes=None, excludes=None, orders=None):
        conditions = [{
            "includes": includes or {},
            "excludes": excludes or {}
        }]
        query_set, _ = self.find(conditions, orders)
        return query_set

    # @abstractmethod
    # def values(self, props, conditions, orders=None):
    #     pass
    #
    # @abstractmethod
    # def group(self, props, conditions, orders=None):
    #     pass
    #
    # @abstractmethod
    # def count(self, props, conditions):
    #     pass



