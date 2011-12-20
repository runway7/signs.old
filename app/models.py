from google.appengine.ext.ndb import model, key
from google.appengine.api import files

import StringIO, logging
as_file = lambda d : StringIO.StringIO(d)

def create_blobstore_file(data):
    file_name = files.blobstore.create()
    with files.open(file_name, 'a') as f: f.write(data)
    files.finalize(file_name)
    return files.blobstore.get_blob_key(file_name)


class Account(model.Model):
    secret_key = model.StringProperty(indexed = False)
    
    @classmethod
    def is_authentic(cls, client_id, secret_key):
        account = cls.get_by_id(int(client_id))
        return account and secret_key == account.secret_key
    
    @property
    def client_id(self):
        return self.key.id()
            
    def _pre_put_hook(self):
        if not self.secret_key: self._genereate_secret_key()

    def _genereate_secret_key(self):
        import hashlib, random
        sha = hashlib.sha1()
        sha.update(str(random.random()))
        self.secret_key = sha.hexdigest()
     
        
class Image(model.Model):    
    blob_key = model.BlobKeyProperty()
    format = model.StringProperty()
    
    @classmethod
    def get_by_urlsafe(cls, image_key):
        return key.Key(urlsafe = image_key).get()

    @classmethod
    def create(cls, data = None):
        import imghdr
        format = imghdr.what(as_file(data))    
        image_blob_key = create_blobstore_file(data)
        return Image(blob_key = image_blob_key, format = format).put()
        
        