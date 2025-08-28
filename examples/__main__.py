"""
Entrypoint para python -m examples

Uso:
  python -m examples.demo_url
  python -m examples.demo_gdrive

Se executado sem argumentos, mostra ajuda.
"""
import sys

def _help():
    print("Examples package - comandos disponíveis:")
    print("  python -m examples.demo_url     # roda demo de URL")
    print("  python -m examples.demo_gdrive  # roda demo de Google Drive")
    print("  python -m examples.demo_<name>  # outros demos se existirem")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        _help()
    else:
        # permite: python -m examples demo_url  -> despacha
        name = sys.argv[1]
        if name.startswith("demo_"):
            module = f"examples.{name}"
        else:
            module = f"examples.demo_{name}"
        try:
            __import__(module)
        except Exception:
            print("Falha ao executar:", module)
            raise