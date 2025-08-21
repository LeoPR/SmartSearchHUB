import sqlite3
import os
import json

class Storage:
    def __init__(self, uri):
        assert uri.startswith("sqlite://")
        db_path = uri.replace("sqlite://", "")
        self.db_path = db_path
        db_exists = os.path.exists(db_path)
        self.conn = sqlite3.connect(db_path)
        self._ensure_tables()
        self._folders = self._load_folders()

    def _ensure_tables(self):
        # Cria a tabela se não existir
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS folders (
                driver TEXT,
                location TEXT
            )
        """)
        self.conn.commit()

    def _load_folders(self):
        folders = []
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT driver, location FROM folders")
            for driver, location in cursor.fetchall():
                folders.append(f"{driver}://{location}")
        except Exception:
            folders = []
        return folders

    def __getitem__(self, idx):
        return self._folders[idx]

    def __len__(self):
        return len(self._folders)

    def reset(self):
        # Apaga e recria a tabela folders
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS folders")
        self.conn.commit()
        self._ensure_tables()
        self._folders = []

    def bootstrap_from_file(self, file_path="config/bootstrap_folders.json"):
        # Lê os dados do arquivo JSON e popula a tabela folders
        self.reset()
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            cursor = self.conn.cursor()
            for entry in data:
                driver = entry.get("driver")
                location = entry.get("location")
                if driver and location:
                    cursor.execute(
                        "INSERT INTO folders (driver, location) VALUES (?, ?)",
                        (driver, location)
                    )
            self.conn.commit()
            self._folders = self._load_folders()
        except Exception as e:
            print(f"Erro ao fazer bootstrap: {e}")

    def close(self):
        """Fecha conexão com banco (importante no Windows)."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup automático."""
        self.close()