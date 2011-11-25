from google.appengine.ext.ndb import model

class Account(model.Model):
    secret_key = model.StringProperty(indexed = False)
    
    @property
    def client_id(self):
        return self.key.id()
            
    def _pre_put_hook(self):
        if not self.secret_key: self._genereate_secret_key()

    def _genereate_secret_key(self):
        import hashlib, random
        sha = hashlib.sha1()
        sha.update(str(random.random()))
        self.secret_key = sha.hexdigest()