import base64
import hashlib
import os

from requests import Session

from haplohub_cli.auth.token_storage import TokenStorage, token_storage
from haplohub_cli.config.config_manager import config_manager


class AuthRequest:
    def __init__(
        self,
        client: "Auth0Client",
        scopes: list[str],
    ):
        self.client = client
        self.scopes = scopes
        self.code_verifier, self.code_challenge = self.generate_code_verifier()

    @property
    def auth_url(self):
        return (
            f"https://{self.client.domain}/authorize"
            f"?client_id={self.client.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.client.redirect_uri}"
            f"&scope={' '.join(self.scopes)}"
            f"&code_challenge={self.code_challenge}"
            f"&code_challenge_method=S256"
            f"&audience={self.client.audience}"
        )

    def generate_code_verifier(self):
        verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
        challenge = hashlib.sha256(verifier.encode("utf-8")).digest()
        challenge = base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
        return verifier, challenge

    def exchange_code(self, code: str):
        return self.client.exchange_code(code, self.code_verifier)


class Auth0Client:
    http = Session()

    def __init__(self, token_storage: TokenStorage, domain: str, client_id: str, audience: str, redirect_uri: str):
        self.token_storage = token_storage
        self.domain = domain
        self.client_id = client_id
        self.audience = audience
        self.redirect_uri = redirect_uri

    def init_auth_request(self, scopes: list[str] = ("openid", "profile", "email")):
        return AuthRequest(client=self, scopes=scopes)

    def exchange_refresh_token(self, refresh_token: str):
        return self._make_request(
            "oauth/token",
            "POST",
            json={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": refresh_token,
                "audience": self.audience,
            },
        )

    def exchange_code(self, code: str, code_verifier: str):
        return self._make_request(
            "oauth/token",
            "POST",
            json={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "code": code,
                "redirect_uri": self.redirect_uri,
                "code_verifier": code_verifier,
                "audience": self.audience,
            },
        )

    def get_user_info(self):
        return self._make_request("userinfo", "GET")

    def _make_request(self, path: str, method: str, data: dict = None, json: dict = None):
        url = f"https://{self.domain}/{path}"

        headers = None
        if self.token_storage.credentials_exist:
            headers = {"Authorization": f"Bearer {self.token_storage.get_access_token()}"}

        response = self.http.request(method, url, headers=headers, data=data, json=json)
        response.raise_for_status()
        return response.json()


auth0_client = Auth0Client(
    token_storage=token_storage,
    domain=config_manager.config.auth0_domain,
    client_id=config_manager.config.auth0_client_id,
    audience=config_manager.config.auth0_audience,
    redirect_uri=config_manager.config.auth0_redirect_uri,
)
