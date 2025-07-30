from datetime import datetime
import pytz
import logging


def time_parser(time_string):
    """Parses the time string into a datetime object"""
    logger = logging.getLogger("pyglog")
    try:
        parts = time_string.split(".")
        dt = parts[0]
        offset = parts[1].split("-")
        time_string = dt + "_" + "-" + offset[1]
        format_data = "%Y-%m-%dT%H:%M:%S_%z"
        time_obj = datetime.strptime(time_string, format_data)
        return time_obj
    except (ValueError, IndexError) as e:
        logger.error("Error parsing time string: %s", time_string)
        logger.error("Assigning epoch date")
        logger.error("Error: %s", e)
        time_obj = datetime.fromtimestamp(0, pytz.utc)
        return time_obj


def check_sidecar_has_config(sidecar, config_id):
    """Checks if the sidecar has the configuration"""
    for assignment in sidecar["assignments"]:
        if assignment["configuration_id"] == config_id:
            return True
    return False


def filter_sidecars_by_search(sidecars, search_string):
    """Filter sidecars by search string in node name"""
    return [
        sidecar for sidecar in sidecars 
        if search_string.lower() in sidecar["node_name"].lower()
    ]


def filter_configurations_by_tag(configurations, tag):
    """Filter configurations by tag"""
    tag_match = []
    for configuration in configurations:
        if len(configuration["tags"]) == 0:
            continue
        for t in configuration["tags"]:
            if tag.lower() == t.lower():
                tag_match.append(configuration)
                break
    return tag_match


def sort_by_name(items, name_key="name"):
    """Sort items by name key"""
    return sorted(items, key=lambda x: x[name_key])


def sort_sidecars_by_node_name(sidecars):
    """Sort sidecars by node_name"""
    return sorted(sidecars, key=lambda x: x["node_name"])