# copyright 2020-2023 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import unittest
import urllib.parse
from unittest.mock import MagicMock

import responses
from authlib.jose import jwt
from cubicweb.devtools import BASE_URL
from cubicweb_web.devtools.testlib import PyramidWebCWTC

from cubicweb_oauth2.auth import Oauth2, Oauth2PKCE

HERE = os.path.dirname(__file__)


def create_token(payload):
    # use a RSA 256 keypair for tests, generated with:
    # ssh-keygen -t rsa -b 4096 -m PEM -f jwt.key
    # openssl rsa -in jwt.key -pubout -outform PEM -out jwt.pub
    with open(os.path.join(HERE, "jwt.key")) as f:
        privkey = f.read()
    return jwt.encode({"alg": "RS256"}, payload, privkey).decode()


class AuthenticationTC(PyramidWebCWTC):
    settings = {
        **PyramidWebCWTC.settings,
        "cubicweb.includes": ["cubicweb.pyramid.auth", "cubicweb.pyramid.session"],
    }

    @classmethod
    def init_config(cls, config):
        super().init_config(config)
        config.global_set_option("oauth2-enabled", True)
        config.global_set_option("oauth2-client-id", "id")
        config.global_set_option("oauth2-client-secret", "secret")
        config.global_set_option("oauth2-authorization-url", "https://provider/auth")
        config.global_set_option("oauth2-token-url", "https://provider/token")
        config.global_set_option("oauth2-jwk-path", os.path.join(HERE, "jwt.pub"))
        config.global_set_option("oauth2-provider-name", "Logilab")

    def test_login_page(self):
        resp = self.webapp.get("/login?postlogin_path=/schema", status=200)
        assert (
            f'<a href="{BASE_URL}oauth2/start?rd=%2Fschema">'
            f'<button class="validateButton" type="button" '
            f'value="Log in with Logilab">Log in with Logilab</button></a>'
        ).encode() in resp.body

    def test_login_page_auto_login(self):
        self.set_option("oauth2-auto-login", True)
        try:
            resp = self.webapp.get("/login?postlogin_path=/schema", status=302)
        finally:
            self.set_option("oauth2-auto-login", False)
        assert resp.location == f"{BASE_URL}oauth2/start?rd=%2Fschema"

    def test_force_login(self):
        self.set_option("oauth2-force-login", True)
        try:
            resp = self.webapp.get("/poulet", status=401)
        finally:
            self.set_option("oauth2-force-login", False)
        assert (
            resp.body
            == (
                f'<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; '
                f'url={BASE_URL}oauth2/start?rd={urllib.parse.quote(BASE_URL, safe="")}poulet" />'
                f"</head></html>"
            ).encode()
        )

    def test_force_login_signedrequest(self):
        # we should not block requests with signedrequest token authentication
        self.set_option("oauth2-force-login", True)
        try:
            self.webapp.get(
                "/poulet", headers={"Authorization": "Cubicweb foo"}, status=404
            )
        finally:
            self.set_option("oauth2-force-login", False)

    @responses.activate
    def test_full_login(self):
        resp = self.webapp.get("/oauth2/start?rd=/page", status=302)
        url = urllib.parse.urlparse(resp.location)
        assert url.scheme + "://" + url.netloc + url.path == "https://provider/auth"
        qs = urllib.parse.parse_qs(url.query)
        state = qs["state"][0]
        assert qs == {
            "response_type": ["code"],
            "client_id": ["id"],
            "redirect_uri": [f"{BASE_URL}oauth2/callback?rd=%2Fpage"],
            "scope": ["openid email profile"],
            "state": [state],
        }
        resp = self.webapp.get(
            "/oauth2/callback?rd=%2Fpage&state=invalid",
            status=400,
        )
        assert b"invalid state" in resp.body
        # this is a typical simplified keycloak token
        token = {
            "aud": "test",
            "email": "jdoe@logilab.fr",
            "family_name": "Doe",
            "given_name": "John",
            "name": "John Doe",
            "preferred_username": "jdoe",
            "sub": "6e349788-4b4a-4176-bc0a-81b1c48a675e",
        }
        responses.add(
            responses.POST,
            "https://provider/token",
            json={"id_token": create_token(token)},
            status=200,
        )
        resp = self.webapp.get(
            f"/oauth2/callback?rd=%2Fpage&state={state}&code=sesame",
            status=302,
        )
        assert resp.location == f"{BASE_URL}page"
        with self.admin_access.cnx() as cnx:
            user = cnx.find("CWUser", login="jdoe").one()
            assert (user.surname, user.firstname) == ("Doe", "John")
            assert [a.address for a in user.use_email] == ["jdoe@logilab.fr"]


def register_provide_response_ok(responses):
    responses.add(
        responses.GET,
        "https://provider/.well-known/openid-configuration",
        json={
            "authorization_endpoint": "https://provider/auth",
            "token_endpoint": "https://provider/token",
            "jwks_uri": "https://provider/certs",
        },
        status=200,
    )
    dummy_jwk = {"keys": [{"alg": "RS256", "kty": "RSA", "n": "dummy"}]}
    responses.add(
        responses.GET,
        "https://provider/certs",
        json=dummy_jwk,
        status=200,
    )
    return dummy_jwk


def parse_url(url):
    url_parser = urllib.parse.urlparse(url)
    return urllib.parse.parse_qs(url_parser.query)


class Oauth2TC(unittest.TestCase):
    def test_required_params(self):
        msg = (
            "You should either set `url` or all "
            "`authorization_url`, `token_url` and `jwk_path`"
        )
        with self.assertRaises(ValueError) as cm:
            Oauth2("id", "secret")
        assert str(cm.exception) == msg

        with self.assertRaises(ValueError) as cm:
            Oauth2("id", "secret", authorization_url="/auth")
        assert str(cm.exception) == msg

        # This should not raise
        Oauth2("id", "secret", server_url="/")
        Oauth2(
            "id",
            "secret",
            token_url="/token",
            authorization_url="/auth",
            jwk_path=os.path.join(HERE, "jwt.pub"),
        )

    @responses.activate
    def test_url_discovery(self):
        dummy_jwk = register_provide_response_ok(responses)
        client_id = "id"
        oauth2 = Oauth2(client_id, "secret", server_url="https://provider")
        assert oauth2.authorization_url == "https://provider/auth"
        assert oauth2.token_url == "https://provider/token"
        assert oauth2.jwk == dummy_jwk
        request = MagicMock()
        rd = "/42"
        authorization_url = oauth2.create_authorization_url(request, rd)
        params = parse_url(authorization_url)
        expected_params = {
            "response_type",
            "client_id",
            "redirect_uri",
            "scope",
            "state",
        }

        assert set(params.keys()) == expected_params
        assert params["client_id"] == [client_id]
        assert params["scope"] == ["openid email profile"]


class Oauth2PKCETC(unittest.TestCase):
    @responses.activate
    def test_create_authorization_url(self):
        register_provide_response_ok(responses)
        oauth2 = Oauth2PKCE("id", "secret", server_url="https://provider")
        request = MagicMock()
        rd = "/42"
        authorization_url = oauth2.create_authorization_url(request, rd)
        params = parse_url(authorization_url)
        expected_params = {
            "response_type",
            "client_id",
            "redirect_uri",
            "scope",
            "state",
            "code_challenge",
            "code_challenge_method",
        }
        assert set(params.keys()) == expected_params
        assert params["code_challenge_method"] == ["S256"]
        assert request.session.__setitem__.called
        state = request.session.__setitem__.call_args_list[0].args[1]
        assert params["state"][0] == state["state"]
