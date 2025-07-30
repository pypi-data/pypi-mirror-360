import os
import sys
import logging
import structlog
from datetime import datetime
from opensearchpy import OpenSearch
from structlog.contextvars import bind_contextvars, clear_contextvars
from structlog.processors import CallsiteParameter

# Map string log levels to logging constants
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Default log level if not specified
DEFAULT_LOG_LEVEL = logging.INFO


def get_log_level():
    """Get log level from environment variable"""
    level_str = os.environ.get('ECL_LOGGING_UTILITY_LOG_LEVEL', 'INFO').upper()
    return LOG_LEVEL_MAP.get(level_str, DEFAULT_LOG_LEVEL)


# Custom processor to rename fields
def rename_fields(_, __, event_dict):
    field_mappings = {
        'pathname': 'file_path',
        'lineno': 'line_number',
        'func_name': 'function_name'
    }
    for old_key, new_key in field_mappings.items():
        if old_key in event_dict:
            event_dict[new_key] = event_dict.pop(old_key)
    return event_dict


class OpenSearchLogger:
    def __init__(self, service_name: str):
        self.host = os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_HOST', 'localhost')
        self.port = os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_PORT', '9200')
        self.index_prefix = service_name if service_name else "logs"
        self.client = OpenSearch(
            hosts=[{'host': self.host, 'port': self.port}],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

    def __call__(self, logger, method_name, event_dict):
        # Create index name with Y-m suffix for easier management
        index_name = f"{self.index_prefix}-{datetime.now().strftime('%Y.%m')}"
        try:
            self.client.index(
                index=index_name,
                body=event_dict,
                refresh=True
            )
        except Exception as e:
            logger.error(f"Failed to send log to OpenSearch: {e}", file=sys.stderr)

        return event_dict


def configure_logging():
    # Get environment variables
    app_version = os.environ.get('ECL_LOGGING_UTILITY_APP_VERSION', 'AMBIVALENT_APP_VERSION')
    service_name = os.environ.get('ECL_LOGGING_UTILITY_SERVICE_NAME', 'AMBIVALENT_SERVICE_NAME')
    log_level = get_log_level()

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.CallsiteParameterAdder(
            [
                CallsiteParameter.PATHNAME,
                CallsiteParameter.LINENO,
                CallsiteParameter.MODULE,
                CallsiteParameter.FUNC_NAME,
            ]
        ),
        rename_fields,
        structlog.processors.EventRenamer(to='message'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ]

    if os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_ENABLED', 'False').lower() == 'true':
        # Initialize OpenSearch logger
        processors.append(OpenSearchLogger(service_name=service_name))

    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=False,
    )

    # Create logger with static context
    return structlog.get_logger(service_name).bind(
        app_version=app_version,
        service_name=service_name
    )


# Initialize logger with static context
logger = configure_logging()