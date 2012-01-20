VERSION = 'v1'

from google.appengine.ext import deferred
from google.appengine.api import urlfetch

from models import Image, Options
from utils import *

class ImageLoader(object):
    @classmethod
    def load(cls, key, options):
        loader = cls()
        loader.key = key
        loader.options = options
        return loader
        
    @cached_property
    def image(self):
        return Image.get_by_short_key(self.key)
    
    @cached_property
    def thumbnail(self):
        return Image.thumbnail(self.key, self.options)
    
    def send_image(self, response, image):
        response.headers[BLOB_KEY_HEADER] = str(image.blob_key)
        response.headers['Content-Type'] = str(image.format)
        return response
                
    def write_to(self, response):
        image = self.image if not self.options.are_relevant else self.thumbnail
        return self.send_image(response, image)

@authenticated
@namespaced
def upload(request):
    image = Image.create(data = request.get('image'))
    return send(dict(image_key = image.short_key))

def download(request, client_id, key):
    set_namespace(client_id)    
    options = Options(request)
    loader = ImageLoader.load(key, options)
    return loader.write_to(make_response())

ROUTES = [
    ('/upload', upload),
    ('/serve/<client_id>/<key>', download)
]   