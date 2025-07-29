from LIBS_BUS import find_onyx_project
from LIBS_CLI import cli_create_tenant, cli_connect_api


def check_project_existence(source_tenant, target_tenant, project):
    status=True

    tenant_src = cli_create_tenant(source_tenant)
    onyx_src = cli_connect_api(tenant_src)
    # Check if the project exists in the source tenant
    project_id_source = find_onyx_project(onyx_src, project)


    tenant_trg = cli_create_tenant(target_tenant)
    onyx_trg = cli_connect_api(tenant_trg)
    # Check if the project exists in the source tenant
    project_id_target = find_onyx_project(onyx_trg, project)


    if project_id_source is None:
        print(f"Project '{project}' does not exist in the source tenant '{source_tenant}'.")
        status= False

    if project_id_target is None:
        print(f"Project '{project}' does not exist in the target tenant '{target_tenant}'.")
        status= False

    return status