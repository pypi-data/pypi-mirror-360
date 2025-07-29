import typer
from rich.console import Console
from rich.traceback import install

from gh.commands.network_scanner import network_scanner
from gh.commands.vuln_scanner import vuln_scanner

console = Console()

install(show_locals=True)

app = typer.Typer()


@app.callback()
def presentation():
    console.print(r"""[bold cyan]
   ______                __                _           
  / ____/___ _____ ___  / /_  ____  ____  (_)___  ____ 
 / / __/ __ `/ __ `__ \/ __ \/ __ \/_  / / / __ \/ __ \
/ /_/ / /_/ / / / / / / /_/ / /_/ / / /_/ / / / / /_/ /
\____/\__,_/_/ /_/ /_/_.___/\____/ /___/_/_/ /_/\____/ 
    __  __            __                               
   / / / /_  ______  / /____  _____                    
  / /_/ / / / / __ \/ __/ _ \/ ___/                    
 / __  / /_/ / / / / /_/  __/ /                        
/_/ /_/\__,_/_/ /_/\__/\___/_/                         
    [/bold cyan]""")


app.command()(network_scanner)
app.command()(vuln_scanner)


if __name__ == "__main__":
    app()
