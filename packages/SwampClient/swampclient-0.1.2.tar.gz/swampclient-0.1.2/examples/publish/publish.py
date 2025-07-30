# swamp_mqtt_client/examples/basic.py

import asyncio
from dotenv import load_dotenv
import SwampClient as sc

load_dotenv()
logger = sc.setup_logger(__name__)

async def publish_keys(mqtt_client):
    loop = asyncio.get_running_loop()
    while True:
        try:
            key = await loop.run_in_executor(None, input, "Press a key (or type 'exit' to quit): ")
            if key.lower() == 'exit':
                logger.info("Exit command received. Stopping MQTT client.")
                mqtt_client.stop()
                break
            topic = "keyboard/keys"
            mqtt_client.publish(topic=topic, data={"key": key})
            logger.info(f"Published key: {key} to topic: {topic}")
        except Exception as e:
            logger.error(f"Error publishing key: {e}")

async def main():    
    global mqtt_client
    mqtt_client = sc.MQTTClient(
        name="MQTTCLIENT1"
    )
    
    try:
        await asyncio.gather(
            mqtt_client.run(),
            publish_keys(mqtt_client)
        )
    except ConnectionError as e:
        logger.error(f"MQTT Client encountered a connection error: {e}")
    except Exception as e:
        logger.error(f"MQTT Client encountered an error: {e}")
    except KeyboardInterrupt:
        logger.info("MQTT client stopped manually via KeyboardInterrupt.")
    finally:
        mqtt_client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MQTT client stopped manually via KeyboardInterrupt.")
