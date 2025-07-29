from CLASSES.NxProject import NxProject
from CLASSES.NxComponantAttributes import NxComponantAttributes
from LIBS_BUS.apply_transco import apply_transco

def compare_onyx_projects(project_pkg: NxProject, project_tnt: NxProject):
    project_result = NxProject(project_tnt.id, project_tnt.content, project_tnt.name, [])
    transco_matrix = []
    comparison_matrix = {
        "connection": NxComponantAttributes("oConnection", ["connectionType", "isWritable", "name", "documentation"]),
        "fileprovider": NxComponantAttributes("oFileProvider", ["connectionString", "containerName", "name", "organizationUnitId","type"]),
        "sqlscript": NxComponantAttributes("osqlScript", ["query", "oConnectionName","oConnectionId"]),
        "shellscript": NxComponantAttributes("oShellScript", ["packages", "script", "type","env","args"]),
        "notification": NxComponantAttributes("oNotification", ["type", "subject", "body", "recipients"]),
        "variable": NxComponantAttributes("oVariable", ["name", "description", "value", "query", "oVariableType", "oConnectionId"]),
        "pipeline": NxComponantAttributes("oDatapipeline", ["sourceConnectionId", "sourceConnectionType", "destinationConnectionId", "destinationConnectionType", "sourceTable", "destinationTable", "queryFilter"]),
        "pipeline_column": NxComponantAttributes("oColumnDatapipeline", ["oFlowId", "sourceColumnName", "destinationColumnDataType", "sourceCharacterMaximumLength", "sourceColumnNumericPrecision", "sourceColumnNumericScale", "sourceColumnDatatype", "ordinal"]),
        "form": NxComponantAttributes("oForm", ["displayedName", "documentation", "isActive","oConnectionId"]),
        "form_column": NxComponantAttributes("oFormColumn", ["displayedName", "type", "isNullable","displayOrder", "isDisplayed", "isDropDown", "dropDownQuery", "characterMaximumLength", "numericPrecision", "numericScale", "editorType", "editorConfiguration"]),
        "workflow": NxComponantAttributes("oWorkflow", ["oProjectId", "name","enableCrossProject", "emailSentOnError", "emailRecipients"]),
        "workflow_step": NxComponantAttributes("oWorkflowStep", ["name","jobType", "stepOrder", "isActive", "stopWorkflowOnError"]),
        "report": NxComponantAttributes("oReport", ["configuration", "name", "oProjectId", "documentation", "configuration"]),
        "widget": NxComponantAttributes("oWidget", ["query", "configuration", "oConnectionId", "oWorkflowId", "oFormId", "oFileProviderId", "type"]),
        "widget_filter": NxComponantAttributes("oWFilter", ["description", "query", "oConnectionId", "type", "value"]),
        "widget_button": NxComponantAttributes("oWButton", ["configuration", "actionType", "osqlScriptId"]),
        "schedules": NxComponantAttributes("oSchedule", ["name", "cronFormula", "isActive"])
    }

    for key, comp_attributes in comparison_matrix.items():
        for pkg_componant in project_pkg.componants:
            if pkg_componant.object_type == key:
                pkg_componant.content["trg_id"]=None
                object_exist = False
                for tnt_componant in project_tnt.componants:
                    if tnt_componant.object_type == key:
                        if pkg_componant.primary_key == tnt_componant.primary_key:
                            object_exist = True
                            matching_component = tnt_componant

                            if comp_attributes.json_object == None:
                                transco_matrix.append({"package_object_id": pkg_componant.content["id"], "tenant_object_id": tnt_componant.content["id"]})
                                pkg_componant.content["trg_id"]=tnt_componant.content["id"]
                            else:
                                transco_matrix.append({"package_object_id": pkg_componant.content[comp_attributes.json_object]["id"], "tenant_object_id": tnt_componant.content[comp_attributes.json_object]["id"]})
                                pkg_componant.content["trg_id"]=tnt_componant.content[comp_attributes.json_object]["id"]
                if object_exist:
                    diff = obj_diff(pkg_componant.content, matching_component.content, comp_attributes.json_object, comp_attributes.comparable_attributes, transco_matrix)
                    diff[:] = [objet for objet in diff if not objet.endswith("Id")]
                    if len(diff) > 0:
                        pkg_componant.action_required = "U"
                        pkg_componant.list_of_diff = ','.join(diff)
                    else:
                        pkg_componant.action_required = "N"
                else:
                    pkg_componant.action_required = "C"
                project_result.componants.append(pkg_componant)

    return project_result



def obj_diff(pkg, tnt, obj, tag_list, transco_matrix):
    res = []
    for tag in tag_list:
        if obj is None:
            val_pkg = apply_transco(transco_matrix, str(pkg[tag]))
            val_tnt = str(tnt[tag])
        else:
            val_pkg = apply_transco(transco_matrix, str(pkg[obj][tag]))
            val_tnt = str(tnt[obj][tag])
        if not val_pkg == val_tnt:

            res.append(tag)
    return res
