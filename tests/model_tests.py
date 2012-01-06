import unittest
import logging
import os

from models import Account, Image, Options

from google.appengine.ext.ndb import key

from google.appengine.api import images
from google.appengine.ext.blobstore import BlobReader
from google.appengine.api.files import file_service_stub
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage

from mockito import *

read_blob = lambda (blob_key): BlobReader(blob_key).read()


class ModelTest(unittest.TestCase):
    def setUp(self):
        app_id = 'TEST'
        from google.appengine.ext import testbed
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(app_id=app_id)
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub()
        temp_dir = os.path.join(os.getcwd(), 'tmp')
        storage = file_blob_storage.FileBlobStorage(temp_dir, app_id)
        blob_stub = blobstore_stub.BlobstoreServiceStub(storage)
        self.testbed._register_stub('blobstore', blob_stub)
        self.testbed._register_stub('file', file_service_stub.FileServiceStub(storage))
    
    def tearDown(self):
        unstub()

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
        
        image = Image.create(data=data)
        reader = BlobReader(image.blob_key)
        self.assertEqual(data, reader.read())
        image = image.key.get()
        self.assertEqual('image/jpeg', image.format)

class ThumbnailTest(ModelTest):             
    def test_thumbnail_creation(self):        
        data = 'big_image_data'        
        compressed_data = 'cmprsd_data'
        image = Image.create(data=data)
        mock_service_image = mock()
        when(images).Image(blob_key=image.blob_key).thenReturn(mock_service_image)
        when(mock_service_image).execute_transforms().thenReturn(compressed_data)
        options = Options(dict(width=420))
        thumbnail = Image.thumbnail(image.short_key, options)
        verify(mock_service_image).resize(width=420)
        self.assertEqual(compressed_data, read_blob(thumbnail.blob_key))
        self.assertEqual(thumbnail.key, key.Key(Image, options.key, parent = image.key))
        original_blob_key = thumbnail.blob_key
        thumbnail = Image.thumbnail(image.short_key, options)
        self.assertEqual(original_blob_key, thumbnail.blob_key)

        

class OptionsTest(ModelTest):
    def test_resize(self):        
        opts = Options(dict(width=42, height='35'))                        
        self.assertEqual(dict(width=42, height=35), opts.resize_opts)
        opts = Options(dict(width=42))      
        self.assertEqual(dict(width=42), opts.resize_opts)  

    def test_exec_options(self):
        opts = Options(dict(height=34, format='png', quality=90))
        self.assertEqual(dict(height=34), opts.resize_opts)                  
        self.assertEquals(dict(output_encoding=images.PNG, quality=90), opts.exec_opts)

    def test_relevance(self):
        opts = Options(dict(lsdkj=3453, lkjdtlrk=45645))
        self.assertFalse(opts.are_relevant)
        opts = Options(dict(width=43))
        self.assertTrue(opts.are_relevant)
    
    def test_key(self):
        opts = Options(dict(width=42))
        self.assertEqual('w42', opts.key)
        opts = Options(dict(width=42, height=654))
        self.assertEqual('h654|w42', opts.key)
        opts = Options(dict(width=42, quality=56))
        self.assertEqual('q56|w42', opts.key)
        opts = Options(dict(width=42, quality=56, format='jpeg'))
        self.assertEqual('fJPEG|q56|w42', opts.key)
