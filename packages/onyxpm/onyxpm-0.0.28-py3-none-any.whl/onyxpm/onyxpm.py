import click
import os
import warnings
from LIBS_CLI.action_5 import action_5
from LIBS_CLI.action_1 import action_1
from LIBS_CLI.check_project_existence import check_project_existence
from LIBS_CLI.cli_tenant_validation import cli_tenant_validation
from LIBS_CLI.get_tenantname import get_tenantname
from LIBS_CLI.action_2 import action_2
from LIBS_CLI.action_3 import action_3
from LIBS_CLI.action_4 import action_4
from LIBS_CLI.get_envconf import get_envconf
from LIBS_CLI import load_envconf
from LIBS_CLI.exist_envconf import exist_envconf
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Suppress other warnings
warnings.filterwarnings('ignore')

@click.group()
def onyxpm():
    print("start onyxpm")
    os.environ["conf_file_path"] = os.path.join(os.getcwd(), "env.conf")
    dotenv_file = get_envconf()
    print("get_envconf fini")
    env = load_envconf(dotenv_file)
    print("env file")


@onyxpm.group()
def tenant():
    pass

@onyxpm.group()
def project():
    pass

@tenant.command(help="Configure parameters - tenant, tenantname, tenantdomain, tenantusername, tenantpassword, tenantid")
@click.option('-t', '--tenant', help='Set the Tenant parameters. Example: "prod"')
@click.option('-tn', '--tenantname', help='Set the Tenant Name. Example: "MyTenant"')
@click.option('-td', '--tenantdomain', help='Set the Tenant Domain. Example: "example.com"')
@click.option('-tu', '--tenantusername', help='Set the Tenant Username. Example: "user"')
@click.option('-tp', '--tenantpassword', help='Set the Tenant Password. Example: "password"')
@click.option('-ti', '--tenantid', help='Set the Tenant ID. Example: "123456"')
def set(tenant, tenantname, tenantdomain, tenantusername, tenantpassword, tenantid):
    """
    usage: onyxpm.py tenant set [OPTIONS]

    configure parameters - tenant, tenantname, tenantdomain, tenantusername, tenantpassword, tenantid

    Options:
    -t, --tenant TEXT                            Set the Tenant Parameters. Example: "prod"
    -tn, --tenantname TEXT                       Set the Tenant Name. Example: "MyTenant"
    -td, --tenantdomain TEXT                     Set the Tenant Domain. Example: "example.com"
    -tu, --tenantusername TEXT                   Set the Tenant Username. Example: "user"
    -tp, --tenantpassword TEXT                   Set the Tenant Password. Example: "password"
    -ti, --tenantid TEXT                         Set the Tenant ID. Example: "123456"
    --help                                       Show this message and exit
    """
    action_1(tenant, tenantname, tenantdomain, tenantusername, tenantpassword, tenantid)

@tenant.command(help="List all available tenants.")
def list():
    if exist_envconf() != False:
        get_tenantname()

@project.command(help='List of projects in the tenant')
@click.option('-t', '--tenant', help='List of projects in the tenant', required=True)
def list(tenant):
    if exist_envconf() != False:
        action_5(tenant)
    if not tenant:
        click.echo("Please specify a valid tenant name.")


@tenant.command(help='Create a directory and store all project components')
@click.option('-t', '--tenant', help='Tenant name', required=True)
@click.option('-f', '--folder', help='Folder path', required=True)
def dump(tenant, folder):
    if exist_envconf() != False:
        click.echo(f'Dumping data for tenant {tenant} to folder {folder}')
        action_4(tenant, folder)
    if not tenant:
        click.echo("Please specify a valid tenant name.")

@project.command(help='Compare the desired projects in source and target tenants')
@click.option('-ts', '--source_tenant', help='Source tenant name', required=True)
@click.option('-tt', '--target_tenant', help='Target tenant name', required=True)
@click.option('-p', '--project', help='Project name', required=True)
def compare(source_tenant, target_tenant, project):
    if exist_envconf() != False:
        # Call the cli_tenant_validation function
        if not cli_tenant_validation(source_tenant, target_tenant):
            return

        # Check if the project exists
        project_exists = check_project_existence(source_tenant, target_tenant, project)
        if project_exists:
            click.echo(f'Comparing projects for source tenant {source_tenant} to target tenant {target_tenant} for project {project}')
            action_2(source_tenant, target_tenant, project)

@project.command(help='Choose to update your target tenant with desired project or a specfic object in a project from the source tenant.')
@click.option('-i', '--script_type', help='Select the type o object to deploy (o Types: CONNECTION, NOTIFICATION, DATAPIPELINE, FORM, SHELL_SCRIPT, SQL_SCRIPT,FILE_PROVIDER, VARIABLE, WORKFLOW, REPORT, WIDGET)')
@click.option('-o', '--object_name', help='Select the Object to deploy (not Mandatory)', default='ALL')
@click.option('-p', '--project', help='Project name', required=True) #possibilité de le rendre non obligatoire (j'ai envie de le faire)
@click.option('-ts', '--source_tenant', help='Source tenant name', required=True)
@click.option('-tt', '--target_tenant', help='Target tenant name', required=True)
def deploy(script_type, project, source_tenant, target_tenant, object_name):
    if exist_envconf() != False:
        # Call the cli_tenant_validation function
        if not cli_tenant_validation(source_tenant, target_tenant):
            return

        # Check if the project exists
        project_exists = check_project_existence(source_tenant, target_tenant, project)
        if project_exists:
            click.echo(f'Deploying {script_type} script {object_name} for project {project} from {source_tenant} to {target_tenant}')
            action_3(script_type, object_name, project, source_tenant, target_tenant)

if __name__ == '__main__':
    onyxpm()

