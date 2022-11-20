import os

mongo_uri = "mongodb://localhost:27017/"
mongo_db = "newsDB"


def export(newsname):
    output = "./results/" + newsname + ".json"
    cmd = f"mongoexport --uri={mongo_uri} --db={mongo_db} --collection={newsname} --out={output} "
    print(os.system(cmd))
    
export("baotoudaily")