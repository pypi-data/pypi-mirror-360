"""Enums for DFT types"""

from enum import Enum


class SourceType(Enum):
    """Available data source types"""
    DATABASE = "database"
    POSTGRESQL = "postgresql" 
    CLICKHOUSE = "clickhouse"
    MYSQL = "mysql"
    API = "api"
    FILE = "file"
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    SLACK = "slack"
    MATTERMOST = "mattermost"
    WEBHOOK = "webhook"


class EndpointType(Enum):
    """Available data endpoint types"""
    DATABASE = "database"
    POSTGRESQL = "postgresql"
    CLICKHOUSE = "clickhouse" 
    MYSQL = "mysql"
    FILE = "file"
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    API = "api"
    SLACK = "slack"
    MATTERMOST = "mattermost"
    EMAIL = "email"
    WEBHOOK = "webhook"


class ProcessorType(Enum):
    """Available data processor types"""
    AGGREGATOR = "aggregator"
    FILTER = "filter"
    TRANSFORMER = "transformer"
    JOINER = "joiner"
    VALIDATOR = "validator"
    AB_TEST_CALCULATOR = "ab_test_calculator"
    CUSTOM = "custom"