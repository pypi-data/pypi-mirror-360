import requests
import json

class NxOnyxApi:
    def __init__(self, domain, username, password, tenantId):
        self.__domain = domain
        self.__username = username
        self.__password = password
        self.__tenantId = tenantId
        self.__token = self.getToken()

    def getToken(self):
        url = f"{self.__domain}/api/TokenAuth/Authenticate"

        payload = json.dumps({
            "userNameOrEmailAddress": self.__username,
            "password": self.__password
        })
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data=payload, verify=False)
            if response.status_code == 200:
                token = response.json().get('result').get('accessToken')
                # print("Accessed bearer token and connection successful : {}".format(token))
                return token
            else:
                response = requests.post(url, headers=headers, data=payload)
                raise Exception(f"Connection failed with status code: {response.status_code}, {response.json()}")

        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred in getToken:\n" + str(e))

    def startWorkflow(self, workflowId):
        url = f"{self.__domain}/api/services/app/OWorkflows/Start"

        payload = json.dumps({
            "id": workflowId
        })
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response_json = response.json()

            if response.status_code == 200:
                scriptId = response_json.get('result')
                print("Workflow successfully created")
                return scriptId
            else:
                check_if_already_running = 'Une instance de la tâche est déjà en cours' in response_json
                if not check_if_already_running:
                    raise Exception(f"StartWorkFlow failed with status code: {response.status_code}, {response_json}")

        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred in StartWorkFow:\n" + str(e))

    def registerSchedule(self, scheduleId):
        url = f"{self.__domain}/api/services/app/OSchedules/Register?id=" + scheduleId
        payload = json.dumps({
            "id": scheduleId
        })
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data={})
            response_json = response.json()

            if response.status_code == 200:
                scriptId = response_json.get('result')
                print("Schedule successfully activated")
                return scriptId
            else:
                raise Exception(f"Activation failed with status code: {response.status_code}, {response_json}")

        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred in activation :\n" + str(e))

    def unregisterSchedule(self, scheduleId):
        url = f"{self.__domain}/api/services/app/OSchedules/Unregister?id=" + scheduleId
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data={})
            response_json = response.json()

            if response.status_code == 200:
                scriptId = response_json.get('result')
                print("Schedule successfully desactivated")
                return scriptId
            else:
                raise Exception(f"Desactivation failed with status code: {response.status_code}, {response_json}")

        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred in Desactivation :\n" + str(e))

    def getTree(self):
        url = f"{self.__domain}/api/services/app/OProjects/GetTree"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                tree = response_json.get('result')
                return tree
            else:
                raise Exception(f"GetTree failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getOrganisationUnits(self):
        url = f"{self.__domain}/api/services/app/OrganizationUnit/GetOrganizationUnits"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                tree = response_json.get('result')
                return tree
            else:
                raise Exception(
                    f"GetOrganisationUnits failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getProject(self, id):
        url = f"{self.__domain}/api/services/app/OProjects/GetOProjectForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                tree = response_json.get('result')
                return tree
            else:
                raise Exception(f"GetProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createProject(self, name, organizationUnitId: int):
        url = f"{self.__domain}/api/services/app/OProjects/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'name': name,
            'organizationUnitId': organizationUnitId
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                tree = response_json.get('result')
                return tree
            else:
                raise Exception(f"GetProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getConnection(self, id):
        url = f"{self.__domain}/api/services/app/OConnections/GetOConnectionForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                tree = response_json.get('result')
                return tree
            else:
                raise Exception(f"GetConnection failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getConnectionsByProject(self, id):
        url = f"{self.__domain}/api/services/app/OConnections/GetConnectionsByProject?ProjectId=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(
                    f"GetConnectionsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getFileProvidersByProject(self, id):
        url = f"{self.__domain}/api/services/app/OFileProviders/GetFileProvidersByProject?ProjectId=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(
                    f"GetFileProvidersByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getFileProvider(self, id):
        url = f"{self.__domain}/api/services/app/OFileProviders/GetOFileProviderForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"GetFileProvider failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createFileProvider(self, connectionString, containerName, name, organizationUnitId, type, id=None):
        url = f"{self.__domain}/api/services/app/OFileProviders/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'connectionString': connectionString,
            'containerName': containerName,
            'name': name,
            'organizationUnitId': organizationUnitId,
            'type': type
        }
        if not id == None:
            payload = {
                'connectionString': connectionString,
                'containerName': containerName,
                'name': name,
                'organizationUnitId': organizationUnitId,
                'type': type,
                'id': id
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateFileProvider failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getConnections(self):
        url = f"{self.__domain}/api/services/app/OConnections/GetAll"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"GetConnections failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createConnection(self, connectionType: int, isWritable: bool, name: str, organizationUnitId: int,
                         shortName: str, documentation, id=None):
        url = f"{self.__domain}/api/services/app/OConnections/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'connectionType': connectionType,
            'isWritable': isWritable,
            'name': name,
            'organizationUnitId': organizationUnitId,
            'shortName': shortName,
            'documentation': documentation,
        }
        if not id == None:
            payload = {
                'connectionType': connectionType,
                'isWritable': isWritable,
                'name': name,
                'organizationUnitId': organizationUnitId,
                'shortName': shortName,
                'documentation':documentation,
                'id': id
            }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateConnection failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def updateConnectionString(self, id, ConnectionString):
        url = f"{self.__domain}/api/services/app/OConnections/UpdateCS"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'id': id,
            'ConnectionString': ConnectionString
        }
        try:
            print(payload)
            response = requests.put(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(
                    f"UpdateConnectionString failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getVariablesByProject(self, id):
        url = f"{self.__domain}/api/services/app/OVariable/GetAll?Filter=&NameFilter=&CodeFilter=&OProjectIdFilter=" + id + "&SkipCount=0&MaxResultCount=100"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(
                    f"GetVariablesByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getVariable(self, id):
        url = f"{self.__domain}/api/services/app/OVariable/GetOVariableForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"GetVariable failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createVariable(self, code, name, description, oConnectionId, oProjectId, query, value,oVariableType, tenantId, id=None):
        url = f"{self.__domain}/api/services/app/OVariable/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'name': name,
            'code': code,
            'description': description,
            'value': value,
            'oConnectionId': oConnectionId,
            'oProjectId': oProjectId,
            'query': query,
            'oVariableType': oVariableType,
            'tenantId': tenantId
        }
        if not id == None:
            payload = {
                'id': id,
                'name': name,
                'code': code,
                'description': description,
                'value': value,
                'oConnectionId': oConnectionId,
                'oProjectId': oProjectId,
                'query': query,
                'oVariableType': oVariableType,
                'tenantId': tenantId
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateVariable failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def updateVariable(self, id, code, name, oConnectionId, oProjectId, query, value, oVariableType):
        url = f"{self.__domain}/api/services/app/OVariable/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'tenantId': self.__tenantId,
            'id': id,
            'code': code,
            'name': name,
            'oConnectionId': oConnectionId,
            'oProjectId': oProjectId,
            'query': query,
            'value': value,
            'oVariableType': oVariableType
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateFileProvider failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getSqlScriptsByProject(self, id):
        url = f"{self.__domain}/api/services/app/OSQLScripts/GetAll?NameFilter=&OProjectNameFilter=" + id + "&OConnectionNameFilter=&Sorting=&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(
                    f"GetSqlScriptsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getSqlScript(self, id):
        url = f"{self.__domain}/api/services/app/OSQLScripts/GetOSQLScriptForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetSqlScript failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createSqlScript(self, name, oConnectionId, oProjectId, commandTimeout, query, documentation, id=None):
        url = f"{self.__domain}/api/services/app/OSQLScripts/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'commandTimeout': commandTimeout,
            'name': name,
            'oConnectionId': oConnectionId,
            'oProjectId': oProjectId,
            'query': query,
            'documentation': documentation
        }
        if not id == None:
            payload = {
                'id': id,
                'commandTimeout': commandTimeout,
                'name': name,
                'oConnectionId': oConnectionId,
                'oProjectId': oProjectId,
                'query': query,
                'documentation': documentation
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateSqlScript failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createShellScript(self, name, oProjectId, type, script, documentation, packages, env, args, id=None):
        url = f"{self.__domain}/api/services/app/OShellScripts/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'type': type,
            'name': name,
            'oProjectId': oProjectId,
            'script': script,
            'documentation': documentation,
            'packages': packages,
            'env' : env,
            'args' : args
        }
        if not id == None:
            payload = {
                'id': id,
                'type': type,
                'name': name,
                'oProjectId': oProjectId,
                'script': script,
                'documentation': documentation,
                'packages': packages,
                'env' : env,
                'args' : args
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateShellScript failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createNotification(self, name, oProjectId, recipients, subject, body, tenant, type, id=None):
        url = f"{self.__domain}/api/services/app/ONotifications/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'name': name,
            'oProjectId': oProjectId,
            'recipients': recipients,
            'subject': subject,
            'tenantId': tenant,
            'type' : type,
            'body': body
        }
        if not id == None:
            payload = {
                'name': name,
                'recipients': recipients,
                'subject': subject,
                'body': body,
                'oProjectId': oProjectId,
                'tenantId': tenant,
                'type' : type,
                'id': id
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"createNotification failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createForm(self, displayedName, oProjectId, oConnectionId, technicalName, isActive, documentation, id=None):
        url = f"{self.__domain}/api/services/app/OForms/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'displayedName': displayedName,
            'oProjectId': oProjectId,
            'oConnectionId': oConnectionId,
            'technicalName': technicalName,
            'isActive': isActive,
            'documentation': documentation
        }
        if not id == None:
            payload = {
                'displayedName': displayedName,
                'oProjectId': oProjectId,
                'oConnectionId': oConnectionId,
                'technicalName': technicalName,
                'isActive': isActive,
                'documentation': documentation,
                'id': id
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"createForm failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createFormColumn(self, characterMaximumLength, displayOrder, displayedName, dropDownQuery, editorType,
                         isDisplayed, isDropDown, isNullable, numericPrecision, technicalName, numericScale, oFormId,
                         type, id=None):
        url = f"{self.__domain}/api/services/app/OFormColumns/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'characterMaximumLength': characterMaximumLength,
            'displayOrder': displayOrder,
            'displayedName': displayedName,
            'technicalName': technicalName,
            'dropDownQuery': dropDownQuery,
            'editorType': editorType,
            'isDisplayed': isDisplayed,
            'isDropDown': isDropDown,
            'isNullable': isNullable,
            'numericPrecision': numericPrecision,
            'numericScale': numericScale,
            'oFormId': oFormId,
            'type': type
        }
        if not id == None:
            payload = {
                'characterMaximumLength': characterMaximumLength,
                'displayOrder': displayOrder,
                'displayedName': displayedName,
                'technicalName': technicalName,
                'dropDownQuery': dropDownQuery,
                'editorType': editorType,
                'isDisplayed': isDisplayed,
                'isDropDown': isDropDown,
                'isNullable': isNullable,
                'numericPrecision': numericPrecision,
                'numericScale': numericScale,
                'oFormId': oFormId,
                'id': id
            }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"createForm failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getShellScriptsByProject(self, id):
        url = f"{self.__domain}/api/services/app/OShellScripts/GetAll?NameFilter=&OProjectIdFilter=" + id + "&Sorting=&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(
                    f"GetShellScriptsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getShellScript(self, id):
        url = f"{self.__domain}/api/services/app/OShellScripts/GetOShellScriptForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetShellScript failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getFormsByProject(self, id):
        url = f"{self.__domain}/api/services/app/OForms/GetAll?OProjectIdFilter=" + id + "&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetFormsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getForm(self, id):
        url = f"{self.__domain}/api/services/app/OForms/GetOFormForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetForm failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getFormColumns(self, id):
        url = f"{self.__domain}/api/services/app/OFormColumns/GetAll?Filter=&TechnicalNameFilter=&DisplayedNameFilter=&DropDownQueryFilter=&OFormTechnicalNameFilter=" + id + "&Sorting=&SkipCount=0"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetFormColumns failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWidgetsByProject(self, id):
        url = f"{self.__domain}/api/services/app/OWidgets/GetAll?OProjectId=" + id + "&WithFilters=false&WithRowButtons=false&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWidgetsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWidget(self, id):
        url = f"{self.__domain}/api/services/app/OWidgets/GetOWidgetForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWidget failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWidgetFilters(self, id):
        url = f"{self.__domain}/api/services/app/OWidgets/GetAllFilters?OWidgetId=" + id + "&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWidgetFilters failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWidgetRowButtons(self, id):
        url = f"{self.__domain}/api/services/app/OWidgets/GetAllRowButtons?OWidgetId=" + id + "&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWidgetRowButtons failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getReportsByProject(self, id):
        url = f"{self.__domain}/api/services/app/OReports/GetAll?OProjectId=" + id + "&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetReportsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getReportForEdit(self, id):
        url = f"{self.__domain}/api/services/app/OReports/GetOReportForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetReportForEdit failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getReport(self, id):
        url = f"{self.__domain}/api/services/app/OReports/GetOReportForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GeReport failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getSchedulesByProject(self, id):
        url = f"{self.__domain}/api/services/app/OSchedules/GetAll?nameFilter=&ObjectIdFilter=&OProjectNameFilter=" + id + "&Sorting=&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(
                    f"GetSchedulesByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getSchedule(self, id):
        url = f"{self.__domain}/api/services/app/OSchedules/GetOScheduleForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "Id": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetSchedule failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getNotificationsByProject(self, id):
        url = f"{self.__domain}/api/services/app/ONotifications/GetAll?NameFilter=&OProjectIdFilter=" + id + "&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(
                    f"GetNotificationsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getNotification(self, id):
        url = f"{self.__domain}/api/services/app/ONotifications/GetONotificationForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "Id": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetNotification failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWorkflowsByProject(self, id):
        url = f"{self.__domain}/api/services/app/OWorkflows/GetAll?NameFilter=&OProjectIdFilter=" + id + "&Sorting=&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(
                    f"GetWorkflowsByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWorkflow(self, id):
        url = f"{self.__domain}/api/services/app/OWorkflows/GetOWorkflowForEdit?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "Id": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWorkflow failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWorkflowSteps(self, id):
        url = f"{self.__domain}/api/services/app/OWorkflows/GetAllSteps?OWorkflowIdFilter=" + id + "&Sorting=&SkipCount=0&MaxResultCount=1000"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "Id": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWorkflowSteps failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWorkflowStepForView(self, id):
        url = f"{self.__domain}/api/services/app/OWorkflows/GetOWorkflowStepForView?id" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "Id": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWorkflowSteps failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))



    def getPipelinesByProject(self, id):
        url = f"{self.__domain}/api/services/app/OProjects/GetFlows?input=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:

                return response_json.get('result')
            else:
                raise Exception(
                    f"GetPipelinesByProject failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getPipeline(self, id):
        url = f"{self.__domain}/api/services/app/OProjects/GetFlow?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "Id": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetPipeline failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getPipelineColumnsIncluded(self, id):
        url = f"{self.__domain}/api/services/app/OProjects/GetFlowColumns?input=" + id + "&included=true"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "input": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetPipelineColumns failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getPipelineColumnsExcluded(self, id):
        url = f"{self.__domain}/api/services/app/OProjects/GetFlowColumns?input=" + id + "&included=false"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            "input": id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetPipelineColumns failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createPipeline(self, id, oProjectId, SourceConnectionId, SourceConnectionType, DestinationConnectionId,
                       DestinationConnectionType, Name, SourceTable, DestinationTable, QueryFilter, NbColumns,
                       ActionIfTableExists, ActionIfTableNotExists, DesactivateIndexes, CreatePrimaryKey, CreateIndexes,
                       NumberOfSchedules):
        url = f"{self.__domain}/api/services/app/OProjects/AddFlow"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        if id == None:
            payload = {
                'oProjectId': oProjectId,
                'SourceConnectionId': SourceConnectionId,
                'SourceConnectionType': SourceConnectionType,
                'DestinationConnectionId': DestinationConnectionId,
                'DestinationConnectionType': DestinationConnectionType,
                'Name': Name,
                'SourceTable': SourceTable,
                'DestinationTable': DestinationTable,
                'QueryFilter': QueryFilter,
                'NbColumns': NbColumns,
                'ActionIfTableExists': ActionIfTableExists,
                'ActionIfTableNotExists': ActionIfTableNotExists,
                'DesactivateIndexes': DesactivateIndexes,
                'CreatePrimaryKey': CreatePrimaryKey,
                'CreateIndexes': CreateIndexes,
                'NumberOfSchedules': NumberOfSchedules
            }
            try:
                response = requests.post(url, headers=headers, json=payload)
                response_json = response.json()
                if response.status_code == 200:
                    cnx = response_json.get('result')
                    return cnx
                else:
                    raise Exception(f"CreatePipeline failed with status code: {response.status_code}, {response_json}")
            except requests.exceptions.RequestException as e:
                raise ValueError("An error occurred :\n" + str(e))
        if not id == None:
            url = f"{self.__domain}/api/services/app/OProjects/UpdateFlow"
            payload = {
                'oProjectId': oProjectId,
                'SourceConnectionId': SourceConnectionId,
                'SourceConnectionType': SourceConnectionType,
                'DestinationConnectionId': DestinationConnectionId,
                'DestinationConnectionType': DestinationConnectionType,
                'Name': Name,
                'SourceTable': SourceTable,
                'DestinationTable': DestinationTable,
                'QueryFilter': QueryFilter,
                'NbColumns': NbColumns,
                'ActionIfTableExists': ActionIfTableExists,
                'ActionIfTableNotExists': ActionIfTableNotExists,
                'DesactivateIndexes': DesactivateIndexes,
                'CreatePrimaryKey': CreatePrimaryKey,
                'CreateIndexes': CreateIndexes,
                'NumberOfSchedules': NumberOfSchedules,
                'id': id
            }
            try:
                response = requests.put(url, headers=headers, json=payload)
                response_json = response.json()
                if response.status_code == 200:
                    cnx = response_json.get('result')
                    return cnx
                else:
                    raise Exception(f"CreatePipeline failed with status code: {response.status_code}, {response_json}")
            except requests.exceptions.RequestException as e:
                raise ValueError("An error occurred :\n" + str(e))

    def createPipelineColumn(self, oFlowId, sourceColumnName, destinationColumnName, destinationColumnDataType,
                             sourceCharacterMaximumLength, sourceColumnNumericPrecision, sourceColumnNumericScale,
                             sourceColumnDatatype, ordinal, missingInSource,id):
        if id is None:
            url = f"{self.__domain}/api/services/app/OProjects/AddFlowColumn"
            headers = {
                'Abp.TenantId': self.__tenantId,
                'Accept': 'text/plain',
                'Authorization': f'Bearer {self.__token}'
            }
            payload = {
                "oFlowId": oFlowId,
                "sourceColumnName": sourceColumnName,
                "destinationColumnName": destinationColumnName,
                "destinationColumnDataType": destinationColumnDataType,
                "sourceCharacterMaximumLength": sourceCharacterMaximumLength,
                "sourceColumnNumericPrecision": sourceColumnNumericPrecision,
                "sourceColumnNumericScale": sourceColumnNumericScale,
                "sourceColumnDatatype": sourceColumnDatatype,
                "ordinal": ordinal,
                "missingInSource": missingInSource
            }
            try:
                response = requests.post(url, headers=headers, json=payload)
                response_json = response.json()
                if response.status_code == 200:
                    cnx = response_json.get('result')
                    return cnx
                else:
                    raise Exception(
                        f"CreatePipelineColumn failed with status code: {response.status_code}, {response_json}")
            except requests.exceptions.RequestException as e:
                raise ValueError("An error occurred :\n" + str(e))
        else:
            url=f"{self.__domain}/api/services/app/OProjects/UpdateFlowColumn"
            headers = {
                'Abp.TenantId': self.__tenantId,
                'Accept': 'text/plain',
                'Authorization': f'Bearer {self.__token}'
            }
            payload = {
                "oFlowId": oFlowId,
                "sourceColumnName": sourceColumnName,
                "destinationColumnName": destinationColumnName,
                "destinationColumnDataType": destinationColumnDataType,
                "sourceCharacterMaximumLength": sourceCharacterMaximumLength,
                "sourceColumnNumericPrecision": sourceColumnNumericPrecision,
                "sourceColumnNumericScale": sourceColumnNumericScale,
                "sourceColumnDatatype": sourceColumnDatatype,
                "ordinal": ordinal,
                "missingInSource": missingInSource,
                "id": id
            }
            try:
                response = requests.put(url, headers=headers, json=payload)
                response_json = response.json()
                if response.status_code == 200:
                    cnx = response_json.get('result')
                    return cnx
                else:
                    raise Exception(
                        f"CreatePipelineColumn failed with status code: {response.status_code}, {response_json}")
            except requests.exceptions.RequestException as e:
                raise ValueError("An error occurred :\n" + str(e))

    def deletePipelineColumn(self, id):
        url = f"{self.__domain}/api/services/app/OProjects/DeleteFlowColumn?input=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.delete(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(
                    f"DeletePipelineColumn failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createWorkflow(self, oProjectId, name, enableCrossProject, emailSentOnError, emailRecipients, id=None):
        url = f"{self.__domain}/api/services/app/OWorkflows/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'oProjectId': oProjectId,
            'name': name,
            'enableCrossProject': enableCrossProject,
            'emailSentOnError': emailSentOnError,
            'emailRecipients': emailRecipients
        }
        if not id == None:
            payload = {
                'oProjectId': oProjectId,
                'name': name,
                'enableCrossProject': enableCrossProject,
                'emailSentOnError': emailSentOnError,
                'emailRecipients': emailRecipients,
                'id': id
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateWorkflow failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createWorkflowStep(self, oWorkflowId, objectId, stepOrder, isActive, stopWorkflowOnError, jobType):
        url = f"{self.__domain}/api/services/app/OWorkflows/CreateOrEditStep"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'oWorkflowId': oWorkflowId,
            'objectId': objectId,
            'stepOrder': stepOrder,
            'stopWorkflowOnError': stopWorkflowOnError,
            'isActive': isActive,
            'jobType': jobType
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateWorkflowStep failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def deleteWorkflowStep(self, id):
        url = f"{self.__domain}/api/services/app/OWorkflows/DeleteStep?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.delete(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"DeleteWorkflowStep failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createWidget(self, oProjectId, name, description, query, configuration, oConnectionId, oWorkflowId, oFormId,
                     oFileProviderId, type,id=None):
        url = f"{self.__domain}/api/services/app/OWidgets/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'oProjectId': oProjectId,
            'name': name,
            'description': description,
            'query': query,
            'configuration': configuration,
            'oConnectionId': oConnectionId,
            'oWorkflowId': oWorkflowId,
            'oFormId': oFormId,
            'oFileProviderId': oFileProviderId,
            'type': type
        }
        if not id == None:
            payload = {
                'oProjectId': oProjectId,
                'name': name,
                'description': description,
                'query': query,
                'configuration': configuration,
                'oConnectionId': oConnectionId,
                'oWorkflowId': oWorkflowId,
                'oFormId': oFormId,
                'oFileProviderId': oFileProviderId,
                'type': type,
                'id': id
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateWidget failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def deleteWidgetFilter(self, id):
        url = f"{self.__domain}/api/services/app/OWidgets/DeleteFilter?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.delete(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"DeleteWidgetFilter failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def deleteWidgetRowButton(self, id):
        url = f"{self.__domain}/api/services/app/OWidgets/DeleteRowButton?Id=" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        try:
            response = requests.delete(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(
                    f"DeleteWidgetRowButton failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createWidgetFilter(self, name, description, oConnectionId, oWidgetId, query, type, id=None):
        url = f"{self.__domain}/api/services/app/OWidgets/CreateOrEditFilter"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'name': name,
            'description': description,
            'oConnectionId': oConnectionId,
            'oWidgetId': oWidgetId,
            'query': query,
            'type': type
        }

        if not id == None:
            payload = {
                'name': name,
                'description': description,
                'oConnectionId': oConnectionId,
                'oWidgetId': oWidgetId,
                'query': query,
                'type': type,
                'id':id
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateWidgetFilter failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createWidgetRowButton(self, actionType, configuration, description, name, oSqlScriptId, oWidgetId, oWorkflowId,id):
        url = f"{self.__domain}/api/services/app/OWidgets/CreateOrEditRowButton"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'actionType': actionType,
            'configuration': configuration,
            'description': description,
            'name': name,
            'oSqlScriptId': oSqlScriptId,
            'oWidgetId': oWidgetId,
            'oWorkflowId': oWorkflowId,
            "id":id
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(
                    f"CreateWidgetRowButton failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def getWidgetForView(self, id):
        url = f"{self.__domain}/api/services/app/OWidgets/GetOWidgetForView?id" + id
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = json.dumps({
            'id': id
        })
        try:
            response = requests.get(url, headers=headers, data=payload)
            response_json = response.json()
            if response.status_code == 200:
                return response_json.get('result')
            else:
                raise Exception(f"GetWidgetForView failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))

    def createReport(self, name, oProjectId, documentation, configuration, id=None):
        url = f"{self.__domain}/api/services/app/OReports/CreateOrEdit"
        headers = {
            'Abp.TenantId': self.__tenantId,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.__token}'
        }
        payload = {
            'name': name,
            'oProjectId': oProjectId,
            'configuration': configuration,
            'documentation': documentation
        }
        if not id == None:
            payload = {
                'name': name,
                'oProjectId': oProjectId,
                'configuration': configuration,
                'documentation': documentation,
                'id': id
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response.status_code == 200:
                cnx = response_json.get('result')
                return cnx
            else:
                raise Exception(f"CreateReport failed with status code: {response.status_code}, {response_json}")
        except requests.exceptions.RequestException as e:
            raise ValueError("An error occurred :\n" + str(e))
