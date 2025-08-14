from src.api.facade import Folder
from src.providers.storage import Storage
from src.providers.config import Config

cfg = Config(file="./config/gdrive_auth.json")

folders = Storage("sqlite://./config/db.sqlite")
FOLDER_URI = folders[0]


folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache", save=None)

print(">>> INFO:", folder.info())
print(">>> LISTA RAW:")
for f in folder.list():
    print(f"- {f.name} ({f.mimetype})  id={f.id}")


print(">>> LISTA OBJ:")
for f in folder.list():
    print(f"- {f.name} ({f.mimetype})  id={f.id}")
