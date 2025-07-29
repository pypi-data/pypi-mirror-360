import re
from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.deploy_oVariables import deploy_oVariables



def deploy_oNotifications(onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src: NxTenant,
                      tenant_trg: NxTenant, source_id, target_id, script_type,name):
    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type, name=name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type, name=name)
    comp = compare_onyx_projects(project_src, project_tnt)

    target_id = str(target_id)
    response=None

    for obj in comp.componants:
        response=obj.content["trg_id"]
        if "oNotification" in obj.content and obj.action_required == 'U' or obj.action_required == 'C':

            data = obj.content["oNotification"]
            response= onyx_trg.createNotification(id=obj.content["trg_id"],name=data["name"], oProjectId=target_id, recipients=data["recipients"],
                                        subject=data["subject"], body=data["body"], type=data["type"], tenant=tenant_trg.tenant_id)

    return response

    # /!\ DESTINATAIRES NON MISE A JOUR

