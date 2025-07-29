from CLASSES.NxOnyxApi import NxOnyxApi
from CLASSES.NxTenant import NxTenant

def cli_connect_api(tenant : NxTenant):

    onyx = NxOnyxApi(tenant.domain, tenant.username, tenant.password, tenant.tenant_id)

    return onyx