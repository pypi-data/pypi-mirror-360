from CLASSES import NxOnyxApi
from LIBS_CLI.parameter_selector import paramter_selector


def transco_id(comp,id_src,onyx_src : NxOnyxApi,onyx_trg : NxOnyxApi,paramters):


    dl=paramter_selector(paramters)



    dict={"SQL_SCRIPT":{},"CONNECTION":{}}
    for obj in comp.componants:

        if "osqlScript" in obj and 1 in dl:
            data = onyx_src.getSqlScript(obj.content["osqlScript"]["id"])
            get_sql_scripts = onyx_trg.getSqlScriptsByProject(id)

            for element in get_sql_scripts["items"]:
                if element["osqlScript"]["name"] == data["name"]:
                    trg_id = element["osqlScript"]["id"]

                    dict["SQL_SCRIPT"][obj["id"]]=trg_id

        if "oConnection" in obj and 2 in dl:
            data = onyx_src.getConnection(id_src)
            get_connection = onyx_trg.getConnectionsByProject(id)

            for element in get_connection["items"]:
                if element["oConnection"]["name"] == data["name"]:
                    trg_id = element["oConnection"]["id"]

                    dict["CONNECTION"][obj["id"]] = trg_id
    return dict