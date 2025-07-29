import re
from CLASSES.NxOnyxApi import NxOnyxApi
from CLASSES.NxTenant import NxTenant
from LIBS_BUS.compare_onyx_projects import compare_onyx_projects
from LIBS_BUS.read_onyx_project_api import read_onyx_project_api
from LIBS_CLI.cli_get_connection import cli_get_connection_name
from LIBS_CLI.cli_get_connection import cli_get_connection_widget
from LIBS_CLI.deploy_oConnections import deploy_oConnections
from LIBS_CLI.deploy_oVariables import deploy_oVariables


def deploy_oWidgetFilter(onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg : NxTenant, source_id, target_id, script_type,object_name,newWidgetId,oldWidgetId):
    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type, name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type, name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)
    response=None
    lst=[]

    for obj in comp.componants:
        if "oWFilter" in obj.content:
            response = obj.content["trg_id"]
            if obj.action_required == 'U' or obj.action_required == 'C':

                data = obj.content["oWFilter"]

                conn_id=data["oConnectionId"]
                if data["oConnectionId"] is not None:
                    conn_id = cli_get_connection_widget(data["oConnectionId"], target_id, onyx_src, onyx_trg)
                    if conn_id is None:
                        object_name = cli_get_connection_name(data["oConnectionId"], onyx_src)
                        conn_id = deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id,
                                                      "CONNECTION", object_name)

                if oldWidgetId==data["oWidgetId"]:

                    response=onyx_trg.createWidgetFilter(id=obj.content["trg_id"],name=data["name"], description=data["description"],
                                        oConnectionId=conn_id,
                                        oWidgetId=newWidgetId, query=data["query"], type=data["type"])

            lst.append(response)
    return lst