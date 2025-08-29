"""
Teste unitário para DriveClient.list_children sem tocar rede e sem exigir credenciais reais.
- Patch em Config.build_credentials para retornar um objeto fictício.
- Patch em googleapiclient.discovery.build (símbolo importado no módulo client) para um FakeService paginado.
"""
from types import SimpleNamespace
from unittest.mock import patch

def test_list_children_pagination():
    # Duas páginas simuladas
    pages = [
        {"files": [{"id": "1", "name": "A", "mimeType": "text/plain"}], "nextPageToken": "t1"},
        {"files": [{"id": "2", "name": "B", "mimeType": "text/plain"}], "nextPageToken": None},
    ]

    class FakeService:
        def __init__(self):
            self._i = 0
        def files(self):
            return self
        def list(self, **kwargs):
            page = pages[self._i]
            self._i += 1
            return SimpleNamespace(execute=lambda: page)

    fake_build = lambda *args, **kwargs: FakeService()

    # Importar após os patches para garantir que o símbolo 'build' do módulo seja substituído
    with patch("src.providers.google_drive.client.build", fake_build):
        from src.providers.google_drive.client import DriveClient
        from src.providers.google_drive.config import Config

        # Patch build_credentials para evitar acesso a arquivos/Google
        with patch.object(Config, "build_credentials", return_value=object()):
            cfg = Config(auth_method="service-account", credentials_file="/tmp/fake.json")
            client = DriveClient(cfg)
            items = client.list_children("fake-folder")
            assert isinstance(items, list)
            assert len(items) == 2
            assert items[0]["name"] == "A"
            assert items[1]["name"] == "B"