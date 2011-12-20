from google.appengine.ext import webapp
import routes

debug = True

ROUTES = routes.get_all()

if debug:
    import testing_handlers
    ROUTES.insert(0, ('/testing/create', testing_handlers.CreateHandler))
    
application = webapp.WSGIApplication(ROUTES, debug = debug)


