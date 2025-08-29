"""
Exemplo primitivo para fetch recursivo de URLs com suporte a autenticação simples.

Funcionalidade:
- Recebe <start_url> e opcional --depth
- Suporta autenticação:
    * --auth-type bearer --auth-value <token>
    * --auth-type basic  --auth-value <user:pass>
    * OU via env URL_AUTH_TYPE / URL_AUTH_VALUE
    * OU headers adicionais via env URL_EXTRA_HEADERS (JSON string) que é mesclado nos headers
- Uso PowerShell:
    $env:URL_AUTH_TYPE="bearer"
    $env:URL_AUTH_VALUE="MY_TOKEN"
    python examples/url_recursive_fetch.py https://example.com --depth 2

Dependências:
- requests
- beautifulsoup4
"""
from __future__ import annotations
import sys
import argparse
import base64
import json
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from collections import deque
import os

DEFAULT_USER_AGENT = "SmartSearchHUB-crawler/1.0"

def build_auth_headers(auth_type: str | None, auth_value: str | None):
    headers = {}
    if not auth_type or not auth_value:
        return headers
    t = auth_type.lower()
    if t == "bearer":
        headers["Authorization"] = f"Bearer {auth_value}"
    elif t == "basic":
        # auth_value expected as "user:pass"
        token = base64.b64encode(auth_value.encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {token}"
    return headers

def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    text = soup.get_text(separator="\n")
    return text.strip()

def crawl(start_url: str, max_depth: int = 1, same_domain: bool = True, max_pages: int = 50, headers=None):
    parsed = urlparse(start_url)
    base_domain = parsed.netloc
    seen = set()
    q = deque()
    q.append((start_url, 0))
    results = []
    headers = headers or {}
    while q and len(results) < max_pages:
        url, depth = q.popleft()
        if url in seen or depth > max_depth:
            continue
        seen.add(url)
        try:
            r = requests.get(url, timeout=10, headers=headers)
            r.raise_for_status()
            content_type = r.headers.get("content-type", "")
            if "text/html" not in content_type:
                continue
            text = extract_text_from_html(r.text)
            results.append({"url": url, "depth": depth, "text": text[:2000]})
            if depth < max_depth:
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    joined = urljoin(url, href)
                    p = urlparse(joined)
                    if same_domain and p.netloc != base_domain:
                        continue
                    if joined not in seen:
                        q.append((joined, depth + 1))
        except Exception as e:
            print(f"warn: error fetching {url}: {e}", file=sys.stderr)
            continue
    return results

def parse_args():
    p = argparse.ArgumentParser(description="Simple recursive URL fetcher with auth support (primitive).")
    p.add_argument("start_url", help="Start URL (http[s]://...)")
    p.add_argument("--depth", type=int, default=1, help="Recursion depth")
    p.add_argument("--max-pages", type=int, default=30, help="Max pages to fetch")
    p.add_argument("--auth-type", choices=("bearer", "basic"), help="Auth type (bearer|basic)")
    p.add_argument("--auth-value", help="Auth value (token for bearer, 'user:pass' for basic)")
    p.add_argument("--same-domain/--any-domain", dest="same_domain", default=True)
    return p.parse_args()

def main():
    args = parse_args()

    # Resolve auth: CLI > env
    auth_type = args.auth_type or os.getenv("URL_AUTH_TYPE")
    auth_value = args.auth_value or os.getenv("URL_AUTH_VALUE")

    headers = {"User-Agent": DEFAULT_USER_AGENT}
    # Merge auth headers
    headers.update(build_auth_headers(auth_type, auth_value))

    # Merge extra headers from env
    extra = os.getenv("URL_EXTRA_HEADERS")
    if extra:
        try:
            j = json.loads(extra)
            if isinstance(j, dict):
                headers.update({str(k): str(v) for k, v in j.items()})
        except Exception:
            print("Warning: URL_EXTRA_HEADERS parsing failed; expected JSON object.", file=sys.stderr)

    res = crawl(args.start_url, max_depth=args.depth, same_domain=args.same_domain, max_pages=args.max_pages, headers=headers)
    print(f"Pages fetched: {len(res)}")
    for r in res:
        snippet = r["text"][:400].replace("\n", " ")
        print(f"- {r['url']} (depth={r['depth']}) snippet: {snippet}")

if __name__ == "__main__":
    main()