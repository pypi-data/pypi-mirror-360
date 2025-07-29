from CLASSES.NxOnyxApi import NxOnyxApi

def find_onyx_project(onyx: NxOnyxApi, name):
    # Recuperation de l arbre des projects
    tree = onyx.getTree()
    return search_object_in_tree(tree, name)

def search_object_in_tree(tree, name):
    # Recuperation de l arbre des projects
    id = None
    for object in tree:
        if object["detailType"] == 'project':
            if object["name"] == name:
                id = object["projectId"]
    return id