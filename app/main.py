from google.appengine.ext import webapp
from google.appengine.ext.ndb import context
import routes

debug = True

ROUTES = routes.get_all()

if debug:
    import testing_handlers
    ROUTES.insert(0, ('/testing/create', testing_handlers.CreateHandler))

application = context.toplevel(
                    webapp.WSGIApplication(ROUTES, debug=debug).__call__
                )
