import unittest, logging, os, mockito
from models import Account, Image
from google.appengine.ext.blobstore import BlobReader
from mockito import *

class ModelTest(unittest.TestCase):
    def setUp(self):
        app_id = 'TEST'
        from google.appengine.ext import testbed
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(app_id = app_id)
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub()
        
        from google.appengine.api.files import file_service_stub
        from google.appengine.api.blobstore import blobstore_stub, file_blob_storage                
        temp_dir = os.path.join(os.getcwd(), 'tmp')
        storage = file_blob_storage.FileBlobStorage(temp_dir, app_id)        
        self.testbed._register_stub('blobstore', blobstore_stub.BlobstoreServiceStub(storage))
        self.testbed._register_stub('file', file_service_stub.FileServiceStub(storage))

class AccountTest(ModelTest):
    def test_secret_key_generation(self):
        account = Account()
        self.assertIsNone(account.secret_key)
        account.put()
        self.assertIsNotNone(account.secret_key)
        secret_key = account.secret_key
        account.put()
        account.put()
        account.put()
        self.assertEqual(secret_key, account.secret_key)

class ImageTest(ModelTest):
    def test_blob_creation(self):
        import imghdr, StringIO
        data = 'some_image_data'
        when(StringIO).StringIO(data).thenReturn('data_file')
        when(imghdr).what('data_file').thenReturn('jpeg')
        
        image_key = Image.create(data = data)
        reader = BlobReader(image_key.get().blob_key)
        self.assertEqual(data, reader.read())
        image = image_key.get()
        self.assertEqual('jpeg', image.format)
