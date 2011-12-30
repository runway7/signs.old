from google.appengine.ext.ndb import model, key
from google.appengine.api import files, images
import StringIO, imghdr

as_file = lambda data : StringIO.StringIO(data)
read_format = lambda file: imghdr.what(file)

def create_blobstore_file(data):
    file_name = files.blobstore.create()
    with files.open(file_name, 'a') as f: f.write(data)
    files.finalize(file_name)
    return files.blobstore.get_blob_key(file_name)

class Model(model.Model):
    updated_at = model.DateTimeProperty(auto_now = True)
    created_at = model.DateTimeProperty(auto_now_add = True)
    
    @classmethod
    def get_by_urlsafe(cls, urlsafe):
        return key.Key(urlsafe = urlsafe).get()
            

class Account(Model):
    secret_key = model.StringProperty(indexed = False)
    
    @classmethod
    def is_authentic(cls, client_id, secret_key):
        account = cls.get_by_id(int(client_id))
        return account and secret_key == account.secret_key
    
    @property
    def client_id(self):
        return str(self.key.id())
            
    def _pre_put_hook(self):
        if not self.secret_key: self._genereate_secret_key()

    def _genereate_secret_key(self):
        import hashlib, uuid
        sha = hashlib.sha1()
        sha.update(str(uuid.uuid4()))
        self.secret_key = sha.hexdigest()
     
        
class Image(Model):    
    blob_key = model.BlobKeyProperty()
    format = model.StringProperty()
    
    @classmethod
    def create(cls, data = None):
        format = read_format(as_file(data))    
        image_blob_key = create_blobstore_file(data)
        return Image(blob_key = image_blob_key, format = format).put()        

    def get_serving_url(self, size = None):
        return images.get_serving_url(self.blob_key, size = int(size))

        