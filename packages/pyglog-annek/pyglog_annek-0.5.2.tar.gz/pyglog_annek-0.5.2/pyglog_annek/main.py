from pprint import pprint as pp
import typer
import warnings

from .config import setup_environment, setup_logging
from .api_client import GraylogAPIClient
from .models import Sidecar
from .utils import (
    check_sidecar_has_config,
    filter_sidecars_by_search,
    filter_configurations_by_tag,
    sort_by_name,
    sort_sidecars_by_node_name,
)

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Setup
graylog_address, graylog_token = setup_environment()
logger = setup_logging()
client = GraylogAPIClient(graylog_address, graylog_token)

app = typer.Typer(no_args_is_help=True)




@app.callback()
def callback():
    """
    A CLI for Graylog API calls

    You must set GRAYLOG_ADDR and GRAYLOG_TOKEN or define them in a .env file.

    Example:

    GRAYLOG_ADDR="https://graylog.example.com"

    GRAYLOG_TOKEN="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    """


@app.command()
def list_sidecars(
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    List Sidecars
    """
    if not silent:
        print(f"Making request to {graylog_address}/api/sidecars/all")
    logger.info("list_sidecar invoked")
    response_data = client.get_all_sidecars()
    sidecar_list = response_data["sidecars"]
    sidecar_sorted = sort_sidecars_by_node_name(sidecar_list)
    if not silent:
        for sidecar in sidecar_sorted:
            print(
                f"{sidecar['node_name']}\tID: {sidecar['node_id']}\tLast_Seen: {sidecar['last_seen']}"
            )
    return sidecar_sorted


@app.command()
def list_configurations(
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    List Sidecar Configurations
    """
    if not silent:
        print(f"Making request to {graylog_address}/api/sidecar/configurations")
    logger.info("list_configurations invoked")
    response_data = client.get_configurations()
    configuration_list = response_data["configurations"]
    configuration_sorted = sort_by_name(configuration_list)
    for configuration in configuration_sorted:
        if not silent:
            print(
                f"{configuration['name']:<40} ID: {configuration['id']:<30} Tags: {str(configuration['tags']):<15}"
            )
    return configuration_sorted


@app.command()
def list_configurations_by_tag(
    tag: str,
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    List Sidecar Configurations associated with tag

    Arguments:

    tag: The name of the tag.
    """
    if not silent:
        print(f"Making request to {graylog_address}/api/sidecar/configurations")
    logger.info("list_configurations_by_tag invoked")
    response_data = client.get_configurations()
    configuration_list = response_data["configurations"]
    configuration_sorted = sort_by_name(configuration_list)
    tag_match = filter_configurations_by_tag(configuration_sorted, tag)
    
    if not silent:
        for configuration in tag_match:
            print(
                f"{configuration['name']:<40} ID: {configuration['id']:<30} Tags: {str(configuration['tags']):<15}"
            )
    return tag_match


@app.command()
def list_matching_sidecars(search_string: str):
    """
    List Sidecars that contain the search string

    Arguments:

    search_string: A substring that matches one or more sidecar hostnames.
    """
    print(f"Making request to {graylog_address}/api/sidecars/all")
    logger.info("list_matching_sidecars invoked")
    response_data = client.get_all_sidecars()
    sidecar_list = response_data["sidecars"]
    sidecar_sorted = sort_sidecars_by_node_name(sidecar_list)
    matching_sidecars = []
    for sidecar in sidecar_sorted:
        if search_string in sidecar["node_name"]:
            matching_sidecars.append(sidecar)
            print(
                f"{sidecar['node_name']}\tID: {sidecar['node_id']}\tLast_Seen: {sidecar['last_seen']}"
            )
    return matching_sidecars


@app.command()
def get_configuration_by_id(
    configuration_id: str,
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    Get details for a configuration by ID.
    """
    if not silent:
        print(f"Making request to {graylog_address}/api/sidecar/configurations/{configuration_id}")
    logger.info("get_configurations_by_id invoked")
    result = client.get_configuration_by_id(configuration_id)
    if not silent:
        pp(result)
    return result


@app.command()
def get_configuration_by_tag(
    configuration_tag: str,
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    Get details for a configuration by tag name.
    """
    configurations = list_configurations_by_tag(configuration_tag, silent=True)
    configuration_id = None
    if configurations:
        configuration_id = configurations[0]["id"]
    if configuration_id is None:
        print("No matching configuration found.")
        return
    if not silent:
        print(f"Making request to {graylog_address}/api/sidecar/configurations/{configuration_id}")
    logger.info("get_configurations_by_tag invoked")
    result = client.get_configuration_by_id(configuration_id)
    if not silent:
        pp(result)
    return result


@app.command()
def get_sidecar_by_id(sidecar_id: str):
    """
    Get sidecar by ID
    """
    logger.info("get_sidecar_by_id invoked")
    result = client.get_sidecar_by_id(sidecar_id)
    pp(result)
    return result


@app.command()
def get_sidecar_details(
    search_string: str,
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    Get details for Sidecars that match the search string

    Arguments:

    search_string: A string that matches sidecar hostnames.
    """
    logger.info("get_sidecar_details invoked")
    response_data = client.get_all_sidecars()
    sidecar_list = response_data["sidecars"]
    sidecar_sorted = sort_sidecars_by_node_name(sidecar_list)
    matching_sidecars = filter_sidecars_by_search(sidecar_sorted, search_string)
    matching_sidecar_objects = []
    
    if not silent:
        for sidecar in matching_sidecars:
            print(
                f"{sidecar['node_name']}\tID: {sidecar['node_id']}\tLast_Seen: {sidecar['last_seen']}"
            )
    if len(matching_sidecars) == 0:
        if not silent:
            print("No matching sidecars found.")
        return
    for sidecar in matching_sidecars:
        if not silent:
            print(f"Making request to {graylog_address}/api/sidecars/{sidecar['node_id']}")
        sidecar_data = client.get_sidecar_by_id(sidecar["node_id"])
        if not silent:
            pp(sidecar_data)
        sidecar_obj = Sidecar(**sidecar_data)
        matching_sidecar_objects.append(sidecar_obj)
    return matching_sidecar_objects


@app.command()
def apply_configuration_sidecars(
    search_string: str,
    tag_id: str,
    noconfirm: bool = typer.Option(
        False, "--no-confirm", help="Do not prompt for confirmation."
    ),
):
    """
    Apply a Configuration to Sidecars with a hostname that contains the search string.

    Arguments:

    search_string: A substring that matches one or more sidecar hostnames.

    tag_id: The tag used to locate the configuration to be applied
    """
    logger.info("get all sidecars invoked")
    response_data = client.get_all_sidecars()
    configurations = list_configurations_by_tag(tag_id, silent=True)
    if len(configurations) == 0:
        print("No matching configurations found.")
        return
    print(
        f"\n"
        f"Matching configuration found available for tag.\n"
        f"Name: {configurations[0]['name']} ID: {configurations[0]['id']}"
    )
    print("\n")
    config_id = configurations[0]["id"]
    config_details = get_configuration_by_id(config_id, silent=True)
    collector_id = config_details["collector_id"]
    request_origin = "pyglog"
    sidecar_list = response_data["sidecars"]
    sidecar_sorted = sort_sidecars_by_node_name(sidecar_list)
    matching_sidecars = filter_sidecars_by_search(sidecar_sorted, search_string)
    if len(matching_sidecars) == 0:
        print("No matching sidecars found.")
        return
    to_remove = []
    for sidecar in matching_sidecars:
        if check_sidecar_has_config(sidecar, config_id):
            print(
                f"Sidecar {sidecar['node_name']} already has the configuration applied, skipping."
            )
            to_remove.append(sidecar)
    for sidecar in to_remove:
        matching_sidecars.remove(sidecar)
    if len(matching_sidecars) == 0:
        print("\nAll listed sidecars already have that configuration applied.")
        return
    for sidecar in matching_sidecars:
        print(
            f"{sidecar['node_name']}\tID: {sidecar['node_id']}\tLast_Seen: {sidecar['last_seen']}"
        )
    if not noconfirm:
        input(
            "\nThe Configuration will be applied to the above sidecars, press CTRL + C to abort."
        )
    for sidecar in matching_sidecars:
        print(f"Making request to {graylog_address}/api/sidecars/configurations")
        print(f"Applying configuration to {sidecar['node_name']}")
        print(configurations)
        collector_id = configurations[0]["collector_id"]
        config_id = configurations[0]["id"]
        config_dict = {
            "assigned_from_tags": [],
            "collector_id": collector_id,
            "configuration_id": config_id,
        }
        sidecar["assignments"].append(config_dict)
        data = {
            "nodes": [
                {
                    "node_id": sidecar["node_id"],
                    "assignments": sidecar["assignments"]
                }
            ]
        }
        print(f"Data: {data}")
        logger.info("apply configuration posted to API")
        response = client.update_sidecar_configurations(data, request_origin)
        print(response.status_code)
        print(response.text)


@app.command()
def remove_configuration_sidecars(
    search_string: str,
    tag_id: str,
    noconfirm: bool = typer.Option(
        False, "--no-confirm", help="Do not prompt for confirmation."
    ),
):
    """
    Remove a Configuration from Sidecars with a hostname that contains the search string.

    Arguments:

    search_string: A substring that matches one or more sidecar hostnames.

    tag_id: The tag used to locate the configuration to be applied
    """
    response_data = client.get_all_sidecars()
    configurations = list_configurations_by_tag(tag_id, silent=True)
    if len(configurations) == 0:
        print("No matching configurations found.")
        return
    print(
        f"\n"
        f"Matching configuration found available for tag.\n"
        f"Name: {configurations[0]['name']} ID: {configurations[0]['id']}"
    )
    print("\n")
    config_id = configurations[0]["id"]
    request_origin = "pyglog"
    sidecar_list = response_data["sidecars"]
    sidecar_sorted = sort_sidecars_by_node_name(sidecar_list)
    matching_sidecars = filter_sidecars_by_search(sidecar_sorted, search_string)
    if len(matching_sidecars) == 0:
        print("No matching sidecars found.")
        return
    to_remove = []
    for sidecar in matching_sidecars:
        if not check_sidecar_has_config(sidecar, config_id):
            print(
                f"Sidecar {sidecar['node_name']} does not have the configuration applied, skipping."
            )
            to_remove.append(sidecar)
    for sidecar in to_remove:
        matching_sidecars.remove(sidecar)
    if len(matching_sidecars) == 0:
        print("\nNone of the listed sidecars have that configuration applied.")
        return
    for sidecar in matching_sidecars:
        print(
            f"{sidecar['node_name']}\tID: {sidecar['node_id']}\tLast_Seen: {sidecar['last_seen']}"
        )
    if not noconfirm:
        input(
            "\nThe Configuration will be removed from the above sidecars, press CTRL + C to abort."
        )
    for sidecar in matching_sidecars:
        print(f"Making request to {graylog_address}/api/sidecars/configurations")
        print(f"Removing configuration from {sidecar['node_name']}")
        config_id = configurations[0]["id"]
        removed = 0
        for assignment in sidecar["assignments"]:
            if assignment["configuration_id"] == config_id:
                sidecar["assignments"].remove(assignment)
                removed += 1
        if removed == 0:
            print(f"Configuration not applied to {sidecar['node_name']}.")
            print(
                "Configuration not found, or configuration was assigned via local tag."
            )
            break
        data = {
            "nodes": [
                {"node_id": sidecar["node_id"], "assignments": sidecar["assignments"]}
            ]
        }
        logger.info("remove configuration posted to API")
        response = client.update_sidecar_configurations(data, request_origin)
        print(response.status_code)
        print(response.text)
