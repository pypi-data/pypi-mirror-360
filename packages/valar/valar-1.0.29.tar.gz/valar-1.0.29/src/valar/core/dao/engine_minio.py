
import json
from io import BytesIO

from django.conf import settings
from minio import Minio
from urllib3 import  BaseHTTPResponse

from ..singleton_meta import SingletonMeta

class MinioEngine(metaclass=SingletonMeta):

    def __int__(self):
        self.client = Minio(**settings.MINIO_SETTINGS)

    def __load_bucket__(self, bucket_name):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
            policy = __generate_policy__(bucket_name)
            self.client.set_bucket_policy(bucket_name, policy)

    @staticmethod
    def get_object_name(_id, prop, file_name):
        return f"{_id}-{prop}-{file_name}"

    @staticmethod
    def get_bucket_name(entity):
        name = f'{settings.BASE_DIR.name}.{entity}'
        return name.replace('_', '-').lower()

    def upload(self, bucket_name, object_name, _bytes):
        self.__load_bucket__(bucket_name)
        file_data = BytesIO(_bytes)
        file_size = len(_bytes)  # file.siz
        self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=file_data,
            length=file_size
        )
        return f'{bucket_name}/{object_name}'

    def remove_path(self, path):
        if path:
            bucket_name, object_name = path.split('/')
            self.remove(bucket_name, object_name)

    def remove(self, bucket_name, object_name):
        self.client.remove_object(
            bucket_name=bucket_name,
            object_name=object_name
        )

    def read(self, bucket_name, object_name) -> BytesIO:
        ret: BaseHTTPResponse = self.client.get_object(bucket_name=bucket_name, object_name=object_name)
        return BytesIO(ret.read())


def __generate_policy__(bucket_name):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetBucketLocation",
                "Resource": f"arn:aws:s3:::{bucket_name}"
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:ListBucket",
                "Resource": f"arn:aws:s3:::{bucket_name}"
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]})