from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_get_connection import cli_get_connection_form, cli_get_connection_name
from LIBS_CLI.cli_get_id import cli_get_id_form
from LIBS_CLI.deploy_oConnections import deploy_oConnections


def deploy_oForms(onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src: NxTenant, tenant_trg: NxTenant, source_id, target_id, script_type,name):
    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type, name=name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type, name=name)
    comp = compare_onyx_projects(project_src, project_tnt)

    new_form_id=None
    for obj in comp.componants:
        new_form_id=obj.content["trg_id"]
        if "oForm" in obj.content:
            old_form_id = obj.content["oForm"]["id"]

            conn_id = cli_get_connection_form(obj.content["oForm"]["id"], target_id, onyx_src,onyx_trg)
            if conn_id is None:
                object_name=cli_get_connection_name(obj.content["oForm"]["oConnectionId"],onyx_src)
                conn_id=deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "CONNECTION", object_name)

            new_form_id = create_oForms(obj, target_id, onyx_trg, conn_id)
            if new_form_id is None:
                new_form_id = cli_get_id_form(obj.content["oForm"]["displayedName"], target_id, onyx_trg)

            create_formColumn(onyx_trg, comp, old_form_id, new_form_id)

    return new_form_id
def create_oForms(obj, id, onyx_trg: NxOnyxApi, conn_id):
    id = str(id)
    response = None
    if "oForm" in obj.content and obj.action_required == 'U' or obj.action_required == 'C':

        data = obj.content["oForm"]
        response = onyx_trg.createForm(id=obj.content["trg_id"],displayedName= data["displayedName"], documentation=data["documentation"], oProjectId=id,
                                    oConnectionId=conn_id, technicalName= data["technicalName"], isActive=data["isActive"])
    return response


def create_formColumn(onyx_trg: NxOnyxApi, comp, old_form_id, new_form_id):

    for obj in comp.componants:
        if "oFormColumn" in obj.content and (obj.action_required == 'U'  or obj.action_required == 'C'):
            if obj.content["oFormColumn"]["oFormId"] == old_form_id:
                data = obj.content["oFormColumn"]
                onyx_trg.createFormColumn(id=obj.content["trg_id"],characterMaximumLength=data["characterMaximumLength"],
                                          displayOrder=data["displayOrder"],
                                          displayedName=data["displayedName"], dropDownQuery=data["dropDownQuery"],
                                          editorType=data["editorType"],
                                          isDisplayed=data["isDisplayed"], isDropDown=data["isDropDown"],
                                          isNullable=data["isNullable"],
                                          numericPrecision=data["numericPrecision"],
                                          technicalName=data["technicalName"], numericScale=data["numericScale"],
                                          oFormId=new_form_id, type=data["type"])
