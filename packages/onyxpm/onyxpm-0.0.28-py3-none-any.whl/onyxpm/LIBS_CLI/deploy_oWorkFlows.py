from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_add_to_workflow import add_to_workflow_shellscript, add_to_workflow_sqlscript, add_to_workflow_notification

def deploy_oWorkFlows( onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg : NxTenant, source_id, target_id, script_type,object_name):
    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type,name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type,name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)

    new_workflow_id=None
    for obj in comp.componants:

        if "oWorkflow" in obj.content :#and ( obj.action_required == 'U' or obj.action_required == 'C') :
            new_workflow_id = obj.content["trg_id"]
            old_workflow_id=obj.content["oWorkflow"]["id"]

            new_workflow_id = create_oWorkFlows(obj, target_id, onyx_trg)
            if new_workflow_id is None:
                new_workflow_id = obj.content["trg_id"]
            for obj in comp.componants:
                if "oWorkflowStep" in obj.content :
                    if obj.content["oWorkflowStep"]["oWorkflowId"] == old_workflow_id:

                        if obj.content["oWorkflowStep"]["jobType"] == 1:
                            pass

                        if obj.content["oWorkflowStep"]["jobType"] == 2:
                            pass

                        if obj.content["oWorkflowStep"]["jobType"] == 3: #SQL SCRIPT
                            add_to_workflow_sqlscript(obj,onyx_src,onyx_trg,tenant_src,tenant_trg,source_id,target_id,new_workflow_id)

                        if obj.content["oWorkflowStep"]["jobType"] == 4: #SCRIPT_SHELL
                            add_to_workflow_shellscript(obj,onyx_src,onyx_trg,tenant_src,tenant_trg,source_id,target_id,new_workflow_id)

                        if obj.content["oWorkflowStep"]["jobType"] == 5:
                            pass

                        if obj.content["oWorkflowStep"]["jobType"] == 6:
                            add_to_workflow_notification(obj,onyx_src,onyx_trg,tenant_src,tenant_trg,source_id,target_id,new_workflow_id)
    return new_workflow_id
def create_oWorkFlows(obj, id, onyx_trg: NxOnyxApi):
    id = str(id)

    if "oWorkflow" in obj.content and obj.action_required == 'U' or obj.action_required == 'C':
        data = obj.content["oWorkflow"]
        response= onyx_trg.createWorkflow(id = obj.content["trg_id"],name=data["name"], oProjectId=id,
                                enableCrossProject=data["enableCrossProject"],
                                emailSentOnError=data["emailSentOnError"], emailRecipients=data["emailRecipients"])
        return response