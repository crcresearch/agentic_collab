import paho.mqtt.client as mqtt
import logging
import time
from typing import List, Dict
from dataclasses import dataclass

from mqtt_gateway.config import (
  MQTT_BROKER_HOST,
  MQTT_BROKER_PORT,
  TOPIC_GATEWAY_MOVEMENT,
  TOPIC_ROBOTS_ENVIRONMENT,
)
from mqtt_gateway.models import (
  GatewayToRobotsMessage,
  RobotCommand,
  Position,
  RobotEnvironment,
  RobotsToGatewayMessage,
)


@dataclass
class Robot:
  """Represents a single robot managed by the server."""

  id: str
  position: Position
  status: str = "idle"


class RobotServer:
  def __init__(self, robot_ids: List[str]):
    self.robots: Dict[str, Robot] = {
      robot_id: Robot(id=robot_id, position=Position(x=0, y=0))
      for robot_id in robot_ids
    }

    # Initialize MQTT client
    self.mqtt_client = mqtt.Client(
      client_id=f"mock_robots_client",
    )
    self.mqtt_client.on_connect = self._on_connect
    self.mqtt_client.on_message = self._on_message

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(__name__)

  def _on_connect(self, client, userdata, flags, rc):
    """Callback for MQTT connection."""
    if rc == 0:
      self.logger.info("Robot server connected to MQTT broker")
      # Subscribe to movement commands
      self.mqtt_client.subscribe(TOPIC_GATEWAY_MOVEMENT)
    else:
      self.logger.error(f"Failed to connect to MQTT broker with code: {rc}")

  def _on_message(self, client, userdata, msg):
    """Callback for MQTT messages."""
    try:
      # Parse the message using Pydantic model
      message = GatewayToRobotsMessage.model_validate_json(msg.payload)

      # Process each command
      for command in message.commands:
        if command.robot_id in self.robots:
          self._execute_movement(command)
        else:
          self.logger.warning(f"Received command for unknown robot: {command.robot_id}")

      # After processing all commands, send a single environment update
      self._publish_environment_update()

    except Exception as e:
      self.logger.error(f"Error processing movement command: {e}")

  def _execute_movement(self, command: RobotCommand):
    """Execute the movement command."""
    try:
      robot = self.robots[command.robot_id]

      # Update robot position
      robot.position = command.position
      robot.status = "moving"
      self.logger.info(f"Robot {robot.id} moved to position: {command.position}")

      # Reset robot status after movement
      robot.status = "idle"

    except Exception as e:
      self.logger.error(f"Error executing movement: {e}")

  def _publish_environment_update(self):
    """Publish a single environment update message with all robots' status."""
    try:
      # Simulate perception for each robot
      robot_envs = []
      for robot in self.robots.values():
        perceived = (
          f"Robot '{robot.id}' is at position {robot.position} (status: {robot.status})"
        )
        robot_env = RobotEnvironment(
          robot_id=robot.id, position=robot.position, perceived=perceived
        )
        robot_envs.append(robot_env)

      # Create and publish message with all robots' status
      message = RobotsToGatewayMessage(robots=robot_envs)
      self.mqtt_client.publish(TOPIC_ROBOTS_ENVIRONMENT, message.model_dump_json())
      self.logger.info(f"Published environment update for {len(robot_envs)} robots")

    except Exception as e:
      self.logger.error(f"Error publishing environment update: {e}")

  def start(self):
    """Start the robot server."""
    try:
      self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
      self.mqtt_client.loop_start()
      self.logger.info(f"Robot server started with {len(self.robots)} robots")
    except Exception as e:
      self.logger.error(f"Failed to start robot server: {e}")
      raise

  def stop(self):
    """Stop the robot server."""
    self.mqtt_client.loop_stop()
    self.mqtt_client.disconnect()
    self.logger.info("Robot server stopped")


def main():
  # Create and start robot server with multiple robots
  robot_ids = ["Robot 1", "Robot 2", "Robot 3"]
  server = RobotServer(robot_ids=robot_ids)

  try:
    server.start()
    # Keep the server running
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    pass
  finally:
    server.stop()


if __name__ == "__main__":
  main()
