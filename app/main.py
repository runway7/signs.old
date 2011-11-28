
from google.appengine.ext import webapp
from webapp2_extras import routes
import json, logging

debug = True

class JsonHandler(webapp.RequestHandler):
    def send(self, data):
        self.response.out.write(json.dumps(data))

class ImagesHandler(JsonHandler):
    def get(self):
        self.send([])

class UploadHandler(JsonHandler):
    def post(self):
        logging.info(len(self.request.get('image')))
        logging.info(len(self.request.get('test')))
        self.send([])

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


def route_with_prefix(prefix, route_defs):
    return routes.PathPrefixRoute(prefix, 
        [webapp.Route(route[0], route[1]) for route in route_defs]
    )

API_V1 = route_with_prefix('/api/v1',[
    ('/images', ImagesHandler),
    ('/upload', UploadHandler)
])

ROUTES = [
    API_V1,
    ('/', MainHandler)
]

if debug:
    import testing_handlers
    ROUTES.insert(0, ('/testing/create', testing_handlers.CreateHandler))
    
application = webapp.WSGIApplication(ROUTES, debug = debug)


