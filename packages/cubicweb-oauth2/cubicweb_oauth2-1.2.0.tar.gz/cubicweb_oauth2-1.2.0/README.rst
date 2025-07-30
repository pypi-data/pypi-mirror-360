Summary
-------

Oauth2/OpenID connect authentication client for cubicweb.

All configuration is done in `all-in-one.conf`. Defaults values should work
fine with Keycloak, for other provider refer to the documentation of the
content of the JWT token.

* `oauth2-enabled` should be set to `yes` once it is configured
* `oauth2-client-id` and `oauth2-client-secret` should be set (given by the
  provider).
* For OpenID connect providers `oauth2-server-url` can be set. For keycloak it
  is https://<server>/auth/realms/<realm>. The configuration is then obtained
  from the metadata url /.well-known/openid-configuration
* If you want to avoid a request to the metadata url, or if your provider
  doesn't implement OpenID, you should to configure `oauth2-authorization-url`,
  `oauth2-token-url` and `oauth2-jwk-path`.
* `oauth2-token-login` is used to map a field of the JWT token with CubicWeb
  login.
* On the provider side, the callback url should be configured to
  https://<cubicweb>/oauth2/callback

At this point you should be able to log in an existing user through the login
page using the "Log in with Oauth2" button.

If you want to automatically register new users, you must set
`oauth2-register-user` to `yes` and configure `oauth2-default-group`,
`oauth2-token-firstname`, `oauth2-token-surname` and `oauth2-token-email`.


If your instance only accepts users from the Oauth2 provider, you can set
`oauth2-auto-login` which skip the login page and start oauth2 authentication
directly.


If your instance require authenticated users from Oauth2 provider only, you
can set `oauth2-force-login` to `yes`, this will redirect all unauthenticated
requests to oauth2 login.

How to test this with keycloak
------------------------------

Using standard flow and confidential (client_id/client_secret) access.

test_full_login() might be a good entry point to understand the authentication
flow.

Here is how to test this with keycloak:

1. Create a new client using url http://:8080
2. Set Access Type to "confidential" with standard flow enabled
3. Get client_id & client_secret from the "Credentials" tab
4. Enable the oauth2 cube to your project
5. In all-in-one.conf set these parameters:
     oauth2-enabled=yes
     oauth2-server-url=https://keycloak/auth/realms/master
     oauth2-client-id=<client_id>
     oauth2-client-secret=<client_secret>
6. Start your instance, go to login page and click on "Log in with Oauth2"


