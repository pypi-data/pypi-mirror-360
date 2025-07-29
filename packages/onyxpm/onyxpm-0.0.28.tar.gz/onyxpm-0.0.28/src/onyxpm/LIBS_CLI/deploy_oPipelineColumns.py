from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects


def deploy_oPipelineColumns(onyx_src : NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src, tenant_trg, source_id, target_id, script_type, object_name,
                         new_datapipeline_id):


    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name), object=script_type, name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name), object=script_type, name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)

    lst=[]
    for obj in comp.componants:

        if "oColumnDatapipeline" in obj.content and (obj.action_required == 'U' or obj.action_required == 'C'):
            data = obj.content["oColumnDatapipeline"]
            response = onyx_trg.createPipelineColumn(oFlowId=new_datapipeline_id, sourceColumnName=data["sourceColumnName"], destinationColumnName=data["destinationColumnName"],
                                    destinationColumnDataType=data["destinationColumnDataType"], sourceCharacterMaximumLength=data["sourceCharacterMaximumLength"],
                                    sourceColumnNumericPrecision=data["sourceColumnNumericPrecision"], sourceColumnNumericScale=data["sourceColumnNumericScale"],
                                     sourceColumnDatatype=data["sourceColumnDatatype"], ordinal=data["ordinal"],missingInSource=data["missingInSource"],id=obj.content["trg_id"])


