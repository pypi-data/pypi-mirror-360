import typer
import subprocess
import shutil
import os
from colorama import Fore, Style

app = typer.Typer()
_v = "16.0.0"

@app.command()
def create_project(
    name: str = typer.Argument(..., help="The name of the new project"),
    is_empty: bool = typer.Option(False, "--is-empty", "-e", help="If true, use the empty template; otherwise, use the starter template")
):
    """
    Create a new project by copying a template folder.

    Args:
        name (str): The name of the new project.
        is_empty (bool): If True, copy the empty template. Otherwise, copy the starter template.
    """
    try:
        typer.echo(Fore.BLUE + "Installing lilliepy..." + Style.DIM)
        subprocess.run(["pip", "install", f"lilliepy=={_v}"], check=True)
        subprocess.run(["pip", "install", "https://github.com/websitedeb/reactpy-material/archive/master.zip"], check=True)
        typer.echo(Fore.GREEN + "Installed lilliepy successfully." + Style.BRIGHT)
        
        global source_folder
        if not is_empty:
            subprocess.run(["git", "clone", "https://github.com/websitedeb/starter"], check=True)
            typer.echo(Fore.GREEN + "Cloned starter project successfully." + Style.BRIGHT)
            source_folder = os.path.join(os.getcwd(), "starter")
        else:
            subprocess.run(["git", "clone", "https://github.com/websitedeb/empty"], check=True)
            typer.echo(Fore.GREEN + "Cloned empty project successfully." + Style.BRIGHT)
            source_folder = os.path.join(os.getcwd(), "empty")

        current_dir = os.getcwd()
        destination_folder = os.path.join(current_dir, name)

        if os.path.exists(destination_folder):
            typer.echo(Fore.RED + f"Error: A folder named '{name}' already exists.")
            raise FileExistsError(Fore.RED + f"Destination folder '{destination_folder}' already exists.")
        
        shutil.move(source_folder, destination_folder)
        typer.echo(Fore.GREEN + f"Project '{name}' created successfully in {destination_folder}." + Style.BRIGHT)
        typer.echo(Fore.WHITE + Style.NORMAL)

    except subprocess.CalledProcessError as e:
        typer.echo(Fore.RED + f"Failed to install lilliepy: {e}")
    except Exception as e:
        typer.echo(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    app()
