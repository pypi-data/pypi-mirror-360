import os
from LIBS_CLI.init_envconf import init_envconf
from rich.console import Console


def exist_envconf():
    filepath=os.environ["conf_file_path"]
    if os.path.exists(filepath) == False:
        console = Console()
        console.print("Please configure the tenant parameters before executing this command.", style="yellow")
        return False