from src.providers.storage import Storage

folders = Storage("sqlite://./config/db.sqlite")
#folders.bootstrap_from_file(file_path="./config/bootstrap_folders.json")  # Só na primeira vez, ou quando quiser restaurar os dados
FOLDER_URI = folders[0]

#FOLDER_URI = "gdrive://1teCa93xk9Qn71xVSMIkfxTlRasa5jAic"
FOLDER_URI = folders[0]
print(FOLDER_URI)


