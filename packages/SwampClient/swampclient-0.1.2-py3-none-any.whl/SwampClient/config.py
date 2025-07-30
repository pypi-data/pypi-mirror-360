# swamp_mqtt_client/config.py

import os
from .logger import setup_logger
from paho.mqtt.subscribeoptions import SubscribeOptions

# Default values
DEFAULT_URL = "mqtt://localhost:1883"
DEFAULT_TOPICS = ""
DEFAULT_JSONATA = ""
DEFAULT_TOPIC2PAYLOAD = ""

# Logging stuff
ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
DEFAULT_LOG_LEVEL = "DEBUG"

# Raw data handling
ALLOWED_RAW_DATA_HANDLING = {"wrap", "pass_through", "timeseries"}
DEFAULT_RAW_DATA_HANDLING = "wrap"  # "wrap", "pass_through", "timeseries"
DEFAULT_RAW_DATA_KEY = "raw_data"
DEFAULT_SPLIT_PAYLOAD = None

# Timestamp format stuff
ALLOWED_TIMESTAMP_FORMATS = {"RFC3339", "UNIX", "ISO", "EPOCH_S", "EPOCH_NS", 'NONE'}
DEFAULT_TIMESTAMP_FROM = 'NONE'
DEFAULT_TIMESTAMP_TO = "RFC3339"

DEFAULT_AUTO_CONVERT_TS = "false"
DEFAULT_ORIGIN_FORMAT = r".+/.+"

# Data columns config
DEFAULT_DATA_COLUMNS = "value"  # minimal
DEFAULT_TIMESTAMP_COLUMN = "timestamp"

ALLOWED_EXTRA_COLUMNS_HANDLING = {"ignore", "error", "append"}
DEFAULT_EXTRA_COLUMNS_HANDLING = "append"

def parse_topics(topics_str: str) -> list[(str, SubscribeOptions)]:
    """Parses a 'topic:qos, topic:qos' string into (topic, SubscribeOptions) pairs."""
    topics = []
    for topic_qos in topics_str.split(','):
        if topic_qos.strip() == "":
            continue
        try:
            topic, qos_str = topic_qos.split(':')
            subscribe_options = SubscribeOptions(
                qos=int(qos_str.strip()),
                noLocal=False,
                retainAsPublished=False,
                retainHandling=SubscribeOptions.RETAIN_SEND_ON_SUBSCRIBE
            )
            topics.append((topic.strip(), subscribe_options))
        except ValueError:
            raise ValueError(f"Invalid topic format: '{topic_qos}'. Expected 'topic:qos'.")
    return topics

class Config:
    """
    Configuration class for MQTTClient, loaded from environment.
    
    Environment Variables:
    - {PREFIX}_URL, {PREFIX}_USERNAME, {PREFIX}_PASSWORD, ...
    - {PREFIX}_DATA_COLUMNS  -> e.g. "value" (comma-separated)
    - {PREFIX}_TIMESTAMP_COLUMN
    - {PREFIX}_ORIGIN_FORMAT
    - {PREFIX}_EXTRA_COLUMNS_HANDLING -> "ignore","error","append"
    ...
    """

    def __init__(self, env_prefix: str = "MQTT"):
        self.env_prefix: str = env_prefix.upper()

        self.url: str = os.getenv(f"{self.env_prefix}_URL", DEFAULT_URL)
        self.username: str = os.getenv(f"{self.env_prefix}_USERNAME")
        self.password: str = os.getenv(f"{self.env_prefix}_PASSWORD")

        topics_str: str = os.getenv(f"{self.env_prefix}_TOPICS", DEFAULT_TOPICS)
        self.subscriptions = parse_topics(topics_str)

        self.jsonata_expression: str = os.getenv(f"{self.env_prefix}_JSONATA", DEFAULT_JSONATA)
        self.topic2payload: str = os.getenv(f"{self.env_prefix}_TOPIC2PAYLOAD", DEFAULT_TOPIC2PAYLOAD)
        
        log_level = os.getenv(f"{self.env_prefix}_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
        if log_level not in ALLOWED_LOG_LEVELS:
            raise ValueError(f"Invalid LOG_LEVEL '{log_level}', allowed: {ALLOWED_LOG_LEVELS}")
        self.log_level = log_level

        raw_data_handling = os.getenv(f"{self.env_prefix}_RAW_DATA_HANDLING", DEFAULT_RAW_DATA_HANDLING).lower()
        if raw_data_handling not in ALLOWED_RAW_DATA_HANDLING:
            raise ValueError(f"Invalid RAW_DATA_HANDLING '{raw_data_handling}', allowed: {ALLOWED_RAW_DATA_HANDLING}")
        self.raw_data_handling = raw_data_handling

        self.raw_data_key = os.getenv(f"{self.env_prefix}_RAW_DATA_KEY", DEFAULT_RAW_DATA_KEY)
        self.split_payload = os.getenv(f"{self.env_prefix}_SPLIT_PAYLOAD", DEFAULT_SPLIT_PAYLOAD)

        # Validate timestamp_from/timestamp_to
        ts_from = os.getenv(f"{self.env_prefix}_TIMESTAMP_FROM", DEFAULT_TIMESTAMP_FROM).upper()
        if ts_from not in ALLOWED_TIMESTAMP_FORMATS:
            raise ValueError(f"Invalid TIMESTAMP_FROM '{ts_from}', allowed: {ALLOWED_TIMESTAMP_FORMATS}")
        if ts_from == 'NONE':
            ts_from = None
        self.timestamp_from = ts_from

        ts_to = os.getenv(f"{self.env_prefix}_TIMESTAMP_TO", DEFAULT_TIMESTAMP_TO).upper()
        if ts_to not in ALLOWED_TIMESTAMP_FORMATS:
            raise ValueError(f"Invalid TIMESTAMP_TO '{ts_to}', allowed: {ALLOWED_TIMESTAMP_FORMATS}")
        self.timestamp_to = ts_to

        auto_ts = os.getenv(f"{self.env_prefix}_AUTO_CONVERT_TS", DEFAULT_AUTO_CONVERT_TS).lower()
        self.auto_convert_ts = (auto_ts in ["true", "1", "yes"])

        self.origin_format = os.getenv(f"{self.env_prefix}_ORIGIN_FORMAT", DEFAULT_ORIGIN_FORMAT)

        # Data columns
        data_cols_str = os.getenv(f"{self.env_prefix}_DATA_COLUMNS", DEFAULT_DATA_COLUMNS)
        self.data_columns = [col.strip() for col in data_cols_str.split(',') if col.strip()]

        # Timestamp column
        self.timestamp_column = os.getenv(f"{self.env_prefix}_TIMESTAMP_COLUMN", DEFAULT_TIMESTAMP_COLUMN)

        # Extra columns handling
        extra_handling = os.getenv(f"{self.env_prefix}_EXTRA_COLUMNS_HANDLING", DEFAULT_EXTRA_COLUMNS_HANDLING).lower()
        if extra_handling not in ALLOWED_EXTRA_COLUMNS_HANDLING:
            raise ValueError(
                f"Invalid EXTRA_COLUMNS_HANDLING '{extra_handling}', must be one of {ALLOWED_EXTRA_COLUMNS_HANDLING}"
            )
        self.extra_columns_handling = extra_handling

        from .logger import setup_logger
        self.logger = setup_logger("CONFIG_" + self.env_prefix, level=self.log_level)
        self.logger.debug(self)

    def __repr__(self):
        return (f"Config("
                f"url={self.url}, log_level={self.log_level}, data_columns={self.data_columns}, "
                f"timestamp_column={self.timestamp_column}, extra_columns_handling={self.extra_columns_handling}, "
                f"subscriptions={self.subscriptions}, jsonata_expression={self.jsonata_expression}, "
                f"topic2payload={self.topic2payload}, raw_data_handling={self.raw_data_handling}, "
                f"raw_data_key={self.raw_data_key}, split_payload={self.split_payload}, "
                f"timestamp_from={self.timestamp_from}, timestamp_to={self.timestamp_to}, "
                f"auto_convert_ts={self.auto_convert_ts}, origin_format={self.origin_format}"
                ")")
    