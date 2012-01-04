
from google.appengine.ext.ndb import model, key
from google.appengine.api import files, images

import StringIO
import imghdr
import string
import hashlib
import uuid

as_file = lambda data: StringIO.StringIO(data)
read_format = lambda file: imghdr.what(file)

def filter_none(seq):
    filtered = {}
    for key in seq.keys():
        if seq.get(key):
            filtered[key] = seq.get(key)
    return filtered

def extract(seq, keys):
    extracted = {}
    for key in keys:
        extracted[key] = seq.get(key)
    return extracted


def create_blobstore_file(data, mime_type='application/octet-stream'):
    file_name = files.blobstore.create(mime_type=mime_type)
    with files.open(file_name, 'a') as f: 
        f.write(data)
    files.finalize(file_name)
    return files.blobstore.get_blob_key(file_name)


class Model(model.Model):
    updated_at = model.DateTimeProperty(auto_now=True)
    created_at = model.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_by_urlsafe(cls, urlsafe):
        return key.Key(urlsafe=urlsafe).get()

    @classmethod
    def get_by_short_key(cls, short_key):
        return cls.get_by_id(int(short_key))

    @property
    def short_key(self):
        return self.key.id()


class Account(Model):
    secret_key = model.StringProperty(indexed=False)
    
    @classmethod
    def is_authentic(cls, client_id, secret_key):
        account = cls.get_by_id(int(client_id))
        return account and secret_key == account.secret_key
    
    @property
    def client_id(self):
        return str(self.key.id())
            
    def _pre_put_hook(self):
        if not self.secret_key: 
            self._genereate_secret_key()

    def _genereate_secret_key(self):       
        sha = hashlib.sha1()
        sha.update(str(uuid.uuid4()))
        self.secret_key = sha.hexdigest()
     
        
class Image(Model):    
    blob_key = model.BlobKeyProperty()
    format = model.StringProperty()
    
    @classmethod
    def create(cls, data=None, parent=None):
        format = 'image/%s' % read_format(as_file(data))    
        image_blob_key = create_blobstore_file(data, mime_type=format)
        image = Image(blob_key=image_blob_key, format=format) 
        image.put()
        return image
    
    @classmethod
    def thumbnail(cls, key, options):        
        image = Image.get_by_short_key(key)
        service_image = images.Image(blob_key=image.blob_key)
        service_image.resize(**options.resize_opts)
        thumbnail_data = service_image.execute_transforms(**options.exec_opts) 
        return Image.create(data=thumbnail_data)


class Options(object):    
    option_keys = ['width', 'height', 'quality', 'format']    

    def __init__(self, holder):
        self.opts = {}
        get = lambda key: holder.get(key)
        value = lambda key, modifier: None if not get(key) else modifier(get(key))
        pull_value = lambda key, modifier: self.opts.setdefault(key, value(key, modifier))
        [pull_value(key, int) for key in self.option_keys[0:3]]
        pull_value(self.option_keys[3], string.upper)        
    
    def load_if_present(self, args):                    
        return filter_none(extract(self.opts, args))
    
    @property
    def resize_opts(self):        
        return self.load_if_present(self.option_keys[0:2])        

    @property
    def exec_opts(self):
        exec_opts = self.load_if_present([self.option_keys[2]])
        if self.format in ['JPEG', 'PNG', 'WEBP']:
            exec_opts['output_encoding'] = getattr(images, self.format)
        return exec_opts
    
    @property
    def are_relevant(self):
        return not not self.load_if_present(self.option_keys)        
    
    @property
    def key(self):                
        options = self.load_if_present(self.option_keys)
        available_keys = sorted(options.keys())
        key_parts = [str(key[0]) + str(options.get(key)) for key in available_keys]        
        return '|'.join(key_parts)
    
    @property
    def format(self):
        return self.opts['format']




