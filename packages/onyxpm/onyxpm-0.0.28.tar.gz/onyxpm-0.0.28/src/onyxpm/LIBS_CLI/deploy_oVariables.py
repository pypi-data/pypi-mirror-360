from CLASSES import NxProject, NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import compare_onyx_projects, read_onyx_project_api
from LIBS_CLI.cli_get_connection import cli_get_connection_variable, cli_get_connection_name
from LIBS_CLI.deploy_oConnections import deploy_oConnections


def deploy_oVariables( onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg : NxTenant, source_id, target_id, script_type, object_name):

    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type,name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type,name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)

    for obj in comp.componants:
        if obj.content["oVariable"]["oConnectionId"] is not None:
            conn_id = cli_get_connection_variable(obj.content["oVariable"]["id"], target_id, onyx_src,onyx_trg)
            if conn_id is None:
                object_name = cli_get_connection_name(obj.content["oVariable"]["oConnectionId"], onyx_src)
                conn_id=deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "CONNECTION",object_name)
                create_oVariables(obj, target_id, onyx_trg, conn_id,tenant_trg.tenant_id)
            else:

                create_oVariables(obj, target_id, onyx_trg, conn_id,tenant_trg.tenant_id)
        else:
            conn_id = None

            create_oVariables(obj, target_id, onyx_trg, conn_id,tenant_trg.tenant_id)


def create_oVariables(obj, id, onyx_trg: NxOnyxApi,conn_id,tenant_id):
    id = str(id)
    response=None
    if "oVariable" in obj.content and obj.action_required == 'C' or obj.action_required == 'U':

        data = obj.content["oVariable"]
        response=onyx_trg.createVariable(id = obj.content["trg_id"], code=data["code"], name=data["name"], description=data["description"],
                                oConnectionId=conn_id,
                                oProjectId=id, oVariableType=data["oVariableType"], tenantId=tenant_id,
                                query=data["query"], value=data["value"])
    return response
