import logging
import os
import sys
import traceback

from sentry_sdk import start_transaction, configure_scope

import s1_cns_cli.cli.command_line_arguments as CommandLineArgs
from s1_cns_cli.cli.config import config
from s1_cns_cli.cli.registry import MainSubParser, MissingConfigException, MissingRequiredFlagsException, \
    PlatformNotSupportedException, \
    RequestTimeoutException, HttpConnectionException, MissingDependenciesException, UnauthorizedUserException, \
    CodeTypeSubParser, InvalidInputException, \
    NotFoundException, ScanNotEnabledException, BadRequestException, GET_LATEST_VERSION_API, HttpMethod, \
    ServiceNotAvailableException, AccessDeniedException, ScanFailedException
from s1_cns_cli.cli.scan import code_scanner
from s1_cns_cli.cli.utils import initialize_logger, get_cache_directory, get_exit_code_on_crash, \
    send_exception_to_sentry, add_sentry_tags, DownloadException, delete_all_cache, get_config_path, read_json_file, \
    make_request, get_version
from s1_cns_cli.sentry import init_sentry, drain_sentry

root_logger = logging.getLogger()
if root_logger.hasHandlers():
    for handler in root_logger.handlers:
        handler.setLevel(logging.CRITICAL)
LOGGER = logging.getLogger("cli")


def main(args, cache_directory):
    # print(SENTINELONE_CNS_ART)
    if args.main_sub_parser == MainSubParser.SCAN:
        return code_scanner.handle_scan_sub_parser(args, cache_directory)
    elif args.main_sub_parser == MainSubParser.CONFIG:
        return config.configure(args)

def get_latest_version(cache_directory):
    try:
        global_config_file_path = get_config_path(cache_directory)
        if not os.path.exists(global_config_file_path):
            return None

        global_config_data = read_json_file(global_config_file_path)

        management_console_url = global_config_data["management_console_url"]
        api_token = global_config_data["service_user_api_token"]
        vuln_db_url = management_console_url + GET_LATEST_VERSION_API
        query_params = {
            "scopeType": global_config_data["scope_type"],
            "scopeIds": global_config_data["scope_id"]
        }
        response = make_request(HttpMethod.GET, vuln_db_url, api_token, query_params)
        return response.json()["data"]
    except Exception as e:
        LOGGER.debug(str(e))
        return None

def check_update_available(latest_version_details):
    if latest_version_details is None:
        return
    current_version = get_version()
    latest_version = latest_version_details.get("version", current_version)
    message = latest_version_details.get("message", "")
    formatted_message = message.format(current_version=current_version)
    if current_version < latest_version and len(formatted_message) > 0:
        LOGGER.warning(formatted_message)

def start():
    cache_directory = ""
    log_level = 20
    args = None
    try:
        # when s1-cns-cli invoked without any arguments.
        if (len(sys.argv) < 2) or \
                (len(sys.argv) == 2 and (sys.argv[1] == MainSubParser.SCAN or sys.argv[1] == MainSubParser.CONFIG)) or \
                (len(sys.argv) == 3 and \
                 sys.argv[1] == MainSubParser.SCAN and \
                 (sys.argv[2] == CodeTypeSubParser.IAC or
                  sys.argv[2] == CodeTypeSubParser.SECRET or
                  sys.argv[2] == CodeTypeSubParser.VULN)):
            sys.argv.append("--help")

        args = CommandLineArgs.evaluate_command_line_arguments()

        if args.debug:
            log_level = 10
        initialize_logger("cli", log_level)

        cache_directory = get_cache_directory()

        if cache_directory and not args.disable_sentry:
            init_sentry(cache_directory)

        with start_transaction(name=args.main_sub_parser) as transaction:
            latest_version_details = get_latest_version(cache_directory)
            exit_code = main(args, cache_directory)
            LOGGER.debug(f"Exiting with code {exit_code}")
            check_update_available(latest_version_details)
            with configure_scope() as scope:
                add_sentry_tags(scope, cache_directory)
                transaction.finish()
                sys.exit(exit_code)
    except KeyboardInterrupt:
        pass
    except NotFoundException as e:
        LOGGER.error(e)
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except InvalidInputException as e:
        LOGGER.warning(e)
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except UnauthorizedUserException as e:
        LOGGER.warning(f"{e}. Please use a valid token to access SentinelOne CNS CLI.")
        delete_all_cache(cache_directory)
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except BadRequestException as e:
        LOGGER.warning(f"{e}")
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except MissingDependenciesException as e:
        LOGGER.warning(
            "Missing some required dependencies.\nTry reconfiguring: s1-cns-cli config --api-token "
            "<sentinelone-cns-api-token> ...")
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except ScanFailedException as e:
        exception_args = e.args
        if len(exception_args) > 0:
            LOGGER.error(exception_args[0])
        else:
            LOGGER.error(f"Scan failed, please try again. If problem still persist please contact SentinelOne support")
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except HttpConnectionException as e:
        LOGGER.error("Something went wrong. Please check your internet connection or contact SentinelOne CNS customer "
                       "support.")
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except ServiceNotAvailableException as e:
        LOGGER.error(e)
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except AccessDeniedException as e:
        LOGGER.error(e)
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except RequestTimeoutException as e:
        LOGGER.error("request timed out, please try again")
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except MissingConfigException as e:
        exception_args = e.args
        if len(exception_args) == 0:
            LOGGER.error(
                "Missing required configurations.\nTry reconfiguring: s1-cns-cli config --service-user-api-token "
                " <api-token> --management-console-url <url>"
                "...")
        else:
            LOGGER.error(exception_args[0])
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except MissingRequiredFlagsException as e:
        LOGGER.error(e)
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except PlatformNotSupportedException as e:
        LOGGER.warning(e)
        send_exception_to_sentry(e, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except ScanNotEnabledException as e:
        LOGGER.error(e)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except DownloadException as e:
        LOGGER.error("Failed to download some required dependencies")
        LOGGER.debug(e)
        msg = str(e) + f", \n\nurl : `{e.url}`" + f", \n\nfile: `{e.filename}`"
        send_exception_to_sentry(DownloadException(msg), cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except KeyError as e:
        msg = f"key: {e.args[0]} not found in the dictionary"
        LOGGER.error(msg)
        LOGGER.debug(traceback.format_exc())
        send_exception_to_sentry(msg, cache_directory)
        sys.exit(get_exit_code_on_crash(cache_directory))
    except Exception as e:
        if log_level == 10:
            LOGGER.debug(str(e))
            # print stacktrace
            LOGGER.debug(traceback.format_exc())
        code = get_exit_code_on_crash(cache_directory)
        send_exception_to_sentry(e, cache_directory)
        LOGGER.error(f"Something went wrong. Exiting with status code: {code}")
        sys.exit(code)
    finally:
        if args and not args.disable_sentry:
            drain_sentry()


if __name__ == "__main__":
    start()
