# swamp_mqtt_client/examples/basic.py

import asyncio

from dotenv import load_dotenv
import SwampClient as sc

load_dotenv()
logger = sc.setup_logger(__name__)

def on_data(client, userdata, topic, payload):
    logger.info(f"Received data on topic '{topic}': {payload}")
    
async def main():    
    
    mqtt_client = sc.MQTTClient(
        name="MQTTCLIENT1",
        on_data=on_data
    )

    mqtt_client.config.subscriptions.append(("test/topic", 0)) # either like this or in the env variables
    mqtt_client.config.subscriptions.append(("test/topic2", 1))
    try:
        await mqtt_client.run()
    except ConnectionError as e:
        logger.error(f"MQTT Client encountered a connection error: {e}")
    except Exception as e:
        logger.error(f"MQTT Client encountered an error: {e}")
    except KeyboardInterrupt:
        logger.info("MQTT client stopped manually.")
    finally:
        mqtt_client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MQTT client stopped manually.")
