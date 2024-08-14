"""Command Line Interface"""

import click
from meorg_client.client import Client
import meorg_client.utilities as mcu
from meorg_client import __version__
import os
import sys
import getpass
from pathlib import Path
import json


def _get_client() -> Client:
    """Get an authenticated client.

    Returns
    -------
    meorg_client.client.Client
        Client object.
    """
    # Get the dev-mode flag from the environment, better than passing the dev flag everywhere.
    dev_mode = os.getenv("MEORG_DEV_MODE", "0") == "1"

    credentials = mcu.get_user_data_filepath("credentials.json")
    credentials_dev = mcu.get_user_data_filepath("credentials-dev.json")

    # In dev mode and the configuration file exists
    if dev_mode and credentials_dev.is_file():
        credentials = mcu.load_user_data("credentials-dev.json")

    # In dev mode and it doesn't (i.e. Actions)
    elif dev_mode and not credentials_dev.is_file():
        credentials = dict(
            email=os.getenv("MEORG_EMAIL"), password=os.getenv("MEORG_PASSWORD")
        )

    # Production credentials
    else:
        credentials = mcu.load_user_data("credentials.json")

    # Get the client
    return Client(
        email=credentials["email"], password=credentials["password"], dev_mode=dev_mode
    )


def _call(func: callable, **kwargs) -> dict:
    """Simple wrapper to handle exceptions.

    Exceptions are captured broadly and raw error message printed before non-zero exit.

    Parameters
    ----------
    func : callable
        Method to call.
    **kwargs :
        Additional arguments to method.

    Returns
    -------
    dict
        Response dictionary.
    """
    try:
        return func(**kwargs)
    except Exception as ex:
        click.echo(ex.msg, err=True)

        # Bubble up the exception
        if os.getenv("MEORG_DEV_MODE") == "1":
            raise

        sys.exit(1)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__)
def cli():
    """
    ModelEvaluation.org client utility.

    For more detail run:
    meorg [SUBCOMMAND] --help
    """
    pass


@click.command("list")
def list_endpoints():
    """
    List the available endpoints for the server.
    """
    client = _get_client()
    endpoints = _call(client.list_endpoints)

    for url, config in endpoints.get("paths").items():
        for method in config.keys():
            out = " ".join(
                [
                    method.upper(),
                    url,
                    endpoints.get("paths")[url][method]["description"],
                ]
            )

            click.echo(out)


@click.command("upload")
@click.argument("file_path", nargs=-1)
@click.option(
    "--attach_to",
    default=None,
    help="Supply a model output id to immediately attach the file to.",
)
def file_upload(file_path, attach_to=None):
    """
    Upload a file to the server.

    Prints Job ID on success, which is used by file-status to check transfer status.

    If attach_to is used then no ID is returned.
    """
    client = _get_client()

    # Upload the file, get the job ID
    response = _call(client.upload_files, files=list(file_path), attach_to=attach_to)

    # Different logic if we are attaching to a model output immediately
    if not attach_to:
        files = response.get("data").get("files")
        for f in files:
            click.echo(f.get("file"))
    else:
        click.echo("SUCCESS")


@click.command("upload_parallel")
@click.argument("file_paths", nargs=-1)
@click.option(
    "-n", default=2, help="Number of simultaneous parallel uploads (default=2)."
)
@click.option(
    "--attach_to",
    default=None,
    help="Supply a model output id to immediately attach the file to.",
)
def file_upload_parallel(file_paths: tuple, n: int = 2, attach_to: str = None):
    """Upload files in parallel.

    Parameters
    ----------
    file_paths : tuple
        Sequence of file paths.
    n : int, optional
        Number of parallel uploads, by default 2
    """
    client = _get_client()
    responses = _call(client.upload_files_parallel, files=list(file_paths), n=n)
    for response in responses:
        click.echo(response.get("data").get("files")[0].get("file"))


@click.command("list")
@click.argument("id")
def file_list(id: str):
    """
    List the files currently attached to a model output.

    Prints 1 File ID per line.
    """
    client = _get_client()
    response = _call(client.list_files, id=id)

    for f in response.get("data").get("files"):
        click.echo(f)


@click.command("attach")
@click.argument("file_id")
@click.argument("output_id")
def file_attach(file_id: str, output_id: str):
    """
    Attach a file to a model output.
    """
    client = _get_client()

    _ = _call(client.attach_files_to_model_output, id=output_id, files=[file_id])

    click.echo("SUCCESS")


@click.command("start")
@click.argument("id")
def analysis_start(id: str):
    """
    Start the analysis for the model output id.

    Prints the Analysis ID, which can be used in analysis-status.
    """
    client = _get_client()

    response = _call(client.start_analysis, id=id)

    if client.success():
        analysis_id = response.get("data").get("analysisId")
        click.echo(analysis_id)


@click.command("status")
@click.argument("id")
def analysis_status(id: str):
    """
    Get the status of the analysis.

    Prints the status of the analysis and the URL to the dashboard.
    """
    client = _get_client()
    response = _call(client.get_analysis_status, id=id)
    status = response.get("status")

    # Error case
    if status == "error":
        click.echo(response.get("message"), err=True)
        sys.exit(1)

    # Get the status out of the data object
    status = response.get("data").get("status")
    url = response.get("data").get("url")

    click.echo(status)
    click.echo(url)


@click.command()
@click.option(
    "--dev", is_flag=True, default=False, help="Setup for the development server."
)
def initialise(dev: bool = False):
    """
    Initialise the client on the system.
    """
    email = input("Enter your email for modelevaluation.org: ")
    password = getpass.getpass("Enter your password for modelevaluation.org: ")

    click.echo("Testing connection...")
    client = Client(dev_mode=dev)

    try:
        client.login(email, password)
    except Exception as ex:
        click.echo("Unable to establish connection to server.", err=True)
        click.echo(ex.msg, err=True)
        sys.exit(1)

    click.echo("Connection established.")

    # Build out the dictionary and save it to the user home.
    credentials = dict(email=email, password=password)

    filename = "credentials.json" if not dev else "credentials-dev.json"

    cred_dir = Path.home() / ".meorg"
    cred_dir.mkdir(parents=True, exist_ok=True)
    cred_filepath = cred_dir / filename
    json.dump(credentials, open(cred_filepath, "w"), indent=4)

    click.echo("Credentials written to " + str(cred_filepath))


# Add groups for nested subcommands
@click.group("endpoints", help="API endpoint commands.")
def cli_endpoints():
    pass


@click.group("file", help="File commands.")
def cli_file():
    pass


@click.group("analysis", help="Analysis commands.")
def cli_analysis():
    pass


# Add file commands
cli_file.add_command(file_list)
cli_file.add_command(file_upload)
cli_file.add_command(file_upload_parallel)
cli_file.add_command(file_attach)

# Add endpoint commands
cli_endpoints.add_command(list_endpoints)

# Add analysis commands
cli_analysis.add_command(analysis_start)
cli_analysis.add_command(analysis_status)

# Add subparsers to the master
cli.add_command(cli_endpoints)
cli.add_command(cli_file)
cli.add_command(cli_analysis)
cli.add_command(initialise)


if __name__ == "__main__":
    cli()
