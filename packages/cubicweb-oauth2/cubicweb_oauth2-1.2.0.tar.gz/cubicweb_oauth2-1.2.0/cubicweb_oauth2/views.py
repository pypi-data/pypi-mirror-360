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

"""cubicweb-oauth2 views/forms/actions/components for web ui"""

from cubicweb import _, tags
from cubicweb_web.formwidgets import Button
from cubicweb_web.views.basetemplates import LogForm, LogFormView
from pyramid.httpexceptions import HTTPFound


class LoginWithOauth2Button(Button):
    def __init__(self, label, url):
        super().__init__(label=label)
        self._url = url

    def render(self, *args, **kwargs):
        button = super().render(*args, **kwargs)
        return tags.div(tags.a(button, href=self._url, escapecontent=False))


def start_login_url(cw):
    return cw._request.route_url(
        "oauth2-start",
        _query={"rd": cw._request.params.get("postlogin_path")},
    )


def login_button(cw):
    name = cw.vreg.config["oauth2-provider-name"]
    return LoginWithOauth2Button(
        _("Log in with %s") % (name,),
        start_login_url(cw),
    )


class Oauth2LogFormView(LogFormView):
    def call(self, *args, **kwargs):
        config = self._cw.vreg.config
        if config["oauth2-enabled"]:
            if config["oauth2-auto-login"]:
                raise HTTPFound(start_login_url(self._cw))

            cw = self._cw
            form = cw.vreg["forms"].select("logform", cw)
            if not any(isinstance(b, LoginWithOauth2Button) for b in form.form_buttons):
                form.form_buttons.append(login_button(self._cw))
        return super().call(*args, **kwargs)


class Oauth2LogForm(LogForm):
    @property
    def form_buttons(self):
        buttons = super().form_buttons
        if self._cw.vreg.config["oauth2-enabled"]:
            buttons.append(login_button(self._cw))
        return buttons


def registration_callback(vreg):
    vreg.register_and_replace(Oauth2LogFormView, LogFormView)
    if "bootstrap" not in vreg.config.cubes():
        vreg.register_and_replace(Oauth2LogForm, LogForm)
