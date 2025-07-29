from CLASSES.NxOnyxApi import NxOnyxApi
def cli_get_oWorkflowId(data,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):


    workflow_name=onyx_src.getWorkflow(data["oWorkflowId"])
    get_workflows = onyx_trg.getWorkflowsByProject(id)["items"]

    for element in get_workflows:

        if element["oWorkflow"]["name"] == workflow_name["oWorkflow"]["name"]:
            workflow_id = element["oWorkflow"]["id"]
            return workflow_id

def cli_get_oFormId(obj,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):
    data = onyx_src.getWidget(obj.content["oWidget"]["id"])
    data = data["oWidget"]
    form_name = onyx_src.getForm(data["oFormId"])
    get_forms = onyx_trg.getFormsByProject(id)

    for element in get_forms:
        if element["oForm"]["name"] == form_name["oForm"]["name"]:
            form_id = element["oForm"]["id"]
            return form_id

def cli_get_oFileProviderId(obj,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):
    data = onyx_src.getWidget(obj.content["oWidget"]["id"])
    data = data["oWidget"]
    FileProvider_name = onyx_src.getFileProvider(data["oFileProviderId"])
    get_FileProviders = onyx_trg.getFileProvidersByProject(id)

    for element in get_FileProviders:
        if element["oFileProvider"]["name"] == FileProvider_name["oFileProvider"]["name"]:
            FileProvider_id = element["oFileProvider"]["id"]
            return FileProvider_id

def cli_get_oSqlScriptId(data,id,onyx_src: NxOnyxApi, onyx_trg: NxOnyxApi):

    SqlScript_name = onyx_src.getSqlScript(data["osqlScriptId"])
    get_SqlScripts = onyx_trg.getSqlScriptsByProject(id)["items"]

    for element in get_SqlScripts:

        if element["osqlScript"]["name"] == SqlScript_name["osqlScript"]["name"]:
            SqlScript_id = element["osqlScript"]["id"]
            return SqlScript_id

def cli_get_workflow_name(onyx :NxOnyxApi,id):
    data=onyx.getWorkflow(id)["oWorkflow"]["name"]
    return data


def cli_get_fileprovider_name(onyx :NxOnyxApi,id):
    data=onyx.getFileProvider(id)["oFileProvider"]["name"]
    return data

def cli_get_form_name(onyx :NxOnyxApi,id):
    data=onyx.getForm(id)["oForm"]["name"]
    return data

def cli_get_sql_name(onyx :NxOnyxApi,id):
    data=onyx.getForm(id)["osqlScript"]["name"]
    return data