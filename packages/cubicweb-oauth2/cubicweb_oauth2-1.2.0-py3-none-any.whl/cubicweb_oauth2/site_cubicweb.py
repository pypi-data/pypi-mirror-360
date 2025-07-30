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

options = (
    (
        "oauth2-enabled",
        {
            "type": "yn",
            "default": False,
            "help": "Enable Oauth2 client",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-pkce-workflow",
        {
            "type": "yn",
            "default": False,
            "help": "Use PKCE authorization workflow",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-auto-login",
        {
            "type": "yn",
            "default": False,
            "help": "Skip the login page and try to login directly",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-force-login",
        {
            "type": "yn",
            "default": False,
            "help": "Force login on all unauthenticated requests",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-provider-name",
        {
            "type": "string",
            "default": "Oauth2",
            "help": "Name of the Oauth2 provider displayed in login page",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-server-url",
        {
            "type": "string",
            "default": "",
            "help": (
                "Base URL for Oauth2 server. Will look at "
                "/.well-known/openid-configuration for others urls."
            ),
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-authorization-url",
        {
            "type": "string",
            "default": "",
            "help": (
                "Oauth2 authorization url. "
                "Set this to avoid a request on oauth2-server-url at startup."
            ),
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-token-url",
        {
            "type": "string",
            "default": "",
            "help": (
                "Oauth2 token url "
                "Set this to avoid a request on oauth2-server-url at startup."
            ),
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-jwk-path",
        {
            "type": "string",
            "default": "",
            "help": (
                "Oauth2 server public key path. "
                "Set this to avoid a request to oauth2-server-url at startup."
            ),
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-client-id",
        {
            "type": "string",
            "default": "",
            "help": "Oauth2 client id",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-client-secret",
        {
            "type": "string",
            "default": "",
            "help": "Oauth2 client secret",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-register-user",
        {
            "type": "yn",
            "default": True,
            "help": "Automatically register if it does not exists yet",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-token-login",
        {
            "type": "string",
            "default": "preferred_username",
            "help": "Field on JWT token corresponding to CubicWeb user login",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-default-group",
        {
            "type": "string",
            "default": "guests",
            "help": "Default CWGroup when registering a new user",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-token-firstname",
        {
            "type": "string",
            "default": "given_name",
            "help": "Field on JWT token corresponding to CubicWeb user firstname",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-token-surname",
        {
            "type": "string",
            "default": "family_name",
            "help": "Field on JWT token corresponding to CubicWeb user surname",
            "group": "oauth2",
            "level": 5,
        },
    ),
    (
        "oauth2-token-email",
        {
            "type": "string",
            "default": "email",
            "help": "Field on JWT token corresponding to CubicWeb email address",
            "group": "oauth2",
            "level": 5,
        },
    ),
)
