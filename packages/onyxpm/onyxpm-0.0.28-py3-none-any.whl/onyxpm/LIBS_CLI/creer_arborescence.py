import ast
import astor
import json
import os
import urllib3
from CLASSES.NxOnyxApi import NxOnyxApi
from alive_progress import alive_bar
from urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

def creer_arborescence(donnees,onyx_src:NxOnyxApi, chemin_parent):
    illegal_characters = ["#","%","&","{","}","\\","<",">","*","?","/","$"," ","!","'","""""",":","@","+","`", "|", "=",'"']
    for element in donnees:
        if element.get('detailType') == 'project':
            if element["detailType"] == 'project':
                id = element["projectId"]
                print("Downloading project : ", element["name"])
                project_name = element["name"].rstrip()
                project_name = ''.join([char for char in project_name if char not in illegal_characters])
                path2 = os.path.join(chemin_parent, project_name)
                os.mkdir(path2)

                with alive_bar(11) as bar:
                    # Checking if oConnection directory already exists
                    path3 = os.path.join(path2, "oConnection")
                    if not os.path.exists(path3):
                        os.mkdir(path3)

                        # Downloading connections only if they haven't been downloaded before
                        for obj in onyx_src.getConnectionsByProject(id):
                            connection_name = ''.join(
                                [char for char in obj["oConnection"]['name'] if char not in illegal_characters])
                            json_filename = connection_name + ".json"
                            path4 = os.path.join(path3, json_filename)

                            with open(path4, "w", encoding="utf-8") as outfile:
                                outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                    bar()

                    path3 = os.path.join(path2, "oShellScript")
                    os.mkdir(path3)

                    for obj in onyx_src.getShellScriptsByProject(id)["items"]:
                        path4 = os.path.join(path3, ''.join(
                            [char for char in obj["oShellScript"]['name'] if char not in illegal_characters]))
                        os.mkdir(path4)
                        with open(path4 + "/configuration.json", "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                        data = onyx_src.getShellScript(obj["oShellScript"]['id'])

                        if obj["oShellScript"]['type']==0:
                            ext=".txt"
                        else:
                            ext=".py"
                        if data["oShellScript"]["script"] is None:
                            to_write=''
                        else:
                            to_write =data["oShellScript"]["script"]

                        with open(path4 + "/" +obj["oShellScript"]['name']+ext, "w", encoding="utf-8") as outfile:
                            outfile.write(to_write)

                            # Modify this section to read and write the script without modification
                            if ext == ".py":
                                with open(path4 + "/" + obj["oShellScript"]['name'] + ext, "r",
                                          encoding="utf-8") as infile:
                                    script_contents = infile.read()

                                # Parse the script to maintain original formatting
                                parsed_script = ast.parse(script_contents)

                                # Use astor to unparse the AST
                                formatted_script = astor.to_source(parsed_script)

                                with open(path4 + "/" + obj["oShellScript"]['name'] + ext, "w",
                                          encoding="utf-8") as outfile:
                                    outfile.write(formatted_script)
                    bar()

                    path3 = os.path.join(path2, "oFileProvider")
                    os.mkdir(path3)

                    for obj in onyx_src.getFileProvidersByProject(id):
                        provider_name = ''.join(
                            [char for char in obj["oFileProvider"]['name'] if char not in illegal_characters])
                        json_filename = provider_name + ".json"
                        path4 = os.path.join(path3, json_filename)

                        with open(path4, "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                    bar()

                    path3 = os.path.join(path2, "oNotification")
                    os.mkdir(path3)

                    for obj in onyx_src.getNotificationsByProject(id)["items"]:
                        notification_name = ''.join(
                            [char for char in obj["oNotification"]['name'] if char not in illegal_characters])
                        json_filename = notification_name + ".json"
                        path4 = os.path.join(path3, json_filename)

                        with open(path4, "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                    bar()

                    path3 = os.path.join(path2, "oReport")
                    os.mkdir(path3)

                    reports_response = onyx_src.getReportsByProject(id)["items"]  # Get the list of reports directly

                    for report_item in reports_response:
                        report_id = report_item["oReport"]["id"]  # Extract the ID of the report
                        report_name = ''.join(
                            [char for char in report_item["oReport"]['name'] if char not in illegal_characters])
                        json_filename = report_name + ".json"
                        path4 = os.path.join(path3, json_filename)

                        # Get detailed information about the report using getReportForEdit API
                        detailed_report_info = onyx_src.getReportForEdit(report_id)

                        # Create a JSON file for each report with detailed information
                        with open(path4, "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(detailed_report_info, ensure_ascii=False, indent=4))

                    bar()

                    path3 = os.path.join(path2, "osqlScript")
                    os.mkdir(path3)

                    for obj in onyx_src.getSqlScriptsByProject(id)["items"]:
                        path4 = os.path.join(path3, ''.join(
                            [char for char in obj["osqlScript"]['name'] if char not in illegal_characters]))
                        os.mkdir(path4)
                        with open(path4 + "/configuration.json", "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                        data = onyx_src.getSqlScript(obj["osqlScript"]['id'])
                        if data["osqlScript"]["query"] is None:
                            to_write = ''
                        else:
                            to_write = data["osqlScript"]["query"]

                        # Remove extra lines from the SQL script
                        formatted_script = "\n".join(line.strip() for line in to_write.splitlines())

                        with open(path4 + '/' + obj["osqlScript"]['name'] + ".sql", "w", encoding="utf-8") as outfile:
                            outfile.write(formatted_script)

                    bar()

                    path3 = os.path.join(path2, "oVariable")
                    os.mkdir(path3)

                    for obj in onyx_src.getVariablesByProject(id)["items"]:
                        varibale_name = ''.join(
                            [char for char in obj["oVariable"]['name'] if char not in illegal_characters])
                        json_filename = varibale_name + ".json"
                        path4 = os.path.join(path3, json_filename)

                        with open(path4, "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                    bar()

                    path3 = os.path.join(path2, "oForm")
                    os.mkdir(path3)

                    for obj in onyx_src.getFormsByProject(id)["items"]:
                        path4 = os.path.join(path3, ''.join([char for char in obj["oForm"]['technicalName'] if char not in illegal_characters]))
                        os.mkdir(path4)

                        # From Columns
                        path_formColumns = os.path.join(path4, "column.json")
                        with open(path_formColumns, "w", encoding="utf-8") as outfile:
                            form_column = onyx_src.getFormColumns(obj["oForm"]["id"])["items"]
                            outfile.write(json.dumps(form_column, ensure_ascii=False, indent=4))


                        with open(path4 + "/configuration.json", "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                    bar()

                    path3 = os.path.join(path2, "oWorkflow")
                    os.mkdir(path3)

                    for obj in onyx_src.getWorkflowsByProject(id)["items"]:
                        path4 = os.path.join(path3, ''.join([char for char in obj["oWorkflow"]['name'] if char not in illegal_characters]))
                        os.mkdir(path4)

                        # Workflow Steps
                        path_workFlowSteps = os.path.join(path4, "workflow_steps.json")
                        with open(path_workFlowSteps, "w", encoding="utf-8") as outfile:
                            workFlowSteps = onyx_src.getWorkflowSteps(obj["oWorkflow"]["id"])["items"]
                            outfile.write(json.dumps(workFlowSteps, ensure_ascii=False, indent=4))

                        with open(path4 + "/configuration.json", "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                    bar()

                    path3 = os.path.join(path2, "oPipeline")
                    os.mkdir(path3)

                    for obj in onyx_src.getPipelinesByProject(id)["items"]:
                        path4 = os.path.join(path3,''.join([char for char in obj['name'] if char not in illegal_characters]))
                        os.mkdir(path4)

                        # Pipeline Columns Included
                        pipeline_columns_inc = onyx_src.getPipelineColumnsIncluded(obj["id"])["items"]
                        path_pipelineColumns_Inc = os.path.join(path4, "column_included.json")
                        with open(path_pipelineColumns_Inc, "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(pipeline_columns_inc, ensure_ascii=False, indent=4))

                        # Pipeline Columns Excluded
                        pipeline_columns_exc = onyx_src.getPipelineColumnsExcluded(obj["id"])["items"]
                        path_pipelineColumns_exc = os.path.join(path4, "column_excluded.json")
                        with open(path_pipelineColumns_exc, "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(pipeline_columns_exc, ensure_ascii=False, indent=4))

                        with open(path4 + "/configuration.json", "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))
                    bar()

                    path3 = os.path.join(path2, "oWidget")
                    os.mkdir(path3)

                    for obj in onyx_src.getWidgetsByProject(id)["items"]:
                        widget_name = ''.join(
                            [char for char in obj["oWidget"]['name'] if char not in illegal_characters])
                        path4 = os.path.join(path3, widget_name)
                        os.mkdir(path4)

                        # Widget Filter
                        path_filter = os.path.join(path4, "filter.json")
                        with open(path_filter, "w", encoding="utf-8") as outfile:
                            widget_filter = onyx_src.getWidgetFilters(obj["oWidget"]["id"])["items"]
                            outfile.write(json.dumps(widget_filter, ensure_ascii=False, indent=4))

                        # Widget Button
                        path_button = os.path.join(path4, "button.json")
                        with open(path_button, "w", encoding="utf-8") as outfile:
                            widget_buttons = onyx_src.getWidgetRowButtons(obj["oWidget"]["id"])["items"]
                            outfile.write(json.dumps(widget_buttons, ensure_ascii=False, indent=4))

                        # Widget Configuration
                        path_config = os.path.join(path4, "config.json")
                        with open(path_config, "w", encoding="utf-8") as outfile:
                            outfile.write(json.dumps(obj, ensure_ascii=False, indent=4))

                    bar()
        else:
            chemin_element = os.path.join(chemin_parent, element['name'])
            os.makedirs(chemin_element, exist_ok=True, mode=0o777)
            creer_arborescence(element.get('subproject', []), onyx_src, chemin_element)