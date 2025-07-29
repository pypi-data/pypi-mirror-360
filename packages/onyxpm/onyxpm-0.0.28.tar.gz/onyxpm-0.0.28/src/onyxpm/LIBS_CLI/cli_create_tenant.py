import os
from CLASSES.NxTenant import NxTenant

def cli_create_tenant(tenant):
    tenant=tenant.upper()
    tenant = NxTenant(domain=os.environ[tenant + '_TENANTDOMAIN'],
                      tenant_id=os.environ[tenant + '_TENANTID'],
                      tenant_name=os.environ[tenant + '_TENANTNAME'],
                      username=os.environ[tenant + '_TENANTUSERNAME'],
                      password=os.environ[tenant + '_TENANTPASSWORD'])
    return tenant