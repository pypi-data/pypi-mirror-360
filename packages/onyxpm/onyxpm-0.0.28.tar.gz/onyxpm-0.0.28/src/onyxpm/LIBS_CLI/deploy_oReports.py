import json
from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_get_connection import cli_get_connection_report
from LIBS_CLI.deploy_oWidgets import deploy_oWidgets


def deploy_oReports(onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src : NxTenant, tenant_trg : NxTenant, source_id, target_id, script_type,object_name):

    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type, name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type, name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)

    id = str(target_id)

    for obj in comp.componants:

        if "oReport" in obj.content and obj.action_required == 'U' or obj.action_required == 'C':
            data = obj.content["oReport"]
            if data["configuration"] is not None:
                configuration= json.loads(data["configuration"])
                for config in configuration:
                    # Call replace_widget() function to get the new values
                    new_widgetId = replace_widget(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id,
                                             source_widget_id=config["id"])

                    # Update the values in the config dictionary
                    config["id"] = new_widgetId["widget"]

                    config["inputs"]["widgetId"] = new_widgetId["widget"]
                    config["inputs"]["reportId"] = obj.content["trg_id"]

                    i=0
                    for filter in config["filters"]:
                        # Call cli_get_connection_report() to get the new connection ID
                        if filter["oConnectionId"] is not None:
                            new_connection_id = cli_get_connection_report(filter["oConnectionId"], data, target_id, onyx_src, onyx_trg)
                        else:
                            new_connection_id=None
                        # Update the oConnectionId in the filter
                        filter["oConnectionId"] = new_connection_id
                        filter["id"] = new_widgetId["filters"][i]
                        i+=1

            #4. Deploy_report
            new_configuration=json.dumps(configuration)
            onyx_trg.createReport(id=obj.content["trg_id"], name=data["name"], oProjectId=id,documentation=data["documentation"],configuration=new_configuration)
def get_widget_name_from_id(onyx_src: NxOnyxApi, source_widget_id):
    data = onyx_src.getWidget(source_widget_id)
    return data["oWidget"]["name"]


def replace_widget(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id,source_widget_id):
    # Call function to get widget name from source widget ID
    widget_name = get_widget_name_from_id(onyx_src, source_widget_id)
    response = deploy_oWidgets(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "WIDGET", widget_name)
    return response


