# examples/list_gdrive_htmls.py
from __future__ import annotations
from src.core.io.html import Html
from src.api.facade import Folder
from src.providers.storage import Storage
from src.providers.config import Config

cfg = Config(file="./config/gdrive_auth.json")

folders = Storage("sqlite://./config/db.sqlite")
FOLDER_URI = folders[0]

folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache", save="./permanent")

print(">>> INFO:", folder.info())
print(">>> HTMLs:")

for obj in folder.list():
    if isinstance(obj, Html):
        print(f"- {obj.name} ({obj.mimetype})  id={obj.id}")
        print("  RAW (120 chars):")
        print(obj.get_raw(head={"characters": 120}))
        print("  TEXTO (80 chars):")
        print(obj.get_text(head={"lines": 20, "characters": 80}))
