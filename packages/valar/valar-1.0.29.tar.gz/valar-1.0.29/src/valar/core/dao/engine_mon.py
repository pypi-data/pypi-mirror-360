import pymongo
from django.conf import settings

from .model_mon import MonModel


class MonEngine:

    def __init__(self):
        uri = f'mongodb://localhost:27017/'
        mongo = settings.MONGO
        if mongo:
            param = ['host', 'port', 'username', 'password']
            host, port, username, password = [mongo.get(p) for p in param]
            uri = f'mongodb://{username}:{password}@{host}:{port}/'

        client = pymongo.MongoClient(uri, **{
            'maxPoolSize': 10,
            'minPoolSize': 0,
            'maxIdleTimeMS': 10000,
            'connectTimeoutMS': 10000,
            'socketTimeoutMS': 10000,
            'serverSelectionTimeoutMS': 10000,
        })
        database =  client[settings.BASE_APP]
        self.uri = uri
        self.client = client
        self.database = database

    def get_mapping(self):
        return  {col['name']: self.database[col['name']] for col in self.database.list_collections()}

    def get_model(self,entity)->MonModel:
        return MonModel(self.database, entity)