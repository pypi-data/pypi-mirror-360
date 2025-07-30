import os.path
from enum import Enum
from s1_cns_cli.version import build_type

CONFIG_FILE_NAME = "config.json"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG_ENABLED = 0
BASELINE_FILE = ".baseline"
PACKAGE_NAME = "s1_cns_cli"
DEFAULT_TIMEOUT = 10
BINARY_LIST = ["bin_secret_detector", "bin_eval_rego", "bin_vulnerability_scanner"]
SENTRY_TAGS = ["org_id", "project_id"]

MAIN_PIP_COMMAND = ["pip3", "install", "--upgrade", PACKAGE_NAME]
TEST_PIP_COMMAND = ["pip3", "install", "-i", "https://test.pypi.org/simple/", "--upgrade",
                    PACKAGE_NAME, "--extra-index-url", "https://pypi.org/simple"]

MAIN_PYPI_URL = f'https://pypi.org/pypi/{PACKAGE_NAME}/json'
TEST_PYPI_URL = f'https://test.pypi.org/pypi/{PACKAGE_NAME}/json'

PIP_COMMAND = MAIN_PIP_COMMAND if build_type == "pypi" else TEST_PIP_COMMAND
PYPI_URL = MAIN_PYPI_URL if build_type == "pypi" else TEST_PYPI_URL

APP_URL = "https://app.pingsafe.com"
APP2_URL = "https://app2.pingsafe.com"
LOCAL_URL = "http://localhost:8080"

GET_PRE_SIGNED_URL = "/apis/v1/cli/setup"
GET_CONFIG_DATA_URL = "/apis/v1/cli/config"
DOWNLOAD_CACHE_URL = "/apis/v1/cli/iac/cache"

DEFAULT_SENTINELONE_CNS_DIR = ".s1cns"
BINARY_DIR = "bin"
SENTINELONE_CNS_LOCAL_CONFIG_PATH = os.path.join(DEFAULT_SENTINELONE_CNS_DIR, "local_config.json")
SUPPORTED_FRAMEWORKS = ["TERRAFORM", "TERRAFORM_PLAN", "CLOUDFORMATION", "KUBERNETES", "HELM"]

PUBLISH_ISSUES_API = "/apis/v1/cli/publish/issues"
SUPPORTED_GIT_PROVIDERS = ["GITHUB", "GITLAB", "BITBUCKET", "AZURE"]

SENTINELONE_JSON = "s1-cns-json"
DEFECT_DOJO_GENERIC_FORMAT = "defect-dojo-generic-format"

SEVERITIES = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
DEFAULT_EXTENSIONS_TO_EXCLUDE = [".git", "__pycache__", "venv", ".ttf", ".otf", ".woff", ".woff2", ".svg", ".eot",
                                 ".pdf", ".jpeg", ".png", ".jpg", ".mp3", ".mp4"]

SEVERITY_MAP = {
    "CRITICAL": "10.0",
    "MEDIUM": "6.0",
    "HIGH": "7.0",
    "LOW": "1.0"
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
    API_TOKEN = "api_token"
    CACHE_DIRECTORY = "cache_directory"
    OUTPUT_FILE = "output_file"
    OUTPUT_FORMAT = "output_format"
    ON_CRASH_EXIT_CODE = "on_crash_exit_code"
    WORKERS_COUNT = "workers_count"
    ENDPOINT_URL = "endpoint_url"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"


class IacFramework(str, Enum):
    ALL = "all"
    TERRAFORM = "terraform"
    TERRAFORM_PLAN = "terraform-plan"
    CLOUDFORMATION = "cloudformation"
    KUBERNETES = "kubernetes"
    HELM = "helm"


class IacConfigData(str, Enum):
    LAST_REFRESHED_AT = "last_refreshed_at"


class OutputFormat(str, Enum):
    JSON = "JSON"
    CSV = "CSV"
    SARIF = "SARIF"


class IgnoreStatus(str, Enum):
    PERMANENT = "PERMANENT"
    TEMPORARILY = "TEMPORARILY"


class MissingConfig(Exception):
    pass


class HttpConnectionError(Exception):
    pass


class RequestTimeout(Exception):
    pass


class MissingRequiredFlags(Exception):
    pass


class PlatformNotSupported(Exception):
    pass


class MissingDependencies(Exception):
    pass


class InvalidGraphConnection(Exception):
    pass


class UnauthorizedUser(Exception):
    pass


class NotFound(Exception):
    pass


class InvalidInput(Exception):
    pass


class RegoException(Exception):
    pass


class DownloadException(Exception):
    def __init__(self, message, url="", filename=""):
        super().__init__(message)
        self.url = url
        self.filename = filename


class LogColors(str, Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    OKORANGE = '\033[38;5;208m'


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DefaultGlobalConfigurations(Enum):
    WORKERS_COUNT = 5
    ON_CRASH_EXIT_CODE = 1
    OUTPUT_FORMAT = OutputFormat.JSON


GLOBAL_EPILOG = \
"""
Examples:
    Configure SentinelOne CNS CLI:
        s1-cns-cli config --help

    Scan using SentinelOne CNS CLI:
        s1-cns-cli scan --help

    Get result on a file:
        s1-cns-cli --output-file <path/to/file.ext> --output-format <JSON/CSV> scan [sub-command]

Use "s1-cns-cli [command] --help" for more information about a command.
"""


SCAN_EPILOG = \
"""
Examples:
    IaC Scan:
        s1-cns-cli scan iac --help
        
    Secret Detection Scan:
        s1-cns-cli scan secret --help
        
    Vulnerability Scan & SBOM generator:
        s1-cns-cli scan vuln --help
"""



CONFIG_EPILOG = \
"""
Examples:
    Configure SentinelOne CNS CLI:
        s1-cns-cli config --api-token <SENTINELONE_CNS-API-TOKEN>

    Other flags while configuring:
            s1-cns-cli config --api-token <SENTINELONE_CNS-API-TOKEN> (mandatory)
                                --output-file <path/to/file.ext> (optional)
                                --output-format <JSON/CSV> (optional, default: JSON)
                                --workers-count <int> (optional, default: 5)
                                --on-crash-exit-code <int> (optional, default: 0)
"""


IAC_EPILOG = \
"""
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


SECRET_EPILOG = \
"""
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


VULN_EPILOG = \
"""
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