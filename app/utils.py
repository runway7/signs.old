from google.appengine.ext import webapp, blobstore
from google.appengine.api import namespace_manager

import json

from models import Account

BLOB_KEY_HEADER = blobstore.BLOB_KEY_HEADER
redirect = webapp.redirect

def get_request():
    return webapp.get_request()

def make_response():
    return get_request().app.response_class()    

def read_auth_headers():
    request = get_request()
    client_id = request.headers.get('SIGNS_CLIENT_ID')
    secret_key = request.headers.get('SIGNS_SECRET_KEY')
    return client_id, secret_key
    
def set_namespace(ns):
    namespace_manager.set_namespace(str(ns))
    
def set_client_namespace():
    request = get_request()
    client_id, secret_key = read_auth_headers()
    set_namespace(client_id)

def authenticated(func):
    def authenticate_and_call(*args, **kwargs):
        if not Account.is_authentic(*read_auth_headers()): raise Exception('Authentication Failed.')
        return func(*args, **kwargs)
    return authenticate_and_call

def namespaced(func):
    def set_namespace_and_call(*args, **kwargs):
        set_client_namespace()
        return func(*args, **kwargs)
    return set_namespace_and_call    
    
def send(data):
    response = make_response()
    response.out.write(json.dumps(data))
    return response
