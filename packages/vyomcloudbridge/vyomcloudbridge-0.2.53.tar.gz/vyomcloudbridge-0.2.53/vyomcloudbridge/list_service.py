from vyomcloudbridge.services.queue_worker import QueueWorker
from vyomcloudbridge.services.dir_watcher import DirWatcher
from vyomcloudbridge.services.mission_stats import MissionStats
from vyomcloudbridge.services.machine_stats import MachineStats
from vyomcloudbridge.services.vyom_listener import VyomListener
from vyomcloudbridge.services.ros_publisher import RosPublisher
from typing import Dict, Type


AVAILABLE_SERVICES: Dict[str, Type] = {
    "queueworker": QueueWorker,
    "dirwatcher": DirWatcher,
    "missionstats": MissionStats,
    "machinestats": MachineStats,
    "vyomlistener": VyomListener,
    "rospublisher": RosPublisher,
}
