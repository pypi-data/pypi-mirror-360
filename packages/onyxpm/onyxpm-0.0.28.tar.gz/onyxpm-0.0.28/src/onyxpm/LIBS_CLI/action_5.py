from LIBS_CLI.exist_tenantName import exist_tenantname
from LIBS_CLI.get_envconf import get_envconf
from LIBS_CLI.list_project import list_project
from rich.console import Console


def action_5(tenant):
    console = Console()
    if exist_tenantname(tenantname=tenant) == True:
        i = 1
        for element in list_project(tenant=tenant):
            console.print(str(i) + ' ' + element, style="yellow")
            i += 1
    else:

        console.print("Please configure the tenant parameters before executing this command.", style="red")
