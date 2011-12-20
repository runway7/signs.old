VERSION = 'v1'

from models import Image
from utils import *

@authenticated
@namespaced
def upload(request):
    image_key = Image.create(data = request.get('image'))
    return send(dict(key = image_key.urlsafe()))

@namespaced
def download(request, client_id, key):
    image = Image.get_by_urlsafe(key)
    return send_image(image.blob_key, format = image.format)

ROUTES = [
    ('/upload', upload),
    ('/serve/<client_id>/<key>', download)
]