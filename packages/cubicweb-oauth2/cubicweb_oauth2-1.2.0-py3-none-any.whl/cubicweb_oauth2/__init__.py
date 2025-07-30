"""cubicweb-oauth2 application package

Oauth2/OpenID authentication for cubicweb
"""


def includeme(config):
    cwconfig = config.registry["cubicweb.config"]
    if not cwconfig["oauth2-enabled"]:
        return
    config.include(".auth")
