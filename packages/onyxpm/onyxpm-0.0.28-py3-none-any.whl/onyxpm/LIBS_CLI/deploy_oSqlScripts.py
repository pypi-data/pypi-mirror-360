import re
from CLASSES import NxProject, NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_get_connection import cli_get_connection_sql, cli_get_connection_name
from LIBS_CLI.deploy_oConnections import deploy_oConnections
from LIBS_CLI.deploy_oVariables import deploy_oVariables


def deploy_oSqlScripts(onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src: NxTenant,
                      tenant_trg: NxTenant, source_id, target_id, script_type,name):


    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type,name=name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type,name=name)
    comp = compare_onyx_projects(project_src, project_tnt)

    response = None
    for obj in comp.componants:
        conn_id=deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "CONNECTION",obj.content["osqlScript"]["oConnectionName"])
        response=create_oSqlScripts(obj, target_id, onyx_trg, conn_id)

    return response

def create_oSqlScripts(obj, id, onyx_trg: NxOnyxApi,conn_id):
    id = str(id)
    response = None

    if "osqlScript" in obj.content and obj.action_required == 'C' or obj.action_required == 'U':
        data = obj.content["osqlScript"]
        response=onyx_trg.createSqlScript(id=obj.content["trg_id"], name=data["name"], oConnectionId=conn_id, oProjectId=id,
                                 commandTimeout=data["commandTimeout"], query=data["query"],
                                 documentation=data["documentation"])

    return response


