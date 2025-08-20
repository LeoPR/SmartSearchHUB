import pytest
from pathlib import Path

@pytest.fixture
def sample_html():
    """HTML de exemplo para testes."""
    return """
    <html>
    <head><title>Teste</title></head>
    <body>
        <h1>Título Principal</h1>
        <p>Parágrafo com <a href="https://example.com">link</a></p>
        <img src="image.jpg" alt="Imagem teste"/>
        <table>
            <tr><th>Col1</th><th>Col2</th></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
    </body>
    </html>
    """

@pytest.fixture
def mock_gdrive_response():
    """Resposta simulada do Google Drive."""
    return {
        'files': [
            {
                'id': 'abc123',
                'name': 'documento.html',
                'mimeType': 'text/html',
                'modifiedTime': '2024-01-01T10:00:00Z'
            }
        ]
    }