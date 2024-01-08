from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_DIR_NAME = 'logs'
MAXBYTES_LOG_FILE = 10 ** 6
BACKUPCOUNT_LOG_FILE = 5
LOG_FILE_NAME = 'parser.log'
ARGUMENT_PRETTY = 'pretty'
ARGUMENT_FILE = 'file'
OUTPUT_DIR = 'results'
WHATS_NEW = 'whatsnew/'
DOWNLOAD = 'download.html'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
