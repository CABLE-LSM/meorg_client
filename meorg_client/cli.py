"""Command Line Interface"""
import click
from meorg_client.client import Client
import meorg_client.utilities as mcu
import os
import sys
from inspect import getmembers
import getpass
from pathlib import Path
import json


def _get_client():
    """Get an authenticated client.

    Returns
    -------
    meorg_client.client.Client
        Client object.
    """
    # Get the dev-mode flag from the environment, better than passing the dev flag everywhere.
    dev_mode = os.getenv("MEORG_DEV_MODE", "0") == "1"

    credentials = mcu.get_user_data_filepath('credentials.json')
    credentials_dev = mcu.get_user_data_filepath('credentials-dev.json')

    # In dev mode and the configuration file exists
    if dev_mode and credentials_dev.is_file():
        credentials = mcu.load_user_data('credentials-dev.json')
    
    # In dev mode and it doesn't (i.e. Actions)
    elif dev_mode and not credentials_dev.is_file():
        credentials = dict(
            email=os.getenv('MEORG_EMAIL'),
            password=os.getenv('MEORG_PASSWORD')
        )
    
    # Production credentials
    else:
        credentials = mcu.load_user_data("credentials.json")

    # Get the client
    return Client(
        email=credentials["email"], password=credentials["password"], dev_mode=dev_mode
    )


def _call(func, **kwargs):
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
        sys.exit(1)


@click.group()
def cli():
    """
    ModelEvaluation.org client utility.
    """
    pass


@click.command()
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


@click.command()
@click.argument("id")
def file_status(id):
    """
    Check the file status based on the job ID from file-upload.

    Prints the true file ID or a status.
    """
    client = _get_client()
    response_data = _call(client.get_file_status, id=id).get("data")

    # If the file is complete (transferred to object store), get the true ID
    if response_data.get("status") == "complete":
        file_id = response_data.get("files")[0].get("file")
        click.echo(file_id)
    else:
        click.echo("Pending")


@click.command()
@click.argument("file_path")
def file_upload(file_path):
    """
    Upload a file to the server.

    Prints Job ID on success, which is used by file-status to check transfer status.
    """
    client = _get_client()

    # Upload the file, get the job ID
    response = _call(client.upload_file, file_path=file_path)
    job_id = response.get("data").get("jobId")
    click.echo(job_id)


@click.command()
@click.argument("id")
def file_list(id):
    """
    List the files currently attached to a model output.

    Prints 1 File ID per line.
    """
    client = _get_client()
    response = _call(client.list_files, id=id)

    for f in response.get("data").get("files"):
        click.echo(f)


@click.command()
@click.argument("file_id")
@click.argument("output_id")
def file_attach(file_id, output_id):
    """
    Attach a file to a model output.
    """
    client = _get_client()

    response = _call(client.attach_files_to_model_output, id=output_id, files=[file_id])

    click.echo("SUCCESS")


@click.command()
@click.argument("id")
def analysis_start(id):
    """
    Start the analysis for the model output id.

    Prints the Analysis ID, which can be used in analysis-status.
    """
    client = _get_client()

    response = _call(client.start_analysis, id=id)

    if client.success():
        analysis_id = response.get("data").get("analysisId")
        click.echo(analysis_id)


@click.command()
@click.argument("id")
def analysis_status(id):
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
def initialise(dev=False):
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

    print("Connection established.")

    # Build out the dictionary and save it to the user home.
    credentials = dict(email=email, password=password)

    filename = "credentials.json" if not dev else "credentials-dev.json"

    cred_dir = Path.home() / ".meorg"
    cred_dir.mkdir(parents=True, exist_ok=True)
    cred_filepath = cred_dir / filename
    json.dump(credentials, open(cred_filepath, "w"), indent=4)

    click.echo("Credentials written to " + str(cred_filepath))


# Add all of the commands automatically
for name, obj in getmembers(sys.modules[__name__]):
    if isinstance(obj, click.core.Command) and name != "cli":
        cli.add_command(obj)


if __name__ == "__main__":
    cli()
