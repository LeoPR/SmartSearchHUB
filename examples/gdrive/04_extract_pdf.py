# examples/gdrive/04_extract_pdf.py
"""
Extração avançada de conteúdo PDF do Google Drive.

Funcionalidades:
- Filtra automaticamente arquivos PDF
- Extrai texto, metadados e estatísticas
- Suporte a diferentes métodos de extração
- Análise página por página
- Configurável via variáveis de ambiente

Uso:
    GDRIVE_TEST_FOLDER=1AbCdEf python -m examples.gdrive.04_extract_pdf

Variáveis de ambiente:
    GDRIVE_TEST_FOLDER=folder_id           # ID da pasta (obrigatório)
    GDRIVE_PDF_MAX_FILES=3                 # Máximo de arquivos a processar (default: 3)
    GDRIVE_PDF_MAX_PAGES=5                 # Máximo de páginas por PDF (default: 5)
    GDRIVE_PDF_PREVIEW_LENGTH=200          # Tamanho do preview por página (default: 200)
    GDRIVE_PDF_EXTRACT_METADATA=true       # Extrair metadados detalhados (default: true)
"""

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    from examples.common.auth_manager import AuthManager
    from examples.common.content_extractor import ContentExtractor
    from src.api.facade import Folder
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)


def main():
    """Extração avançada de conteúdo PDF."""
    print("=" * 70)
    print("📄 EXTRAÇÃO DE CONTEÚDO PDF - GOOGLE DRIVE")
    print("=" * 70)

    # Configuração a partir de variáveis de ambiente
    folder_id = os.getenv("GDRIVE_TEST_FOLDER")
    if not folder_id:
        print("❌ Defina GDRIVE_TEST_FOLDER com o ID da pasta")
        print("💡 Exemplo: GDRIVE_TEST_FOLDER=1AbCdEf python -m examples.gdrive.04_extract_pdf")
        return 1

    max_files = int(os.getenv("GDRIVE_PDF_MAX_FILES", "3"))
    max_pages = int(os.getenv("GDRIVE_PDF_MAX_PAGES", "5"))
    preview_length = int(os.getenv("GDRIVE_PDF_PREVIEW_LENGTH", "200"))
    extract_metadata = os.getenv("GDRIVE_PDF_EXTRACT_METADATA", "true").lower() == "true"

    print(f"📂 Pasta: {folder_id}")
    print(f"📊 Máximo de arquivos: {max_files}")
    print(f"📊 Máximo de páginas por PDF: {max_pages}")
    print(f"📏 Tamanho do preview: {preview_length} caracteres")
    print(f"🔍 Extrair metadados: {'✅ Sim' if extract_metadata else '❌ Não'}")

    try:
        # Verificar dependências PDF
        print("\n🔍 Verificando bibliotecas PDF...")
        pdf_lib = check_pdf_libraries()
        if pdf_lib == 'none':
            print("⚠️  AVISO: Nenhuma biblioteca PDF detectada!")
            print("💡 Para melhor extração, instale uma das seguintes:")
            print("   pip install PyMuPDF  # (recomendado)")
            print("   pip install pdfplumber")
            print("   pip install PyPDF2")
            print("\n🔄 Continuando com extração básica...")
        else:
            print(f"✅ Biblioteca PDF detectada: {pdf_lib}")

        # Autenticação
        print("\n🔐 Autenticando...")
        auth = AuthManager(interactive=True, save_tokens=True)
        config = auth.get_gdrive_config()

        # Conectar à pasta
        print(f"\n🔗 Conectando à pasta...")
        folder_uri = f"gdrive://{folder_id}"
        folder = Folder.from_uri(
            folder_uri,
            config=config,
            tmp="./tmp",
            cache="./cache"
        )

        # Listar arquivos
        print(f"\n📋 Listando arquivos...")
        all_objects = folder.list()

        # Filtrar PDFs especificamente
        pdf_files = [obj for obj in all_objects if obj.get_type() == "pdf"]

        if not pdf_files:
            print("⚠️  Nenhum arquivo PDF encontrado na pasta.")
            print("💡 Verifique se a pasta contém arquivos .pdf")
            return 0

        # Limitar quantidade
        files_to_process = pdf_files[:max_files]

        print(f"\n📊 Arquivos encontrados:")
        print(f"   Total na pasta: {len(all_objects)}")
        print(f"   Arquivos PDF: {len(pdf_files)}")
        print(f"   A processar: {len(files_to_process)}")

        # Processamento
        print(f"\n🚀 Processando PDFs...")
        print("=" * 70)

        total_pages = 0
        total_words = 0
        processed_count = 0
        pdf_stats = {
            'text_based': 0,
            'image_based': 0,
            'mixed': 0,
            'unknown': 0,
            'encrypted': 0
        }

        for i, pdf_obj in enumerate(files_to_process, 1):
            print(f"\n[{i}/{len(files_to_process)}] 📄 {pdf_obj.name}")
            print(f"   Tipo: {pdf_obj.mimetype}")

            try:
                # Extração de metadados
                if extract_metadata:
                    print("   🔍 Extraindo metadados...")
                    metadata = pdf_obj.get_metadata()
                    
                    print(f"   📊 Informações básicas:")
                    if metadata.get('title'):
                        title = metadata['title'][:50] + "..." if len(metadata['title']) > 50 else metadata['title']
                        print(f"      Título: {title}")
                    if metadata.get('author'):
                        print(f"      Autor: {metadata['author']}")
                    print(f"      Páginas: {metadata.get('pages_count', 'N/A')}")
                    print(f"      Tipo PDF: {metadata.get('pdf_type', 'unknown')}")
                    
                    # Atualiza estatísticas
                    pdf_type = metadata.get('pdf_type', 'unknown')
                    if pdf_type in pdf_stats:
                        pdf_stats[pdf_type] += 1
                    if metadata.get('encrypted', False):
                        pdf_stats['encrypted'] += 1

                # Extração de texto
                print("   📝 Extraindo texto...")
                
                # Usa método específico do PDF
                if hasattr(pdf_obj, 'get_text'):
                    text = pdf_obj.get_text(
                        max_pages=max_pages,
                        include_page_breaks=True
                    )
                else:
                    # Fallback para método genérico
                    text = pdf_obj.get_raw(
                        head={"characters": max_pages * 2000},
                        permanent=False
                    )

                if not text.strip():
                    print("   ⚠️  Nenhum texto extraído (PDF pode ser baseado em imagens)")
                    continue

                # Estatísticas básicas
                words = text.split()
                lines = text.splitlines()
                word_count = len(words)
                line_count = len([line for line in lines if line.strip()])

                print(f"   📊 Estatísticas do texto:")
                print(f"      Caracteres: {len(text):,}")
                print(f"      Palavras: {word_count:,}")
                print(f"      Linhas: {line_count:,}")

                # Análise por páginas (se suportado)
                if hasattr(pdf_obj, 'get_pages'):
                    try:
                        pages_data = pdf_obj.get_pages(max_pages=max_pages)
                        if pages_data:
                            print(f"   📋 Análise por páginas:")
                            print(f"      Páginas processadas: {len(pages_data)}")
                            
                            for page_info in pages_data[:3]:  # Mostra primeiras 3 páginas
                                page_num = page_info.get('page_number', 'N/A')
                                page_words = page_info.get('word_count', 0)
                                print(f"        Página {page_num}: {page_words} palavras")

                            total_pages += len(pages_data)
                    except Exception as e:
                        print(f"   ⚠️  Erro na análise por páginas: {e}")

                # Preview do conteúdo
                print(f"   📝 Preview do conteúdo:")
                preview_lines = text.split('\n')[:3]
                for line in preview_lines:
                    if line.strip():
                        line_preview = line[:80] + "..." if len(line) > 80 else line
                        print(f"      {line_preview}")

                # Acumuladores
                total_words += word_count
                processed_count += 1

            except Exception as e:
                print(f"   ❌ Erro no processamento: {e}")
                if os.getenv("DEBUG"):
                    import traceback
                    traceback.print_exc()

        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO FINAL - EXTRAÇÃO DE PDFs")
        print("=" * 70)
        print(f"✅ PDFs processados: {processed_count}/{len(files_to_process)}")
        print(f"📄 Total de páginas analisadas: {total_pages}")
        print(f"📝 Total de palavras: {total_words:,}")

        if processed_count > 0:
            avg_words = total_words / processed_count
            print(f"📊 Média de palavras por PDF: {avg_words:.0f}")
            
            if total_pages > 0:
                avg_words_page = total_words / total_pages
                print(f"📊 Média de palavras por página: {avg_words_page:.0f}")

        # Estatísticas por tipo
        if extract_metadata and any(pdf_stats.values()):
            print(f"\n📈 Distribuição por tipo de PDF:")
            for pdf_type, count in pdf_stats.items():
                if count > 0:
                    print(f"   {pdf_type.replace('_', ' ').title()}: {count} PDF(s)")

        print(f"\n💡 Para processar mais PDFs:")
        print(f"   GDRIVE_PDF_MAX_FILES={len(pdf_files)} python -m examples.gdrive.04_extract_pdf")

        print(f"\n💡 Para análise mais profunda:")
        print(f"   GDRIVE_PDF_MAX_PAGES=10 python -m examples.gdrive.04_extract_pdf")

        print("\n🎉 EXTRAÇÃO DE PDFs CONCLUÍDA COM SUCESSO!")

        return 0

    except KeyboardInterrupt:
        print("\n⏹️  Operação interrompida pelo usuário.")
        return 130

    except Exception as e:
        print(f"\n❌ Erro: {e}")

        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()

        return 1


def check_pdf_libraries():
    """Verifica bibliotecas PDF disponíveis."""
    try:
        import fitz  # PyMuPDF
        return 'PyMuPDF (recomendado)'
    except ImportError:
        try:
            import pdfplumber
            return 'pdfplumber'
        except ImportError:
            try:
                import PyPDF2
                return 'PyPDF2'
            except ImportError:
                return 'none'


if __name__ == "__main__":
    exit(main())