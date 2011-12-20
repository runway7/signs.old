from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from webapp2_extras import routes
import json, logging
from models import Image, Account

debug = True

def set_client_namespace(client_id):
    from google.appengine.api import namespace_manager
    namespace_manager.set_namespace(str(client_id))

def walled_request(func):
    def set_namespaces_first(*args, **kwargs):
        request = webapp.get_request()
        client_id = request.headers.get('SIGNS_CLIENT_ID')
        secret_key = request.headers.get('SIGNS_SECRET_KEY')
        if not Account.is_authentic(client_id, secret_key): raise Exception('Authentication Failed.')
        set_client_namespace(client_id)
        return func(*args, **kwargs)
    return set_namespaces_first

def make_response():
    return webapp.get_request().app.response_class()    
    
def send(data):
    response = make_response()
    response.out.write(json.dumps(data))
    return response

def send_blob(key, format = 'jpeg'):
    response = make_response()
    response.headers[blobstore.BLOB_KEY_HEADER] = str(key)
    response.headers['Content-Type'] = str('image/%s' % format)
    return response

@walled_request
def list_images(request):
    image_keys = [image.key.urlsafe() for image in Image.query().fetch()]
    return send(image_keys)

@walled_request        
def upload(request):
    image_key = Image.create(data = request.get('image'))
    return send(dict(key = image_key.urlsafe()))

def download(request, client_id, key):
    set_client_namespace(client_id)
    image = Image.get_by_urlsafe(key)
    return send_blob(image.blob_key, format = image.format)
    
def route_with_prefix(prefix, route_defs):
    return routes.PathPrefixRoute(prefix, 
        [webapp.Route(route[0], handler = route[1]) for route in route_defs]
    )

API_V1 = route_with_prefix('/api/v1',[
    ('/images', list_images),
    ('/upload', upload),
    ('/serve/<client_id>/<key>', download)
])

ROUTES = [
    API_V1
]

if debug:
    import testing_handlers
    ROUTES.insert(0, ('/testing/create', testing_handlers.CreateHandler))
    
application = webapp.WSGIApplication(ROUTES, debug = debug)


