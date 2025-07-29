import re
from CLASSES import NxTenant
from CLASSES.NxOnyxApi import NxOnyxApi
from LIBS_BUS import read_onyx_project_api, compare_onyx_projects
from LIBS_CLI.cli_get_connection import cli_get_connection_datapipeline, cli_get_connection_name
from LIBS_CLI.deploy_oConnections import deploy_oConnections
from LIBS_CLI.deploy_oPipelineColumns import deploy_oPipelineColumns
from LIBS_CLI.deploy_oVariables import deploy_oVariables



def deploy_oDataPipelines(onyx_src : NxOnyxApi, onyx_trg: NxOnyxApi, tenant_src, tenant_trg, source_id, target_id, script_type, object_name):


    project_src = read_onyx_project_api(onyx_src, source_id, tenant_name=(tenant_src.tenant_name), object=script_type, name=object_name)
    project_tnt = read_onyx_project_api(onyx_trg, target_id, tenant_name=(tenant_trg.tenant_name), object=script_type, name=object_name)
    comp = compare_onyx_projects(project_src, project_tnt)

    response=None

    for obj in comp.componants:
        response = obj.content["trg_id"]
        if "oDatapipeline" in obj.content:

            src_conn_id = cli_get_connection_datapipeline(obj.content["oDatapipeline"]["sourceConnectionId"], target_id, onyx_src, onyx_trg)
            if src_conn_id is None:
                object_name = cli_get_connection_name(obj.content["oDatapipeline"]["sourceConnectionId"], onyx_src)
                src_conn_id = deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id,
                                              "CONNECTION", object_name)

            trg_conn_id = cli_get_connection_datapipeline(obj.content["oDatapipeline"]["destinationConnectionId"], target_id,
                                                          onyx_src, onyx_trg)
            if trg_conn_id is None:
                object_name = cli_get_connection_name(obj.content["oDatapipeline"]["destinationConnectionId"], onyx_src)
                trg_conn_id = deploy_oConnections(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id,
                                                  "CONNECTION", object_name)

            response=create_oDatapipeline(obj, target_id, onyx_trg, src_conn_id, trg_conn_id)

            deploy_oPipelineColumns(onyx_src, onyx_trg, tenant_src, tenant_trg, source_id, target_id, script_type, obj.content['oDatapipeline']['name'],response)


    return response


def create_oDatapipeline(obj,target_id, onyx_trg, src_conn_id, trg_conn_id):
    response = obj.content["trg_id"]
    if "oDatapipeline" in obj.content and (obj.action_required == 'U' or obj.action_required == 'C'):

        data = obj.content["oDatapipeline"]
        response = onyx_trg.createPipeline(id=obj.content["trg_id"], oProjectId=target_id, SourceConnectionId=src_conn_id,
                                           SourceConnectionType=data["sourceConnectionType"],
                                           DestinationConnectionType=data["destinationConnectionType"],
                                           DestinationConnectionId=trg_conn_id, Name=data["name"],
                                           SourceTable=data["sourceTable"],
                                           DestinationTable=data["destinationTable"], QueryFilter=data["queryFilter"],
                                           NbColumns=data["nbColumns"],
                                           ActionIfTableExists=data["actionIfTableExists"],
                                           ActionIfTableNotExists=data["actionIfTableNotExists"],
                                           DesactivateIndexes=data["desactivateIndexes"],
                                           CreatePrimaryKey=data["createPrimaryKey"],
                                           CreateIndexes=data["createIndexes"],
                                           NumberOfSchedules=data["numberOfSchedules"])
        #mettre à jour le nom du pipeline
        onyx_trg.createPipeline(id=response, oProjectId=target_id, SourceConnectionId=src_conn_id,
                                SourceConnectionType=data["sourceConnectionType"],
                                DestinationConnectionType=data["destinationConnectionType"],
                                DestinationConnectionId=trg_conn_id, Name=data["name"],
                                SourceTable=data["sourceTable"],
                                DestinationTable=data["destinationTable"], QueryFilter=data["queryFilter"],
                                NbColumns=data["nbColumns"],
                                ActionIfTableExists=data["actionIfTableExists"],
                                ActionIfTableNotExists=data["actionIfTableNotExists"],
                                DesactivateIndexes=data["desactivateIndexes"],
                                CreatePrimaryKey=data["createPrimaryKey"],
                                CreateIndexes=data["createIndexes"],
                                NumberOfSchedules=data["numberOfSchedules"])
    return response