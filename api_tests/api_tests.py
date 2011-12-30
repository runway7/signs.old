import unittest, logging, sys, time
from api import *

size = sys.getsizeof

class SignsTestServer(JsonServer):
    def create_test_account(self):
        return self.get('/testing/create/')        
        
class ApiTest(unittest.TestCase):
    def setUp(self):
        self.test_server = SignsTestServer('http://localhost:8080/')
        self.account = self.test_server.create_test_account()
        self.server = SignsServer(
                            client_id = self.account['client_id'], 
                            secret_key = self.account['secret_key']
                            )
            
    def test_upload_and_serving(self):        
        image_file = lambda: open('api_tests/test2.jpg', 'rb')
        image_data = self.server.upload(image_file())                
        image = self.server.download(image_data['key'])
        self.assertEqual(len(image_file().read()), len(image))
        
        serving_url = self.server.get_serving_url(image_data['key'])        
        self.assertEqual(len(image_file().read()), len(self.server.raw_get(serving_url).content))
    
    def test_redirect_on_size(self):
        image_file = lambda: open('api_tests/test1.jpg', 'rb')
        image_data = self.server.upload(image_file())                
        serving_url = self.server.get_serving_url(image_data['key'], size = 420)                
        response = self.server.raw_get(serving_url, allow_redirects = False)        
        self.assertEqual(302, response.status_code)
        self.assertTrue(response.headers['location'].endswith('s420'))
        
        
        