valar for morghulis
# 1. install
```shell
pip install valar
```


# 1. settings
```python

from pathlib import Path

""" Compulsory settings """
DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_APP = str(BASE_DIR.name)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECRET_KEY = 'django-insecure-of@tfouoq^_f$l!yki#m=6j7)@&kjri$1_$!mca-=%7=+@f@5^'
""" Minimized compulsory settings """

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS = [
    'django.contrib.sessions',
    "corsheaders",
    'channels',
    'valar.data',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = "%s.urls" % BASE_APP
ASGI_APPLICATION = "%s.asgi.application" % BASE_APP

MONGO = {
    'host': '<IP>',
    'port': '<PORT>',
    "username": "<USERNAME>",
    "password": '<PASSWORD>'
}

MINIO = {
    'endpoint': '<IP>:<PORT>',
    'access_key': '<USERNAME>',
    "secret_key": "<PASSWORD>",
    'secure': False
}

""" Optional settings """
# ALLOWED_HOSTS = ['*']
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'Asia/Shanghai'
# USE_I18N = True
# USE_TZ = False
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_COOKIE_AGE = 60 * 60
# FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100
# DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100

```
# 2. asgi
```python
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from valar.channels.consumer import ValarConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter([
        re_path(r'(?P<client>\w+)/$', ValarConsumer.as_asgi()),
    ])
})

```

# 3. migrate
```shell
python manage.py makemigrations
python manage.py migrate
```


# 4. root urls
```python
from django.urls import path, include

urlpatterns = [
    path('data/', include('valar.data.urls')),
]

channel_mapping = {
    # 'test': test_handler
}
```

# 5. channel_handler
```python

import time

from valar.channels.sender import ValarSocketSender
from valar.core.counter import Counter

def test_handler(sender: ValarSocketSender):
    data = sender.data
    length = data.get('length',50)
    counter = Counter(length)
    for i in range(length):
        time.sleep(0.1)
        sender.to_clients(counter.tick() ,sender.client, wait=True)
```