import os
import shutil
from CLASSES.EnvConfElement import EnvConfElement
from CLASSES.NxOnyxApi import NxOnyxApi
from CLASSES.NxTenant import NxTenant
from LIBS_CLI.update_envconf import update_envconf
from rich.console import Console


#new corrections
def action_1(tenant=None, tenantName=None, tenantDomain=None, tenantUsername=None, tenantPassword=None, tenantId=None):

    if tenant is not None:
        tenant=tenant.upper()
    if tenantName is not None:
        tenantName=tenantName.upper()

    dict= {"TENANT":tenant, "TENANTDOMAIN":tenantDomain,"TENANTID":tenantId,"TENANTNAME":tenantName,"TENANTUSERNAME":tenantUsername,"TENANTPASSWORD":tenantPassword}
    for key in dict:
        if dict[key]==None:
            if key =="TENANT":
                dict[key]=str(input("Enter "+ key +" : ")).upper()
            else:
                dict[key] = str(input("Enter " + key + " : "))

    try:
        tenant_dict = NxTenant(domain=dict["TENANTDOMAIN"], tenant_id=dict["TENANTID"],
                            tenant_name=dict["TENANTNAME"], username=dict["TENANTUSERNAME"],
                            password=dict["TENANTPASSWORD"])

        tenant_dict = NxOnyxApi(tenant_dict.domain, tenant_dict.username, tenant_dict.password, tenant_dict.tenant_id)
        print("Connection to source", dict["TENANTNAME"], "successful.")

        #conf_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../env.conf"))
        #conf_file_path = shutil.copy(conf_file_path, os.path.join(os.getcwd(), "env.conf"))
        conf_file_path = os.path.join(os.getcwd(), "env.conf")
        os.environ["conf_file_path"] = os.path.join(os.getcwd(), "env.conf")

        if not os.path.exists(conf_file_path) or os.getenv(dict["TENANT"] + "_TENANTNAME") is None:
            with open(conf_file_path, 'a+') as file:
                file.write('\n#' + dict["TENANT"].upper() + '\n')
                for Element in dict:
                    if Element != "TENANT":
                        file.write(dict["TENANT"] + "_" + str(Element) + '=' + str(dict[Element]) + '\n')
            print("New env.conf file created in the src folder.")
        else:
            for Element in dict:
                if Element != "tenant":
                    update_envconf(EnvConfElement(filename=conf_file_path, key=dict["TENANT"] + "_" + Element,
                                                value=dict[Element]))
            print("Tenant information updated in env.conf.")
        return conf_file_path

    except Exception as e:
        console = Console()
        console.print("Connection to tenant  impossible:" + str(e), style="red")