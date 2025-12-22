from django.core.files.storage import Storage
from django.conf import settings
from oss2 import Auth, Bucket
import os

class AliyunOSSStorage(Storage):
    def __init__(self):
        self.auth = Auth(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET)
        self.bucket = Bucket(self.auth, settings.ENDPOINT, settings.BUCKET_NAME)
    
    def _open(self, name, mode='rb'):
        pass
    
    def _save(self, name, content):
        self.bucket.put_object(name, content)
        return name
    
    def url(self, name):
        return f'{settings.ENDPOINT.replace("http://", "https://")}/{name}'
    
    def exists(self, name):
        return self.bucket.object_exists(name)
