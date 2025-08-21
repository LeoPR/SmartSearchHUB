import pytest
import os
from pathlib import Path
from src.api.facade import Folder
from src.providers.storage import Storage
from src.providers.config import Config
from src.core.io.html import Html


@pytest.mark.integration
@pytest.mark.slow
class TestRealGoogleDrive:
    """Testes que requerem conexão real com Google Drive."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup que só roda se as configurações existirem."""
        config_path = Path("./config/gdrive_auth.json")
        db_path = Path("./config/db.sqlite")

        if not config_path.exists() or not db_path.exists():
            pytest.skip("Configurações do Google Drive não encontradas")

        self.cfg = Config(file=str(config_path))
        self.storage = Storage(f"sqlite://{db_path}")

        if len(self.storage) == 0:
            pytest.skip("Nenhuma pasta configurada no storage")

        self.folder_uri = self.storage[0]

    def test_basic_connectivity(self):
        """Testa conectividade básica (baseado em list_gdrive_load.py)."""
        assert self.folder_uri.startswith("gdrive://")
        print(f"Conectado com: {self.folder_uri}")

    def test_folder_listing(self):
        """Testa listagem de pasta (baseado em list_gdrive_min.py)."""
        folder = Folder.from_uri(
            self.folder_uri,
            config=self.cfg,
            tmp="./tmp",
            cache="./cache"
        )

        info = folder.info()
        assert info["provider"] == "gdrive"

        files = folder.list()
        print(f"Encontrados {len(files)} arquivos")

        for f in files[:3]:  # Só os primeiros 3
            assert hasattr(f, 'name')
            assert hasattr(f, 'mimetype')
            assert hasattr(f, 'id')

    def test_html_extraction(self):
        """Testa extração de HTML (baseado em list_gdrive_htmls.py)."""
        folder = Folder.from_uri(
            self.folder_uri,
            config=self.cfg,
            tmp="./tmp",
            cache="./cache"
        )

        html_files = [obj for obj in folder.list() if isinstance(obj, Html)]

        if html_files:
            html_file = html_files[0]

            # Testa métodos básicos
            raw_content = html_file.get_raw(head={"characters": 100})
            assert len(raw_content) <= 100

            text_content = html_file.get_text(head={"characters": 100})
            assert isinstance(text_content, str)

            print(f"Processado: {html_file.name}")
        else:
            pytest.skip("Nenhum arquivo HTML encontrado")