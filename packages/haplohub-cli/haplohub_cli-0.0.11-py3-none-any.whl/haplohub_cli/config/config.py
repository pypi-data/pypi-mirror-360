from pydantic import BaseModel


class Config(BaseModel):
    api_url: str
    redirect_port: int
    auth0_domain: str
    auth0_client_id: str
    auth0_audience: str

    @property
    def auth0_redirect_uri(self):
        return f"http://localhost:{self.redirect_port}/"
