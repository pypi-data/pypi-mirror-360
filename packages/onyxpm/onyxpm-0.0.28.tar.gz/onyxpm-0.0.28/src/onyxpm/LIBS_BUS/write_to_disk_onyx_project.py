import os
import json
import shutil
from CLASSES.NxProject import NxProject

def write_to_disk_onyx_project(project: NxProject, folder, filename):
    print("Ecriture du package du projet : {}".format(project.name))

    # Création du dossier racine du projet
    temp_folder = folder + "write_to_disk_tempfolder"
    if os.path.exists(temp_folder):
        print("Deleting folder: "+temp_folder)
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    # Ecriture du fichier descriptif du projet
    file = open(temp_folder + "\\project.json", 'w', encoding="utf-8")
    file.write(json.dumps(project.json, indent=4, ensure_ascii=False))
    file.close()

    # Création de l'aborescence de dossiers du projet et écriture des composants
    for componant in project.componants:
        component_folder = temp_folder + "\\" + componant.object_type
        if not os.path.exists(component_folder):
            os.makedirs(component_folder)
        file = open(component_folder + "\\" + componant.primary_key + ".json", 'w', encoding="utf-8")
        file.write(json.dumps(componant.content, indent=4, ensure_ascii=False))
        file.close()

    # Création du package zip
    shutil.make_archive(folder + "\\" + filename, 'zip', temp_folder)
    shutil.rmtree(temp_folder)