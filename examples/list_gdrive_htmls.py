# examples/list_gdrive_htmls.py
from __future__ import annotations
from src.api.facade import Folder
from src.providers.google_drive.config import Config
from src.core.io.html import Html  # só p/ isinstance

cfg = Config(
    auth_method="oauth",
    credentials_file="./config/credentials/client_secret_737482562292-hrpme53jvk24vs2vvucai2h5v0p2b42i.apps.googleusercontent.com.json",
    token_file="./config/credentials/client_token.json",
)

folders = []
with open("./config/docs_sources.csv", mode="r") as f:
    lines=f.readlines()
    folders = [ line.split(",") for line in lines]
    folders = [ [d,l.replace('"','')] for d,l in folders]
    folders = [ f"{d}://{l}" for d,l in folders]

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
