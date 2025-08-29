"""
Exemplo primitivo para conexão em URL e extração de textos recursiva (apenas http/https).
- Muito simples: requests + BeautifulSoup para extrair links e texto.
- Limitado a um domínio (opcional) e profundidade para evitar runaway crawling.
Uso:
  python examples/url_recursive_fetch.py https://example.com --depth 2
Observação:
- Este script é um utilitário de teste, não um crawler robusto.
"""
from __future__ import annotations
import sys
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from collections import deque

def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # remover scripts/styles
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    text = soup.get_text(separator="\n")
    return text.strip()

def crawl(start_url: str, max_depth: int = 1, same_domain: bool = True, max_pages: int = 50):
    parsed = urlparse(start_url)
    base_domain = parsed.netloc
    seen = set()
    q = deque()
    q.append((start_url, 0))
    results = []
    while q and len(results) < max_pages:
        url, depth = q.popleft()
        if url in seen or depth > max_depth:
            continue
        seen.add(url)
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "SmartSearchHUB-crawler/1.0"})
            r.raise_for_status()
            content_type = r.headers.get("content-type", "")
            if "text/html" not in content_type:
                continue
            text = extract_text_from_html(r.text)
            results.append({"url": url, "depth": depth, "text": text[:1000]})
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
            # swallow errors for demo
            print(f"warn: error fetching {url}: {e}", file=sys.stderr)
            continue
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/url_recursive_fetch.py <start_url> [depth]")
        sys.exit(1)
    start = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    res = crawl(start, max_depth=depth, same_domain=True, max_pages=30)
    print(f"Pages fetched: {len(res)}")
    for r in res:
        print(f"- {r['url']} (depth={r['depth']}) snippet: {r['text'][:200].replace('\\n', ' ')}")

if __name__ == "__main__":
    main()