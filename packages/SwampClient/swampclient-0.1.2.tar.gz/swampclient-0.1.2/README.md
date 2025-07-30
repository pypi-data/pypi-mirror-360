# SwampClient

**SwampClient** is an MQTT client library built as a wrapper around the [Paho MQTT](https://www.eclipse.org/paho/) library. It is configureable using environment variables and integrates timestamp handling through the [Zeitgleich](https://pypi.org/project/Zeitgleich/) library. SwampClient supports managing multiple MQTT clients simultaneously and provides functionalities for message transformation and timestamp management within MQTT-based applications.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Usage and Examples](#usage-and-examples)
  - [Basic Example](#basic-example)
  - [Bridge Example](#bridge-example)
  - [Publish Example](#publish-example)
- [Data Formats](#data-formats)
- [TODOs](#todos)
- [License](#license)

## Features

- **Environment Variable Configuration:** Configure multiple MQTT clients using prefixed environment variables.
- **JSONata Transformations:** Apply JSONata expressions to transform MQTT message payloads.
- **Timestamp Handling:** Integrate with Zeitgleich for timestamp parsing, conversion, and validation.
- **Multiple Transport Protocols:** Supports MQTT over TCP, TLS, WebSockets, and Secure WebSockets.
- **Subscription Management:** Subscribe to multiple topics with configurable QoS levels.
- **Asynchronous Operations:** Utilize `asyncio` for non-blocking MQTT operations and concurrent tasks.
- **Logging:** Configurable log levels for monitoring and debugging.
- **Graceful Shutdown:** Ensure proper disconnection from MQTT brokers on application exit.

## Installation

Install SwampClient using `pip`:

```bash
pip install SwampClient
```

Ensure you also have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Configuration

SwampClient is configured through environment variables, allowing for easy management of multiple MQTT clients by using unique prefixes.

### Environment Variables

**Note:** All environment variable names are prefixed with the client name (e.g., `MQTTCLIENT1_`) to support multiple clients simultaneously.

| Environment Variable         | Description                                                                                                   | Default Value          | Tested |
|------------------------------|---------------------------------------------------------------------------------------------------------------|------------------------|--------|
| `[PREFIX]_URL`               | **MQTT Broker URL.** Connection string, including the protocol. Supported schemes: `mqtt`, `mqtts`, `ws`, `wss`. | `mqtt://localhost:1883`| ✅      |
| `[PREFIX]_USERNAME`          | **MQTT Username.** Username for MQTT broker authentication.                                                 | *None*                 | ❌      |
| `[PREFIX]_PASSWORD`          | **MQTT Password.** Password for MQTT broker authentication.                                                 | *None*                 | ❌      |
| `[PREFIX]_TOPICS`            | **MQTT Topics.** Comma-separated list of topics to subscribe to, each followed by `:qos`. Example: `topic1:0,topic2:1`. | *Empty String*         | ✅      |
| `[PREFIX]_JSONATA`           | **JSONata Expression Path.** Path to a JSONata expression file for transforming MQTT message payloads.      | *Empty String*         | ✅      |
| `[PREFIX]_TOPIC2PAYLOAD`     | **Topic to Payload Key.** Key name to inject the topic into the payload.                                    | *Empty String*         | ❌      |
| `[PREFIX]_LOG_LEVEL`         | **Log Level.** Sets the logging level for the client. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. | `DEBUG`                | ✅      |
| `[PREFIX]_RAW_DATA_HANDLING` | **Raw Data Handling.** Defines how to handle non-JSON payloads. Options: `wrap`, `pass_through`, `timeseries`.             | `wrap`                 | ❌      |
| `[PREFIX]_RAW_DATA_KEY`      | **Raw Data Key.** Key name used when wrapping raw data. Applicable if `RAW_DATA_HANDLING` is set to `wrap`.  | `raw_data`             | ✅      |
| `[PREFIX]_SPLIT_PAYLOAD`     | **Split Payload Expression.** JSONata expression to split payloads into multiple messages.                   | *None*                 | ❌      |
| `[PREFIX]_TIMESTAMP`         | **Timestamp Key.** Key name in the payload that contains the timestamp.                                      | `timestamp`            | ✅      |
| `[PREFIX]_TIMESTAMP_FROM`    | **Input Timestamp Format.** Format of the incoming timestamp. Options: `RFC3339`, `UNIX`, `ISO`, `EPOCH_S`, `EPOCH_NS`. | `EPOCH_S`              | ✅      |
| `[PREFIX]_TIMESTAMP_TO`      | **Output Timestamp Format.** Desired format for the timestamp in outgoing messages. Options: `RFC3339`, `UNIX`, `ISO`, `EPOCH_S`, `EPOCH_NS`. | `RFC3339`              | ✅      |

#### Example `.env` Configuration

```dotenv
# Example for MQTTCLIENT1
MQTTCLIENT1_URL="mqtt://localhost:1884"
MQTTCLIENT1_LOG_LEVEL="DEBUG"

# Example for MQTTCLIENT2
MQTTCLIENT2_URL="wss://broker.example.com:443"
MQTTCLIENT2_LOG_LEVEL="INFO"
```

## Usage and Examples

SwampClient provides interfaces to interact with MQTT brokers. Below are examples demonstrating different use cases, including initializing clients, subscribing to topics, handling incoming messages, and publishing messages.

### Basic Example

The **Basic Example** demonstrates initializing a single MQTT client, subscribing to topics, and handling incoming messages.

#### Running the Basic Example

1. **Set Up Environment Variables:**

   Ensure your `.env` file includes the necessary configurations for `MQTTCLIENT1`.

2. **Run the Example:**

   ```bash
   python swamp_mqtt_client/examples/basic.py
   ```

   **Functionality:**
   - Connects to the specified MQTT broker.
   - Subscribes to `test/topic` with QoS 0 and `test/topic2` with QoS 1.
   - Logs received messages on subscribed topics.
   - Handles graceful shutdown on receiving `KeyboardInterrupt`.

### Bridge Example

The **Bridge Example** shows how to bridge messages between two MQTT brokers. It subscribes to topics on a source broker and republishes messages to a target broker.

#### Running the Bridge Example

1. **Set Up Environment Variables:**

   Ensure your `.env` file includes the necessary configurations for both `SUBSCRIBE_CLIENT` and `PUBLISH_CLIENT`.

2. **Run the Example:**

   ```bash
   python swamp_mqtt_client/examples/bridge/bridge.py
   ```

   **Functionality:**
   - Subscribes to `source/topic` with QoS 0 and `source/topic2` with QoS 1 on the source broker.
   - Transforms incoming messages using the specified JSONata expression.
   - Republishes the transformed messages to `target/topic` on the target broker.
   - Handles graceful shutdown on receiving termination signals (`SIGINT`, `SIGTERM`).

### Publish Example

The **Publish Example** illustrates how to publish messages based on keyboard input to an MQTT topic.

#### Running the Publish Example

1. **Set Up Environment Variables:**

   Ensure your `.env` file includes the necessary configurations for `MQTTCLIENT1`.

2. **Run the Example:**

   ```bash
   python swamp_mqtt_client/examples/publish/publish.py
   ```

   **Functionality:**
   - Connects to the specified MQTT broker.
   - Listens for keyboard inputs and publishes each key press to the `keyboard/keys` topic.
   - Stops publishing and disconnects gracefully when the user types `exit` or interrupts the program.

## Data Formats

SwampClient uses the **Zeitgleich** library for timestamp handling. For detailed information on timestamp normalization and conversion, refer to the [Zeitgleich documentation](https://pypi.org/project/Zeitgleich/).

## TODOs

- **Unit Tests:**
  - Implement unit tests for SwampClient functionalities.
  - Test support for `mqtts`, `ws`, `wss` schemes.
  - Verify MQTT broker authentication with username and password.
  - Test `topic2payload` feature.
  - Validate `pass_through` raw data handling.
  - Test split payload functionality.

- **Configuration Enhancements:**
  - Add configuration options for Bridge mode.
  - Implement configuration for retaining messages.
  - Make configuration options dependent on each other (e.g., `split_payload` requires `jsonata_expression`).

- **Exception Handling:**
  - Wrap certain exceptions in custom exception classes.
  - Improve error handling for connection and publishing failures.

- **Documentation:**
  - Expand documentation for advanced configurations.
  - Provide more examples covering additional features.

- **Code-Level TODOs:**
  - Support configuration of all subscription options, not just QoS.
  - Use `ts.Origin` for origin handling.
  - Test `topic2payload` integration.
  - Handle additional payload cases in message processing.
  - Wrap disconnect errors in custom exceptions and handle logging appropriately.

- client.py 
  - line 142 publishes all payloads with retain = false by default.
  - Missing env var to configure required behavior
  
## License

Licensed under the [MIT License](LICENSE).