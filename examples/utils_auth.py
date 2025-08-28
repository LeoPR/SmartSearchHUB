#!/usr/bin/env python3
"""
Utilitários de autenticação para examples:
- Carrega informações de auth a partir de uma entrada do bootstrap_folders.json
- Monta headers para URLs (bearer/headers)
- Cria credenciais para Google Drive (service account ou OAuth)
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def _read_json_file(path: str | Path) -> Dict[str, Any]:
    p = Path(path).expanduser()
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_auth_for_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza o bloco de autenticação da entry do bootstrap.

    Convenções suportadas:
    - method: "service_account" | "oauth" | "bearer" | "headers" | "none"
    - service_account:
        - env_var (opcional, default "GOOGLE_APPLICATION_CREDENTIALS")
        - file (caminho para o JSON de service account)
        - scopes (lista de scopes; default drive readonly)
    - oauth:
        - credentials_file (client_secret.json)
        - token_file (arquivo onde o token OAuth será salvo/lido)
        - scopes (opcional, default drive readonly)
    - bearer:
        - token_env (nome da env var com o token; default "URL_BEARER_TOKEN")
        - token (opcional, não recomendado em repositório)
    - headers:
        - headers_file (JSON com {"headers": {...}} ou direto {...})
        - headers (dict inline; evitar em repo público)

    Retorna um dict padronizado com os campos resolvidos.
    """
    auth = entry.get("auth") or {}
    method = str(auth.get("method", "none")).strip().lower()

    result: Dict[str, Any] = {"method": method}

    if method == "service_account":
        env_var = auth.get("env_var") or "GOOGLE_APPLICATION_CREDENTIALS"
        env_path = os.getenv(env_var)
        file_path = auth.get("file")
        if env_path:
            result["file"] = env_path
            result["from_env"] = True
        elif file_path:
            result["file"] = str(Path(file_path).expanduser())
        result["scopes"] = auth.get("scopes") or DEFAULT_DRIVE_SCOPES
        result["env_var"] = env_var
        return result

    if method == "oauth":
        result["credentials_file"] = auth.get("credentials_file")
        result["token_file"] = auth.get("token_file")
        result["scopes"] = auth.get("scopes") or DEFAULT_DRIVE_SCOPES
        return result

    if method == "bearer":
        token_env = auth.get("token_env") or "URL_BEARER_TOKEN"
        result["token_env"] = token_env
        result["token"] = os.getenv(token_env) or auth.get("token")
        return result

    if method == "headers":
        headers_file = auth.get("headers_file")
        headers: Dict[str, Any] = {}
        if headers_file:
            p = Path(headers_file).expanduser()
            if p.exists():
                try:
                    data = _read_json_file(p)
                    # aceita {"headers": {...}} ou direto {...}
                    headers = data.get("headers", data)
                except Exception:
                    headers = {}
        # Merge com headers inline (inline tem menor prioridade)
        headers_inline = auth.get("headers") or {}
        headers = {**headers_inline, **headers} if headers else headers_inline
        result["headers"] = headers
        return result

    # none / padrão
    return result


def get_url_headers(auth_info: Dict[str, Any]) -> Dict[str, str]:
    """
    A partir de auth_info (load_auth_for_entry), retorna um dict de headers para requests.
    Regras:
    - method=bearer: usa Authorization: Bearer <token>
    - method=headers: usa headers do arquivo/inline
    - URL_EXTRA_HEADERS (JSON) pode complementar/override os headers (para testes)
    """
    headers: Dict[str, str] = {}

    method = auth_info.get("method")
    if method == "bearer":
        token = auth_info.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

    elif method == "headers":
        for k, v in (auth_info.get("headers") or {}).items():
            headers[str(k)] = str(v)

    # Extra overrides via env var (útil para testes sem mexer no arquivo)
    extra_json = os.getenv("URL_EXTRA_HEADERS")
    if extra_json:
        try:
            extra = json.loads(extra_json)
            if isinstance(extra, dict):
                # env tem prioridade
                headers.update({str(k): str(v) for k, v in extra.items()})
        except Exception:
            pass

    return headers


def get_gdrive_credentials(auth_info: Dict[str, Any]):
    """
    Cria credenciais do Google Drive conforme auth_info.
    Suporta:
      - method=service_account: requer 'file' (ou env var definida)
      - method=oauth: requer 'credentials_file' e opcional 'token_file'
        - Se token_file existir, carrega; senão, inicia fluxo e salva token_file
    Retorna o objeto credentials adequado ou lança ValueError em erro de configuração.

    Importante: imports de bibliotecas Google são feitos dentro da função
    para não exigir dependências quando não usadas.
    """
    method = auth_info.get("method")

    if method == "service_account":
        sa_file = auth_info.get("file")
        if not sa_file:
            env_var = auth_info.get("env_var") or "GOOGLE_APPLICATION_CREDENTIALS"
            raise ValueError(
                f"Service account não configurada. Defina {env_var} ou entry.auth.file no bootstrap."
            )
        try:
            from google.oauth2 import service_account
        except Exception as e:
            raise RuntimeError(
                "Dependências do Google não instaladas. Instale: pip install google-api-python-client google-auth"
            ) from e

        scopes = auth_info.get("scopes") or DEFAULT_DRIVE_SCOPES
        creds = service_account.Credentials.from_service_account_file(sa_file, scopes=scopes)
        return creds

    if method == "oauth":
        credentials_file = auth_info.get("credentials_file")
        token_file = auth_info.get("token_file") or "./config/credentials/client_token.json"
        if not credentials_file:
            raise ValueError("OAuth requer 'credentials_file' no entry.auth.")

        try:
            from google.oauth2.credentials import Credentials as OAuthCredentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except Exception as e:
            raise RuntimeError(
                "Dependências OAuth não instaladas. Instale: pip install google-auth-oauthlib google-auth google-api-python-client"
            ) from e

        scopes = auth_info.get("scopes") or DEFAULT_DRIVE_SCOPES
        creds = None

        # Tenta carregar token existente
        token_path = Path(token_file).expanduser()
        if token_path.exists():
            try:
                creds = OAuthCredentials.from_authorized_user_file(str(token_path), scopes)
            except Exception:
                creds = None

        # Se não tem token válido, inicia o fluxo interativo
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(str(Path(credentials_file).expanduser()), scopes)
            # Usa run_local_server para UX melhor; se falhar, use run_console
            try:
                creds = flow.run_local_server(port=0)
            except Exception:
                creds = flow.run_console()
            # Garante que a pasta existe e salva token
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with token_path.open("w", encoding="utf-8") as f:
                f.write(creds.to_json())

        return creds

    raise ValueError(f"Método de autenticação não suportado para GDrive: {method}")