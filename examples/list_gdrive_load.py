
with open("./config/docs_sources.csv", mode="r") as f:
    lines=f.readlines()
    folders = [ line.split(",") for line in lines]
    folders = [ [d,l.replace('"','')] for d,l in folders]
    folders = [ f"{d}://{l}" for d,l in folders]

#FOLDER_URI = "gdrive://1teCa93xk9Qn71xVSMIkfxTlRasa5jAic"
FOLDER_URI = folders[0]
print(FOLDER_URI)


