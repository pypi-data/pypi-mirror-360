from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS.compare_onyx_projects import compare_onyx_projects
from LIBS_BUS.read_onyx_project_api import read_onyx_project_api
from LIBS_CLI.cli_get_organisation_unit import cli_get_organisation_unit_name, cli_get_organisation_unit_id


def deploy_oFileProviders(onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src: NxTenant,
                      tenant_trg: NxTenant, source_id, target_id, script_type,name):

    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type,name=name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type,name=name)

    comp = compare_onyx_projects(project_src, project_tnt)
    response = None
    for obj in comp.componants:


        if "oFileProvider" in obj.content and obj.action_required == 'U' or obj.action_required == 'C':
            data = obj.content["oFileProvider"]
            ou_name = cli_get_organisation_unit_name(onyx_src, data["organizationUnitId"])
            ou_id = cli_get_organisation_unit_id(onyx_trg, ou_name)
            if ou_id is not None:
                response=onyx_trg.createFileProvider(id=obj.content["trg_id"],connectionString=data["connectionString"], containerName=data["containerName"],name=data["name"], organizationUnitId=ou_id, type=data["type"])

    return response
