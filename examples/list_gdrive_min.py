from src.api.facade import Folder
from src.providers.google_drive.config import Config

# Ajuste os caminhos abaixo:
#cfg = Config(
#    auth_method="oauth",  # ou "service-account"
#    credentials_file="./config/credentials/client_secret_737482562292-hrpme53jvk24vs2vvucai2h5v0p2b42i.apps.googleusercontent.com.json",  # oauth
#    token_file="./config/credentials/leo_token.json",                # oauth
#    # se for service account:
#    # credentials_file="./config/credentials/service_account.json",
#)

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

folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache", save=None)

print(">>> INFO:", folder.info())
print(">>> LISTA RAW:")
for f in folder.list():
    print(f"- {f.name} ({f.mimetype})  id={f.id}")


print(">>> LISTA OBJ:")
for f in folder.list():
    print(f"- {f.name} ({f.mimetype})  id={f.id}")
