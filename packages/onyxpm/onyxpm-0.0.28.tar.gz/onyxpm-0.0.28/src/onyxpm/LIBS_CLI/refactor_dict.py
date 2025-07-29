
def refactor_dict(donnees, parent_id=None):
    sous_projets = []
    for element in donnees:
        if element['categoryId'] == parent_id:
            sous_projet = element
            sous_projet['subproject'] = refactor_dict(donnees, element['id'])
            sous_projets.append(sous_projet)
    return sous_projets

