# utilitários para diagnóstico e fallback de PDF
from __future__ import annotations
import base64
import io
import tempfile
import os
from typing import Tuple, Optional

def ensure_bytes(content) -> bytes:
    """
    Garante que 'content' seja bytes.
    Se for str e parecer base64 (ex.: começa com 'JVBER'), tenta decodificar.
    """
    if isinstance(content, bytes):
        return content
    if isinstance(content, str):
        s = content.strip()
        # detectable base64 of '%PDF' often starts with 'JVBER'
        if s.startswith("JVBER") or all(c.isalnum() or c in "+/=\n\r" for c in s[:8]):
            try:
                return base64.b64decode(s)
            except Exception:
                # fallback: encode as utf-8 bytes (menos provável útil)
                return s.encode("utf-8")
        else:
            return s.encode("utf-8")
    raise TypeError("Conteúdo PDF deve ser bytes ou str")

def looks_like_pdf(b: bytes) -> bool:
    return bool(b and b.startswith(b"%PDF"))

def write_temp_pdf(b: bytes) -> str:
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tf.write(b)
    tf.flush()
    tf.close()
    return tf.name

def safe_remove(path: str):
    try:
        os.unlink(path)
    except Exception:
        pass

def try_open_with_fitz_bytes(b: bytes) -> Tuple[bool, Optional[str]]:
    try:
        import fitz
    except Exception as e:
        return False, f"PyMuPDF não disponível: {e}"
    try:
        doc = fitz.open(stream=b, filetype="pdf")
        n = len(doc)
        doc.close()
        return True, f"open stream OK ({n} páginas)"
    except Exception as e:
        return False, f"PyMuPDF stream erro: {type(e).__name__}: {e}"

def try_open_with_fitz_file(b: bytes) -> Tuple[bool, Optional[str]]:
    try:
        import fitz
    except Exception as e:
        return False, f"PyMuPDF não disponível: {e}"
    tmp = None
    try:
        tmp = write_temp_pdf(b)
        doc = fitz.open(tmp)
        n = len(doc)
        doc.close()
        return True, f"open file OK ({n} páginas) - path: {tmp}"
    except Exception as e:
        return False, f"PyMuPDF file erro: {type(e).__name__}: {e}"
    finally:
        if tmp:
            safe_remove(tmp)

def try_other_backends(b: bytes) -> Tuple[bool, str]:
    # pdfplumber
    try:
        import pdfplumber, io
        with pdfplumber.open(io.BytesIO(b)) as doc:
            return True, f"pdfplumber OK ({len(doc.pages)} páginas)"
    except Exception as _:
        pass
    # PyPDF2
    try:
        import PyPDF2, io
        reader = PyPDF2.PdfReader(io.BytesIO(b))
        return True, f"PyPDF2 OK ({len(reader.pages)} páginas)"
    except Exception as _:
        pass
    return False, "Todos os backends falharam"