import logging
import os
from urllib.parse import urlparse

from s1_cns_cli.cli.config.config_manager import ConfigManager
from s1_cns_cli.cli.registry import InvalidInputException, \
    CONFIG_FILE_NAME, GlobalConfig, MissingConfigException
from s1_cns_cli.cli.utils import add_global_config_file, \
    upsert_s1_cns_cli, read_json_file, write_json_to_file, \
    get_cache_directory

LOGGER = logging.getLogger("cli")
manager: ConfigManager = None


def configure(args):
    if args.service_user_api_token == "":
        update_global_configurations(args, get_cache_directory())
        return

    parsed_url = urlparse(args.management_console_url)
    if parsed_url.scheme != "http" and parsed_url.scheme != "https":
        raise InvalidInputException("Please add a valid protocol.")
    args.management_console_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    add_global_config_file(args)
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
    if args.workers_count != stored_config_data[GlobalConfig.WORKERS_COUNT]:
        updated_config_data[GlobalConfig.WORKERS_COUNT] = args.workers_count
    if args.on_crash_exit_code != stored_config_data[GlobalConfig.ON_CRASH_EXIT_CODE]:
        updated_config_data[GlobalConfig.ON_CRASH_EXIT_CODE] = args.on_crash_exit_code

    if len(updated_config_data) == 0:
        return

    write_json_to_file(global_config_file_path, {**stored_config_data, **updated_config_data})
    LOGGER.info("Configurations updated successfully!!")


def init_config_manager(config):
    global manager
    manager = ConfigManager(config)


def get_config_manager() -> ConfigManager:
    if manager is None:
        raise MissingConfigException()
    return manager
