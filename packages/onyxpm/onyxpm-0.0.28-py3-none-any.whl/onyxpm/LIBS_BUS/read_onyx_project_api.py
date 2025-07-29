from alive_progress import alive_bar
from CLASSES.NxOnyxApi import NxOnyxApi
from CLASSES.NxProject import NxProject
from CLASSES.NxComponant import NxComponant

def read_onyx_project_api(onyx: NxOnyxApi, id, tenant_name,object,name):
    #illegal_characters = ["#","%","&","{","}","\\","<",">","*","?","/","$"," ","!","'","""""",":","@","+","`", "|", "="]
    #illegal_characters = """#%&{}\\<>*?/$ !'":@+,`|="""
    illegal_characters = ""
    exported_project = NxProject("", "", "", [])
    exported_project.id = id
    exported_project.json = onyx.getProject(id)
    exported_project.name = exported_project.json["oProject"]["name"]
    print("Downloading project \"{}\" from tenant \"{}\"".format(exported_project.name, tenant_name))

    if object=="ALL":
        i=12
    else:
        i=1

    with alive_bar(i) as bar:
        if object.upper()=="CONNECTION" or object=="ALL":
            for obj in onyx.getConnectionsByProject(id):
                if obj["oConnection"]["shortName"]==name or name == "ALL":
                    component = NxComponant("connection", obj["oConnection"]["shortName"].translate(str.maketrans('', '', illegal_characters)), onyx.getConnection(obj["oConnection"]["id"]), "", "")
                    exported_project.componants.append(component)
            bar()

        if object.upper() == "FILE_PROVIDER" or object=="ALL":
            for obj in onyx.getFileProvidersByProject(id):
                if obj["oFileProvider"]["name"] == name or name == "ALL":
                    component = NxComponant("fileprovider", obj["oFileProvider"]["name"].translate(str.maketrans('', '', illegal_characters)), onyx.getFileProvider(obj["oFileProvider"]["id"]), "", "")
                    exported_project.componants.append(component)
            bar()

        if object.upper() == "NOTIFICATION" or object=="ALL":
            for obj in onyx.getNotificationsByProject(id)["items"]:
                if obj["oNotification"]["name"] == name or name == "ALL":
                    component = NxComponant("notification", obj["oNotification"]["name"].translate(str.maketrans('', '', illegal_characters)), onyx.getNotification(obj["oNotification"]["id"]), "", "")
                    exported_project.componants.append(component)
            bar()

        if object.upper() == "REPORT" or object=="ALL":
            for obj in onyx.getReportsByProject(id)["items"]:
                if obj["oReport"]["name"] == name or name == "ALL":
                    component = NxComponant("report", obj["oReport"]["name"].translate(str.maketrans('', '', illegal_characters)), onyx.getReport(obj["oReport"]["id"]), "", "")
                    exported_project.componants.append(component)
            bar()

        if object.upper() == "SHELL_SCRIPT" or object=="ALL":
            for obj in onyx.getShellScriptsByProject(id)["items"]:
                if obj["oShellScript"]["name"] == name or name == "ALL":
                    component = NxComponant("shellscript", obj["oShellScript"]["name"].translate(str.maketrans('', '', illegal_characters)), onyx.getShellScript(obj["oShellScript"]["id"]), "", "")
                    exported_project.componants.append(component)

            bar()

        if object.upper() == "SQL_SCRIPT" or object=="ALL":

            for obj in onyx.getSqlScriptsByProject(id)["items"]:
                if obj["osqlScript"]["name"] == name or name == "ALL":
                    if obj["osqlScript"]["oConnectionId"] is not None:
                        oConnectionName=onyx.getConnection(obj["osqlScript"]["oConnectionId"])["oConnection"]["shortName"]
                    else:
                        oConnectionName=""
                    data= onyx.getSqlScript(obj["osqlScript"]["id"])
                    data["osqlScript"]["oConnectionName"]=oConnectionName
                    component = NxComponant("sqlscript", obj["osqlScript"]["name"].translate(str.maketrans('', '', illegal_characters)), data, "", "")
                    exported_project.componants.append(component)
            bar()

        if object.upper() == "VARIABLE" or object=="ALL":
            for obj in onyx.getVariablesByProject(id)["items"]:
                if obj["oVariable"]["code"] == name or name == "ALL":
                    onyx.getVariable(obj["oVariable"]["id"])
                    component = NxComponant("variable", obj["oVariable"]["code"].translate(str.maketrans('', '', illegal_characters)), onyx.getVariable(obj["oVariable"]["id"]), "", "")
                    exported_project.componants.append(component)
            bar()

        if object.upper() == "SCHEDULES" or object=="ALL":
            for obj in onyx.getSchedulesByProject(id)["items"]:
                if obj["oSchedule"]["name"] == name or name == "ALL":
                    component = NxComponant("schedules", obj["oSchedule"]["name"].translate(str.maketrans('', '', illegal_characters)), onyx.getSchedule(obj["oSchedule"]["id"]), "", "")
                    exported_project.componants.append(component)
            bar()

        if object.upper() == "FORM" or object=="ALL":
            for obj in onyx.getFormsByProject(id)["items"]:
                if obj["oForm"]["technicalName"] == name or name == "ALL":

                    component = NxComponant("form", obj["oForm"]["technicalName"].translate(str.maketrans('', '', illegal_characters)), onyx.getForm(obj["oForm"]["id"]), "", "")
                    exported_project.componants.append(component)
                    for col in onyx.getFormColumns(obj["oForm"]["id"])["items"]:
                        col['oFormColumn']['oFormId']=obj["oForm"]["id"]
                        component = NxComponant("form_column", (obj["oForm"]["technicalName"] + "$$" + col["oFormColumn"]["technicalName"]).translate(str.maketrans('', '', illegal_characters)), col, "", "")
                        exported_project.componants.append(component)
            bar()

        if object.upper() == "WORKFLOW" or object=="ALL":
            for obj in onyx.getWorkflowsByProject(id)["items"]:
                if obj["oWorkflow"]["name"] == name or name == "ALL":
                    component = NxComponant("workflow", obj["oWorkflow"]["name"].translate(str.maketrans('', '', illegal_characters)), onyx.getWorkflow(obj["oWorkflow"]["id"]), "", "")
                    exported_project.componants.append(component)
                    for step in onyx.getWorkflowSteps(obj["oWorkflow"]["id"])["items"]:
                        step["oWorkflowStep"]['oWorkflowId']=obj['oWorkflow']['id']
                        component = NxComponant(object_type="workflow_step", primary_key=(obj["oWorkflow"]["name"] + "$$" + str(step["oWorkflowStep"]["stepOrder"])).translate(str.maketrans('', '', illegal_characters)),  content=step ,action_required="",list_of_diff="")
                        exported_project.componants.append(component)
            bar()

        if object.upper() == "DATAPIPELINE" or object=="ALL":
            for obj in onyx.getPipelinesByProject(id)["items"]:
                if obj["name"] == name or name == "ALL":
                    dataPipeline={"oDatapipeline":onyx.getPipeline(obj["id"])}
                    component = NxComponant("pipeline", obj["name"].translate(str.maketrans('', '', illegal_characters)), dataPipeline, "", "")
                    exported_project.componants.append(component)
                    for col in onyx.getPipelineColumnsIncluded(obj["id"])["items"]:
                        dataColumnPipeline={"oColumnDatapipeline":col}
                        component = NxComponant("pipeline_column", (obj["name"] + "$$" + col["destinationColumnName"]).translate(str.maketrans('', '', illegal_characters)), dataColumnPipeline, "", "")
                        exported_project.componants.append(component)
            bar()

        if object.upper() == "WIDGET" or object=="ALL":
            for obj in onyx.getWidgetsByProject(id)["items"]:
                if obj["oWidget"]["name"] == name or name == "ALL":

                    component = NxComponant("widget", obj["oWidget"]["name"].translate(str.maketrans('', '', illegal_characters)), onyx.getWidget(obj["oWidget"]["id"]), "", "")
                    exported_project.componants.append(component)
                    for filter in onyx.getWidgetFilters(obj["oWidget"]["id"])["items"]:

                        datafilter={"oWFilter":filter}
                        component = NxComponant("widget_filter", (obj["oWidget"]["name"] + "$$" + filter["name"]).translate(str.maketrans('', '', illegal_characters)), datafilter, "", "")
                        exported_project.componants.append(component)

                    for button in onyx.getWidgetRowButtons(obj["oWidget"]["id"])["items"]:

                        databutton={"oWButton":button}
                        component = NxComponant("widget_button", (obj["oWidget"]["name"] + "$$" + button["name"]).translate(str.maketrans('', '', illegal_characters)), databutton, "", "")
                        exported_project.componants.append(component)

            bar()

    return exported_project