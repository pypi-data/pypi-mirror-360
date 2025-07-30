import json
from genericpath import exists

from haplohub_cli import settings


class TokenStorage:
    def __init__(self, token_file: str):
        self.token_file = token_file

    @property
    def credentials_exist(self):
        return exists(self.token_file)

    def store_credentials(self, credentials: dict):
        with open(self.token_file, "w") as f:
            json.dump(credentials, f)

    def get_credentials(self):
        with open(self.token_file, "r") as f:
            return json.load(f)

    def get_access_token(self):
        return self.get_credentials()["access_token"]


token_storage = TokenStorage(settings.CREDENTIALS_FILE)
