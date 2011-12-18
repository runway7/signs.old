from google.appengine.ext.ndb import model
from google.appengine.api import files

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
    
    @classmethod
    def create(cls, data = None):
        image_file_name = files.blobstore.create()
        with files.open(image_file_name, 'a') as f:
            f.write(data)
        files.finalize(image_file_name)
        image_blob_key = files.blobstore.get_blob_key(image_file_name)
        return Image(blob_key = image_blob_key).put()