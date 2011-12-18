import unittest, logging

class JsonServer(object):
    import requests

    def __init__(self, host, *args, **kwargs):
        self._host = host
        
    @staticmethod    
    def url_join(*args):
        return '/'.join([arg.strip('/') for arg in args])
        
    def _send(method):
        import json
        def make_call(self, path, *args, **kwargs):
            url = self.url_join(self._host, path)
            response = method(url, *args, **kwargs)
            return response.raise_for_status() or json.loads(response.content)
        return make_call        
    
    get = _send(requests.get)
    post = _send(requests.post)    


class SignsServer(JsonServer):
    def __init__(self, client_id = None, 
                        secret_key = None,
                        host = 'http://localhost:8080/api/v1/',
                        *args, **kwargs):
        self._client_id = str(client_id)
        self._secret_key = str(secret_key)
        super(self.__class__, self).__init__(host, *args, **kwargs)

    def _add_auth_headers(func):
        def set_auth_headers_first(self, *args, **kwargs):        
            headers = kwargs.setdefault('headers', {})
            headers['SIGNS_CLIENT_ID'] = self._client_id
            headers['SIGNS_SECRET_KEY'] = self._secret_key
            return func(self, *args, **kwargs)
        return set_auth_headers_first
    
    get = _add_auth_headers(JsonServer.get)    
    post = _add_auth_headers(JsonServer.post)

    def get_images(self):
        return self.get('/images/')
        
    def upload(self, image_data):
        self.post('/upload/', {}, files={'image': image_data})


class SignsTestServer(JsonServer):
    def create_test_account(self):
        return self.get('/testing/create/')
        
        
class ApiTest(unittest.TestCase):
    def test_base_api(self):
        test_server = SignsTestServer('http://localhost:8080/')
        account = test_server.create_test_account()
        server = SignsServer(client_id = account['client_id'], 
                            secret_key = account['secret_key'])
        self.assertListEqual([], server.get_images())
        server.upload(open('api_tests/test2.jpg', 'rb'))
        self.assertEqual(1, len(server.get_images()))
    