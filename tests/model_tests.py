import unittest, logging
from models import Account
from google.appengine.ext.ndb.test_utils import NDBTest

class AccountTest(NDBTest):
    def test_secret_key_generation(self):
        account = Account()
        self.assertIsNone(account.secret_key)
        account.put()
        self.assertIsNotNone(account.secret_key)
        secret_key = account.secret_key
        account.put()
        self.assertEqual(secret_key, account.secret_key)
        