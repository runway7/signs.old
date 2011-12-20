from webapp2_extras import routes
from google.appengine.ext import webapp

import v1
versions = [v1]

def route_with_prefix(prefix, route_defs):
    return routes.PathPrefixRoute(prefix, 
        [webapp.Route(route[0], handler = route[1]) for route in route_defs]
    )

def get_all():    
    return [route_with_prefix('/api/%s' % v.VERSION, v.ROUTES) for v in versions]
