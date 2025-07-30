import logging
import os
from s1_cns_cli.cli.registry import HttpMethod, GET_CONFIG_DATA_URL, InvalidInput, ConfigTypeSubParser, \
    CONFIG_FILE_NAME, GlobalConfig
from s1_cns_cli.cli.utils import make_request, add_global_config_file, add_iac_config_file, \
    add_secret_config_file, add_vulnerability_config_file, upsert_s1_cns_cli, read_json_file, write_json_to_file, \
    get_cache_directory
from urllib.parse import urlparse

LOGGER = logging.getLogger("cli")


def set_configs(args):
    if args.api_token == "":
        update_global_configurations(args, get_cache_directory())
        return

    parsed_url = urlparse(args.endpoint_url)
    if parsed_url.scheme != "http" and parsed_url.scheme != "https":
        raise InvalidInput("Please add a valid protocol.")
    args.endpoint_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    response = make_request(HttpMethod.GET, args.endpoint_url + GET_CONFIG_DATA_URL, args.api_token)
    admin_configs = response.json()

    add_global_config_file(args, admin_configs)
    add_iac_config_file(args.cache_directory, admin_configs)
    add_secret_config_file(args.cache_directory, admin_configs)
    add_vulnerability_config_file(args.cache_directory, admin_configs)

    upsert_s1_cns_cli(args.cache_directory)
    LOGGER.info("SentinelOne CNS CLI Configured Successfully!")
    return 0


def update_global_configurations(args, cache_directory):
    global_config_file_path = os.path.join(cache_directory, CONFIG_FILE_NAME)

    if not os.path.exists(global_config_file_path):
        LOGGER.warning("Please configure SentinelOne CNS CLI using s1-cns-cli config --api-token <API-TOKEN>")
        return

    updated_config_data = {}
    stored_config_data = read_json_file(global_config_file_path)
    if args.output_format != stored_config_data[GlobalConfig.OUTPUT_FORMAT]:
        updated_config_data[GlobalConfig.OUTPUT_FORMAT] = args.output_format
    if args.output_file != "":
        updated_config_data[GlobalConfig.OUTPUT_FILE] = args.output_file
    if args.workers_count != stored_config_data[GlobalConfig.WORKERS_COUNT]:
        updated_config_data[GlobalConfig.WORKERS_COUNT] = args.workers_count
    if args.on_crash_exit_code != stored_config_data[GlobalConfig.ON_CRASH_EXIT_CODE]:
        updated_config_data[GlobalConfig.ON_CRASH_EXIT_CODE] = args.on_crash_exit_code

    if len(updated_config_data) == 0:
        return


    write_json_to_file(global_config_file_path, {**stored_config_data, **updated_config_data})
    LOGGER.info("Configurations updated successfully!!")