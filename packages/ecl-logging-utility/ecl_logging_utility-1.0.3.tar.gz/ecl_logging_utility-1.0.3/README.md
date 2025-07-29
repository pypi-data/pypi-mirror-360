# Structured Logging Utilities for ECL microservices

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-Proprietary-lightgrey)

Internal package for consistent structured logging across ECL microservices. Features JSON formatting, automatic metadata capture, and environment-based configuration.

## Features

- 📝 **Structured JSON logs** with consistent schema
- 🕒 **Automatic timestamping** in ISO 8601 format
- 📍 **Complete source location** (file path, line number, module, function)
- 🔍 **Query-ready fields** (transaction_id, request_ip, service_name)
- ⚙️ **Environment-controlled** log levels
- 🔗 **Request context propagation** across services
- 🛡 **Private package** for internal use of ECL

## Environment Variables
- **ECL_LOGGING_UTILITY_LOG_LEVEL**: Set the log level, default: *INFO*
- **ECL_LOGGING_UTILITY_APP_VERSION**: Denotes the app version which will be displayed in the log, default: *AMBIVALENT_APP_VERSION*
- **ECL_LOGGING_UTILITY_SERVICE_NAME**: Denotes the service name which will be displayed in the log, default: *AMBIVALENT_SERVICE_NAME*

## Installation

```bash
pip install ecl-logging-utility
```

## Version History  
See [CHANGELOG.md](CHANGELOG.md) for release notes.  