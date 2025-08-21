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