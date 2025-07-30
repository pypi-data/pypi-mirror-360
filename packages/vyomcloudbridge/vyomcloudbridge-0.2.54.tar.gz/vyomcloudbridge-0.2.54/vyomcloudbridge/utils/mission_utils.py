import pika
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Union
import time
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.constants.constants import (
    DEFAULT_RABBITMQ_URL,
)
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.utils.common import get_mission_upload_dir
from vyomcloudbridge.constants.constants import (
    default_project_id,
)
from vyomcloudbridge.utils.logger_setup import setup_logger


class MissionUtils:
    """
    A service that maintains mission data statistics using RabbitMQ as a persistent store.
    Each mission_id has its own queue in RabbitMQ that stores the latest state of its data.
    Also maintains current mission and current user data in dedicated queues.
    """

    def __init__(self):
        """
        Initialize the mission data service with RabbitMQ connection.

        Args:
            rabbitmq_url: Connection URL for RabbitMQ
            logger: Optional logger instance
        """
        self.logger = setup_logger(
            name=self.__class__.__module__ + "." + self.__class__.__name__,
            show_terminal=False,
        )
        self.host: str = "localhost"
        self.rabbitmq_url = DEFAULT_RABBITMQ_URL
        self.mission_live_priority = 3

        self.rmq_conn = None
        self.rmq_channel = None
        self.rabbit_mq = RabbitMQ()
        self.machine_config = Configs.get_machine_config()
        self.machine_id = self.machine_config.get("machine_id", "-") or "-"
        self.organization_id = self.machine_config.get("organization_id", "-") or "-"
        self.data_source_name = "mission_stats"

    def generate_mission_id(self):
        try:
            epoch_ms = int(time.time() * 1000)
            mission_id = f"{epoch_ms}{self.machine_id}"
            return int(mission_id)
        except Exception as e:
            self.logger.error(f"Failed to generate unique mission_id: {str(e)}")
            raise

    def _setup_connection(self):
        """Set up RabbitMQ connection and declare the exchange for mission data."""
        try:
            # Establish connection
            self.rmq_conn = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            # self.rmq_conn = pika.BlockingConnection(
            #     pika.ConnectionParameters(
            #         host=self.host,
            #         heartbeat=600,
            #         blocked_connection_timeout=300,
            #         socket_timeout=300,
            #     )
            # )
            self.rmq_channel = self.rmq_conn.channel()
            self.rmq_channel.queue_declare(queue="current_mission", durable=True)

            self.logger.info("RabbitMQ connection established successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize RabbitMQ: {str(e)}")
            raise

    def _ensure_connection(self) -> bool:
        """Ensure connection and channel are active and working"""
        try:
            if not self.rmq_conn or self.rmq_conn.is_closed:
                self._setup_connection()
                return True

            if not self.rmq_channel or self.rmq_channel.is_closed:
                self.logger.info("Closed channel found, re-establishing...")
                self.rmq_channel = self.rmq_conn.channel()
                self.rmq_channel.queue_declare(queue="current_mission", durable=True)
                self.logger.info("Channel re-established successfully")

            return True
        except Exception as e:
            self.logger.error(f"Failed to ensure connection: {e}")
            self.rmq_conn = None
            self.rmq_channel = None
            return False

    def get_current_mission(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Retrieve the current mission details from RabbitMQ.

        Returns:
            Tuple:
                - dict or None: Current mission details if available, else None
                - str or None: Error message if any issue occurs, else None
        """
        try:
            if not self._ensure_connection():
                error_message = "Could not establish connection"
                self.logger.error(error_message)
                return None, error_message

            method_frame, _, body = self.rmq_channel.basic_get(
                queue="current_mission", auto_ack=False
            )

            mission_detail = None
            if method_frame:
                mission_detail = json.loads(body.decode("utf-8"))
                self.rmq_channel.basic_nack(
                    delivery_tag=method_frame.delivery_tag, requeue=True
                )
                self.logger.info(
                    f"Retrieved current mission: {mission_detail.get('id', 'unknown')}"
                )
            return mission_detail, None
        except Exception as e:
            error_message = f"Warning getting current mission: {str(e)}"
            self.logger.warning(error_message)
            return None, error_message

    def start_mission(
        self,
        id=None,  # Unique mission_id from Vyom services if available
        name=None,  # Human-readable name for the mission
        description=None,  # Description about the mission
        creator_id=None,  # User ID of the person initiating the mission
        owner_id=None,  # If someone else is the mission owner, provide their user ID
        project_id: Optional[Union[str, int]] = None,  # Project ID if available
        mission_date: Optional[str] = None,
        start_time: Optional[str] = None,
    ):
        """
        Start a new mission and publish its details to RabbitMQ for VyomIQ.

        Args:
            id (integer, optional): Unique mission ID. Auto-generated if not provided.
            name (str, optional): Name of the mission. Defaults to timestamp-based string.
            description (str, optional): Description of the mission.
            creator_id (int, optional): ID of the user creating the mission. Defaults to 1.
            owner_id (int, optional): ID of the mission owner. Defaults to creator_id.

        Returns:
            Tuple:
                - dict or None: Mission details if mission is successfully started, else None
                - str or None: Error message if any issue occurs, else None
        """
        existing_mission, mission_read_error = self.get_current_mission()
        if mission_read_error is not None:
            self.logger.error(
                f"Error in checking existing mission -{mission_read_error}"
            )
            return None, mission_read_error

        if existing_mission is not None:
            if existing_mission.get("mission_status") == 1:
                existing_mission_id = existing_mission.get("id")
                error_message = f"Mission with id={existing_mission_id} is already in progress, please complete it OR mark complete before starting new mission"
                self.logger.error(error_message)
                return None, error_message
            else:
                pass  # Existing mission already completed, so start new one
        try:
            project_id = int(project_id)
        except Exception as e:
            project_id = None
            pass

        if id is None:
            id = self.generate_mission_id()

        if name is None:
            name = (
                f"M_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')[:-3]}_UTC"
            )

        if mission_date is None:
            mission_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            if creator_id is None:
                creator_id = 1
            if owner_id is None:
                owner_id = creator_id

            mission_detail = {
                "id": id,
                "name": name,
                "description": description,
                "creator_id": creator_id,
                "owner_id": owner_id,
                "mission_status": 1,
                "campaign_id": project_id,  # campaign ID if available, else None
                "mission_date": mission_date,
                "start_time": start_time or datetime.now(timezone.utc).isoformat(),
                "end_time": None,
                "mission_type": "",
                "machine_id": self.machine_id,
                "json_data": {},
            }

            if not self._ensure_connection():
                error_message = "Could not establish connections, please try again"
                return None, error_message

            while True:
                method_frame, _, _ = self.rmq_channel.basic_get(
                    queue="current_mission", auto_ack=True
                )
                if not method_frame:
                    break

            self.rmq_channel.basic_publish(
                exchange="",
                routing_key="current_mission",
                body=json.dumps(mission_detail),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type="application/json",
                ),
            )
            self.logger.info(
                f"Updated current mission to {mission_detail.get('id', 'unknown')}"
            )

            # Publish mission data in real time
            now = datetime.now(timezone.utc)
            date = now.strftime("%Y-%m-%d")
            filename = int(time.time() * 1000)
            mission_upload_dir: str = get_mission_upload_dir(
                organization_id=self.organization_id,
                machine_id=self.machine_id,
                mission_id=id,
                data_source=self.data_source_name,
                date=date,
                project_id=default_project_id,
            )

            message_body = json.dumps({"mission": mission_detail, "data_stats": None})
            headers = {
                "topic": f"{mission_upload_dir}/{filename}.json",
                "message_type": "json",
                "destination_ids": ["s3"],
                "data_source": self.data_source_name,
                # meta data
                "buffer_key": str(id),
                "buffer_size": 0,
                "data_type": "json",
            }
            self.rabbit_mq.enqueue_message(
                message=message_body,
                headers=headers,
                priority=self.mission_live_priority,
            )

            return mission_detail, None
        except Exception as e:
            error_message = f"Error updating current mission: {str(e)}"
            self.logger.error(error_message)
            return None, error_message

    def end_current_mission(self):
        """
        Mark the current mission as completed and update RabbitMQ.

        Returns:
            Tuple:
                - success (bool): success, True if mission successfully marked as completed or no active mission found; False if error
                - error_message (str): error message if there is any error, else None in case of success
        """
        try:
            mission_detail, mission_read_error = self.get_current_mission()
            if mission_read_error is not None:
                return False, mission_read_error
            if mission_detail is not None:
                if mission_detail.get("mission_status") == 1:
                    existing_mission_id = mission_detail.get("id")
                    mission_detail["mission_status"] = 2
                    if not self._ensure_connection():
                        error_message = "Could not establish connection"
                        return False, error_message

                    while True:
                        method_frame, _, _ = self.rmq_channel.basic_get(
                            queue="current_mission", auto_ack=True
                        )
                        if not method_frame:
                            break

                    self.rmq_channel.basic_publish(
                        exchange="",
                        routing_key="current_mission",
                        body=json.dumps(mission_detail),
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                            content_type="application/json",
                        ),
                    )

                    # Publish mission data in real time
                    now = datetime.now(timezone.utc)
                    date = now.strftime("%Y-%m-%d")
                    filename = int(time.time() * 1000)
                    mission_upload_dir: str = get_mission_upload_dir(
                        organization_id=self.organization_id,
                        machine_id=self.machine_id,
                        mission_id=existing_mission_id,
                        data_source=self.data_source_name,
                        date=date,
                        project_id=default_project_id,
                    )

                    message_body = json.dumps(
                        {"mission": mission_detail, "data_stats": None}
                    )
                    headers = {
                        "topic": f"{mission_upload_dir}/{filename}.json",
                        "message_type": "json",
                        "destination_ids": ["s3"],
                        "data_source": self.data_source_name,
                        # meta data
                        "buffer_key": str(existing_mission_id),
                        "buffer_size": 0,
                        "data_type": "json",
                    }
                    self.rabbit_mq.enqueue_message(
                        message=message_body,
                        headers=headers,
                        priority=self.mission_live_priority,
                    )

                    self.logger.info(
                        f"Current mission with id={existing_mission_id}, marked completed"
                    )
                    return True, None
                else:
                    self.logger.info(f"No active mission found to mark completed")
                    return True, None
            else:
                self.logger.info(f"No active mission found to mark completed")
                return True, None
        except Exception as e:
            error_message = f"Error updating current mission: {str(e)}"
            self.logger.error(error_message)
            return False, error_message

    def is_healthy(self):
        """
        Check if the service is healthy.
        """
        return hasattr(self, "rmq_conn") and self.rmq_conn and self.rmq_conn.is_open

    def cleanup(self):
        """
        Clean up resources, closing connections and channels.
        """
        if hasattr(self, "rmq_conn") and self.rmq_conn and self.rmq_conn.is_open:
            self.rmq_conn.close()
            self.logger.info("RabbitMQ connection closed")
        self.rabbit_mq.close()

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            self.logger.error(
                "Destructor called by garbage collector to cleanup MissionUtils"
            )
            self.cleanup()
        except Exception as e:
            pass


def main():
    mission_stats = MissionUtils()

    try:
        success, error = mission_stats.end_current_mission()
        if error:
            print("Failed to end current mission:", error)
        else:
            print("Current mission ended successfully.")

        mission_detail, error = mission_stats.start_mission(
            name="optional_human_readable_name",
            description="Description of mission",
        )

        if error:
            print("Failed to start mission:", error)
        else:
            print("Mission started successfully:", mission_detail)

        # End the mission
        success, error = mission_stats.end_current_mission()
        if error:
            print("Failed to end current mission:", error)
        else:
            print("Mission ended successfully.")
    except KeyboardInterrupt:
        print("MissionUtils service interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        mission_stats.cleanup()
        print("MissionUtils service cleaned up and exited.")


if __name__ == "__main__":
    main()
