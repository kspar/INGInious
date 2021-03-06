# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" linkedin auth plugin """

import web
import json
import os

from inginious.frontend.webapp.user_manager import AuthMethod
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix

authorization_base_url = 'https://www.linkedin.com/uas/oauth2/authorization?scope=r_basicprofile,r_emailaddress'
token_url = 'https://www.linkedin.com/uas/oauth2/accessToken'


class LinkedInAuthMethod(AuthMethod):
    """
    LinkedIn auth method
    """
    def get_auth_link(self, user_manager):
            linkedin = OAuth2Session(self._client_id, redirect_uri=web.ctx.home + self._callback_page)
            linkedin = linkedin_compliance_fix(linkedin)
            authorization_url, state = linkedin.authorization_url(authorization_base_url)
            user_manager.set_session_oauth_state(state)
            return authorization_url

    def callback(self, user_manager):
        linkedin = OAuth2Session(self._client_id, state=user_manager.session_oauth_state(), redirect_uri=web.ctx.home + self._callback_page)
        try:
            linkedin.fetch_token(token_url, client_secret=self._client_secret,
                                 authorization_response=web.ctx.home + web.ctx.fullpath)
            r = linkedin.get('https://api.linkedin.com/v1/people/~:(id,first-name,last-name,email-address)?format=json')
            profile = json.loads(r.content.decode('utf-8'))
            return str(profile["id"]), profile["firstName"] + " " + profile["lastName"], profile["emailAddress"]
        except:
            return None

    def get_id(self):
        return self._id

    def __init__(self, id, name, client_id, client_secret):
        self._id = id
        self._name = name
        self._client_id = client_id
        self._client_secret = client_secret
        self._callback_page = '/auth/' + self._id + '/callback'

    def get_name(self):
        return self._name

    def get_imlink(self):
        return '<i class="fa fa-linkedin-square" style="font-size:50px; color:#008CC9;"></i>'


def init(plugin_manager, course_factory, client, conf):

    if conf.get("debug", False):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    client_id = conf.get("client_id", "")
    client_secret = conf.get("client_secret", "")

    plugin_manager.register_auth_method(LinkedInAuthMethod(conf.get("id"), conf.get('name', 'LinkedIn Login'), client_id, client_secret))
