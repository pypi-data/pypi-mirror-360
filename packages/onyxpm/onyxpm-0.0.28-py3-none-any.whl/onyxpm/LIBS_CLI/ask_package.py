import os

def ask_package(folder):
    print("List of available packages : ")
    packages = os.listdir(folder)
    choice_num = 0
    name = ""
    for package in packages:
        if ".zip" in package:
            choice_num += 1
            print("Choix n°{} : {}".format(str(choice_num).ljust(2), package).ljust(60))
    selected_num = input("\nSaisissez le numéro de package à importer : ")
    choice_num = 0
    for package in packages:
        if ".zip" in package:
            choice_num += 1
            if str(choice_num) == str(selected_num):
                name = package
    print("\nLe package \"{}\" a été sélectionné.\n".format(name))
    return name