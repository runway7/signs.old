import unittest, logging
import requests, json

def join(*args):
    return '/'.join([arg.lstrip('/').rstrip('/') for arg in args])

class JsonServer:
    def __init__(self, host, *args, **kwargs):
        self._host = host
    
    def get(self, path):
        url = join(self._host, path)
        response = requests.get(url)
        logging.info('Hitting %s' % url)
        data = json.loads(response.content)
        logging.info('Recieved: %s' % repr(data))
        return data        
    
    def post(self, path, data):
        pass        


class SignsTestServer(JsonServer):
    def create_test_account(self):
        return self.get('/testing/create')
        

class ApiTest(unittest.TestCase):
    def test_base_api(self):
        server = SignsTestServer('http://localhost:8080')
        account = server.create_test_account()
        
        
