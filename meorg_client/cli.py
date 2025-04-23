"""Command Line Interface"""

import click
from meorg_client.client import Client
import meorg_client.utilities as mcu
import meorg_client.constants as mcc
from meorg_client import __version__
import json
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

    credentials = mcu.get_user_data_filepath("credentials.json")
    credentials_dev = mcu.get_user_data_filepath("credentials-dev.json")

    # In dev mode and the configuration file exists
    if mcu.is_dev_mode() and credentials_dev.is_file():
        credentials = mcu.load_user_data("credentials-dev.json")

    # In dev mode and it doesn't (i.e. Actions)
    elif mcu.is_dev_mode() and not credentials_dev.is_file():
        credentials = dict(
            email=os.getenv("MEORG_EMAIL"), password=os.getenv("MEORG_PASSWORD")
        )

    # Production credentials
    else:
        credentials = mcu.load_user_data("credentials.json")

    # Get the client
    return Client(
        email=credentials["email"],
        password=credentials["password"],
        dev_mode=mcu.is_dev_mode(),
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
        if mcu.is_dev_mode():
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
@click.argument("id")
@click.option("-n", default=1, help="Number of threads for parallel uploads.")
def file_upload(file_path, id, n: int = 1):
    """
    Upload a file to the server.

    Prints Job ID on success, which is used by file-status to check transfer status.

    If attach_to is used then no ID is returned.
    """
    client = _get_client()

    # Upload the file, get the job ID
    responses = _call(
        client.upload_files,
        files=list(file_path),
        n=n,
        id=id,
        progress=True,
    )

    for response in responses:

        files = response.get("data").get("files")
        for f in files:
            click.echo(f.get("id"))


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


@click.command("delete_all")
@click.argument("output_id")
def file_delete_all(output_id: str):
    """Detach all files from a model output.

    Parameters
    ----------
    output_id : str
        Model output ID.
    """
    client = _get_client()
    _ = _call(client.delete_all_files_from_model_output, id=output_id)
    click.echo("SUCCESS")


@click.command("delete")
@click.argument("output_id")
@click.argument("file_id")
def file_delete(output_id: str, file_id: str):
    """Detach a file from a model output.

    Parameters
    ----------
    output_id : str
        Model output ID.
    """
    client = _get_client()
    _ = _call(client.delete_file_from_model_output, id=output_id, file_id=file_id)
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


@click.command("create")
@click.argument("mod_prof_id")
@click.argument("exp_id")
@click.argument("name")
def create_new_model_output(mod_prof_id: str, exp_id: str, name: str):
    """
    Create a new model output profile.


    Parameters
    ----------
    mod_prof_id : str
        Model profile ID.

    exp_id : str
        Experiment ID.

    name : str
        New model output name

    Prints modeloutput ID of created object, and whether it already existed or not.
    """
    client = _get_client()

    response = _call(
        client.model_output_create, mod_prof_id=mod_prof_id, exp_id=exp_id, name=name
    )

    if client.success():
        model_output_id = response.get("data").get("modeloutput")
        existing = response.get("data").get("existing")
        click.echo(f"Model Output ID: {model_output_id}")
        if existing is not None:
            click.echo("Warning: Overwriting existing model output ID")
    return model_output_id


@click.command("query")
@click.argument("model_id")
def model_output_query(model_id: str):
    """
    Get details for a specific new model output entity

    Parameters
    ----------
    model_id : str
        Model Output ID.

    Prints the `id` and `name` of the modeloutput, and JSON representation for the remaining metadata.
    """
    client = _get_client()

    response = _call(client.model_output_query, model_id=model_id)

    if client.success():

        model_output_data = response.get("data").get("modeloutput")
        model_output_id = model_output_data.get("id")
        name = model_output_data.get("name")
        if mcu.is_dev_mode():
            click.echo(f"Model Output: {json.dumps(model_output_data, indent=4)}")
        else:
            click.echo(f"Model Output ID: {model_output_id}")
            click.echo(f"Model Output Name: {name}")


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


@click.group("output", help="Model output commands.")
def cli_model_output():
    pass


# Add file commands
cli_file.add_command(file_list)
cli_file.add_command(file_upload)
cli_file.add_command(file_delete)
cli_file.add_command(file_delete_all)

# Add endpoint commands
cli_endpoints.add_command(list_endpoints)

# Add analysis commands
cli_analysis.add_command(analysis_start)
cli_analysis.add_command(analysis_status)

# Add output command
cli_model_output.add_command(create_new_model_output)
cli_model_output.add_command(model_output_query)

# Add subparsers to the master
cli.add_command(cli_endpoints)
cli.add_command(cli_file)
cli.add_command(cli_analysis)
cli.add_command(initialise)
cli.add_command(cli_model_output)


if __name__ == "__main__":
    cli()
