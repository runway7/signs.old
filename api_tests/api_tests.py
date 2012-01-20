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
        image = self.server.download(image_data['image_key'])
        self.assertEqual(len(image_file().read()), len(image))
        
        serving_url = self.server.get_serving_url(image_data['image_key'])        
        self.assertEqual(len(image_file().read()), len(self.server.raw_get(serving_url).content))
    
    def test_thumbnail(self):
        image_file = lambda: open('api_tests/test1.jpg', 'rb')
        image_data = self.server.upload(image_file())                
        serving_url = self.server.get_serving_url(image_data['image_key'], width = 42)
        response = self.server.raw_get(serving_url)        
        self.assertEqual(200, response.status_code)
        self.assertTrue(size(response.content) < size(image_file().read()))        

    def test_format(self):
        image_file = lambda: open('api_tests/test1.jpg', 'rb')
        image_data = self.server.upload(image_file())                
        serving_url = self.server.get_serving_url(image_data['image_key'], format = 'png', width = 55)
        response = self.server.raw_get(serving_url)        
        self.assertEqual('image/png', response.headers['Content-Type'])

        
        
class UrlBuilderTest(unittest.TestCase):
    def test_basic(self):
        self.assertEquals('http://www.google.com', Url('http://www.google.com').url)

    def test_arguments(self):
        url = Url('http://www.google.com')
        url.add(size = 45)
        self.assertEquals('http://www.google.com?size=45', url.url)
        url.add(size = 45, q = 'ab')
        self.assertEquals('http://www.google.com?q=ab&size=45', url.url)
        url.add(size = 45, q = 'ab', k = None)
        self.assertEquals('http://www.google.com?q=ab&size=45', url.url)

        