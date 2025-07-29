import os
from CLASSES.NxOnyxApi import NxOnyxApi
from CLASSES.NxTenant import NxTenant
from rich.console import Console


def list_project(tenant):
    console = Console()
    project_connection = NxTenant(domain=os.environ[tenant +'_TENANTDOMAIN'], tenant_id=os.environ[tenant +'_TENANTID'],
                          tenant_name=os.environ[tenant +'_TENANTNAME'],
                          username=os.environ[tenant +'_TENANTUSERNAME'], password=os.environ[tenant+'_TENANTPASSWORD'])
    connection_str = NxOnyxApi(project_connection.domain, project_connection.username, project_connection.password, project_connection.tenant_id)
    project_details= connection_str.getTree()
    get_folders_list = []
    for element in project_details:
        if element['projectName'] not in get_folders_list and element['projectName'] is not None:
            get_folders_list.append(element['projectName'])
    return  get_folders_list


