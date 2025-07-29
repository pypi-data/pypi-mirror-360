class NxTenant:
    def __init__(self, domain, tenant_id, tenant_name, username, password):
        self.domain = domain
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name