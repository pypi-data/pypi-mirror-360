import re
from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_get_connection import cli_get_connection_widget, cli_get_connection_name
from LIBS_CLI.cli_get_info import cli_get_oWorkflowId, cli_get_oFormId, cli_get_oFileProviderId, \
    cli_get_workflow_name, cli_get_fileprovider_name, cli_get_form_name
from LIBS_CLI.deploy_oConnections import deploy_oConnections
from LIBS_CLI.deploy_oFileProviders import deploy_oFileProviders
from LIBS_CLI.deploy_oForms import deploy_oForms
from LIBS_CLI.deploy_oVariables import deploy_oVariables
from LIBS_CLI.deploy_oWidgetButton import deploy_oWidgetButton
from LIBS_CLI.deploy_oWidgetFilter import deploy_oWidgetFilter
from LIBS_CLI.deploy_oWorkFlows import deploy_oWorkFlows


def deploy_oWidgets(onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg : NxTenant, source_id, target_id, script_type, object_name):

    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type, name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type, name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)


    id = str(target_id)
    response = None
    list_of_filter = None
    list_of_button = None

    for obj in comp.componants:
        if obj.content.get('oWidget') is not None :

            data = obj.content["oWidget"]
            if data["oConnectionId"] is not None:
                connection_id=cli_get_connection_widget(data["oConnectionId"], id, onyx_src, onyx_trg)
                if connection_id is None:
                    object_name = cli_get_connection_name(obj.content["oWidget"]["oConnectionId"], onyx_src)
                    connection_id=deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "CONNECTION",object_name)
            else:
                connection_id=data["oConnectionId"]


            #GET WORKFLOW ID
            if data["oWorkflowId"] is not None:

                object_name = cli_get_workflow_name(onyx_src, data["oWorkflowId"])

                workflow_id=deploy_oWorkFlows(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "WORKFLOW", object_name)
            else:
                workflow_id = data["oWorkflowId"]


            #GET FILEPROVIDER ID
            if data["oFileProviderId"] is not None:
                object_name = cli_get_fileprovider_name(onyx_src, obj.content["oWidget"]["oFileProviderId"])
                fileprovider_id = deploy_oFileProviders(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "FILE_PROVIDER", object_name)
            else:
                fileprovider_id = data["oFileProviderId"]


            #GET FORM ID
            if data["oFormId"] is not None:
                object_name = cli_get_form_name(onyx_src, obj.content["oWidget"]["oFormId"])
                form_id = cli_get_oFormId(obj, id, onyx_src, onyx_trg)
                if form_id is None:
                    form_id=deploy_oForms(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type,object_name)
            else:
                form_id = data["oFormId"]

            matches = re.findall(r'(?<= \{\{)(.+?)(?=\}\})', obj.content["query"])
            if matches is not None:
                for element in matches:
                    deploy_oVariables(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, 'VARIABLE',
                                      element)

            response=create_oWidget(obj,id,onyx_trg, connection_id, workflow_id, form_id, fileprovider_id)
            list_of_filter=deploy_oWidgetFilter(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type,"ALL", response, data["id"])
            list_of_button=deploy_oWidgetButton(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type,"ALL", response, data["id"])

    return {"widget" : response, "filters" : list_of_filter, "buttons" : list_of_button}


def create_oWidget(obj, id, onyx_trg: NxOnyxApi, connection_id, workflow_id, form_id, fileprovider_id):
    id = str(id)
    response=obj.content["trg_id"]
    if "oWidget" in obj.content and obj.action_required == 'U' or obj.action_required == 'C':
        data = obj.content["oWidget"]

        response = onyx_trg.createWidget(id=obj.content["trg_id"], oProjectId=id, name=data["name"],
                                         description=data["description"], query=data["query"],
                                         configuration=data["configuration"], oConnectionId=connection_id,
                                         oWorkflowId=workflow_id, oFormId=form_id,
                                         oFileProviderId=fileprovider_id, type=data["type"])
    return response
