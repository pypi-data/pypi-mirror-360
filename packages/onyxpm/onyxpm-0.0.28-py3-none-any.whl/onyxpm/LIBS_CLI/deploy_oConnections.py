from CLASSES.NxTenant import NxTenant
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_get_organisation_unit import *


def deploy_oConnections(onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src: NxTenant,
                      tenant_trg: NxTenant, source_id, target_id, script_type,name):

    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name),
                                        object=script_type,name=name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name),
                                        object=script_type,name=name)
    comp = compare_onyx_projects(project_src, project_tnt)

    response=None
    for obj in comp.componants:
        response =obj.content["trg_id"]
        if "oConnection" in obj.content and obj.action_required == 'C' or obj.action_required == 'U':
            data = obj.content["oConnection"]
            ou_name = cli_get_organisation_unit_name(onyx_src, data["organizationUnitId"])
            ou_id = cli_get_organisation_unit_id(onyx_trg, ou_name)

            if ou_id is None:
                print("Cannot deploy connection object : ")
                print("Organisation Unit not found in target")
                exit()
            response=onyx_trg.createConnection(id=obj.content["trg_id"],connectionType=data["connectionType"],  isWritable=data["isWritable"],
                                               name=data["name"], organizationUnitId=ou_id, shortName=data["shortName"],documentation=data["documentation"])
            print("Please finish connection creation in Onyx in your target environement")

    return response
