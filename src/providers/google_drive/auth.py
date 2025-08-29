"""
GDriveAuthManager

Centraliza a lógica de obtenção de credenciais para Google Drive.
- Se a Config passada tiver build_credentials(), delega para ela.
- Caso contrário, aplica um fluxo compatível: suporta service-account e oauth (desktop flow).
- Usa InstalledAppFlow.run_local_server para abrir o navegador padrão do sistema.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any

@dataclass
class GDriveAuthManager:
    config: Any  # idealmente src.providers.google_drive.config.Config

    def get_credentials(self):
        """
        Retorna credenciais válidas para Google Drive.

        Fluxo:
        - Se config tem método build_credentials(), delega para ele.
        - Senão:
          - Se auth_method == "service-account": carrega service account file.
          - Senão (oauth): tenta token_file -> refresh -> run_local_server -> salva token_file.

        Lança ValueError/RuntimeError em problemas de configuração ou falta de dependências.
        """
        # Preferir delegar se Config já implementa isso.
        if hasattr(self.config, "build_credentials"):
            return self.config.build_credentials()

        # Compat fallback (importa dependências só aqui)
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.oauth2 import service_account
        except Exception as e:
            raise RuntimeError(
                "Dependências Google ausentes. Instale: "
                "pip install google-api-python-client google-auth google-auth-oauthlib"
            ) from e

        method = getattr(self.config, "auth_method", "oauth")
        scopes = getattr(self.config, "scopes", ("https://www.googleapis.com/auth/drive.readonly",))

        if method in ("service-account", "service_account"):
            credentials_file = getattr(self.config, "credentials_file", None)
            if not credentials_file:
                raise ValueError("Service account selecionada mas credentials_file não foi fornecido.")
            return service_account.Credentials.from_service_account_file(credentials_file, scopes=list(scopes))

        # OAuth desktop flow
        token_file = getattr(self.config, "token_file", None)
        credentials_file = getattr(self.config, "credentials_file", None)

        creds: Optional[Credentials] = None
        if token_file:
            token_path = Path(token_file).expanduser()
            if token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(str(token_path), scopes)
                except Exception:
                    creds = None

        # Se existe e válido, devolve
        if creds and creds.valid:
            return creds

        # Refresh se possível
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if token_file:
                token_path = Path(token_file).expanduser()
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with token_path.open("w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            return creds

        # Sem token válido -> inicia fluxo interativo no navegador padrão (run_local_server)
        if not credentials_file:
            raise ValueError("OAuth requer credentials_file (client_secret.json) quando não há token válido.")

        flow = InstalledAppFlow.from_client_secrets_file(str(Path(credentials_file).expanduser()), scopes)
        creds = flow.run_local_server(port=0)
        if token_file:
            token_path = Path(token_file).expanduser()
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with token_path.open("w", encoding="utf-8") as f:
                f.write(creds.to_json())
        return creds