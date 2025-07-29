import os
from rich.console import Console
def exist_tenantname(tenantname):
    for element in os.environ:
        if tenantname.upper()+'_TENANTDOMAIN' == element.upper():
            return True
