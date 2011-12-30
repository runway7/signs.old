VERSION = 'v1'

from google.appengine.ext import deferred
from google.appengine.api import urlfetch

from models import Image
from utils import *

class ImageLoader(object):
    @classmethod
    def load(cls, key, size):
        loader = cls()
        loader.key = key
        loader.size = size
        return loader
    
    @staticmethod
    def set_image_format(response, format):
        response.headers['Content-Type'] = str('image/%s' % format)
    
    @cached_property
    def image(self):
        return Image.get_by_urlsafe(self.key)
    
    def send_original(self, response):
        response.headers[BLOB_KEY_HEADER] = str(self.image.blob_key)
        self.set_image_format(response, self.image.format)        
        return response
    
    def send_redirect(self, response):
        serving_url = str(self.image.get_serving_url(size = self.size))
        return redirect(serving_url, permanent = False)
        
    def determine_method(self):
        if self.size and int(self.size): return self.send_redirect 
        return self.send_original
    
    def write_to(self, response):
        method = self.determine_method()
        return method(response)

@authenticated
@namespaced
def upload(request):
    image_key = Image.create(data = request.get('image'))
    return send(dict(key = image_key.urlsafe()))

def download(request, client_id, key):
    set_namespace(client_id)
    size = request.get('size')
    loader = ImageLoader.load(key, size)
    return loader.write_to(make_response())

ROUTES = [
    ('/upload', upload),
    ('/serve/<client_id>/<key>', download)
]   