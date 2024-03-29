"""
Signs Python Client. 
Author: Sudhir Jonathan
License: MIT

Does not currently work on Google App Engine because of it's dependency on the Requests egg. That should be fixed in future versions. 
"""

import requests
import json

class Url:
    def __init__(self, base):
        self.base = base
        self.params = {}
    
    @property
    def url(self):
        query = '&'.join(['%s=%s' % (key, value) for key,value in self.params.items()])             
        return '%s?%s' % (self.base, query) if query else self.base
    
    def add(self, **kwargs):
        for key, value in kwargs.items():
            if value: self.params[key] = value
        
        
class JsonServer(object):
    def __init__(self, host, *args, **kwargs):
        self._host = host
        
    @staticmethod    
    def url_join(*args):
        return '/'.join([arg.strip('/') for arg in args])
        
    def host_url(self, *args):
        return self.url_join(self._host, *args)
        
    def send(method):
        def make_call(self, path, *args, **kwargs):
            url = self.host_url(path)
            is_binary = kwargs.pop('binary', False)
            response = method(url, *args, **kwargs)
            response.raise_for_status()
            return json.loads(response.content) if not is_binary else response.content
        return make_call        
        
    get = send(requests.get)
    post = send(requests.post)    
    
    raw_get = staticmethod(requests.get)
    raw_post = staticmethod(requests.post)
    
    
class SignsServer(JsonServer):
    def __init__(self, client_id = None, 
                        secret_key = None,
                        host = 'http://localhost:8080/api/v1/',
                        *args, **kwargs):
        self._client_id = str(client_id)
        self._secret_key = str(secret_key)
        super(SignsServer, self).__init__(host, *args, **kwargs)

    def with_auth_headers(func):
        def set_auth_headers_and_call(self, *args, **kwargs):        
            headers = kwargs.setdefault('headers', {})
            headers['SIGNS_CLIENT_ID'] = self._client_id
            headers['SIGNS_SECRET_KEY'] = self._secret_key
            return func(self, *args, **kwargs)
        return set_auth_headers_and_call
    
    get = with_auth_headers(JsonServer.get)    
    post = with_auth_headers(JsonServer.post)

    def upload(self, image_data):
        return self.post('/upload/', {}, files={'image': image_data})
        
    def _generate_serving_url(self, image_key, **kwargs):
        url = Url('/serve/%s/%s' % (self._client_id, str(image_key)))             
        url.add(**kwargs)
        return url.url
    
    def download(self, image_key):
        return self.get(self._generate_serving_url(image_key), binary = True)
    
    def get_serving_url(self, image_key, width = None, height = None, quality = None, format = None):
        return self.host_url(self._generate_serving_url(image_key, 
                                                        width = width, 
                                                        height = height, 
                                                        quality = quality, 
                                                        format = format))

