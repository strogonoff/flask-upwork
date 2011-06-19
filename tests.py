"""
Flask-oDesk
-----------
Adds oDesk API support to Flask.

flask-odesk version 0.4.1
(C) 2011 oDesk
"""

from flask import Flask, url_for
from flaskext.odesk import odesk
from mock import patch
import unittest
import odesk as python_odesk
import oauth2 as oauth

class ODeskTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'blahblah'
        app.config['ODESK_KEY'] = 'some_key'
        app.config['ODESK_SECRET'] = 'some_secret'
        app.debug = True
        app.register_module(odesk, url_prefix='/odesk')
        ctx = app.test_request_context()
        ctx.push()
        self.app = app
        self.tc = self.app.test_client()


    def test_url_for(self):
        assert url_for('odesk.login') == '/odesk/login'
        assert url_for('odesk.complete') == '/odesk/complete'
        assert url_for('odesk.logout') == '/odesk/logout'


    def test_login_required(self):

        def patched_oauth_client_request(*args, **kwargs):
            return {'status': '200'},\
                'oauth_callback_confirmed=1&oauth_token=token&oauth_token_secret=secret'

        def patched_get_authorize_url(*args, **kwargs):
            return url_for('odesk.complete', next='/admin',\
                oauth_verifier='verifier')

        def patched_get_request_token(*args, **kwargs):
            return 'request_token', 'request_token_secret'

        def patched_get_get_access_token(*args, **kwargs):
            return 'access_token', 'access_token_secret'

        @self.app.route('/admin')
        @patch('odesk.oauth.OAuth.get_authorize_url', patched_get_authorize_url)
        @patch('odesk.oauth.OAuth.get_request_token', patched_get_request_token)
        @patch('odesk.oauth.OAuth.get_access_token', patched_get_get_access_token)
        @odesk.login_required
        def admin():
            self.odesk_is_authorized = odesk.is_authorized()
            self.odesk_access_token = odesk.get_access_token()
            odesk.logout()
            self.odesk_is_not_authorized = odesk.is_authorized()
            return "Welcome, oDesk user!"

        oauth.Client.request = patched_oauth_client_request
        response = self.tc.get('/admin', follow_redirects=True)
        assert "Welcome" in response.data, response.data
        assert self.odesk_is_authorized == True
        assert self.odesk_access_token == ('token', 'secret')
        assert self.odesk_is_not_authorized == False


if __name__ == '__main__':
    unittest.main()
