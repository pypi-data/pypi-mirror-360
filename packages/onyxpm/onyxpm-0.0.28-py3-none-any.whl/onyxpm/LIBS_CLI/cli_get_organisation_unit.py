from CLASSES import NxOnyxApi


def cli_get_organisation_unit_name(onyx : NxOnyxApi,organisationunitId):
    for item in onyx.getOrganisationUnits()["items"]:
        if organisationunitId== item["id"]:
            return item["displayName"]

def cli_get_organisation_unit_id(onyx: NxOnyxApi, name):
    unit_id_exists=None
    for item in onyx.getOrganisationUnits()["items"]:
        if name == item["displayName"]:
            unit_id_exists = item["id"]
    if unit_id_exists is None:
        print("Please create your organization unit before executing this command")
    return unit_id_exists

