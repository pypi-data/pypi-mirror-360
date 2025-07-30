import os.path
from enum import Enum

from s1_cns_cli.version import build_type

CONFIG_FILE_NAME = "config.json"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG_ENABLED = 0
BASELINE_FILE = ".baseline"
PACKAGE_NAME = "s1_shift_left_cli"
DEFAULT_TIMEOUT = 10
BINARY_LIST = ["bin_secret_detector", "bin_eval_rego", "bin_vulnerability_scanner"]
SENTRY_TAGS = ["management_console_url", "scope_id", "scope_type"]
DEFAULT_IAC_CACHE_UPDATE_FREQUENCY = 12
REPO_URL_MAX_LENGTH = 1024
REPO_FULL_NAME_MAX_LENGTH = 256

MAIN_PIP_COMMAND = ["pip3", "install", "--upgrade", PACKAGE_NAME]
TEST_PIP_COMMAND = [
    "pip3",
    "install",
    "-i",
    "https://test.pypi.org/simple/",
    "--upgrade",
    PACKAGE_NAME,
    "--extra-index-url",
    "https://pypi.org/simple",
]

MAIN_PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
TEST_PYPI_URL = f"https://test.pypi.org/pypi/{PACKAGE_NAME}/json"

PIP_COMMAND = MAIN_PIP_COMMAND if build_type == "pypi" else TEST_PIP_COMMAND
PYPI_URL = MAIN_PYPI_URL if build_type == "pypi" else TEST_PYPI_URL

APP_URL = "https://app.pingsafe.com"
APP2_URL = "https://app2.pingsafe.com"
LOCAL_URL = "http://localhost:8080"

GET_PRE_SIGNED_URL_API = "/web/api/v2.1/cnapp/cli/setup"
GET_CONFIG_DATA_API = "/web/api/v2.1/cnapp/cli/config"
DOWNLOAD_IAC_CACHE_API = "/web/api/v2.1/cnapp/cli/iac/cache"
DOWNLOAD_VULN_DB_INFO_API = "/web/api/v2.1/cnapp/cli/vuln/db"
PUBLISH_ISSUES_API = "/web/api/v2.1/cnapp/cli/publish/issues"
GET_LATEST_VERSION_API = "/web/api/v2.1/cnapp/cli/latest-version"

DEFAULT_SENTINELONE_CNS_DIR = ".s1cns"
BINARY_DIR = "bin"
SENTINELONE_CNS_LOCAL_CONFIG_PATH = os.path.join(
    DEFAULT_SENTINELONE_CNS_DIR, "local_config.json"
)
SUPPORTED_FRAMEWORKS = [
    "TERRAFORM",
    "TERRAFORM_PLAN",
    "CLOUDFORMATION",
    "KUBERNETES",
    "HELM",
]

SUPPORTED_GIT_PROVIDERS = ["GITHUB", "GITLAB", "BITBUCKET", "AZURE_REPOS"]

SENTINELONE_JSON = "s1-cns-json"
DEFECT_DOJO_GENERIC_FORMAT = "defect-dojo-generic-format"

SEVERITIES = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
DEFAULT_EXTENSIONS_TO_EXCLUDE = [
    ".git",
    "__pycache__",
    "venv",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".svg",
    ".eot",
    ".pdf",
    ".jpeg",
    ".png",
    ".jpg",
    ".mp3",
    ".mp4",
]

SEVERITY_MAP = {"CRITICAL": "10.0", "MEDIUM": "6.0", "HIGH": "7.0", "LOW": "1.0"}

SEVERITY_TO_NUMBER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}

SENTINELONE_CNS_ART = """
   _____            _   _            _  ____                _____ _   _  _____    _____ _      _____ 
  / ____|          | | (_)          | |/ __ \              / ____| \ | |/ ____|  / ____| |    |_   _|
 | (___   ___ _ __ | |_ _ _ __   ___| | |  | |_ __   ___  | |    |  \| | (___   | |    | |      | |  
  \___ \ / _ \ '_ \| __| | '_ \ / _ \ | |  | | '_ \ / _ \ | |    | . ` |\___ \  | |    | |      | |  
  ____) |  __/ | | | |_| | | | |  __/ | |__| | | | |  __/ | |____| |\  |____) | | |____| |____ _| |_ 
 |_____/ \___|_| |_|\__|_|_| |_|\___|_|\____/|_| |_|\___|  \_____|_| \_|_____/   \_____|______|_____|                                                                                                         
"""


class MainSubParser(str, Enum):
    SCAN = "scan"
    CONFIG = "config"


class CodeTypeSubParser(str, Enum):
    IAC = "iac"
    SECRET = "secret"
    VULN = "vuln"


class ConfigTypeSubParser(str, Enum):
    SECRET = "secret"


class GlobalConfig(str, Enum):
    SERVICE_USER_API_TOKEN = "service_user_api_token"
    CACHE_DIRECTORY = "cache_directory"
    ON_CRASH_EXIT_CODE = "on_crash_exit_code"
    WORKERS_COUNT = "workers_count"
    MANAGEMENT_CONSOLE_URL = "management_console_url"
    IAC_LAST_REFRESHED_AT = "iac_last_refreshed_at"
    SCOPE_ID = "scope_id"
    SCOPE_TYPE = "scope_type"
    TAG = "tag"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"

class SCOPE_TYPE(str, Enum):
    ACCOUNT = "ACCOUNT"
    SITE = "SITE"

class IacFramework(str, Enum):
    ALL = "all"
    TERRAFORM = "terraform"
    TERRAFORM_PLAN = "terraform-plan"
    CLOUDFORMATION = "cloudformation"
    KUBERNETES = "kubernetes"
    HELM = "helm"


class IacConfigData(str, Enum):
    LAST_REFRESHED_AT = "last_refreshed_at"


class OUTPUT_FORMAT(str, Enum):
    JSON = "JSON"
    CSV = "CSV"
    SARIF = "SARIF"


class MissingConfigException(Exception):
    pass


class HttpConnectionException(Exception):
    pass


class RequestTimeoutException(Exception):
    pass


class MissingRequiredFlagsException(Exception):
    pass


class PlatformNotSupportedException(Exception):
    pass

class ServiceNotAvailableException(Exception):
    pass

class MissingDependenciesException(Exception):
    pass


class InvalidGraphConnection(Exception):
    pass


class UnauthorizedUserException(Exception):
    pass

class AccessDeniedException(Exception):
    pass

class ScanFailedException(Exception):
    pass

class BadRequestException(Exception):
    pass

class NotFoundException(Exception):
    pass


class InvalidInputException(Exception):
    pass


class ScanNotEnabledException(Exception):
    pass


class RegoException(Exception):
    pass


class DownloadException(Exception):
    def __init__(self, message, url="", filename=""):
        super().__init__(message)
        self.url = url
        self.filename = filename


class LogColors(str, Enum):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    OKORANGE = "\033[38;5;208m"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DEFAULT_GLOBAL_CONFIGURATIONS(Enum):
    WORKERS_COUNT = 5
    ON_CRASH_EXIT_CODE = 1
    OUTPUT_FORMAT = OUTPUT_FORMAT.JSON


GLOBAL_EPILOG = """
Examples:
    Configure SentinelOne CNS CLI:
        s1-cns-cli config --help

    Scan using SentinelOne CNS CLI:
        s1-cns-cli scan --help

    Get result on a file:
        s1-cns-cli --output-file <path/to/file.ext> --output-format <JSON/CSV> scan [sub-command]

Use "s1-cns-cli [command] --help" for more information about a command.
"""


SCAN_EPILOG = """
Examples:
    IaC Scan:
        s1-cns-cli scan iac --help
        
    Secret Detection Scan:
        s1-cns-cli scan secret --help
        
    Vulnerability Scan & SBOM generator:
        s1-cns-cli scan vuln --help
"""


CONFIG_EPILOG = """
Examples:
    Configure SentinelOne CNS CLI:
        s1-cns-cli config --api-token <s1-service-user-api-token> --management-console-url <console-url> --scope-type <scope-type> --scope-id <scope-id>

    Other flags while configuring:
             s1-cns-cli config  --service-user-api-token <s1-service-user-api-token> (required)
                                --management-console-url <url> (required)
                                --scope-id <s1-scope-id> (optional: required)
                                --scope-type <s1-scope> (default: ACCOUNT)
                                --workers-count <int> (optional, default: 5)
                                --on-crash-exit-code <int> (optional, default: 1)
"""


IAC_EPILOG = """
Examples:
    List plugins:
        s1-cns-cli scan iac --list-plugins
        
    Scan a directory:
        s1-cns-cli scan iac -d <path/to/dir>
        
    Generate baseline:
        s1-cns-cli scan iac -d <path/to/dir> --generate-baseline (optional, default: false)
        
    Generate sarif report
        s1-cns-cli --output-format SARIF --output-file <path/to/file.sarif> scan iac -d <path/to/dir>
        
    Delete IaC cache:
        s1-cns-cli scan iac --invalidate-cache
    
    Other flags:
        s1-cns-cli scan iac -d <path/to/dir> (mandatory)
                              --frameworks <all/terraform/cloudformation/kubernetes/helm> (optional, default: all)
                              --include-ignored (optional, default: false)
                              --download-external-modules (optional, default: false)
                              --var-file <file/1 file/2 ... file/n> (optional)
                              
"""


SECRET_EPILOG = """
Examples:
    List detectors:
        s1-cns-cli scan secret --list-detectors
    
    Scan a directory:
        s1-cns-cli scan secret -d <path/to/dir>
        
    Generate sarif report
        s1-cns-cli --output-format SARIF --output-file <path/to/file.sarif> scan secret -d <path/to/dir>
        
    Generate baseline:
        s1-cns-cli scan secret -d <path/to/dir> --generate-baseline --range <start_ref end_ref>
        
    Other flags:
        s1-cns-cli scan secret -d <path/to/dir> (mandatory)
                                 --disable-verification (optional, default: false)
                                 --mask-secret (optional, default: false)
                                 --include-ignored (optional, default: false)
                                 --verified-only (optional, default: false)
                                 --pre-commit (optional, default: false)
                                 --scan-commit (optional, default: HEAD)
                                 --range <start_ref end_ref> (optional)
                                 --pull-request <src_branch dest_branch> (optional)
                                 --skip-paths <path/1 path/2 ... path/n> (optional)
                                 --excluded-detectors <DETECTOR_API_KEY_1 DETECTOR_API_KEY_2 ... DETECTOR_API_KEY_N> (optional)
"""


VULN_EPILOG = """
Examples:
    Scan a directory:
        s1-cns-cli scan vuln -d <path/to/dir>
        
    Scan a docker image:
        s1-cns-cli scan vuln --docker-image <image>
        
    Scan a private docker image:
        s1-cns-cli scan vuln --docker-image <image> --username <username> --password <password> --registry <registry>
        
    Generate sarif report
        s1-cns-cli --output-format SARIF --output-file <path/to/file.sarif> scan vuln -d <path/to/dir>
    
    Other flags:
        s1-cns-cli scan vuln --docker-image <image> (mandatory)
                               --fixed-only (optional, default: false)
                               --registry (default: index.docker.io)
                               --username (registry username)
                               --password (registry password)
"""
