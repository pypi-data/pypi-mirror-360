import webbrowser
import hvac
import urllib.parse


OIDC_CALLBACK_PORT = 8250
OIDC_REDIRECT_URI = f"http://localhost:{OIDC_CALLBACK_PORT}/oidc/callback"
ROLE = None  # Use None (not empty string) for the default Role
SELF_CLOSING_PAGE = """
<!doctype html>
<html>
<head>
<script>
// Closes IE, Edge, Chrome, Brave
window.onload = function load() {
  window.open('', '_self', '');
  window.close();
};
</script>
</head>
<body>
  <p>Authentication successful, you can close the browser now.</p>
  <script>
    // Needed for Firefox security
    setTimeout(function() {
          window.close()
    }, 5000);
  </script>
</body>
</html>
"""


def vault_login(url=None, role_id=None, secret_id=None):
    client = hvac.Client(url=url, verify=False)

    if role_id and secret_id:
        client.auth.approle.login(
            role_id=role_id,
            secret_id=secret_id,
        )

    else:
        auth_url_response = client.auth.oidc.oidc_authorization_url_request(
            role=ROLE,
            redirect_uri=OIDC_REDIRECT_URI,
        )
        auth_url = auth_url_response["data"]["auth_url"]
        if auth_url == "":
            return None

        params = urllib.parse.parse_qs(auth_url.split("?")[1])
        auth_url_nonce = params["nonce"][0]
        auth_url_state = params["state"][0]

        webbrowser.open(auth_url, autoraise=False)
        token = login_oidc_get_token()

        auth_result = client.auth.oidc.oidc_callback(
            code=token,
            path="oidc",
            nonce=auth_url_nonce,
            state=auth_url_state,
        )
        new_token = auth_result["auth"]["client_token"]

        # If you want to continue using the client here
        # update the client to use the new token
        client.token = new_token
    return client


# handles the callback
def login_oidc_get_token():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class HttpServ(HTTPServer):
        def __init__(self, *args, **kwargs):
            HTTPServer.__init__(self, *args, **kwargs)
            self.token = None

    class AuthHandler(BaseHTTPRequestHandler):
        token = ""

        def do_GET(self):
            params = urllib.parse.parse_qs(self.path.split("?")[1])
            self.server.token = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(SELF_CLOSING_PAGE))

    server_address = ("", OIDC_CALLBACK_PORT)
    httpd = HttpServ(server_address, AuthHandler)
    httpd.handle_request()
    return httpd.token
