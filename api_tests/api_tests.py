import unittest, logging
from api import *

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
        self.assertEqual(image_file().read(), image)
        
        