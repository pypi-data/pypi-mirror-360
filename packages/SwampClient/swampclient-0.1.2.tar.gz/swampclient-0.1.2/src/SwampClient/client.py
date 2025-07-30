# swamp_mqtt_client/mqtt_client.py

import json
import uuid
import asyncio
import logging
from typing import Callable, Optional
import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
import jsonata
from urllib.parse import urlparse

from Zeitgleich import TimestampFormat, TimeSeriesData, Origin
from .config import Config
from .logger import setup_logger

class MQTTClient:
    def __init__(self, name: str = "MQTT", on_data: Optional[Callable] = None, subscribe_topics: Optional[list] = None):
        self.name = name
        self.on_data = on_data
        self.stop_event = asyncio.Event()
        self.config = Config(env_prefix=self.name.upper())
        self.logger = setup_logger("CLIENT_" + self.name, level=self.config.log_level)
        # list of tuple containing (topic/#, subscribe_options)
        self.subscribe_topics = self.parse_sub_topics(subscribe_topics)
        self.current_subscription = set()
        parsed_url = urlparse(self.config.url)
        scheme = parsed_url.scheme.lower()
        SCHEMAS = {
            "mqtt":  (False, "tcp", 1883),
            "mqtts": (True,  "tcp", 8883),
            "ws":    (False, "websockets", 80),
            "wss":   (True,  "websockets", 443),
        }

        if scheme not in SCHEMAS:
            msg = f"Unsupported URL scheme: '{scheme}'. Supported: {', '.join(SCHEMAS.keys())}"
            self.logger.error(msg)
            raise ValueError(msg)

        self.tls_used, self.transport, default_port = SCHEMAS[scheme]
        self.hostname = parsed_url.hostname or "localhost"
        self.port = parsed_url.port or default_port
        self.ws_path = parsed_url.path if self.transport == "websockets" else None

        self.logger.debug(
            f"Parsed URL: Hostname={self.hostname} Port={self.port} "
            f"Transport={self.transport} TLS={self.tls_used} WS Path={self.ws_path}"
        )

        self.client = self._create_client()
        # self._is_connected = asyncio.Event()

        # try:
        #     self.loop = asyncio.get_running_loop()
        # except RuntimeError:
        #     self.loop = asyncio.get_event_loop()

        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

        # JSONATA
        jsonata_transformation = None
        if self.config.jsonata_expression:
            try:
                with open(self.config.jsonata_expression, 'r') as f:
                    expr_text = f.read()
                jsonata_transformation = jsonata.Jsonata(expr_text)
                self.logger.info(f"JSONATA transformation loaded from '{self.config.jsonata_expression}'")
            except Exception as e:
                self.logger.error(f"Failed to load JSONATA expression: {e}")
        self.jsonata_transformation = jsonata_transformation

    def _create_client(self):
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.name + str(uuid.uuid4()),
            clean_session=None,
            userdata=None,
            protocol=mqtt.MQTTv5,
            transport=self.transport,
            manual_ack=False
        )
        if self.config.username and self.config.password:
            client.username_pw_set(self.config.username, self.config.password)
            self.logger.info(f"Configured MQTT client with username='{self.config.username}'")

        if self.tls_used:
            client.tls_set()
            self.logger.info("TLS is enabled.")
        if self.transport == "websockets" and self.ws_path:
            client.ws_set_options(path=self.ws_path)
            self.logger.info(f"WebSockets path set to '{self.ws_path}'.")

        client.on_connect = self._on_connect
        client.on_connect_fail = self._on_connect_fail
        client.on_disconnect = self._on_disconnect
        client.on_log = None
        client.on_message = self._on_message
        client.on_subscribe = self._on_subscribe
        client.on_unsubscribe = self._on_unsubscribe

        return client

    async def connect(self):
        self.logger.info(f"Connecting to MQTT Broker: {self.hostname}:{self.port}")
        self.client.connect_async(
            host=self.hostname,
            port=self.port,
            keepalive=60,
            bind_address="",
            bind_port=0,
            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
            properties=None
        )
        self.client.loop_start()

        try:
            await asyncio.wait_for(self._is_connected.wait(), timeout=10)
            self.logger.info("Successfully connected to MQTT Broker.")
        except asyncio.TimeoutError:
            self.logger.error("Connection to MQTT Broker timed out.")
            raise ConnectionError("Connection to MQTT Broker timed out.")

    def disconnect(self):
        if self.client.is_connected():
            self.logger.info(f"Disconnecting from MQTT Broker: {self.hostname}:{self.port}")
            result = self.client.disconnect()
            if result != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to initiate disconnect. Error: {mqtt.error_string(result)}")
                raise ConnectionError(f"Failed to initiate disconnect. Error: {mqtt.error_string(result)}")
            self.client.loop_stop()
            self.logger.info(f"Disconnected from MQTT Broker: {self.hostname}:{self.port}")
        else:
            self.logger.info("Client is already disconnected.")

    def publish_timeseries(self, ts_data: TimeSeriesData) -> None:
        if not self._is_connected.is_set():
            self.logger.warning("Cannot publish TimeSeriesData, client is not connected.")
            raise ConnectionError("Cannot publish TimeSeriesData, client is not connected.")

        df = ts_data.df.copy()
        df = df.reset_index()
        rows = df.to_dict(orient="records")

        for row in rows:
            self.publish(topic=ts_data.origin, data=row)


    def publish(self, topic: str, data: dict, qos: int = 0, retain: bool = False):
        if self._is_connected.is_set():
            try:
                payload = json.dumps(data)
                self.logger.debug(f"Publishing: Topic={topic}, Data={payload}, QoS={qos}, Retain={retain}")
                result = self.client.publish(
                    topic=topic,
                    payload=payload,
                    qos=qos,
                    retain=retain,
                    properties=None
                )
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    msg = f"Failed to publish message. Error: {mqtt.error_string(result.rc)}"
                    self.logger.error(msg)
                    raise ValueError(msg)
            except (TypeError, ValueError) as e:
                self.logger.error(f"Failed to serialize data for publishing: {e}")
                raise ValueError(f"Failed to serialize data for publishing: {e}")
        else:
            self.logger.warning("Cannot publish, client is not connected.")
            raise ConnectionError("Cannot publish, client is not connected.")

    def publish_data(self, data: dict, machine: str):
        """A convenience method for publishing data with a constructed topic."""
        if self._is_connected.is_set():
            topic = data.get("id", "default")
            topic = f"{machine}/{topic}/value"
            self.logger.info(f"Publishing data: Topic={topic}, Data={data}")
            timestamp = data.get("target", {}).get("timestamp", None)

            if timestamp is not None:
                try:
                    converted_ts = TimestampFormat.convert(
                        data=timestamp,
                        input_format=TimestampFormat[self.config.timestamp_from],
                        output_format=TimestampFormat[self.config.timestamp_to]
                    )
                    self.publish(
                        topic=topic,
                        data={
                            self.config.timestamp_column: converted_ts,
                            'value': data.get('value', None)
                        }
                    )
                except ValueError as e:
                    self.logger.error(f"Timestamp conversion error: {e}")
            else:
                self.publish(
                    topic=topic,
                    data={
                        self.config.timestamp_column: None,
                        'value': data.get('value', None)
                    }
                )
        else:
            self.logger.warning("Cannot publish data, client is not connected.")
            raise ConnectionError("Cannot publish data, client is not connected.")

    # parses subscribe topics of [Machine/#, qos]
    def parse_sub_topics(self, sub_topics:list[tuple[str, int]]):
        if not sub_topics or sub_topics == []:
            return None
        topics = []
        for topic_tuple in sub_topics:
            try:
                topic = topic_tuple[0]
                qos = topic_tuple[1]
                subscribe_options = SubscribeOptions(
                    qos=qos,
                    noLocal=False,
                    retainAsPublished=False,
                    retainHandling=SubscribeOptions.RETAIN_SEND_ON_SUBSCRIBE
                )
                topics.append((topic.strip(), subscribe_options))
            except Exception as err:
                self.logger.error(f"Error during parsing of subscribe topics: {sub_topics}")
        return topics

    def unsubscribe(self, machine:list):
        if machine:
            result, mid = self.client.unsubscribe(machine)
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Topics {machine} unsubscribed, Message ID={mid}")
                self.current_subscription = self.current_subscription.difference(machine)
            else:
                err = f"Failed to unsubscribe topics: {machine}. Error: {mqtt.error_string(result)}"
                self.logger.error(err)
    
    def get_current_subscriptions(self) -> set:
        return self.current_subscription.copy()
    
    def _on_connect(self, client: mqtt.Client, userdata, connect_flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode, properties):
        if not reason_code.is_failure:
            self.logger.info(f"Connected to MQTT Broker: {self.hostname}:{self.port}")
            self.loop.call_soon_threadsafe(self._is_connected.set)
            
            # overwrite with own subscribe_topics
            topics = self.subscribe_topics if self.subscribe_topics else self.config.subscriptions
            
            if not topics:
                self.logger.warning("No subscriptions configured.")
                return
            
            result, mid = self.client.subscribe(topics)
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Subscribing to topics={topics}, Message ID={mid}")
                for topic in topics:
                    self.current_subscription.add(topic[0])
            else:
                err = f"Failed to subscribe to topics: {topics}. Error: {mqtt.error_string(result)}"
                self.logger.error(err)

        else:
            self.logger.error(f"Failed to connect, return code {reason_code.getName()}")

    def _on_connect_fail(self, client: mqtt.Client, userdata):
        self.logger.error("Connection to MQTT Broker failed.")
        self.loop.call_soon_threadsafe(self._is_connected.clear)

    def _on_disconnect(self, client: mqtt.Client, userdata, disconnect_flags, reason_code, properties):
        if not reason_code or not reason_code.is_failure:
            self.logger.info(f"Disconnected from MQTT Broker: {self.hostname}:{self.port}")
        else:
            self.logger.warning(f"Unexpected disconnection from MQTT Broker: {self.hostname}:{self.port}, Reason: {reason_code.getName()}")
            self.loop.call_soon_threadsafe(self._is_connected.clear)

    def _on_subscribe(self, client: mqtt.Client, userdata, mid, reason_code_list, properties):
        self.logger.debug(f"Subscription successful with Message ID: {mid}")

    def _on_unsubscribe(self, client: mqtt.Client, userdata, mid, reason_code_list, properties):
        self.logger.debug(f"Unsubscription successful with Message ID: {mid}")

    def _on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        """Callback when a message is received on a subscribed topic."""
        self.logger.debug(f"Message received:\nTopic: {message.topic}\nPayload: {message.payload}")
        try:
            payload_str = message.payload.decode('utf-8').strip()
            try:
                payload = json.loads(payload_str)
                is_json = True
            except json.JSONDecodeError:
                payload = payload_str
                is_json = False

            if is_json and isinstance(payload, dict):
                # Insert the topic if configured
                if self.config.topic2payload:
                    payload[self.config.topic2payload] = message.topic

                # JSONATA
                if self.jsonata_transformation:
                    try:
                        payload = self.jsonata_transformation.evaluate(payload)
                        self.logger.debug(f"Jsonata transformed payload: {payload}")
                    except Exception as e:
                        self.logger.error(f"JSONATA transformation failed: {e}")
                        raise ValueError(f"JSONATA transformation failed: {e}")

                
                #! Not needed... Either use autoconvert or manual invoke TimeSeriesData() on payload to convert/normalize ts ...
                # # Convert the timestamp column if present
                # ts_val = payload.get(self.config.timestamp_column)
                # if ts_val is not None:
                #     converted_ts = TimestampFormat.convert(
                #         data=ts_val,
                #         input_format=defaultConfig,
                #         output_format=TimestampFormat[self.config.timestamp_to]
                #     )
                #     payload[self.config.timestamp_column] = converted_ts
                # else:
                #     self.logger.warning(
                #         f"Timestamp column '{self.config.timestamp_column}' not found in payload. Payload={payload}"
                #     )

                # Auto-convert to TimeSeriesData if enabled
                if self.on_data and self.config.auto_convert_ts:
                    try:
                        ts_data = TimeSeriesData(
                            origin=Origin(message.topic),
                            data=payload,
                            input_timestamp_format=TimestampFormat[self.config.timestamp_to],
                            output_timestamp_format=TimestampFormat[self.config.timestamp_to],
                            time_column=self.config.timestamp_column,
                            origin_regex=self.config.origin_format,
                            value_columns=self.config.data_columns,
                            extra_columns_handling=self.config.extra_columns_handling
                        )
                        payload = ts_data
                    except Exception as e:
                        self.logger.error(f"Failed to autoconvert payload to TimeSeriesData for topic: [{message.topic}] and payload: {message.payload}\nError: {str(e)}")

                # Invoke on_data callback
                if self.on_data:
                    if self.config.split_payload and isinstance(payload, list):
                        split = jsonata.Jsonata(self.config.split_payload).evaluate(payload)
                        self.logger.debug(f"Splitting message payload into {len(split)} parts")
                        for msg in split:
                            topic = msg.pop("topic", message.topic)
                            self.on_data(client, userdata, topic, msg)
                    elif self.config.split_payload:
                        split_payload = jsonata.Jsonata(self.config.split_payload).evaluate(payload)
                        if isinstance(split_payload, list):
                            for msg in split_payload:
                                topic = msg.pop("topic", message.topic)
                                self.on_data(client, userdata, topic, msg)
                        else:
                            topic = split_payload.pop("topic", message.topic) if isinstance(split_payload, dict) else message.topic
                            self.on_data(client, userdata, topic, split_payload)
                    else:
                        self.on_data(client, userdata, message.topic, payload)
            else:
                # Non-JSON payload
                if self.config.raw_data_handling == "wrap":
                    structured_payload = {self.config.raw_data_key: payload}
                    if self.on_data:
                        self.on_data(client, userdata, message.topic, structured_payload)
                elif self.config.raw_data_handling == "pass_through":
                    if self.on_data:
                        self.on_data(client, userdata, message.topic, payload)
                elif self.config.raw_data_handling == "timeseries":
                    try:
                        # Use the current timestamp if no timestamp is provided
                        payload = {
                            self.config.timestamp_column: TimestampFormat.get_current_timestamp(),
                            'value': payload
                        }
                        ts_data = TimeSeriesData(
                            origin=Origin(message.topic),
                            data=payload,
                            input_timestamp_format=TimestampFormat.RFC3339,
                            output_timestamp_format=TimestampFormat[self.config.timestamp_to],
                            time_column=self.config.timestamp_column,
                            origin_regex=self.config.origin_format,
                            value_columns=self.config.data_columns,
                            extra_columns_handling=self.config.extra_columns_handling
                        )
                        if self.on_data:
                            self.on_data(client, userdata, message.topic, ts_data)
                    except Exception as e:
                        self.logger.error(f"Failed to convert raw payload to TimeSeriesData: {e}")
                else:
                    self.logger.error(f"Invalid RAW_DATA_HANDLING: {self.config.raw_data_handling}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e} | Topic: {message.topic} | Data: {payload}")

    async def run(self):
        """Async method to connect and keep the MQTT loop running."""
        try:
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.get_event_loop()
            self._is_connected = asyncio.Event()
            await self.connect()
            while not self.stop_event.is_set():
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info("Run loop cancelled.")
        except Exception as e:
            self.logger.error(f"Run loop encountered an error: {e}")
        finally:
            try:
                self.disconnect()
            except ConnectionError as e:
                self.logger.error(f"Error during disconnect: {e}")

    def stop(self):
        """Stop the MQTT loop."""
        self.stop_event.set()
