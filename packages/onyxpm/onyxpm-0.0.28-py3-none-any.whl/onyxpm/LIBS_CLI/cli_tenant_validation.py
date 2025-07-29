import click
from LIBS_CLI.exist_tenantName import exist_tenantname

def cli_tenant_validation(source_tenant, target_tenant):
    # Check if source tenant exists
    if not exist_tenantname(source_tenant):
        click.echo(f"The source tenant '{source_tenant}' does not exist or is invalid.")
        click.echo("Please configure your parameters using the tenantSet command.")
        return False

    # Check if target tenant exists
    if not exist_tenantname(target_tenant):
        click.echo(f"The target tenant '{target_tenant}' does not exist or is invalid.")
        click.echo("Please configure your parameters using the tenantSet command.")
        return False

    return True
