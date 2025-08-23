import pytest
import sys
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def sample_html():
    """HTML de exemplo mais completo para testes."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Documento de Teste</title>
        <style>
            body { margin: 0; }
            .highlight { background: yellow; }
        </style>
    </head>
    <body>
        <h1 id="main-title">Título Principal</h1>
        <h2>Subtítulo</h2>

        <p>Parágrafo com <a href="https://example.com">link externo</a> 
           e <a href="#section">link interno</a>.</p>

        <img src="image.jpg" alt="Imagem teste" width="100" height="50"/>

        <table>
            <caption>Tabela de Exemplo</caption>
            <thead>
                <tr><th>Coluna 1</th><th>Coluna 2</th></tr>
            </thead>
            <tbody>
                <tr><td>Dados A</td><td>Dados B</td></tr>
                <tr><td>Dados C</td><td>Dados D</td></tr>
            </tbody>
        </table>

        <ul>
            <li>Item 1</li>
            <li>Item 2 com <a href="link.html">link</a></li>
        </ul>

        <script src="external.js"></script>
        <script>
            function minhaFuncao() {
                console.log('teste');
            }
        </script>
    </body>
    </html>
    """


@pytest.fixture
def mock_gdrive_file():
    """Mock de arquivo do Google Drive."""
    mock_file = Mock()
    mock_file.id = "abc123"
    mock_file.name = "documento.html"
    mock_file.mimetype = "text/html"
    mock_file.get_raw.return_value = "<html><body><h1>Teste</h1></body></html>"
    return mock_file


@pytest.fixture
def sample_complex_html():
    """HTML complexo para testes avançados."""
    return """
    <html>
    <head>
        <meta charset="utf-8">
        <title>Teste Avançado</title>
    </head>
    <body>
        <article>
            <header>
                <h1>Artigo Principal</h1>
                <p>Por: <a href="/author/joao">João Silva</a></p>
            </header>

            <section id="intro">
                <h2>Introdução</h2>
                <p>Este é um documento complexo com <strong>formatação</strong>.</p>
            </section>

            <section id="content">
                <h2>Conteúdo</h2>
                <p>Parágrafo com <em>ênfase</em> e <code>código inline</code>.</p>

                <figure>
                    <img src="chart.png" alt="Gráfico de vendas"/>
                    <figcaption>Figura 1: Vendas mensais</figcaption>
                </figure>
            </section>
        </article>

        <aside>
            <h3>Links Relacionados</h3>
            <ul>
                <li><a href="artigo1.html">Artigo 1</a></li>
                <li><a href="artigo2.html">Artigo 2</a></li>
            </ul>
        </aside>
    </body>
    </html>
    """


@pytest.fixture
def is_windows():
    """Fixture para detectar Windows."""
    return sys.platform.startswith('win')


@pytest.fixture
def temp_db_path(tmp_path):
    """Fixture para caminho de DB temporário compatível com Windows."""
    return tmp_path / "test.db"


# NOVAS FIXTURES para suporte a testes de encoding e mime detection

@pytest.fixture
def sample_text_files(tmp_path):
    """Cria arquivos de teste em diferentes encodings."""
    files = {}

    # UTF-8 com acentos portugueses
    utf8_file = tmp_path / "test_utf8.txt"
    utf8_file.write_text("configuração técnica açúcar não coração", encoding='utf-8')
    files['utf8'] = utf8_file

    # ASCII simples
    ascii_file = tmp_path / "test_ascii.txt"
    ascii_file.write_text("configuration technical sugar", encoding='ascii')
    files['ascii'] = ascii_file

    # UTF-8 com BOM
    utf8_bom_file = tmp_path / "test_utf8_bom.txt"
    utf8_bom_file.write_text("configuração com BOM", encoding='utf-8-sig')
    files['utf8_bom'] = utf8_bom_file

    # Windows-1252 simulado
    win1252_file = tmp_path / "test_win1252.txt"
    content_1252 = "configura\xe7\xe3o t\xe9cnica"
    win1252_file.write_bytes(content_1252.encode('latin1'))
    files['win1252'] = win1252_file

    return files


@pytest.fixture
def sample_binary_files(tmp_path):
    """Cria arquivos binários de teste para detecção de MIME."""
    files = {}

    # Arquivo PDF simulado (header PDF)
    pdf_file = tmp_path / "test.pdf"
    pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n'
    pdf_file.write_bytes(pdf_content)
    files['pdf'] = pdf_file

    # Arquivo JPEG simulado (header JPEG)
    jpg_file = tmp_path / "test.jpg"
    jpg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb'
    jpg_file.write_bytes(jpg_content)
    files['jpg'] = jpg_file

    # Arquivo PNG simulado (header PNG)
    png_file = tmp_path / "test.png"
    png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    png_file.write_bytes(png_content)
    files['png'] = png_file

    # Arquivo ZIP simulado (header ZIP)
    zip_file = tmp_path / "test.zip"
    zip_content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00'
    zip_file.write_bytes(zip_content)
    files['zip'] = zip_file

    return files


@pytest.fixture
def mock_requests_response():
    """Mock de resposta HTTP para testes de UrlDriver."""
    mock_response = Mock()
    mock_response.content = b"<html><body>Conteudo HTML</body></html>"
    mock_response.status_code = 200
    mock_response.headers = {
        'content-type': 'text/html; charset=utf-8',
        'content-length': '42'
    }
    mock_response.url = "https://example.com"
    return mock_response