import os
from CLASSES.NxOnyxApi import NxOnyxApi
from CLASSES.NxTenant import NxTenant
from LIBS_CLI.creer_arborescence import creer_arborescence
from LIBS_CLI.exist_tenantName import exist_tenantname
from LIBS_CLI.refactor_dict import refactor_dict
from rich.console import Console


def action_4(tenant,folder):
    console = Console()
    #DOWNLOAD
    new_folder=folder+'/'+tenant
    if os.path.exists(new_folder):
        #shutil.rmtree("TENANTS/SRC", onerror=on_rm_error)
        console.print("File named " + tenant + " already exist in " + folder, style="red")
    elif exist_tenantname(tenant)!=True:
        console.print("Tenant name "+tenant+" does not exist !", style="red")
    else:
        localRepositoryFolder = new_folder
        tenant_src = NxTenant(domain=os.environ[tenant + '_TENANTDOMAIN'], tenant_id=os.environ[tenant + '_TENANTID'],
                              tenant_name=os.environ[tenant + '_TENANTNAME'],
                              username=os.environ[tenant + '_TENANTUSERNAME'], password=os.environ[tenant + '_TENANTPASSWORD'])
        onyx_src = NxOnyxApi(tenant_src.domain, tenant_src.username, tenant_src.password, tenant_src.tenant_id)
        tree = onyx_src.getTree()

        dict=refactor_dict(tree)
        creer_arborescence(dict,onyx_src,localRepositoryFolder)


