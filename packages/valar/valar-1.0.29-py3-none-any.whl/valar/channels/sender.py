import json
import time
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpRequest

from ..channels import VALAR_CHANNEL_GROUP


class ValarSocketSender:
    def __init__(self, request: HttpRequest, data=None):
        body = json.loads(request.body)
        auth = request.headers.get('AUTH')
        self.client = request.headers.get('CLIENT')
        self.uid = request.session.get('UID')
        self.handlerKey = body.get('handlerKey')
        self.channelKey = body.get('channelKey', 'default')
        self.data = data or body.get('data')
        self.send = get_channel_layer().group_send
        self.start_time = time.time()
        if auth and not self.uid:
            raise Exception('Unauthorized!')


    def __convert_body(self, emit, payload, status ,clients = None, users = None):
        return {
            'type': emit,
            'data': {
                'status': status,
                'handlerKey': self.handlerKey,
                'channelKey': self.channelKey,
                'payload': payload,
                'timestamp': datetime.now().timestamp()
            },
            'clients': clients or [],
            'users': users or [],
        }


    def to_users(self, payload,  users, status='proceed'):
        body = self.__convert_body(emit='user.emit', payload=payload, status=status, users=users)
        async_to_sync(self.send)(VALAR_CHANNEL_GROUP, body)

    def to_clients(self,payload, clients, status='proceed', wait=False):
        current_time = time.time()
        time_span = current_time - self.start_time
        if (wait and time_span > 1 and status == 'proceed') or not wait:
            body = self.__convert_body(emit='client.emit', payload=payload, status=status, clients=clients)
            async_to_sync(self.send)(VALAR_CHANNEL_GROUP, body)
            self.start_time = current_time

    def broadcast(self, payload, status):
        body = self.__convert_body(emit='broadcast.emit', payload=payload, status=status)
        async_to_sync(self.send)(VALAR_CHANNEL_GROUP, body)

    def register(self):
        body = self.__convert_body(emit='register.emit',  payload=None, status=None,clients=[self.client], users=[self.uid])
        async_to_sync(self.send)(VALAR_CHANNEL_GROUP, body)