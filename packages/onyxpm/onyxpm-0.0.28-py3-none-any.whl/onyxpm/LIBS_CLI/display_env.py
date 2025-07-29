from rich.console import Console
from rich.markdown import Markdown

def display_env(env):
    console = Console()
    console.print(Markdown("""
> Client: {}
>
> Source env: {}
>
> Target env: {}
---
""".format(env["client"], env["source"], env["target"])))


