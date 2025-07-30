import time
import threading
import os
import json
import uuid
from typing import Callable, List, Optional
import paho.mqtt.client as mqtt
import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# formatter = logging.Formatter(
#         "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#     )
# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)


class MqttServerClient:
    def __init__(
        self,
        broker_host: str = "3.110.9.183",
        broker_port: int = 8883,
        username: str = "machine_33",
        password: str = "ec12a22b3e100262f7bf00b9ae11eaa3",
        callback: Optional[Callable] = None,
        client_id_prefix: str = "server",
    ):
        try:
            self.broker_host = broker_host
            self.broker_port = broker_port
            self.username = username
            self.password = password
            self.callback = callback
            self.client_id = f"{client_id_prefix}_{uuid.uuid4().hex[:8]}"

            # Connection state tracking
            self.is_connected = False
            self.connection_lock = threading.Lock()
            self._connection_in_progress = False

            # Subscription tracking
            self.subscribed_topics = set()

            # Connection and reconnection parameters
            self.max_reconnect_attempts = 5
            self.base_reconnect_delay = 1
            self.reconnect_delay_max = 60

            # Initialize MQTT client
            self.mqtt_client = None
            self._create_mqtt_client()

            # Start connection monitoring
            self._start_connection_monitor()

        except Exception as e:
            print(f"Error- Error initializing MqttServerClient: {str(e)}")
            raise

    def _create_mqtt_client(self):
        """Create and configure MQTT client"""
        try:
            # Create MQTT client
            self.mqtt_client = mqtt.Client(
                client_id=self.client_id, clean_session=False, protocol=mqtt.MQTTv311
            )

            # Set username and password if provided
            if self.username and self.password:
                self.mqtt_client.username_pw_set(self.username, self.password)

            # Set callbacks
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.on_message = self._message_callback
            self.mqtt_client.on_subscribe = self._on_subscribe
            self.mqtt_client.on_publish = self._on_publish
            self.mqtt_client.on_log = self._on_log

            # Configure client options
            self.mqtt_client.max_inflight_messages_set(100)
            self.mqtt_client.max_queued_messages_set(1000)

            print("MQTT server client created successfully")

        except Exception as e:
            print(f"Error- Failed to create MQTT client: {str(e)}")
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker"""
        if rc == 0:
            print(
                f"Server client connected successfully to {self.broker_host}:{self.broker_port}"
            )
            with self.connection_lock:
                self.is_connected = True
                self._connection_in_progress = False

            # Resubscribe to topics
            self._resubscribe_to_topics()
        else:
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised",
            }
            print(
                f"Error- Failed to connect: {error_messages.get(rc, f'Unknown error code: {rc}')}"
            )
            with self.connection_lock:
                self.is_connected = False
                self._connection_in_progress = False

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker"""
        if rc != 0:
            print(
                f"Warning -Server client disconnected unexpectedly, return code: {rc}"
            )
        else:
            print("Server client disconnected gracefully")

        with self.connection_lock:
            self.is_connected = False

    def _message_callback(self, client, userdata, msg):
        """Callback for when message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            print(f"Received message from topic '{topic}': {payload}")

            if self.callback:
                self.callback(topic, payload)
            else:
                print(f"Debug - No callback provided, skipping callback execution")

        except Exception as e:
            print(f"Error- Error processing received message: {str(e)}")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for when subscription is confirmed"""
        print(f"Subscription confirmed with mid: {mid}, QoS: {granted_qos}")

    def _on_publish(self, client, userdata, mid):
        """Callback for when message is published"""
        print(f"Debug - Message published with mid: {mid}")

    def _on_log(self, client, userdata, level, buf):
        """Callback for MQTT client logs"""
        pass
        # print(f"Debug - MQTT Log: {buf}")

    def connect(self):
        """Connect to MQTT broker with exponential backoff"""
        with self.connection_lock:
            if self.is_connected:
                print("Already connected to MQTT broker")
                return True

            if self._connection_in_progress:
                print("Connection attempt already in progress")
                return False

            self._connection_in_progress = True

        try:
            for attempt in range(self.max_reconnect_attempts):
                try:
                    delay = min(
                        self.base_reconnect_delay * (2**attempt),
                        self.reconnect_delay_max,
                    )

                    if attempt > 0:
                        print(
                            f"Reconnection attempt {attempt + 1}/{self.max_reconnect_attempts}"
                        )
                        time.sleep(delay)

                    if self.mqtt_client is None:
                        print("Error- MQTT client is not initialized")
                        continue

                    # Connect to broker
                    self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
                    self.mqtt_client.loop_start()

                    # Wait for connection
                    timeout = 10
                    start_time = time.time()
                    while (
                        not self.is_connected and (time.time() - start_time) < timeout
                    ):
                        time.sleep(0.1)

                    if self.is_connected:
                        print("Successfully connected to MQTT broker")
                        return True
                    else:
                        print(f"Warning -Connection attempt {attempt + 1} timed out")

                except Exception as e:
                    print(f"Error- Connection attempt {attempt + 1} failed: {str(e)}")

            print("Error- Failed to connect after all attempts")
            return False

        finally:
            with self.connection_lock:
                self._connection_in_progress = False

    def _resubscribe_to_topics(self):
        """Resubscribe to all previously subscribed topics"""
        for topic in self.subscribed_topics.copy():
            try:
                if self.mqtt_client is None:
                    print("Error- MQTT client is not initialized")
                    continue

                result = self.mqtt_client.subscribe(topic, qos=1)
                if result[0] == mqtt.MQTT_ERR_SUCCESS:
                    print(f"Resubscribed to topic: {topic}")
                else:
                    print(f"Error- Failed to resubscribe to topic: {topic}")
            except Exception as e:
                print(f"Error- Error resubscribing to {topic}: {str(e)}")

    def subscribe_to_topic(self, topic: str, qos: int = 1):
        """Subscribe to any topic (server has full permissions)"""
        try:
            if not self.is_connected:
                if not self.connect():
                    raise ConnectionError("Failed to connect to MQTT broker")

            if self.mqtt_client is None:
                print("Error- MQTT client is not initialized")
                raise RuntimeError("MQTT client is not initialized")

            result = self.mqtt_client.subscribe(topic, qos=qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.subscribed_topics.add(topic)
                print(f"Subscribed to topic: {topic} with QoS: {qos}")
            else:
                print(f"Error- Failed to subscribe to topic: {topic}")
                raise Exception(f"Subscription failed with code: {result[0]}")

        except Exception as e:
            print(f"Error- Subscription to {topic} failed: {str(e)}")
            raise

    def subscribe_to_multiple_topics(self, topics: List[tuple]):
        """
        Subscribe to multiple topics at once
        topics: List of tuples (topic, qos)
        """
        try:
            if not self.is_connected:
                if not self.connect():
                    raise ConnectionError("Failed to connect to MQTT broker")

            if self.mqtt_client is None:
                print("Error- MQTT client is not initialized")
                raise RuntimeError("MQTT client is not initialized")

            # Convert to format expected by paho-mqtt
            topic_list = [(topic, qos) for topic, qos in topics]

            result = self.mqtt_client.subscribe(topic_list)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                for topic, qos in topics:
                    self.subscribed_topics.add(topic)
                print(f"Subscribed to {len(topics)} topics")
            else:
                print(f"Error- Failed to subscribe to multiple topics")
                raise Exception(f"Multiple subscription failed with code: {result[0]}")

        except Exception as e:
            print(f"Error- Multiple subscription failed: {str(e)}")
            raise

    def publish_message(self, topic: str, payload, qos: int = 1, retain: bool = False):
        """Publish message to any topic (server has full permissions)"""
        try:
            if not self.is_connected:
                if not self.connect():
                    print("Error- Failed to connect to MQTT broker for publishing")
                    return False

            if self.mqtt_client is None:
                print("Error- MQTT client is not initialized")
                return False

            # Convert payload to string if it's a dict
            if isinstance(payload, dict):
                payload = json.dumps(payload)

            print(f"Publishing message to topic: {topic}")
            result = self.mqtt_client.publish(topic, payload, qos=qos, retain=retain)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Message published successfully to topic: {topic}")
                return True
            else:
                print(f"Error- Failed to publish message, return code: {result.rc}")
                return False

        except Exception as e:
            print(f"Error- Publish to {topic} failed: {str(e)}")
            return False

    def publish_batch_messages(self, messages: List[dict]):
        """
        Publish multiple messages at once
        messages: List of dicts with keys: topic, payload, qos (optional), retain (optional)
        """
        try:
            if not self.is_connected:
                if not self.connect():
                    print(
                        "Error- Failed to connect to MQTT broker for batch publishing"
                    )
                    return False

            success_count = 0
            for msg in messages:
                topic = msg["topic"]
                payload = msg["payload"]
                qos = msg.get("qos", 1)
                retain = msg.get("retain", False)

                if self.publish_message(topic, payload, qos, retain):
                    success_count += 1

            print(
                f"Batch publish completed: {success_count}/{len(messages)} messages sent"
            )
            return success_count == len(messages)

        except Exception as e:
            print(f"Error- Batch publishing failed: {str(e)}")
            return False

    def unsubscribe_from_topic(self, topic: str):
        """Unsubscribe from a topic"""
        try:
            if not self.is_connected:
                print("Warning -Not connected to broker")
                return False

            if self.mqtt_client is None:
                print("Error- MQTT client is not initialized")
                return False

            result = self.mqtt_client.unsubscribe(topic)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.subscribed_topics.discard(topic)
                print(f"Unsubscribed from topic: {topic}")
                return True
            else:
                print(f"Error- Failed to unsubscribe from topic: {topic}")
                return False

        except Exception as e:
            print(f"Error- Unsubscribe from {topic} failed: {str(e)}")
            return False

    def get_connection_status(self):
        """Get current connection status and statistics"""
        return {
            "is_connected": self.is_connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "client_id": self.client_id,
            "subscribed_topics": list(self.subscribed_topics),
            "topic_count": len(self.subscribed_topics),
        }

    def _start_connection_monitor(self):
        """Start background thread to monitor connection"""

        def monitor_connection():
            while True:
                try:
                    if not self.is_connected and not self._connection_in_progress:
                        print("Warning -Connection lost. Attempting to reconnect...")
                        self.connect()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    print(f"Error- Connection monitoring failed: {str(e)}")
                    time.sleep(30)

        monitor_thread = threading.Thread(target=monitor_connection, daemon=True)
        monitor_thread.start()

    def disconnect(self):
        """Gracefully disconnect from MQTT broker"""
        try:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()

            with self.connection_lock:
                self.is_connected = False

            print("MQTT server client disconnected successfully")

        except Exception as e:
            print(f"Error- Failed to disconnect MQTT client: {str(e)}")

    # Administrative methods for server client
    def broadcast_message(self, topic_pattern: str, payload, qos: int = 1):
        """Broadcast message to all devices matching pattern"""
        try:
            # This would typically be used with topics like "broadcast/all" or "commands/all"
            return self.publish_message(topic_pattern, payload, qos, retain=False)
        except Exception as e:
            print(f"Error- Broadcast failed: {str(e)}")
            return False

    def send_command_to_device(self, device_id: str, command: dict):
        """Send command to specific device"""
        try:
            topic = f"commands/{device_id}"
            payload = json.dumps(command)
            return self.publish_message(topic, payload, qos=1)
        except Exception as e:
            print(f"Error- Failed to send command to device {device_id}: {str(e)}")
            return False

    def get_device_status(self, device_id: str, timeout: int = 5):
        """Request status from specific device"""
        try:
            # Subscribe to response topic
            response_topic = f"status/{device_id}/response"
            self.subscribe_to_topic(response_topic)

            # Send status request
            command_topic = f"commands/{device_id}"
            command = {"type": "status_request", "timestamp": time.time()}

            return self.publish_message(command_topic, json.dumps(command))
        except Exception as e:
            print(f"Error- Failed to request status from device {device_id}: {str(e)}")
            return False


def message_callback(topic, payload):
    try:
        print(f"Received message in callback '{topic}': {json.loads(payload)}")
    except Exception as e:
        print("Error- Error in calling callback")


def main():
    try:
        import signal

        # Connect to AWS IoT Core
        client = MqttServerClient(
            callback=message_callback,
        )

        client = MqttServerClient()
        machine_id = "32"

        # Publish a test message
        publish_topic_1 = f"vyom-mqtt-msg/{machine_id}/sample_source/34343434.json"
        message_connect = {
            "type": "CONNECT_DRONE",
            "data": {"droneId": machine_id, "timestamp": "number", "parameters": {}},
        }
        client.publish_message(
            topic=publish_topic_1, payload=json.dumps(message_connect)
        )

        # Subscribe to a test machine_id
        subscribe_topic_3 = f"vyom-mqtt-msg/{machine_id}/"
        client.subscribe_to_topic(subscribe_topic_3)

        subscribe_topic_4 = f"vyom-mqtt-msg/{machine_id}/#"
        client.subscribe_to_topic(subscribe_topic_4)

        is_running = True

        def signal_handler(sig, frame):
            global is_running
            print(f"Received signal {sig}, shutting down...")
            is_running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Keep the connection alive to receive messages
        print("Listening for messages... Press Ctrl+C to exit")
        while is_running:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
