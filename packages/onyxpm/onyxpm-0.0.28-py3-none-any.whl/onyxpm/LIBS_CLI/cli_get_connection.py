from CLASSES.NxOnyxApi import NxOnyxApi

"""def cli_get_connection_sql(obj,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):

    data = onyx_src.getSqlScript(obj.content["osqlScript"]["id"])
    data = data["osqlScript"]
    connection_name=onyx_src.getConnection(data["oConnectionId"])
    get_connections = onyx_trg.getConnectionsByProject(id)

    for element in get_connections:
        if element["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            connection_id = element["oConnection"]["id"]
            return connection_id"""

"""def cli_get_connection_variable(obj,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):

    data = onyx_src.getVariable(obj.content["oVariable"]["id"])
    data = data["oVariable"]
    connection_name=onyx_src.getConnection(data["oConnectionId"])
    get_connections = onyx_trg.getConnectionsByProject(id)

    for element in get_connections:
        if element["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            connection_id = element["oConnection"]["id"]
            return connection_id"""
def cli_get_connection_variable(obj,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):

    data = onyx_src.getVariable(obj)
    data = data["oVariable"]
    connection_name=onyx_src.getConnection(data["oConnectionId"])
    get_connections = onyx_trg.getConnectionsByProject(id)

    for element in get_connections:
        if element["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            connection_id = element["oConnection"]["id"]
            return connection_id

def cli_get_connection_widget(data,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):
    connection_name=onyx_src.getConnection(data)
    get_connections = onyx_trg.getConnectionsByProject(id)

    for element in get_connections:
        if element["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            connection_id = element["oConnection"]["id"]
            return connection_id

def cli_get_connection_sql(obj,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):

    data = onyx_src.getSqlScript(obj)
    data = data["osqlScript"]
    connection_name=onyx_src.getConnection(data["oConnectionId"])
    print("sql", connection_name)
    get_connections = onyx_trg.getConnectionsByProject(id)

    for element in get_connections:
        if element["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            connection_id = element["oConnection"]["id"]
            return connection_id

def cli_get_connection_form(obj,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):

    data = onyx_src.getForm(obj)
    print("cli_get_connection_form",data)
    data = data["oForm"]
    connection_name=onyx_src.getConnection(data["oConnectionId"])
    print(connection_name)
    get_connections = onyx_trg.getConnectionsByProject(id)

    for element in get_connections:
        if element["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            connection_id = element["oConnection"]["id"]
            return connection_id

def cli_get_connection_name(id,onyx_src : NxOnyxApi):
    data=onyx_src.getConnection(id)
    return data["oConnection"]["shortName"]

def cli_get_connection_datapipeline(data,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):

    connection_name=onyx_src.getConnection(data)
    get_connections = onyx_trg.getConnectionsByProject(id)

    for element in get_connections:
        if element["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            connection_id = element["oConnection"]["id"]
            return connection_id


def cli_get_connection_report(obj, report_data, project_id, onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):
    # Get the report data from the source Onyx instance

    # Extract connection name from the report data
    connection_name = onyx_src.getConnection(obj)

    # Get connections associated with the project from the target Onyx instance
    target_connections = onyx_trg.getConnectionsByProject(project_id)

    # Iterate through connections to find a match based on connection name
    for connection in target_connections:
        if connection["oConnection"]["name"] == connection_name["oConnection"]["name"]:
            # Return the ID of the matching connection
            return connection["oConnection"]["id"]
