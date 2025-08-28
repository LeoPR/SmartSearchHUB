#!/usr/bin/env python3
"""
Demo: captura cookies de sessão para uma URL protegida (ex.: Google Sites) e gera um arquivo de headers.

- Abre o Chromium (via Playwright)
- Você faz login normalmente
- Ao terminar, pressione ENTER no terminal
- O script salva config/credentials/url_headers.json com o header "Cookie" e "User-Agent"

Requisitos:
  pip install playwright
  python -m playwright install chromium

Uso:
  # Usa a primeira entrada "url" do config/bootstrap_folders.json
  python -m examples.demo_auth_url

  # Ou informe diretamente a URL e o arquivo de saída:
  python -m examples.demo_auth_url --url https://sites.google.com/... --out config/credentials/url_headers.json
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

# Primeiro tentamos import relativo (quando rodado como módulo: python -m examples.demo_auth_url)
try:
    from .utils import load_bootstrap, filter_entries
except Exception:
    # Fallback: ajustar sys.path manualmente se estiver rodando o arquivo diretamente
    HERE = Path(__file__).resolve().parent
    PROJECT_ROOT = HERE.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from examples.utils import load_bootstrap, filter_entries  # type: ignore
    except Exception as e:
        print("Falha ao importar utils. Verifique se existe 'examples/__init__.py' e 'examples/utils.py'.")
        raise

def _ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def _build_cookie_header(cookies: list[dict], host: str) -> str:
    """
    Monta o header Cookie a partir dos cookies do contexto.
    Inclui cookies relevantes para o host e domínios superiores (ex.: .google.com).
    """
    host = host.lower()
    parts = []
    for c in cookies:
        domain = (c.get("domain") or "").lower()
        if domain and (domain in host or host.endswith(domain.lstrip("."))):
            name = c.get("name")
            value = c.get("value")
            if name and value is not None:
                parts.append(f"{name}={value}")
    if not parts:  # fallback: inclui todos, se nada combinou
        for c in cookies:
            name = c.get("name")
            value = c.get("value")
            if name and value is not None:
                parts.append(f"{name}={value}")
    return "; ".join(parts)

def _pick_url_from_bootstrap(bootstrap_path: Path | None) -> str | None:
    try:
        entries = load_bootstrap(bootstrap_path)
    except Exception:
        return None
    url_entries = filter_entries(entries, driver="url")
    if not url_entries:
        return None
    return url_entries[0].get("location")

def main():
    parser = argparse.ArgumentParser(description="Captura cookies de sessão para URL protegida e salva headers JSON.")
    parser.add_argument("--url", help="URL alvo (se não informado, usa a primeira entrada 'url' do bootstrap)", default=None)
    parser.add_argument("--bootstrap", help="Caminho do bootstrap_folders.json", default=None)
    parser.add_argument("--out", help="Arquivo de saída dos headers JSON", default="config/credentials/url_headers.json")
    args = parser.parse_args()

    target_url = args.url or _pick_url_from_bootstrap(Path(args.bootstrap) if args.bootstrap else None)
    if not target_url:
        print("Não foi possível determinar a URL. Informe --url ou configure uma entrada 'url' no bootstrap.")
        sys.exit(2)

    out_path = Path(args.out)
    _ensure_dir(out_path)

    parsed = urlparse(target_url)
    host = parsed.hostname or "sites.google.com"

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("Dependência Playwright ausente. Instale e prepare o Chromium:")
        print("  pip install playwright")
        print("  python -m playwright install chromium")
        sys.exit(3)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"Abrindo navegador para: {target_url}")
        page.goto(target_url, wait_until="domcontentloaded")

        print("\nFAÇA LOGIN NA JANELA QUE ABRIU.")
        print("Após concluir o login e conseguir acessar a página, volte aqui e pressione ENTER.")
        input("Pressione ENTER para capturar cookies e salvar headers... ")

        cookies = context.cookies()
        cookie_header = _build_cookie_header(cookies, host)

        headers_obj = {
            "headers": {
                "Cookie": cookie_header,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        }

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(headers_obj, f, ensure_ascii=False, indent=2)

        print(f"\nHeaders salvos em: {out_path.resolve()}")
        print("Agora rode: python -m examples.demo_url")
        storage_state_path = out_path.with_suffix(".storage_state.json")
        context.storage_state(path=str(storage_state_path))
        print(f"Storage state salvo (opcional): {storage_state_path.resolve()}")

        browser.close()

if __name__ == "__main__":
    main()