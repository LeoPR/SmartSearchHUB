#!/usr/bin/env python3
"""
Demo: busca URLs listadas em config/bootstrap_folders.json e processa HTML com HtmlObjectParser.

Execute:
  python -m examples.demo_url
"""
import sys
import requests

# Importa utils primeiro para inserir src/ no sys.path
from examples.utils import load_bootstrap, filter_entries
from examples.utils_auth import load_auth_for_entry, get_url_headers

from core.io.html import HtmlObjectParser


def fetch_url(url: str, headers: dict | None = None, timeout: int = 20) -> str:
    resp = requests.get(url, headers=headers or {}, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def main():
    try:
        entries = load_bootstrap()
    except FileNotFoundError as e:
        print("Erro:", e)
        sys.exit(1)

    url_entries = filter_entries(entries, driver="url")
    if not url_entries:
        print("Nenhuma entrada 'url' em config/bootstrap_folders.json")
        return

    for entry in url_entries:
        loc = entry.get("location")
        if not loc:
            continue

        print(f"\n--- Processando URL: {loc}")

        # Autenticação/headers via bootstrap (com override por env se definido)
        auth_info = load_auth_for_entry(entry)
        headers = get_url_headers(auth_info)

        try:
            html = fetch_url(loc, headers=headers)
        except Exception as e:
            print("Falha ao buscar URL:", e)
            continue

        parser = HtmlObjectParser(
            base_url=loc,
            resolve_relative_urls=True,
            extract_links=True,
            extract_images=True,
            extract_scripts=True,
            extract_styles=True,
        )
        objs = parser.parse(html)

        # Contagem por tipo
        counts: dict[str, int] = {}
        for o in objs:
            counts[o.object_type] = counts.get(o.object_type, 0) + 1

        print("Objetos extraídos (por tipo):")
        for k in sorted(counts.keys()):
            print(f"  {k}: {counts[k]}")

        # Exemplos
        headings = [o for o in objs if getattr(o, "object_type", "") == "heading"]
        links = [o for o in objs if getattr(o, "object_type", "") == "link"]

        print(f"  Headings (ex.): {[h.get_content() for h in headings[:5]]}")
        print(f"  Links (ex.): {[l.get_content() for l in links[:5]]}")


if __name__ == "__main__":
    main()