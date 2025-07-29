from CLASSES import NxOnyxApi


def cli_get_id_sqlScript(script_name,id,onyx_trg: NxOnyxApi):

    get_sqlScripts = onyx_trg.getSqlScriptsByProject(id)

    for element in get_sqlScripts["items"]:
        if element["osqlScript"]["name"] == script_name:
            sqlScript_id = element["osqlScript"]["id"]
            return sqlScript_id

def cli_get_id_shellScript(script_name,id,onyx_trg: NxOnyxApi):

    get_shellScripts = onyx_trg.getShellScriptsByProject(id)

    for element in get_shellScripts["items"]:
        if element["oShellScript"]["name"] == script_name:
            shellScript_id = element["oShellScript"]["id"]
            return shellScript_id

def cli_get_id_notification(script_name,id,onyx_trg: NxOnyxApi):

    get_notifications = onyx_trg.getNotificationsByProject(id)

    for element in get_notifications["items"]:
        if element["oNotification"]["name"] == script_name:
            notification_id = element["oNotification"]["id"]
            return notification_id

def cli_get_id_form(script_name,id,onyx_trg: NxOnyxApi):
    get_form = onyx_trg.getFormsByProject(id)

    for element in get_form["items"]:
        if element["oForm"]["technicalName"] == script_name:
            form_id = element["oForm"]["id"]
            return form_id