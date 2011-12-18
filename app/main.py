from google.appengine.ext import webapp
from webapp2_extras import routes
import json, logging
from models import Image, Account

debug = True

def walled_request(func):
    from google.appengine.api import namespace_manager
    def set_namespaces_first(*args, **kwargs):
        request = webapp.get_request()
        client_id = request.headers.get('SIGNS_CLIENT_ID')
        secret_key = request.headers.get('SIGNS_SECRET_KEY')
        if not Account.is_authentic(client_id, secret_key): raise Exception('Authentication Failed.')
        namespace_manager.set_namespace(str(client_id))
        return func(*args, **kwargs)
    return set_namespaces_first
    
def send(data):
    response = webapp.get_request().app.response_class()
    response.out.write(json.dumps(data))
    return response

@walled_request
def list_images(request):
    image_keys = [image.key.urlsafe() for image in Image.query().fetch()]
    return send(image_keys)

@walled_request        
def upload(request):
    image_key = Image.create(data = request.get('image'))
    return send(dict(key = image_key.urlsafe()))

def route_with_prefix(prefix, route_defs):
    return routes.PathPrefixRoute(prefix, 
        [webapp.Route(route[0], handler = route[1]) for route in route_defs]
    )

API_V1 = route_with_prefix('/api/v1',[
    ('/images', list_images),
    ('/upload', upload)
])

ROUTES = [
    API_V1
]

if debug:
    import testing_handlers
    ROUTES.insert(0, ('/testing/create', testing_handlers.CreateHandler))
    
application = webapp.WSGIApplication(ROUTES, debug = debug)


