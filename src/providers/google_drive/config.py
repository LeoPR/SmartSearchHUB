from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, Tuple
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account

AuthMethod = Literal["oauth", "service-account"]

@dataclass
class Config:
    auth_method: AuthMethod = "oauth"
    credentials_file: Optional[str] = None  # client_secret.json OU service_account.json
    token_file: Optional[str] = None        # só p/ oauth
    scopes: Tuple[str, ...] = ("https://www.googleapis.com/auth/drive.readonly",)

    def build_credentials(self):
        if self.auth_method == "service-account":
            if not self.credentials_file:
                raise ValueError("credentials_file (service account) é obrigatório")
            return service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=list(self.scopes)
            )

        # oauth (desktop flow + token persistente)
        creds: Optional[Credentials] = None
        if self.token_file and os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_file:
                    raise ValueError("credentials_file (client_secret.json) é obrigatório")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                # Abre navegador na primeira vez
                creds = flow.run_local_server(port=0)

            if self.token_file:
                with open(self.token_file, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())

        return creds
