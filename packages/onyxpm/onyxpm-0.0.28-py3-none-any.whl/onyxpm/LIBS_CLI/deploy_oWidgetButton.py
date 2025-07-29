import re
from CLASSES import NxOnyxApi, NxTenant
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_get_connection import cli_get_connection_widget, cli_get_connection_name
from LIBS_CLI.cli_get_info import cli_get_oWorkflowId, cli_get_oSqlScriptId, cli_get_sql_name, \
    cli_get_workflow_name
from LIBS_CLI.deploy_oConnections import deploy_oConnections
from LIBS_CLI.deploy_oSqlScripts import deploy_oSqlScripts
from LIBS_CLI.deploy_oVariables import deploy_oVariables
from LIBS_CLI.deploy_oWorkFlows import deploy_oWorkFlows


def deploy_oWidgetButton(onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg : NxTenant, source_id, target_id,  script_type,object_name, newWidgetId,oldWidgetId):

    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type, name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type, name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)
    response = None
    lst=[]
    for obj in comp.componants:
        response=obj.content["trg_id"]
        if "oWButton" in obj.content and (obj.action_required == 'U' or obj.action_required == 'C'):
            data = obj.content["oWButton"]

            # GET WORKFLOW ID
            if data["oWorkflowId"] is not None:
                object_name=cli_get_workflow_name(onyx_src, obj.content["oWButton"]["oWorkflowId"])
                workflow_id = cli_get_oWorkflowId(obj.content["oWButton"], target_id, onyx_src, onyx_trg)
                if workflow_id is None:
                    workflow_id = deploy_oWorkFlows(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id,
                                                    "WORKFLOW", object_name)
            else:
                workflow_id = data["oWorkflowId"]

            # GET SQL_SCRIPT ID
            if data["osqlScriptId"] is not None:
                object_name = cli_get_sql_name(onyx_src, obj.content["oWButton"]["osqlScriptId"])
                script_id = cli_get_oSqlScriptId(obj.content["oWButton"], target_id, onyx_src, onyx_trg)
                if script_id is None:
                    script_id = deploy_oSqlScripts(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id,
                                                    "SQL_SCRIPT", object_name)
            else:
                script_id = data["osqlScriptId"]

            if oldWidgetId==data["oWidgetId"]:


                response=onyx_trg.createWidgetRowButton(id=obj.content["trg_id"],actionType=data["actionType"], configuration=data["configuration"],
                                               description=data["description"],
                                               name=data["name"], oSqlScriptId=script_id, oWidgetId=newWidgetId,
                                               oWorkflowId=workflow_id)
                lst.append(response)
    return response