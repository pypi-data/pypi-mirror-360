from enum import Enum, unique, IntEnum

PACKAGE_NAME = 'fmdata'

try:
    # Python 3.8+ standard library
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    try:
        # Backport for older Python versions or as an intermediate fallback
        from importlib_metadata import version, PackageNotFoundError
    except ImportError:
        try:
            # Legacy support using pkg_resources if other methods fail
            from pkg_resources import get_distribution, DistributionNotFound

            class PackageNotFoundError(Exception):
                pass

            def version(package_name):
                try:
                    return get_distribution(package_name).version
                except DistributionNotFound:
                    raise PackageNotFoundError
        except ImportError:
            raise ImportError(
                "No supported methods for retrieving package version are available."
            )

# Retrieve the package version, with a fallback for local test environments
try:
    __version__ = version(PACKAGE_NAME)
except PackageNotFoundError:
    # Fallback version string for local development or testing scenarios
    __version__ = "0.0.0-dev"

class APIPath(Enum):
    META_PRODUCT = '/fmi/data/{api_version}/productInfo'
    META_DATABASES = '/fmi/data/{api_version}/databases'
    META_LAYOUTS = '/fmi/data/{api_version}/databases/{database}/layouts'
    META_LAYOUT = '/fmi/data/{api_version}/databases/{database}/layouts/{layout}'
    META_SCRIPTS = '/fmi/data/{api_version}/databases/{database}/scripts'

    AUTH_SESSION = '/fmi/data/{api_version}/databases/{database}/sessions/{token}'
    RECORDS = '/fmi/data/{api_version}/databases/{database}/layouts/{layout}/records'
    RECORD_ACTION = '/fmi/data/{api_version}/databases/{database}/layouts/{layout}/records/{record_id}'
    UPLOAD_CONTAINER = '/fmi/data/{api_version}/databases/{database}/layouts/{layout}/records/{record_id}/containers/{field_name}/{field_repetition}'
    FIND = '/fmi/data/{api_version}/databases/{database}/layouts/{layout}/_find'
    SCRIPT = '/fmi/data/{api_version}/databases/{database}/layouts/{layout}/script/{script_name}'
    GLOBALS = '/fmi/data/{api_version}/databases/{database}/globals'


@unique
class FMErrorEnum(IntEnum):
    def __new__(cls, value, description):
        obj = int.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    UNKNOWN_ERROR = (-1, "Unknown error")
    NO_ERROR = (0, "No error")
    USER_CANCELED_ACTION = (1, "User canceled action")
    MEMORY_ERROR = (2, "Memory error")
    COMMAND_UNAVAILABLE = (3, "Command is unavailable (for example, wrong operating system or mode)")
    COMMAND_UNKNOWN = (4, "Command is unknown")
    COMMAND_INVALID = (
        5, "Command is invalid (for example, a Set Field script step does not have a calculation specified)")
    FILE_READ_ONLY = (6, "File is read-only")
    RUNNING_OUT_OF_MEMORY = (7, "Running out of memory")
    INSUFFICIENT_PRIVILEGES = (9, "Insufficient privileges")
    REQUESTED_DATA_MISSING = (10, "Requested data is missing")
    NAME_NOT_VALID = (11, "Name is not valid")
    NAME_ALREADY_EXISTS = (12, "Name already exists")
    FILE_OR_OBJECT_IN_USE = (13, "File or object is in use")
    OUT_OF_RANGE = (14, "Out of range")
    CANNOT_DIVIDE_BY_ZERO = (15, "Can't divide by zero")
    OPERATION_FAILED_REQUEST_RETRY = (16, "Operation failed; request retry (for example, a user query)")
    ATTEMPT_CONVERT_FOREIGN_CHARSET_FAILED = (17, "Attempt to convert foreign character set to UTF-16 failed")
    CLIENT_MUST_PROVIDE_ACCOUNT_INFO = (18, "Client must provide account information to proceed")
    STRING_HAS_INVALID_CHARACTERS = (19, "String contains characters other than A-Z, a-z, 0-9 (ASCII)")
    COMMAND_OPERATION_CANCELED = (20, "Command/operation canceled by triggered script")
    REQUEST_NOT_SUPPORTED = (21,
                             "Request not supported (for example, when creating a hard link on a file system that does not support hard links)")
    NO_SUPPORTED_EMAIL_CLIENT_FOUND = (119, "No supported email client found")
    FILE_IS_MISSING = (100, "File is missing")
    RECORD_IS_MISSING = (101, "Record is missing")
    FIELD_IS_MISSING = (102, "Field is missing")
    RELATIONSHIP_IS_MISSING = (103, "Relationship is missing")
    SCRIPT_IS_MISSING = (104, "Script is missing")
    LAYOUT_IS_MISSING = (105, "Layout is missing")
    TABLE_IS_MISSING = (106, "Table is missing")
    INDEX_IS_MISSING = (107, "Index is missing")
    VALUE_LIST_IS_MISSING = (108, "Value list is missing")
    PRIVILEGE_SET_IS_MISSING = (109, "Privilege set is missing")
    RELATED_TABLES_ARE_MISSING = (110, "Related tables are missing")
    FIELD_REPETITION_INVALID = (111, "Field repetition is invalid")
    WINDOW_IS_MISSING = (112, "Window is missing")
    FUNCTION_IS_MISSING = (113, "Function is missing")
    FILE_REFERENCE_IS_MISSING = (114, "File reference is missing")
    MENU_SET_IS_MISSING = (115, "Menu set is missing")
    LAYOUT_OBJECT_IS_MISSING = (116, "Layout object is missing")
    DATA_SOURCE_IS_MISSING = (117, "Data source is missing")
    THEME_IS_MISSING = (118, "Theme is missing")
    CANNOT_OPEN_FILE_LICENSED_USER_CONTACT_MANAGER = (
        219, "Cannot open file; must be licensed user; contact team manager")
    FILES_DAMAGED_OR_MISSING = (130, "Files are damaged or missing and must be reinstalled")
    LANGUAGE_PACK_FILES_MISSING = (131, "Language pack files are missing")
    RECORD_ACCESS_DENIED = (200, "Record access is denied")
    FIELD_CANNOT_BE_MODIFIED = (201, "Field cannot be modified")
    FIELD_ACCESS_DENIED = (202, "Field access is denied")
    NO_RECORDS_TO_PRINT = (203, "No records in file to print, or password doesn't allow print access")
    NO_ACCESS_TO_FIELDS_IN_SORT_ORDER = (204, "No access to field(s) in sort order")
    USER_NO_PRIVILEGES_CREATE_RECORDS = (
        205, "User does not have access privileges to create new records; import will overwrite existing data")
    USER_NO_PASSWORD_CHANGE_PRIVILEGES = (
        206, "User does not have password change privileges, or file is not modifiable")
    USER_NO_PRIVILEGES_CHANGE_SCHEMA = (
        207, "User does not have privileges to change database schema, or file is not modifiable")
    PASSWORD_TOO_SHORT = (208, "Password does not contain enough characters")
    NEW_PASSWORD_SAME_AS_EXISTING = (209, "New password must be different from existing one")
    USER_ACCOUNT_INACTIVE = (210, "User account is inactive")
    PASSWORD_EXPIRED = (211, "Password has expired")
    INVALID_USER_OR_PASSWORD = (212, "Invalid user account or password")
    TOO_MANY_LOGIN_ATTEMPTS = (214, "Too many login attempts")
    ADMIN_PRIVILEGES_CANNOT_BE_DUPLICATED = (215, "Administrator privileges cannot be duplicated")
    GUEST_ACCOUNT_CANNOT_BE_DUPLICATED = (216, "Guest account cannot be duplicated")
    USER_NO_PRIVILEGES_MODIFY_ADMIN_ACCOUNT = (
        217, "User does not have sufficient privileges to modify administrator account")
    PASSWORDS_DO_NOT_MATCH = (218, "Password and verify password do not match")
    FILE_LOCKED_OR_IN_USE = (300, "File is locked or in use")
    RECORD_IN_USE_BY_ANOTHER_USER = (301, "Record is in use by another user")
    TABLE_IN_USE_BY_ANOTHER_USER = (302, "Table is in use by another user")
    DATABASE_SCHEMA_IN_USE_BY_ANOTHER_USER = (303, "Database schema is in use by another user")
    LAYOUT_IN_USE_BY_ANOTHER_USER = (304, "Layout is in use by another user")
    CANNOT_MODIFY_ITEMS_ANOTHER_USER_MODIFYING = (310, "Cannot modify items because another user is modifying them")
    RECORD_MODIFICATION_ID_MISMATCH = (306, "Record modification ID does not match")
    TRANSACTION_COULD_NOT_BE_LOCKED = (
        307, "Transaction could not be locked because of a communication error with the host")
    THEME_LOCKED_AND_IN_USE = (308, "Theme is locked and in use by another user")
    FIND_CRITERIA_EMPTY = (400, "Find criteria are empty")
    NO_RECORDS_MATCH_REQUEST = (401, "No records match the request")
    SELECTED_FIELD_NOT_MATCH_FIELD = (402, "Selected field is not a match field for a lookup")
    SORT_ORDER_INVALID = (404, "Sort order is invalid")
    NUMBER_OF_RECORDS_EXCEEDS_OMIT = (405, "Number of records specified exceeds number of records that can be omitted")
    REPLACE_RESERIALIZE_CRITERIA_INVALID = (406, "Replace/reserialize criteria are invalid")
    MATCH_FIELDS_MISSING = (407, "One or both match fields are missing (invalid relationship)")
    FIELD_INAPPROPRIATE_DATA_TYPE = (408, "Specified field has inappropriate data type for this operation")
    IMPORT_ORDER_INVALID = (409, "Import order is invalid")
    EXPORT_ORDER_INVALID = (410, "Export order is invalid")
    WRONG_FILEMAKER_VERSION_RECOVER = (412, "Wrong version of FileMaker Pro used to recover file")
    FIELD_INAPPROPRIATE_FIELD_TYPE = (413, "Specified field has inappropriate field type")
    LAYOUT_CANNOT_DISPLAY_RESULT = (414, "Layout cannot display the result")
    REQUIRED_RELATED_RECORDS_NOT_AVAILABLE = (415, "One or more required related records are not available")
    PRIMARY_KEY_REQUIRED = (416, "A primary key is required from the data source table")
    FILE_NOT_SUPPORTED_DATA_SOURCE = (417, "File is not a supported data source")
    INTERNAL_FAILURE_INSERT_FIELD = (418, "Internal failure in INSERT operation into a field")
    DATE_VALIDATION_FAILED = (500, "Date value does not meet validation entry options")
    TIME_VALIDATION_FAILED = (501, "Time value does not meet validation entry options")
    NUMBER_VALIDATION_FAILED = (502, "Number value does not meet validation entry options")
    VALUE_NOT_IN_RANGE = (503, "Value in field is not within the range specified in validation entry options")
    VALUE_NOT_UNIQUE = (504, "Value in field is not unique, as required in validation entry options")
    VALUE_NOT_EXISTING = (
        505, "Value in field is not an existing value in the file, as required in validation entry options")
    VALUE_NOT_LISTED = (506, "Value in field is not listed in the value list specified in validation entry option")
    VALUE_FAILED_CALCULATION_TEST = (507, "Value in field failed calculation test of validation entry option")
    INVALID_VALUE_FIND_MODE = (508, "Invalid value entered in Find mode")
    FIELD_REQUIRES_VALID_VALUE = (509, "Field requires a valid value")
    RELATED_VALUE_EMPTY_OR_UNAVAILABLE = (510, "Related value is empty or unavailable")
    VALUE_EXCEEDS_MAX_FIELD_SIZE = (511, "Value in field exceeds maximum field size")
    RECORD_ALREADY_MODIFIED = (512, "Record was already modified by another user")
    NO_VALIDATION_SPECIFIED_DATA_DOESNT_FIT = (513, "No validation was specified but data cannot fit into the field")
    PRINT_ERROR_OCCURRED = (600, "Print error has occurred")
    COMBINED_HEADER_FOOTER_EXCEEDS_PAGE = (601, "Combined header and footer exceed one page")
    BODY_DOESNT_FIT_ON_PAGE = (602, "Body doesn't fit on a page for current column setup")
    PRINT_CONNECTION_LOST = (603, "Print connection lost")
    WRONG_FILE_TYPE_IMPORT = (700, "File is of the wrong file type for import")
    EPS_NO_PREVIEW_IMAGE = (706, "EPS file has no preview image")
    GRAPHIC_TRANSLATOR_NOT_FOUND = (707, "Graphic translator cannot be found")
    CANNOT_IMPORT_FILE_COLOR_SUPPORT = (708, "Can't import the file, or need color monitor support to import file")
    IMPORT_TRANSLATOR_NOT_FOUND = (711, "Import translator cannot be found")
    PASSWORD_PRIVILEGES_DO_NOT_ALLOW = (714, "Password privileges do not allow the operation")
    SPECIFIED_EXCEL_WORKSHEET_MISSING = (715, "Specified Excel worksheet or named range is missing")
    SQL_QUERY_NOT_ALLOWED_ODBC = (716, "A SQL query using DELETE, INSERT, or UPDATE is not allowed for ODBC import")
    NOT_ENOUGH_XML_XSL_INFO = (717, "There is not enough XML/XSL information to proceed with the import or export")
    ERROR_PARSING_XML = (718, "Error in parsing XML file (from libxml2)")
    ERROR_TRANSFORMING_XML_XSL = (719, "Error in transforming XML using XSL (from libxslt)")
    ERROR_EXPORTING_FORMAT_NOT_SUPPORT_REPEATING = (
        720, "Error when exporting; intended format does not support repeating fields")
    UNKNOWN_PARSER_TRANSFORMER_ERROR = (721, "Unknown error occurred in the parser or the transformer")
    CANNOT_IMPORT_NO_FIELDS = (722, "Cannot import data into a file that has no fields")
    NO_PERMISSION_ADD_OR_MODIFY_TARGET_TABLE = (
        723, "You do not have permission to add records to or modify records in the target table")
    NO_PERMISSION_ADD_TARGET_TABLE = (724, "You do not have permission to add records to the target table")
    NO_PERMISSION_MODIFY_TARGET_TABLE = (725, "You do not have permission to modify records in the target table")
    SOURCE_FILE_HAS_MORE_RECORDS = (
        726, "Source file has more records than the target table; not all records were imported")
    TARGET_TABLE_HAS_MORE_RECORDS = (
        727, "Target table has more records than the source file; not all records were updated")
    ERRORS_DURING_IMPORT = (729, "Errors occurred during import; records could not be imported")
    UNSUPPORTED_EXCEL_VERSION = (
        730, "Unsupported Excel version; convert file to the current Excel format and try again")
    IMPORTING_FILE_HAS_NO_DATA = (731, "File you are importing from contains no data")
    FILE_CONTAINS_OTHER_FILES = (732, "This file cannot be inserted because it contains other files")
    TABLE_CANNOT_BE_IMPORTED_ITSELF = (733, "A table cannot be imported into itself")
    FILE_TYPE_CANNOT_BE_DISPLAYED_AS_PICTURE = (734, "This file type cannot be displayed as a picture")
    FILE_TYPE_CANNOT_BE_DISPLAYED_AS_PICTURE_FILE_INSERTED = (
        735, "This file type cannot be displayed as a picture; it will be inserted and displayed as a file")
    TOO_MUCH_DATA_TO_EXPORT = (736, "Too much data to export to this format; data will be truncated")
    THEME_ALREADY_EXISTS = (738, "The theme you are importing already exists")
    UNABLE_TO_CREATE_FILE_ON_DISK = (800, "Unable to create file on disk")
    UNABLE_TO_CREATE_TEMP_FILE_SYSTEM_DISK = (801, "Unable to create temporary file on System disk")
    UNABLE_TO_OPEN_FILE = (802, "Unable to open file")
    FILE_SINGLE_USER_OR_HOST_NOT_FOUND = (803, "File is single-user, or host cannot be found")
    FILE_CANNOT_OPEN_READ_ONLY = (804, "File cannot be opened as read-only in its current state")
    FILE_IS_DAMAGED_USE_RECOVER = (805, "File is damaged; use Recover command")
    FILE_CANNOT_OPEN_THIS_VERSION = (806, "File cannot be opened with this version of a FileMaker client")
    FILE_NOT_FILEMAKER_PRO_ADVANCED = (807, "File is not a FileMaker Pro Advanced file or is severely damaged")
    CANNOT_OPEN_FILE_ACCESS_PRIVILEGES_DAMAGED = (808, "Cannot open file because access privileges are damaged")
    DISK_VOLUME_FULL = (809, "Disk/volume is full")
    DISK_VOLUME_LOCKED = (810, "Disk/volume is locked")
    TEMP_FILE_CANNOT_OPEN_FILEMAKER_PRO_ADVANCED = (
        811, "Temporary file cannot be opened as FileMaker Pro Advanced file")
    EXCEEDED_HOST_CAPACITY = (812, "Exceeded host’s capacity")
    RECORD_SYNC_ERROR_ON_NETWORK = (813, "Record synchronization error on network")
    FILES_MAXIMUM_NUMBER_OPEN = (814, "File(s) cannot be opened because maximum number is open")
    COULDNT_OPEN_LOOKUP_FILE = (815, "Couldn't open lookup file")
    UNABLE_TO_CONVERT_FILE = (816, "Unable to convert file")
    UNABLE_TO_OPEN_FILE_NOT_BELONG_SOLUTION = (817, "Unable to open file because it does not belong to this solution")
    CANNOT_SAVE_LOCAL_COPY_REMOTE_FILE = (819, "Cannot save a local copy of a remote file")
    FILE_IS_BEING_CLOSED = (820, "File is being closed")
    HOST_FORCED_DISCONNECT = (821, "Host forced a disconnect")
    FILEMAKER_PRO_ADVANCED_FILES_NOT_FOUND = (822, "FileMaker Pro Advanced files not found; reinstall missing files")
    CANNOT_SET_SINGLE_USER_GUESTS_CONNECTED = (823, "Cannot set file to single-user; guests are connected")
    FILE_DAMAGED_OR_NOT_FILEMAKER_PRO_ADVANCED = (824, "File is damaged or not a FileMaker Pro Advanced file")
    FILE_NOT_AUTHORIZED_REFERENCE_PROTECTED = (825, "File is not authorized to reference the protected file")
    INVALID_FILE_PATH = (826, "File path specified is not a valid file path")
    FILE_NOT_CREATED_SOURCE_NO_DATA_OR_REFERENCE = (
        827, "File was not created because the source contained no data or is a reference")
    PATH_NOT_VALID_FOR_OS = (850, "Path is not valid for the operating system")
    CANNOT_DELETE_EXTERNAL_FILE = (851, "Cannot delete an external file from disk")
    CANNOT_WRITE_FILE_TO_EXTERNAL_STORAGE = (852, "Cannot write a file to the external storage")
    CONTAINERS_FAILED_TO_TRANSFER = (853, "One or more containers failed to transfer")
    CANNOT_MODIFY_FILE_ANOTHER_USER_MODIFYING = (870, "Cannot modify file because another user is modifying it")
    ERROR_OCCURRED_LOADING_CORE_ML_MODEL = (871, "Error occurred loading Core ML model")
    CORE_ML_MODEL_UNSUPPORTED_INPUT_OUTPUT = (
        872, "Core ML model was not loaded because it contained an unsupported input or output parameter")
    ENDPOINT_EMPTY = (875, "Endpoint is empty")
    CANT_FIND_AI_ACCOUNT = (877, "Can't find AI account")
    JSON_DATA_OPTIONS_FORMATTING_ERROR = (
        878, "JSON data for Options contains a formatting error and couldn't be parsed")
    INVALID_AI_REQUEST = (882, "Invalid AI request")
    INVALID_REQUEST_CUSTOM_MODEL_PROVIDER = (883, "Invalid request to custom model provider")
    INVALID_AI_REQUEST_DUPLICATE = (884, "Invalid AI request")
    ENDPOINT_INVALID_OR_UNREACHABLE = (885, "Endpoint is invalid or server is unreachable")
    GENERAL_SPELLING_ENGINE_ERROR = (900, "General spelling engine error")
    MAIN_SPELLING_DICTIONARY_NOT_INSTALLED = (901, "Main spelling dictionary not installed")
    COMMAND_CANNOT_BE_USED_SHARED_FILE = (903, "Command cannot be used in a shared file")
    COMMAND_REQUIRES_ACTIVE_FIELD = (905, "Command requires a field to be active")
    CURRENT_FILE_NOT_SHARED_COMMAND_ONLY_SHARED = (
        906, "Current file is not shared; command can be used only if the file is shared")
    CANNOT_INITIALIZE_SPELLING_ENGINE = (920, "Cannot initialize the spelling engine")
    USER_DICTIONARY_CANNOT_LOAD_EDITING = (921, "User dictionary cannot be loaded for editing")
    USER_DICTIONARY_CANNOT_BE_FOUND = (922, "User dictionary cannot be found")
    USER_DICTIONARY_IS_READ_ONLY = (923, "User dictionary is read-only")
    UNEXPECTED_ERROR_OCCURRED = (951, "An unexpected error occurred (*)")
    INVALID_FILEMAKER_DATA_API_TOKEN = (952, "Invalid FileMaker Data API token (*)")
    EXCEEDED_FILEMAKER_DATA_API_LIMIT = (953, "Exceeded limit on data the FileMaker Data API can transmit (*)")
    UNSUPPORTED_XML_GRAMMAR = (954, "Unsupported XML grammar (*)")
    NO_DATABASE_NAME = (955, "No database name (*)")
    MAX_DB_SESSIONS_EXCEEDED = (956, "Maximum number of database sessions exceeded (*)")
    CONFLICTING_COMMANDS = (957, "Conflicting commands (*)")
    PARAMETER_MISSING = (958, "Parameter missing (*)")
    CUSTOM_WEB_PUBLISHING_DISABLED = (959, "Custom Web Publishing technology is disabled")
    PARAMETER_INVALID = (960, "Parameter is invalid")
    GENERIC_CALCULATION_ERROR = (1200, "Generic calculation error")
    TOO_FEW_PARAMETERS_FUNCTION = (1201, "Too few parameters in the function")
    TOO_MANY_PARAMETERS_FUNCTION = (1202, "Too many parameters in the function")
    UNEXPECTED_END_OF_CALCULATION = (1203, "Unexpected end of calculation")
    EXPECTED_NUMBER_TEXT_FIELD_OR_OPEN_PAREN = (1204, "Number, text constant, field name, or '(' expected")
    COMMENT_NOT_TERMINATED = (1205, "Comment is not terminated with '*/'")
    TEXT_CONSTANT_MUST_END_WITH_QUOTATION_MARK = (1206, "Text constant must end with a quotation mark")
    UNBALANCED_PARENTHESIS = (1207, "Unbalanced parenthesis")
    OPERATOR_MISSING_FUNCTION_NOT_FOUND = (1208, "Operator missing, function not found, or '(' not expected")
    NAME_MISSING = (1209, "Name (such as field name or layout name) is missing")
    PLUGIN_FUNCTION_OR_SCRIPT_STEP_REGISTERED = (1210, "Plug-in function or script step has already been registered")
    LIST_USAGE_NOT_ALLOWED = (1211, "List usage is not allowed in this function")
    OPERATOR_EXPECTED = (1212, "An operator (for example, +, -, *) is expected here")
    VARIABLE_ALREADY_DEFINED = (1213, "This variable has already been defined in the Let function")
    SUMMARY_FIELD_EXPRESSION_ERROR = (1214,
                                      "Average, Count, Extend, GetRepetition, Max, Min, NPV, StDev, Sum, and GetSummary: expression found where a field alone is needed")
    INVALID_GET_FUNCTION_PARAMETER = (1215, "This parameter is an invalid Get function parameter")
    ONLY_SUMMARY_FIELDS_ALLOWED = (1216, "Only summary fields are allowed as first argument in GetSummary")
    BREAK_FIELD_INVALID = (1217, "Break field is invalid")
    CANNOT_EVALUATE_NUMBER = (1218, "Cannot evaluate the number")
    FIELD_IN_OWN_FORMULA = (1219, "A field cannot be used in its own formula")
    FIELD_TYPE_INVALID = (1220, "Field type must be normal or calculated")
    DATA_TYPE_INVALID = (1221, "Data type must be number, date, time, or timestamp")
    CALCULATION_CANNOT_BE_STORED = (1222, "Calculation cannot be stored")
    FUNCTION_NOT_YET_IMPLEMENTED = (1223, "Function referred to is not yet implemented")
    FUNCTION_DOES_NOT_EXIST = (1224, "Function referred to does not exist")
    FUNCTION_NOT_SUPPORTED_CONTEXT = (1225, "Function referred to is not supported in this context")
    SPECIFIED_NAME_CANT_BE_USED = (1300, "The specified name can't be used")
    PARAMETER_SAME_NAME_AS_FUNCTION = (
        1301, "A parameter of the imported or pasted function has the same name as a function in the file")
    ODBC_CLIENT_DRIVER_INIT_FAILED = (
        1400, "ODBC client driver initialization failed; make sure ODBC client drivers are properly installed")
    FAILED_ALLOCATE_ENV_ODBC = (1401, "Failed to allocate environment (ODBC)")
    FAILED_FREE_ENV_ODBC = (1402, "Failed to free environment (ODBC)")
    FAILED_DISCONNECT_ODBC = (1403, "Failed to disconnect (ODBC)")
    FAILED_ALLOCATE_CONNECTION_ODBC = (1404, "Failed to allocate connection (ODBC)")
    FAILED_FREE_CONNECTION_ODBC = (1405, "Failed to free connection (ODBC)")
    FAILED_CHECK_SQL_API_ODBC = (1406, "Failed check for SQL API (ODBC)")
    FAILED_ALLOCATE_STATEMENT_ODBC = (1407, "Failed to allocate statement (ODBC)")
    EXTENDED_ERROR_ODBC = (1408, "Extended error (ODBC)")
    ERROR_ODBC = (1409, "Error (ODBC)")
    FAILED_COMMUNICATION_LINK_ODBC = (1413, "Failed communication link (ODBC)")
    SQL_STATEMENT_TOO_LONG = (1414, "SQL statement is too long")
    CONNECTION_IS_BEING_DISCONNECTED_ODBC = (1415, "Connection is being disconnected (ODBC)")
    ACTION_REQUIRES_PHP_PRIVILEGE_EXTENSION = (1450, "Action requires PHP privilege extension (*)")
    ACTION_REQUIRES_CURRENT_FILE_REMOTE = (1451, "Action requires that current file be remote")
    SMTP_AUTH_FAILED = (1501, "SMTP authentication failed")
    CONNECTION_REFUSED_BY_SMTP = (1502, "Connection refused by SMTP server")
    ERROR_WITH_SSL = (1503, "Error with SSL")
    SMTP_CONNECTION_NEEDS_ENCRYPTION = (1504, "SMTP server requires the connection to be encrypted")
    SPECIFIED_AUTH_NOT_SUPPORTED_SMTP = (1505, "Specified authentication is not supported by SMTP server")
    EMAIL_MESSAGES_COULD_NOT_BE_SENT = (1506, "Email message(s) could not be sent successfully")
    UNABLE_TO_LOGIN_SMTP = (1507, "Unable to log in to the SMTP server")
    CANNOT_LOAD_PLUGIN_INVALID = (1550, "Cannot load the plug-in, or the plug-in is not a valid plug-in")
    CANNOT_INSTALL_PLUGIN = (
        1551, "Cannot install the plug-in; cannot delete an existing plug-in or write to the folder or disk")
    RETURNED_BY_PLUGINS_1552 = (1552, "Returned by plug-ins; see the documentation that came with the plug-in")
    RETURNED_BY_PLUGINS_1553 = (1553, "Returned by plug-ins; see the documentation that came with the plug-in")
    RETURNED_BY_PLUGINS_1554 = (1554, "Returned by plug-ins; see the documentation that came with the plug-in")
    RETURNED_BY_PLUGINS_1555 = (1555, "Returned by plug-ins; see the documentation that came with the plug-in")
    RETURNED_BY_PLUGINS_1556 = (1556, "Returned by plug-ins; see the documentation that came with the plug-in")
    RETURNED_BY_PLUGINS_1557 = (1557, "Returned by plug-ins; see the documentation that came with the plug-in")
    RETURNED_BY_PLUGINS_1558 = (1558, "Returned by plug-ins; see the documentation that came with the plug-in")
    RETURNED_BY_PLUGINS_1559 = (1559, "Returned by plug-ins; see the documentation that came with the plug-in")
    PROTOCOL_NOT_SUPPORTED = (1626, "Protocol is not supported")
    AUTHENTICATION_FAILED = (1627, "Authentication failed")
    ERROR_WITH_SSL_1628 = (1628, "There was an error with SSL")
    CONNECTION_TIMED_OUT = (1629, "Connection timed out; the timeout value is 60 seconds")
    URL_FORMAT_INCORRECT = (1630, "URL format is incorrect")
    CONNECTION_FAILED = (1631, "Connection failed")
    CERTIFICATE_EXPIRED = (1632, "The certificate has expired")
    CERTIFICATE_SELF_SIGNED = (1633, "The certificate is self-signed")
    CERTIFICATE_VERIFICATION_ERROR = (1634, "A certificate verification error occurred")
    CONNECTION_UNENCRYPTED = (1635, "Connection is unencrypted")
    ERROR_HOST_NOT_ALLOWING_NEW_CONNECTIONS = (1638, "The host is not allowing new connections. Try again later.")
    RESOURCE_DOES_NOT_EXIST = (1700, "Resource doesn't exist (*)")
    HOST_UNABLE_RECEIVE_REQUESTS = (1701, "Host is currently unable to receive requests (*)")
    AUTH_INFO_WRONG_FORMAT = (1702,
                              "Authentication information wasn't provided in the correct format; verify the value of the Authorization header (*)")
    INVALID_USERNAME_OR_PASSWORD_OR_JWT = (1703, "Invalid username or password, or JSON Web Token (*)")
    RESOURCE_DOES_NOT_SUPPORT_HTTP_VERB = (1704, "Resource doesn't support the specified HTTP verb (*)")
    REQUIRED_HTTP_HEADER_NOT_SPECIFIED = (1705, "Required HTTP header wasn't specified (*)")
    PARAMETER_NOT_SUPPORTED = (1706, "Parameter isn't supported (*)")
    REQUIRED_PARAMETER_NOT_SPECIFIED = (1707, "Required parameter wasn't specified in the request (*)")
    PARAMETER_VALUE_INVALID = (1708, "Parameter value is invalid (*)")
    OPERATION_INVALID_FOR_RESOURCE_STATUS = (1709, "Operation is invalid for the resource's current status (*)")
    JSON_INPUT_NOT_VALID = (1710, "JSON input isn't syntactically valid (*)")
    HOST_LICENSE_EXPIRED = (1711, "Host's license has expired (*)")
    PRIVATE_KEY_FILE_EXISTS = (1712, "Private key file already exists; remove it and run the command again (*)")
    API_REQUEST_NOT_SUPPORTED_OS = (1713, "The API request is not supported for this operating system (*)")
    EXTERNAL_GROUP_NAME_INVALID = (1714, "External group name is invalid (*)")
    EXTERNAL_SERVER_ACCOUNT_SIGNIN_NOT_ENABLED = (1715, "External server account sign-in is not enabled (*)")

    def __str__(self):
        return f"{self.name} ({self.value}): {self.description}"
