import json

class Config:
    def __init__(self, file):
        with open(file, "r") as f:
            cfg = json.load(f)
        self.auth_method = cfg.get("auth_method")
        self.credentials_file = cfg.get("credentials_file")
        self.token_file = cfg.get("token_file")

    def build_credentials(self):
        # Importe e delegue para o método original, se necessário
        # ou implemente a lógica mínima aqui
        from src.providers.google_drive.config import Config as GoogleConfig
        google_cfg = GoogleConfig(
            auth_method=self.auth_method,
            credentials_file=self.credentials_file,
            token_file=self.token_file,
        )
        return google_cfg.build_credentials()