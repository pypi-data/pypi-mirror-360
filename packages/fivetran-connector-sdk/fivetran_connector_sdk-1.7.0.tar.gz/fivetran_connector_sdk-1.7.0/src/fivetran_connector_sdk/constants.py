import re

TESTER_VER = "0.25.0521.001"

WIN_OS = "windows"
ARM_64 = "arm64"
X64 = "x64"

OS_MAP = {
    "darwin": "mac",
    "linux": "linux",
    WIN_OS: WIN_OS
}

ARCH_MAP = {
    "x86_64": X64,
    "amd64": X64,
    ARM_64: ARM_64,
    "aarch64": ARM_64
}

# Global constants - use constants.<Global_variable> to access them as they can be overridden in the
DEBUGGING = False
EXECUTED_VIA_CLI = False
TABLES = {}

TESTER_FILENAME = "run_sdk_tester.jar"
VERSION_FILENAME = "version.txt"
UPLOAD_FILENAME = "code.zip"
LAST_VERSION_CHECK_FILE = "_last_version_check"
ROOT_LOCATION = ".ft_sdk_connector_tester"
CONFIG_FILE = "_config.json"
OUTPUT_FILES_DIR = "files"
REQUIREMENTS_TXT = "requirements.txt"
PYPI_PACKAGE_DETAILS_URL = "https://pypi.org/pypi/fivetran_connector_sdk/json"
ONE_DAY_IN_SEC = 24 * 60 * 60
MAX_RETRIES = 3
LOGGING_PREFIX = "Fivetran-Connector-SDK"
LOGGING_DELIMITER = ": "
VIRTUAL_ENV_CONFIG = "pyvenv.cfg"
ROOT_FILENAME = "connector.py"

# Compile patterns used in the implementation
WORD_DASH_DOT_PATTERN = re.compile(r'^[\w.-]*$')
NON_WORD_PATTERN = re.compile(r'\W')
WORD_OR_DOLLAR_PATTERN = re.compile(r'[\w$]')
DROP_LEADING_UNDERSCORE = re.compile(r'_+([a-zA-Z]\w*)')
WORD_PATTERN = re.compile(r'\w')

EXCLUDED_DIRS = ["__pycache__", "lib", "include", OUTPUT_FILES_DIR]
EXCLUDED_PIPREQS_DIRS = ["bin,etc,include,lib,Lib,lib64,Scripts,share"]
VALID_COMMANDS = ["debug", "deploy", "reset", "version"]
MAX_ALLOWED_EDIT_DISTANCE_FROM_VALID_COMMAND = 3
COMMANDS_AND_SYNONYMS = {
    "debug": {"test", "verify", "diagnose", "check"},
    "deploy": {"upload", "ship", "launch", "release"},
    "reset": {"reinitialize", "reinitialise", "re-initialize", "re-initialise", "restart", "restore"},
}

CONNECTION_SCHEMA_NAME_PATTERN = r'^[_a-z][_a-z0-9]*$'
PRODUCTION_BASE_URL = "https://api.fivetran.com"
INSTALLATION_SCRIPT_MISSING_MESSAGE = "The 'installation.sh' file is missing in the 'drivers' directory. Please ensure that 'installation.sh' is present to properly configure drivers."
INSTALLATION_SCRIPT = "installation.sh"
DRIVERS = "drivers"
JAVA_LONG_MAX_VALUE = 9223372036854775807
MAX_CONFIG_FIELDS = 100
SUPPORTED_PYTHON_VERSIONS = ["3.12", "3.11", "3.10", "3.9"]
DEFAULT_PYTHON_VERSION = "3.12"
FIVETRAN_HD_AGENT_ID = "FIVETRAN_HD_AGENT_ID"
UTF_8 = "utf-8"
