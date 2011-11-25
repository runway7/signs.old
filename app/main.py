
from google.appengine.ext import webapp

debug = True

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

ROUTES = [('/', MainHandler)]

if debug:
    import testing_handlers
    ROUTES.insert(0, ('/testing/create', testing_handlers.CreateHandler))
    
application = webapp.WSGIApplication(ROUTES, debug = debug)


