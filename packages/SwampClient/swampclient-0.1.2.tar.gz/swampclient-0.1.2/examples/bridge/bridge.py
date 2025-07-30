# examples/bridge/bridge.py

import os
import asyncio
import signal
from dotenv import load_dotenv

from SwampClient import MQTTClient, setup_logger

# Load environment variables from .env if present
load_dotenv()

# Initialize logger
logger = setup_logger("BRIDGE", level=os.getenv("BRIDGE_LOG_LEVEL", "DEBUG"))

# Define the on_data callback function
def on_data_handler(client, userdata, topic, payload):
    logger.warning("TARGET_MQTT_TOPIC not set. Republishing to original topic.")
    target_topic = os.getenv("TARGET_MQTT_TOPIC")
    try:
        publish_client.publish(topic=target_topic, data=payload)
    except Exception as e:
        logger.error(f"Failed to publish to original topic '{topic}': {e}")

async def main():
    global publish_client
    subscribe_client = MQTTClient(
        name="SUBSCRIBE_CLIENT",
        on_data=on_data_handler
    )
    
    publish_client = MQTTClient(
        name="PUBLISH_CLIENT"
    )
    await asyncio.gather(subscribe_client.run(), publish_client.run())

def handle_shutdown(loop, tasks):
    logger.info("Shutdown initiated. Cancelling tasks...")
    for task in tasks:
        task.cancel()
    loop.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    main_task = loop.create_task(main())
    
    for signal_name in {'SIGINT', 'SIGTERM'}:
        try:
            loop.add_signal_handler(getattr(signal, signal_name), handle_shutdown, loop, [main_task])
        except NotImplementedError:
            pass
    
    try:
        loop.run_until_complete(main_task)
    except asyncio.CancelledError:
        logger.info("Main task was cancelled.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        loop.close()
        logger.info("Event loop closed. Application shutdown.")
