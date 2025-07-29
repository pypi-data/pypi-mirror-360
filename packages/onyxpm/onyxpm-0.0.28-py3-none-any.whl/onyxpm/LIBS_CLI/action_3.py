from LIBS_BUS.find_onyx_project import find_onyx_project
from LIBS_CLI.cli_connect_api import cli_connect_api
from LIBS_CLI.cli_create_tenant import cli_create_tenant
from LIBS_CLI.deploy_oConnections import deploy_oConnections
from LIBS_CLI.deploy_oDataPipelines import deploy_oDataPipelines
from LIBS_CLI.deploy_oFileProviders import deploy_oFileProviders
from LIBS_CLI.deploy_oForms import deploy_oForms
from LIBS_CLI.deploy_oNotifications import deploy_oNotifications
from LIBS_CLI.deploy_oReports import deploy_oReports
from LIBS_CLI.deploy_oShellScripts import deploy_oShellScripts
from LIBS_CLI.deploy_oSqlScripts import deploy_oSqlScripts
from LIBS_CLI.deploy_oVariables import deploy_oVariables
from LIBS_CLI.deploy_oWidgets import deploy_oWidgets
from LIBS_CLI.deploy_oWorkFlows import deploy_oWorkFlows
from rich.console import Console


def action_3(script_type, object_name, project, source_tenant, target_tenant):
    console = Console()

    #Creating tenants competcs
    tenant_src=cli_create_tenant(source_tenant)
    tenant_trg=cli_create_tenant(target_tenant)

    #Creating API compects
    onyx_src=cli_connect_api(tenant_src)
    onyx_trg=cli_connect_api(tenant_trg)

    #GET target id
    source_id=find_onyx_project(onyx_src, project)
    target_id=find_onyx_project(onyx_trg, project)

    #Creating project for comparaison
    component_list=["CONNECTION","NOTIFICATION","DATAPIPELINE","FORM","SHELL_SCRIPT","SQL_SCRIPT","FILE_PROVIDER","VARIABLE","WORKFLOW","REPORT","WIDGET"]

    if script_type not in component_list:
        console.print("Component ",script_type," does not exist")
        console.print("Please select one component in the following list")
        for element in component_list:
            console.print(element)
    else:

        if script_type == "CONNECTION":
            deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "NOTIFICATION":
            deploy_oNotifications(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "DATAPIPELINE":
                deploy_oDataPipelines(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "FORM":
            deploy_oForms(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        """if script_type == "SCHEDULE":
            deploy_oSchedules(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type)"""

        if script_type == "SHELL_SCRIPT":
            deploy_oShellScripts(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "SQL_SCRIPT":
            deploy_oSqlScripts(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "FILE_PROVIDER":
            deploy_oFileProviders(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "VARIABLE":
            deploy_oVariables(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "WORKFLOW":
            deploy_oWorkFlows(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "REPORT":
            deploy_oReports(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)

        if script_type == "WIDGET":
            deploy_oWidgets(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, object_name)





