import unittest, logging
import requests, json

def join(*args):
    return '/'.join([arg.strip('/') for arg in args])

class JsonServer:
    def __init__(self, host, *args, **kwargs):
        self._host = host
    
    def get(self, path, *args, **kwargs):
        url = join(self._host, path)
        response = requests.get(url, *args, **kwargs)
        response.raise_for_status()
        logging.info('GETting %s' % url)
        data = json.loads(response.content)
        logging.info('Recieved: %s' % repr(data))
        return data        
    
    def post(self, path, data, *args, **kwargs):
        url = join(self._host, path)
        logging.info('POSTing to %s' % url)
        response = requests.post(url, data = data, *args, **kwargs)        
        response.raise_for_status()
        logging.info('Recieved: %s' % repr(response))

class SignsServer(JsonServer):
    def __init__(self, client_id = None, 
                        secret_key = None,
                        host = 'http://localhost:8080/api/v1/',
                        *args, **kwargs):
        self._client_id = client_id
        self._secret_key = secret_key
        JsonServer.__init__(self, host, *args, **kwargs)
        
    def get_images(self):
        return self.get('/images')
        
    def upload(self, file):
        self.post('/upload', data=dict(test = 'hello there'), files={'image':file})

class SignsTestServer(JsonServer):
    def create_test_account(self):
        return self.get('/testing/create')
        

class ApiTest(unittest.TestCase):
    def test_base_api(self):
        test_server = SignsTestServer('http://localhost:8080')
        account = test_server.create_test_account()
        server = SignsServer(client_id = account['client_id'], 
                            secret_key = account['secret_key'])
        self.assertListEqual([], server.get_images())
        server.upload(open('api_tests/test2.jpg', 'rb'))
        self.assertEqual(1, len(server.get_images()))
        
        
        
        
