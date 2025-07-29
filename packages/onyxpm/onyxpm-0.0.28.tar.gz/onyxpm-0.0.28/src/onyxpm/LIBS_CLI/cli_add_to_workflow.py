from CLASSES import NxOnyxApi
from CLASSES import NxTenant
from LIBS_CLI.cli_get_id import *
from LIBS_CLI.deploy_oNotifications import deploy_oNotifications
from LIBS_CLI.deploy_oShellScripts import deploy_oShellScripts
from LIBS_CLI.deploy_oSqlScripts import deploy_oSqlScripts


def add_to_workflow_sqlscript(obj,onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg: NxTenant, source_id, target_id,new_workflow_id):
    jobid = obj.content["oWorkflowStep"]["objectId"]
    script_name = onyx_src.getSqlScript(jobid)["osqlScript"]["name"]
    scriptid = deploy_oSqlScripts(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "SQL_SCRIPT",
                                  script_name)
    if scriptid is None:
        scriptid = cli_get_id_sqlScript(script_name,target_id, onyx_trg)
    if obj.action_required == 'C':

        onyx_trg.createWorkflowStep(new_workflow_id, scriptid,
                                    obj.content["oWorkflowStep"]["stepOrder"],
                                    obj.content["oWorkflowStep"]["isActive"],
                                    obj.content["oWorkflowStep"]["stopWorkflowOnError"],
                                    obj.content["oWorkflowStep"]["jobType"])
    if obj.action_required == 'U':
        onyx_trg.createWorkflowStep(new_workflow_id, scriptid,
                                    obj.content["oWorkflowStep"]["stepOrder"],
                                    obj.content["oWorkflowStep"]["isActive"],
                                    obj.content["oWorkflowStep"]["stopWorkflowOnError"],
                                    obj.content["oWorkflowStep"]["jobType"])

def add_to_workflow_shellscript(obj,onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg: NxTenant, source_id, target_id,new_workflow_id):
    jobid = obj.content["oWorkflowStep"]["objectId"]
    script_name = onyx_src.getShellScript(jobid)["oShellScript"]["name"]

    scriptid = deploy_oShellScripts(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "SHELL_SCRIPT",
                                  script_name)
    if scriptid is None:
        scriptid = cli_get_id_shellScript(script_name, target_id , onyx_trg)
    if obj.action_required == 'C':
        onyx_trg.createWorkflowStep(new_workflow_id, scriptid,
                                    obj.content["oWorkflowStep"]["stepOrder"],
                                    obj.content["oWorkflowStep"]["isActive"],
                                    obj.content["oWorkflowStep"]["stopWorkflowOnError"],
                                    obj.content["oWorkflowStep"]["jobType"])
    if obj.action_required == 'U':
        onyx_trg.createWorkflowStep(new_workflow_id, scriptid,
                                    obj.content["oWorkflowStep"]["stepOrder"],
                                    obj.content["oWorkflowStep"]["isActive"],
                                    obj.content["oWorkflowStep"]["stopWorkflowOnError"],
                                    obj.content["oWorkflowStep"]["jobType"])

def add_to_workflow_notification(obj,onyx_src : NxOnyxApi, onyx_trg : NxOnyxApi, tenant_src : NxTenant, tenant_trg: NxTenant, source_id, target_id,new_workflow_id):
    jobid = obj.content["oWorkflowStep"]["objectId"]
    script_name = onyx_src.getNotification(jobid)["oNotification"]["name"]

    scriptid = deploy_oNotifications(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, "NOTIFICATION", script_name)
    if scriptid is None:
        scriptid = cli_get_id_notification(script_name, target_id , onyx_trg)
    if obj.action_required == 'C':
        onyx_trg.createWorkflowStep(new_workflow_id, scriptid,
                                    obj.content["oWorkflowStep"]["stepOrder"],
                                    obj.content["oWorkflowStep"]["isActive"],
                                    obj.content["oWorkflowStep"]["stopWorkflowOnError"],
                                    obj.content["oWorkflowStep"]["jobType"])
    if obj.action_required == 'U':
        onyx_trg.createWorkflowStep(new_workflow_id, scriptid,
                                    obj.content["oWorkflowStep"]["stepOrder"],
                                    obj.content["oWorkflowStep"]["isActive"],
                                    obj.content["oWorkflowStep"]["stopWorkflowOnError"],
                                    obj.content["oWorkflowStep"]["jobType"])
