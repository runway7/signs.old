from google.appengine.ext import webapp
import json
from models import Account

class CreateHandler(webapp.RequestHandler):
    def get(self):
        account = Account()
        account.put()
        self.response.out.write(json.dumps(dict(client_id = account.client_id, secret_key = account.secret_key)))