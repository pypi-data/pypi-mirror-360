"""
Constants for the MCP KQL Server.

This module contains all the constants used throughout the MCP KQL Server,
including default values, configuration settings, error messages, and other
static values.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

from typing import Dict, List

# Version information
__version__ = "2.0.1"
MCP_PROTOCOL_VERSION = "2024-11-05"

# Server configuration
SERVER_NAME = "mcp-kql-server"
SERVER_DESCRIPTION = "Enhanced MCP server for executing KQL queries with unified memory system, AI-friendly tokens, and cross-cluster support"

# Default paths and directories
DEFAULT_MEMORY_DIR_NAME = "KQL_MCP"
DEFAULT_CLUSTER_MEMORY_DIR = "cluster_memory"
SCHEMA_FILE_EXTENSION = ".json"

# Azure and KQL configuration
DEFAULT_KUSTO_DOMAIN = "kusto.windows.net"
SYSTEM_DATABASES = {"$systemdb"}
DEFAULT_CONNECTION_TIMEOUT = 60  # Increased from 30
DEFAULT_QUERY_TIMEOUT = 600  # Increased from 300

# Schema memory configuration
SCHEMA_CACHE_MAX_AGE_DAYS = 7
MAX_SCHEMA_FILE_SIZE_MB = 10
MAX_TABLES_PER_DATABASE = 1000
MAX_COLUMNS_PER_TABLE = 500

# Query validation
MAX_QUERY_LENGTH = 100000
MIN_QUERY_LENGTH = 10

# Default configuration (no environment variables required)
DEFAULT_CONFIG = {
    "DEBUG_MODE": False,  # Default to production mode
    "AZURE_ERRORS_ONLY": True,  # Hide verbose Azure logs by default
    "CONNECTION_TIMEOUT": DEFAULT_CONNECTION_TIMEOUT,
    "QUERY_TIMEOUT": DEFAULT_QUERY_TIMEOUT,
    "AUTO_CREATE_MEMORY_PATH": True,  # Automatically create memory directories
    "ENABLE_LOGGING": True,  # Enable basic logging
}

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Error messages
ERROR_MESSAGES = {
    "auth_failed": "Authentication failed. Please run 'az login' and try again.",
    "empty_query": "Query cannot be empty.",
    "invalid_cluster": "Invalid cluster URI format.",
    "invalid_database": "Invalid database name format.",
    "connection_timeout": "Connection to cluster timed out.",
    "query_timeout": "Query execution timed out.",
    "permission_denied": "Permission denied. Check your access rights to the cluster.",
    "cluster_not_found": "Cluster not found or not accessible.",
    "database_not_found": "Database not found in the specified cluster.",
    "table_not_found": "Table not found in the specified database.",
    "schema_discovery_failed": "Failed to discover cluster schema.",
    "schema_save_failed": "Failed to save schema memory.",
    "schema_load_failed": "Failed to load schema memory.",
    "memory_path_error": "Error accessing cluster memory path.",
}

# Success messages
SUCCESS_MESSAGES = {
    "query_executed": "Query executed successfully.",
    "schema_discovered": "Cluster schema discovered successfully.",
    "schema_saved": "Schema memory saved successfully.",
    "schema_loaded": "Schema memory loaded successfully.",
    "auth_success": "Authentication successful.",
}

# KQL query patterns for validation
QUERY_PATTERNS = {
    "cluster_pattern": r"cluster\('([^']+)'\)",
    "database_pattern": r"database\('([^']+)'\)",
    "table_pattern": r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\|',
    "from_pattern": r'\.([A-Za-z_][A-Za-z0-9_]*)\s*(?:\||$|;)',
    "comment_pattern": r'//.*$',
    "multiline_comment_pattern": r'/\*.*?\*/',
}

# Schema discovery queries
DISCOVERY_QUERIES = {
    "show_databases": ".show databases",
    "show_tables": ".show tables",
    "show_table_schema": ".show table {table_name} cslschema",
    "show_columns": ".show table {table_name} details",
}

# Column type mappings for better descriptions
COLUMN_TYPE_DESCRIPTIONS = {
    "string": "Text field",
    "int": "Integer number",
    "long": "Large integer number",
    "real": "Decimal number",
    "bool": "Boolean true/false flag",
    "datetime": "Date and time value",
    "timespan": "Time duration value",
    "guid": "Unique identifier (GUID)",
    "dynamic": "Dynamic JSON-like object",
}

# Common security table patterns and their descriptions
SECURITY_TABLE_PATTERNS = {
    "SecurityEvent": "Windows security audit events and logs",
    "SigninLogs": "Azure AD sign-in activity logs",
    "AuditLogs": "Azure AD audit activity logs",
    "Event": "Windows event log entries",
    "Syslog": "Linux/Unix system log messages",
    "CommonSecurityLog": "Common Event Format (CEF) security logs",
    "SecurityAlert": "Security alerts and detections",
    "SecurityIncident": "Security incident records",
    "ThreatIntelligenceIndicator": "Threat intelligence indicators",
    "IdentityInfo": "Identity and user information",
    "DeviceEvents": "Endpoint device events",
    "DeviceProcessEvents": "Process execution events from devices",
    "DeviceNetworkEvents": "Network activity from devices",
    "DeviceFileEvents": "File system activity from devices",
    "DeviceRegistryEvents": "Registry modification events",
    "EmailEvents": "Email security events",
    "UrlClickEvents": "URL click events from email security",
    "CloudAppEvents": "Cloud application activity events",
}

# Common column name patterns and their descriptions
COMMON_COLUMN_PATTERNS = {
    # Time-related columns
    "TimeGenerated": "Timestamp when the event was generated in UTC format",
    "TimeCreated": "Timestamp when the record was created",
    "Timestamp": "Event timestamp in UTC format",
    "EventTime": "Time when the event occurred",
    "CreatedTime": "Creation timestamp of the record",
    "ModifiedTime": "Last modification timestamp",
    
    # Identity columns
    "EventID": "Unique identifier for the event type",
    "ActivityID": "Unique identifier for the activity or session",
    "SessionID": "Identifier for the user or system session",
    "ProcessID": "Operating system process identifier",
    "ThreadID": "Operating system thread identifier",
    
    # User and account columns
    "UserName": "Name of the user account associated with the event",
    "AccountName": "Account name involved in the event",
    "User": "User identifier or name",
    "Subject": "Security principal subject information",
    "TargetUserName": "Target user for the operation",
    
    # System and computer columns
    "ComputerName": "Name of the computer or host system",
    "Computer": "Computer or device name",
    "SourceSystem": "System that generated the log entry",
    "Source": "Source system or application",
    "DeviceName": "Name of the device",
    
    # Network columns
    "IPAddress": "IP address associated with the event",
    "SourceIP": "Source IP address of the connection or request",
    "DestinationIP": "Destination IP address",
    "ClientIP": "IP address of the client",
    "ServerIP": "IP address of the server",
    
    # Process columns
    "ProcessName": "Name of the process or executable",
    "Process": "Process information",
    "CommandLine": "Command line arguments used to start the process",
    "ExecutablePath": "Full path to the executable file",
    
    # Event data columns
    "EventData": "Additional event-specific data in structured format",
    "Message": "Human-readable event message or description",
    "Description": "Detailed description of the event",
    "Details": "Additional details about the event",
    
    # Status and classification columns
    "Severity": "Severity level of the event (e.g., Info, Warning, Error)",
    "Level": "Log level or importance indicator",
    "Category": "Event category or classification",
    "Type": "Type or class of the event",
    
    # Azure-specific columns
    "ResourceId": "Azure resource identifier",
    "SubscriptionId": "Azure subscription identifier",
    "ResourceGroup": "Azure resource group name",
    "TenantId": "Azure tenant identifier",
}

# File and directory permissions
FILE_PERMISSIONS = {
    "schema_file": 0o600,  # Read/write for owner only
    "memory_dir": 0o700,   # Read/write/execute for owner only
}

# Limits and constraints
LIMITS = {
    "max_concurrent_queries": 5,
    "max_result_rows": 10000,
    "max_visualization_rows": 1000,
    "max_column_description_length": 500,
    "max_table_description_length": 1000,
    "max_retry_attempts": 3,
    "retry_delay_seconds": 2,
    "max_connection_pool_size": 10,
}

# Supported MCP tools
MCP_TOOLS = {
    "kql_execute": {
        "name": "kql_execute",
        "description": "Execute a KQL query against an Azure Data Explorer cluster",
        "required_params": ["query"],
        "optional_params": ["visualize", "cluster_memory_path", "use_schema_context"],
    },
    "kql_schema_memory": {
        "name": "kql_schema_memory",
        "description": "Discover and manage cluster schema memory for AI-powered query assistance",
        "required_params": ["cluster_uri"],
        "optional_params": ["memory_path", "force_refresh"],
    },
}

# HTTP status codes for error mapping
HTTP_STATUS_CODES = {
    400: "Bad Request - Invalid query syntax",
    401: "Unauthorized - Authentication failed",
    403: "Forbidden - Access denied to resource",
    404: "Not Found - Cluster, database, or table not found",
    408: "Timeout - Request timed out",
    429: "Too Many Requests - Rate limit exceeded",
    500: "Internal Server Error - Server error occurred",
    503: "Service Unavailable - Service temporarily unavailable",
}

# Azure CLI configuration
AZURE_CLI_CONFIG = {
    "login_experience": "core.login_experience_v2=off",
    "output_format": "output=json",
    "only_show_errors": "AZURE_CORE_ONLY_SHOW_ERRORS=true",
}

# Performance monitoring thresholds
PERFORMANCE_THRESHOLDS = {
    "query_warning_time_seconds": 30,
    "query_error_time_seconds": 300,
    "schema_discovery_warning_time_seconds": 60,
    "schema_discovery_error_time_seconds": 600,
    "memory_usage_warning_mb": 100,
    "memory_usage_error_mb": 500,
}

# Default visualization settings
VISUALIZATION_CONFIG = {
    "max_rows": 1000,
    "max_columns": 20,
    "table_format": "pipe",  # For tabulate library
    "float_format": ".2f",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "truncate_cell_length": 50,
}

# Testing and development constants
TEST_CONFIG = {
    "mock_cluster_uri": "https://test-cluster.kusto.windows.net",
    "mock_database": "TestDatabase",
    "mock_table": "TestTable",
    "sample_query": "TestTable | take 10",
    "test_memory_dir": "test_memory",
}