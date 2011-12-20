
def get_request():
    from google.appengine.ext import webapp
    return webapp.get_request()

def make_response():
    return get_request().app.response_class()    

def read_auth_headers():
    request = get_request()
    client_id = request.headers.get('SIGNS_CLIENT_ID')
    secret_key = request.headers.get('SIGNS_SECRET_KEY')
    return client_id, secret_key
    
def set_client_namespace():
    from google.appengine.api import namespace_manager
    request = get_request()
    client_id, secret_key = read_auth_headers()
    namespace_manager.set_namespace(str(client_id))

def authenticated(func):
    from models import Account
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
    import json
    response = make_response()
    response.out.write(json.dumps(data))
    return response

def send_image(blob_key, format = 'jpeg'):
    from google.appengine.ext import blobstore
    response = make_response()
    response.headers[blobstore.BLOB_KEY_HEADER] = str(blob_key)
    response.headers['Content-Type'] = str('image/%s' % format)
    return response
