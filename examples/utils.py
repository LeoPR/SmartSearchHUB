from pathlib import Path
import json
import sys
from typing import List, Dict, Any, Optional

# Garante que o diretório 'src' esteja no sys.path para que imports como "from core..." funcionem.
# Isso facilita executar: python -m examples.demo_*
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

BOOTSTRAP_PATH = PROJECT_ROOT / "config" / "bootstrap_folders.json"

def load_bootstrap(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Carrega o bootstrap_folders.json (caminho padrão em /config)."""
    p = path or BOOTSTRAP_PATH
    if not p.exists():
        raise FileNotFoundError(f"Bootstrap file not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def filter_entries(entries: List[Dict[str, Any]], driver: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retorna entradas filtradas por driver (se fornecido)."""
    if driver is None:
        return entries
    return [e for e in entries if e.get("driver") == driver]