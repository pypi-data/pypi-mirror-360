from CLASSES.NxOnyxApi import NxOnyxApi
from rich.console import Console


def ask_project(onyx: NxOnyxApi, message):
    console = Console()
    # Récupération de l'arbre des projet
    tree = onyx.getTree()
    project_list = []
    for object in tree:
        if object["detailType"] == 'project':
            prj = {"id": object["projectId"], "name": object["name"]}
            project_list.append(prj)
    # Listing des projets disponibles à l'export
    choice_num = 0
    console.print(f"[magenta]{message}[/magenta]")
    line = ""
    i = 0
    for prj in project_list:
        i += 1
        choice_num += 1
        line += (f"[yellow]{choice_num}[/yellow] . [cyan]{prj['name']}[/cyan]\n")
        if i == 4:
            console.print(line)
            line = ""
            i = 0
    if i > 0:
        console.print(line)
    # Choix du projet à exporter
    choice_num = 0
    id = ""
    selected_num = input("\nType the project's number you want to analyse: ")
    for prj in project_list:
        choice_num += 1
        if str(choice_num) == str(selected_num):
            id = prj["id"]
    return id