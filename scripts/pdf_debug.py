#!/usr/bin/env python3
"""
scripts/pdf_debug.py

Script de diagnóstico para um PDF. Testa:
 - PyMuPDF (stream + arquivo)
 - pdfplumber
 - PyPDF2
 - (opcional) OCR via pytesseract (usa binário tesseract; configure TESSERACT_CMD se necessário)

Uso:
  python scripts/pdf_debug.py /caminho/para/arquivo.pdf [--ocr] [--dpi 200] [--lang por]

Ou defina variável de ambiente PDF_OCR=1 para habilitar OCR por padrão.
"""
from pathlib import Path
import sys
import io
import argparse
import shutil
import os
import traceback

def read_bytes(path: Path) -> bytes:
    return path.read_bytes()

def check_tesseract_available():
    # Prioriza TESSERACT_CMD env var
    tess_cmd = os.getenv("TESSERACT_CMD")
    if tess_cmd and Path(tess_cmd).exists():
        return tess_cmd
    # fallback para which
    found = shutil.which("tesseract")
    return found

def try_pymupdf(data: bytes, path: Path):
    try:
        import fitz
    except Exception as e:
        return {"available": False, "error": f"PyMuPDF não instalado: {e}"}
    out = {"available": True, "stream_ok": False, "file_ok": False, "pages": [], "images_per_page": [], "errors": []}
    # stream
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        out["stream_ok"] = True
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text("text") or ""
            # contar imagens na página
            imgs = page.get_images(full=True) or []
            out["pages"].append(text)
            out["images_per_page"].append(len(imgs))
        doc.close()
    except Exception as e:
        out["errors"].append(("stream", repr(e)))
    # file
    try:
        docf = fitz.open(str(path))
        out["file_ok"] = True
        # se não extraiu via stream, tenta extrair aqui
        if not any(p.strip() for p in out["pages"]):
            out["pages"] = []
            out["images_per_page"] = []
            for i in range(len(docf)):
                page = docf[i]
                text = page.get_text("text") or ""
                imgs = page.get_images(full=True) or []
                out["pages"].append(text)
                out["images_per_page"].append(len(imgs))
        docf.close()
    except Exception as e:
        out["errors"].append(("file", repr(e)))
    return out

def try_pdfplumber(data: bytes):
    try:
        import pdfplumber
    except Exception as e:
        return {"available": False, "error": f"pdfplumber não instalado: {e}"}
    out = {"available": True, "pages": [], "error": None}
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for p in pdf.pages:
                text = p.extract_text() or ""
                out["pages"].append(text)
    except Exception as e:
        out["error"] = repr(e)
    return out

def try_pypdf2(data: bytes):
    try:
        import PyPDF2, io
    except Exception as e:
        return {"available": False, "error": f"PyPDF2 não instalado: {e}"}
    out = {"available": True, "pages": [], "error": None}
    try:
        r = PyPDF2.PdfReader(io.BytesIO(data))
        for p in r.pages:
            try:
                text = p.extract_text() or ""
            except Exception:
                text = ""
            out["pages"].append(text)
    except Exception as e:
        out["error"] = repr(e)
    return out

def ocr_with_pymupdf(data: bytes, dpi: int = 200, lang: str = None, tess_cmd: str | None = None):
    try:
        import fitz
    except Exception as e:
        return {"error": f"PyMuPDF não instalado: {e}"}
    try:
        import pytesseract
        from PIL import Image
    except Exception as e:
        return {"error": f"pytesseract/Pillow não instalado: {e}"}
    if tess_cmd:
        pytesseract.pytesseract.tesseract_cmd = tess_cmd

    pages_text = []
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        for i in range(len(doc)):
            page = doc[i]
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            try:
                img_bytes = pix.tobytes("png")
            except Exception:
                try:
                    img_bytes = pix.getPNGData()
                except Exception:
                    tmpf = f"__tmp_page_{i}.png"
                    pix.save(tmpf)
                    with open(tmpf, "rb") as fh:
                        img_bytes = fh.read()
                    try:
                        os.unlink(tmpf)
                    except Exception:
                        pass
            im = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(im, lang=lang) if lang else pytesseract.image_to_string(im)
            pages_text.append(text)
        doc.close()
    except Exception as e:
        return {"error": repr(e)}
    return {"pages": pages_text}

def summarize(pages):
    total_chars = sum(len(p) for p in pages)
    total_nonempty = sum(1 for p in pages if p.strip())
    return total_chars, total_nonempty

def main():
    ap = argparse.ArgumentParser(description="Diagnóstico de PDF - extração/ocr")
    ap.add_argument("pdf", help="Caminho para o PDF")
    ap.add_argument("--ocr", action="store_true", help="Habilitar OCR (pytesseract + tesseract)")
    ap.add_argument("--dpi", type=int, default=200, help="DPI para rasterização (OCR)")
    ap.add_argument("--lang", type=str, default=None, help="Idioma para pytesseract (ex: por, eng)")
    args = ap.parse_args()

    # permitir habilitar OCR via env var
    env_ocr = os.getenv("PDF_OCR")
    if env_ocr and env_ocr not in ("0", "false", "False"):
        args.ocr = True

    path = Path(args.pdf)
    if not path.exists():
        print("Arquivo não encontrado:", path)
        sys.exit(2)

    data = read_bytes(path)
    print("Arquivo:", path)
    print("Tamanho bytes:", len(data))
    print("Header preview:", data[:64])
    print("Startswith %PDF:", data.startswith(b"%PDF"))

    print("\n>>> PyMuPDF (stream/file) test")
    try:
        r = try_pymupdf(data, path)
        if not r["available"]:
            print(r["error"])
        else:
            print("stream_ok:", r["stream_ok"], "file_ok:", r["file_ok"])
            print("páginas detectadas:", len(r["pages"]))
            print("imagens por página:", r["images_per_page"])
            chars, nonempty = summarize(r["pages"])
            print(f"PyMuPDF extraíu chars={chars}, páginas com texto={nonempty}")
            for i, p in enumerate(r["pages"]):
                if p.strip():
                    print(f"[PyMuPDF] primeira página com texto: {i+1} preview:", p[:300].replace("\n", " "))
                    break
    except Exception:
        traceback.print_exc()

    print("\n>>> pdfplumber test")
    try:
        rp = try_pdfplumber(data)
        if not rp["available"]:
            print(rp["error"])
        else:
            if rp.get("error"):
                print("Erro pdfplumber:", rp["error"])
            else:
                chars, nonempty = summarize(rp["pages"])
                print(f"pdfplumber extraíu chars={chars}, páginas com texto={nonempty}")
                for i, p in enumerate(rp["pages"]):
                    if p.strip():
                        print(f"[pdfplumber] primeira página com texto: {i+1} preview:", p[:300].replace("\n", " "))
                        break
    except Exception:
        traceback.print_exc()

    print("\n>>> PyPDF2 test")
    try:
        r2 = try_pypdf2(data)
        if not r2["available"]:
            print(r2["error"])
        else:
            if r2.get("error"):
                print("Erro PyPDF2:", r2["error"])
            else:
                chars, nonempty = summarize(r2["pages"])
                print(f"PyPDF2 extraíu chars={chars}, páginas com texto={nonempty}")
                for i, p in enumerate(r2['pages']):
                    if p.strip():
                        print(f"[PyPDF2] primeira página com texto: {i+1} preview:", p[:300].replace("\n", " "))
                        break
    except Exception:
        traceback.print_exc()

    # OCR opcional
    if args.ocr:
        print("\n>>> OCR habilitado (pytesseract)")
        tess_cmd = check_tesseract_available()
        if not tess_cmd:
            print("Tesseract não encontrado no PATH e TESSERACT_CMD não setado. Instale o binário ou defina TESSERACT_CMD.")
            print("Windows: instalar Tesseract e ajustar PATH ou setar TESSERACT_CMD para o tesseract.exe")
        else:
            print("Tesseract encontrado em:", tess_cmd)
            try:
                ocrres = ocr_with_pymupdf(data, dpi=args.dpi, lang=args.lang, tess_cmd=tess_cmd)
                if ocrres.get("error"):
                    print("Erro OCR:", ocrres["error"])
                else:
                    chars, nonempty = summarize(ocrres["pages"])
                    print(f"OCR produziu chars={chars}, páginas com texto={nonempty}")
                    for i, p in enumerate(ocrres["pages"]):
                        if p.strip():
                            print(f"[OCR] primeira página com texto: {i+1} preview:", p[:500].replace("\n", " "))
                            break
            except Exception:
                traceback.print_exc()
    else:
        print("\nOCR não habilitado (use --ocr ou defina PDF_OCR=1)")

if __name__ == "__main__":
    main()