
class JsonServer(object):
    def __init__(self, host, *args, **kwargs):
        self._host = host
        
    @staticmethod    
    def url_join(*args):
        return '/'.join([arg.strip('/') for arg in args])
        
    def host_url(self, *args):
        return self.url_join(self._host, *args)
        
    def send(method):
        import json
        def make_call(self, path, *args, **kwargs):
            url = self.host_url(path)
            is_binary = kwargs.pop('binary', False)
            response = method(url, *args, **kwargs)
            response.raise_for_status()
            return json.loads(response.content) if not is_binary else response.content
        return make_call        
        
    import requests    
    get = send(requests.get)
    post = send(requests.post)    


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
    
    def download(self, image_key):
        url = '/serve/%s/%s' % (self._client_id, str(image_key))
        return self.get(url, binary = True)

