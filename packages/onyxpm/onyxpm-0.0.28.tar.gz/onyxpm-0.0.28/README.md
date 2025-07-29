# ONYX PACKAGE MANAGER

Short description or overview of what the project does.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the project from Pipy:

   ```sh
   pip install onyxpm==0.0.24
   ````

## First Steps After Installation

1. After installing the project, locate the installation directory where Onyxpm has been installed. This directory is typically identified during the installation process. Make sure to note down this directory.

    ```sh
    C:\Users\User\AppData\Local\Programs\Python\Python312\Lib\site-packages\onyxpm\onyxpm.py
    ```

2. Create PowerShell script files (.ps1) to set up both the source and target environments. The content of the .ps1 file should resemble the following:

    ```powershell
    Example:
    python InstallationPath\onyxpm.py tenant set -t tenant -tn "tenant_name" -td "tenant_domain" -tu "tenant_username" -tp "tenant_password" -ti "tenant_id"
    ```
   
   **OR Alternatively:**

    ```sh
    cd InstallationPath
    CLI Commands
    ```

    Replace "InstallationPath" with the actual installation path where Onyxpm is installed. Execute the .ps1 file (.\setup.ps1) to configure and set up your environments. If the environment settings are correct, you'll see an `env.conf` file created in your project, which will be used for further operations.



3. Execute the .ps1 files to set up your environment. You can use other CLI commands as shown below.


## Usage

Below are examples demonstrating how to use the project's command-line interface (CLI). Replace `onyxpm.py` with the name of your CLI script if it's different.

### Help

To view the available commands and options, run:

   ```sh
   python onyxpm.py --help
   ```
### Set Tenant Command
To set parameters for a specific tenant, use the following command:

   ```sh
   python onyxpm.py tenant set -t tenant -tn "tenant_name" -td "tenant_domaine" -tu "tenant_username" -tp "tenant_password" -ti "tenant_id"
   ```
Example of the env.conf file:
```
#SOURCE
SOURCE_TENANTDOMAIN='https://example_domain.com'
SOURCE_TENANTID='1'
SOURCE_TENANTNAME='UAT'
SOURCE_TENANTUSERNAME='example@sourceusername.com'
SOURCE_TENANTPASSWORD='example_pwd'
```


### List Tenants Command
To list the names of all tenants, use the following command:
   ```sh
   python onyxpm.py tenant list
  ```

### List Projects Command
To list the names of projects for a specific tenant, use the following command:
   ```sh
   python onyxpm.py "project list" -t "tenant_name"
  ```

### Dump Command
To dump data for a specific tenant to a specified folder, use the following command:
   ```sh
   python onyxpm.py tenant dump -t "tenant_name" -f "destination_folder ./directory"
  ```
This command will dump data to the current directory of the tenant.

### Compare Projects Command
To compare projects between source and target tenants for a specific project, use the following command:
   ```sh
   python onyxpm.py project compare -ts "source_tenant" -tt "target_tenant" -p "project_name" 
  ```

### Deploy Command
To deploy a script for a specific project from a source tenant to a target tenant, use the following command:
   ```sh
   python onyxpm.py project deploy -i "file_type" -o "file_name" -p "project_name" -ts tenant_source -tt tenant_target
  ```
Example Usage:
To deploy Report's (filetype (i): 'REPORT') from project SOPREMA (tenant source(ts): 'SOPREMA') to destination SOPREMAPROD (target tenant (tt): 'SOPREMAPROD'), use the deploy command in the following manner:

```sh
   python onyxpm.py project deploy -i REPORT -ts SOPREMA -tt SOPREMAPROD -p Démonstration
  ```


Writing and exceuting the

## Command Parameters

- `-t`: Set the tenant parameter.
- `-f`: Set the folder parameter.
- `-o`: Specify the name of an object.
- `-p`: Specify the name of a project.
- `-ts`: Specify the name of a source tenant.
- `-tt`: Specify the name of a target tenant.
- `-i`: Specify a keyword : 
  - [CONNECTION, NOTIFICATION, DATAPIPELINE, FORM, SCHEDULE, SHELL_SCRIPT, SQL_SCRIPT, FILE_PROVIDER, VARIABLE, WORKFLOW, REPORT, WIDGET]


### Project Structure
The structure of the project, including important directories and files.
   ```sh
   OnyxCLi/
   │
   ├── src/
   │   └── onyxpm/
   │      ├──onyxpm
   │      ├── CLASSES/
   │      │   ├── EnvConfElement.py
   │      │   ├── NxComponent.py
   │      │   └── ...
   │      ├── LIBS_BUS/
   │      │   ├── apply_transco.py
   │      │   ├── compare_onyx_projects.py
   │      │   └── ...
   │      └── LIBS_CLI/
   │          ├── action_1.py
   │          ├── action_2.py
   │          └── ...
   ├── tests/
   ├── env.conf
   ├── setup.py
   ├── requirements.txt
   └── README.md
   ```
## Want to Contribute ?

If you'd like to contribute to the project, follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add feature'`)
5. Push to the branch (`git push origin feature`)
6. Create a new pull request

## License
MIT License

Copyright (c) 2020 NeuralNine

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.