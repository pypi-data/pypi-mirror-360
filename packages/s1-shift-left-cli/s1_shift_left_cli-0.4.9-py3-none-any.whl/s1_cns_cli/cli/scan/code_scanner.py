import logging

from s1_cns_cli.cli.config import init_config_manager
from s1_cns_cli.cli.registry import CodeTypeSubParser, MissingConfigException, GET_CONFIG_DATA_API, HttpMethod, \
    InvalidInputException, MissingRequiredFlagsException, SUPPORTED_GIT_PROVIDERS, REPO_URL_MAX_LENGTH, \
    REPO_FULL_NAME_MAX_LENGTH
from s1_cns_cli.cli.scan import iac, secret
from s1_cns_cli.cli.scan import vulnerability
from s1_cns_cli.cli.utils import check_if_paths_exist, make_request, read_json_file, get_config_path, upsert_s1_cns_cli

LOGGER = logging.getLogger("cli")


def handle_scan_sub_parser(args, cache_directory):
    global_pre_evaluation(args, cache_directory)
    if args.scan_type_sub_parser == CodeTypeSubParser.IAC:
        return iac.iac_parser(args, cache_directory)
    elif args.scan_type_sub_parser == CodeTypeSubParser.SECRET:
        return secret.secret_parser(args, cache_directory)
    elif args.scan_type_sub_parser == CodeTypeSubParser.VULN:
        return vulnerability.vulnerability_parser(args, cache_directory)

def validate_tag(tag):
    if not isinstance(tag, str):
        return False

    parts = tag.split(':')
    if len(parts) != 2:
        return False

    a, b = parts
    if not a or not b:
        return False

    return True

def get_mandatory_flags(args) -> list[str]:
    if args.scan_type_sub_parser == CodeTypeSubParser.IAC:
        return ["repo_url", "branch", "repo_full_name", "provider"]
    elif args.scan_type_sub_parser == CodeTypeSubParser.SECRET:
        return ["repo_url", "repo_full_name", "provider"]
    else: return []

def snake_to_kebab(snake_case: str) -> str:
    return snake_case.replace('_', '-')

def validate_publish_results_flags(args):
    if not hasattr(args, 'publish_result') or not args.publish_result:
        return

    mandatory_flags = get_mandatory_flags(args)
    for flag in mandatory_flags:
        if not getattr(args, flag, ""):
            raise MissingRequiredFlagsException(
                f"{snake_to_kebab(flag)} required to publish results to sentinelOne cns")

    if len(args.repo_url) > REPO_URL_MAX_LENGTH:
        raise InvalidInputException(f"repo-url exceeds the maximum allowed length of {REPO_URL_MAX_LENGTH} characters")

    if len(args.repo_full_name) > REPO_FULL_NAME_MAX_LENGTH:
        raise InvalidInputException(f"repo-full-name exceeds the maximum allowed length of {REPO_FULL_NAME_MAX_LENGTH} characters")

    if args.provider not in SUPPORTED_GIT_PROVIDERS:
        raise InvalidInputException(f"provider '{args.provider}' is not supported. supported providers are: {SUPPORTED_GIT_PROVIDERS}")

    if not args.repo_url.startswith("https://"):
        raise InvalidInputException( "repository url must start with 'https://'")

    if '/' not in args.repo_full_name:
        raise InvalidInputException("repository full name should be in the format 'owner/repoName'")

# global_pre_evaluation: will check we have updated s1-cns-cli and configs
def global_pre_evaluation(args, cache_directory):
    global_config_file_path = get_config_path(cache_directory)
    if not check_if_paths_exist([cache_directory, global_config_file_path]):
        raise MissingConfigException()

    global_config_data = read_json_file(global_config_file_path)
    management_console_url = global_config_data.get("management_console_url")

    if (hasattr(args, 'list_detectors') and args.list_detectors) or (hasattr(args, 'list_plugins') and args.list_plugins):
        data = {
            "global": global_config_data,
            "secret": {},
            "iac": {},
            "vuln": {}
        }
        init_config_manager(data)
        return

    tag = global_config_data.get("tag")
    scope_type = global_config_data.get("scope_type")
    scope_id = global_config_data.get("scope_id")
    if len(args.tag) > 0:
        tag = args.tag

    if len(tag) == 0:
        raise MissingConfigException("missing 'tag', please reconfigure cli or use the '--tag' flag.")

    if len(management_console_url) == 0:
        raise MissingConfigException("'management_console_url' is required, please reconfigure using '--management_console_url "
                            " flag")

    if not validate_tag(tag):
        raise InvalidInputException("tag must include a colon (':') that separates a non-empty key and value. For example: 'key:value'.")

    validate_publish_results_flags(args)

    response = make_request(HttpMethod.GET, management_console_url + GET_CONFIG_DATA_API, global_config_data["service_user_api_token"],
                            {"tag": tag, "scopeType": scope_type, "scopeIds": scope_id})

    data = response.json()["data"]

    # merge cli_global_config with response global_config
    data["global"] = {**data["global"], **global_config_data}
    init_config_manager(data)
    upsert_s1_cns_cli(cache_directory)
