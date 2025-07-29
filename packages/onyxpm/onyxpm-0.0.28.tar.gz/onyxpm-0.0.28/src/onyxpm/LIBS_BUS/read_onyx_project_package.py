import os
import json
from alive_progress import alive_bar
import shutil
from CLASSES.NxProject import NxProject
from CLASSES.NxComponant import NxComponant

def read_onyx_project_package(package_path, destination_path):
    print("Lecture du package : \"{}\"".format(package_path))
    ropp_result = NxProject("", "", "", [])
    with alive_bar(12, force_tty = True) as bar:
        project_folder = destination_path + "read_package_tempfolder"
        bar()

        if os.path.exists(project_folder):
            shutil.rmtree(project_folder)
        shutil.unpack_archive(package_path, project_folder, 'zip')
        bar()

        for folder in os.listdir(project_folder):
            if not folder == "project.json":
                for file in os.listdir(project_folder + "\\" + folder):
                    componant = NxComponant(folder, file[:-5], json.loads(cust_read(project_folder + "\\" + folder, file)), "", "")
                    ropp_result.componants.append(componant)
                bar()

    return ropp_result

def cust_read(folder_name, file_name):
    try:
        file = open(folder_name + "\\" + file_name, 'r', encoding = "utf-8")
        content = file.read()
        file.close()
        return content
    except Exception as e:
        message = "Echec de lecture du fichier {} | {}".format(folder_name + "\\" + file_name, str(e))
        print(message)

