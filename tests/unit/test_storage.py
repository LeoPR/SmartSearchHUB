import pytest
import tempfile
import json
from pathlib import Path
from src.providers.storage import Storage


class TestStorage:
    def test_storage_creation(self):
        """Testa criação de storage temporário."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"

            storage = Storage(f"sqlite://{db_path}")
            try:
                assert len(storage) == 0
                assert hasattr(storage, 'conn')
            finally:
                storage.conn.close()

    def test_bootstrap_from_data(self):
        """Testa bootstrap com dados simulados."""
        bootstrap_data = [
            {"driver": "gdrive", "location": "123abc"},
            {"driver": "gdrive", "location": "456def"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            bootstrap_path = Path(temp_dir) / "bootstrap.json"

            # Cria arquivo JSON
            with open(bootstrap_path, 'w', encoding='utf-8') as f:
                json.dump(bootstrap_data, f)

            storage = Storage(f"sqlite://{db_path}")
            try:
                storage.bootstrap_from_file(str(bootstrap_path))

                assert len(storage) == 2
                assert storage[0] == "gdrive://123abc"
                assert storage[1] == "gdrive://456def"
            finally:
                storage.conn.close()

    def test_empty_bootstrap(self):
        """Testa bootstrap com arquivo vazio."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            bootstrap_path = Path(temp_dir) / "empty.json"

            # Arquivo JSON vazio
            with open(bootstrap_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

            storage = Storage(f"sqlite://{db_path}")
            try:
                storage.bootstrap_from_file(str(bootstrap_path))
                assert len(storage) == 0
            finally:
                storage.conn.close()