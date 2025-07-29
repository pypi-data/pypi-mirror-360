import click
from CLASSES.NxProject import NxProject
from LIBS_BUS.compare_onyx_projects import compare_onyx_projects
from LIBS_BUS.find_onyx_project import find_onyx_project
from LIBS_BUS.read_onyx_project_api import read_onyx_project_api
from LIBS_CLI.cli_connect_api import cli_connect_api
from LIBS_CLI.cli_create_tenant import cli_create_tenant
from rich.console import Console
from rich.table import Table


def action_2(source_tenant, target_tenant, project):
    console = Console()

    tenant_src = cli_create_tenant(source_tenant)
    onyx_src = cli_connect_api(tenant_src)
    tenant_trg = cli_create_tenant(target_tenant)
    onyx_trg = cli_connect_api(tenant_trg)


    id = find_onyx_project(onyx_src, project)
    project_src = read_onyx_project_api(onyx_src, id, tenant_name=(tenant_src.tenant_name), object="ALL",name="ALL")
    console.print("")
    id = find_onyx_project(onyx_trg, project)
    project_trg = read_onyx_project_api(onyx_trg, id, tenant_name=tenant_trg.tenant_name, object="ALL",name="ALL")
    #clear_screen()
    table = Table(title="Differences detected for the project: {}\n".format(project_trg.name))
    table.add_column("Type", style="cyan", justify="center")
    table.add_column("Name", style="magenta", justify="left")
    table.add_column("Action", style="magenta", justify="center")
    table.add_column("Details", style="magenta", justify="left")
    project_result: NxProject = compare_onyx_projects(project_src, project_trg)
    for componant in project_result.componants:

        if componant.action_required == "C":
            table.add_row(componant.object_type, componant.primary_key, "TO CREATE", "")
        if componant.action_required == "U":
            table.add_row(componant.object_type, componant.primary_key, "TO UPDATE",
                        "diverging field(s): {}".format(componant.list_of_diff))
    console.print(table)

