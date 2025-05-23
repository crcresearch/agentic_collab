import json
import logging
import os
from mqtt_gateway.models import (
  BackendToGatewayMessage,
  RobotsToGatewayMessage,
  GatewayToRobotsMessage,
  GatewayToBackendMessage,
  RobotCommand,
  PersonaEnvironment,
  Position,
)
from mqtt_gateway.coordinate_converter import CoordinateConverter
from mqtt_gateway.coordinate_visualizer import CoordinateVisualizer

class MessageConverter:
  def __init__(self):
    sim_origin = (0, 0)
    sim_unit_ft = 0.784
    sim_unit_m = sim_unit_ft / 3.281

    robots_origin_x = 61.1 / sim_unit_ft
    robots_origin_y = 11.36 / sim_unit_ft
    robots_origin = (robots_origin_x, robots_origin_y)
    robots_unit_m = 1

    print("Creating coordinate converter")
    self.coordinate_converter = CoordinateConverter(
      source_origin=sim_origin,
      target_origin=robots_origin,
      rotation_angle=90,
      scale_factor=robots_unit_m / sim_unit_m,
      reflect_x=False,
      reflect_y=True,
    )
    print("Creating coordinate visualizer")
    self.coordinate_visualizer = CoordinateVisualizer(
      converter=self.coordinate_converter,
      background_image_path=os.path.join(
        os.path.dirname(__file__), "img", "sim_space.png")
    )

    # Initialize state
    self.current_maze = "the_ville"
    self.current_step = 0

  def backend_to_robots(self, mqtt_message: str) -> str:
    """
    Convert backend MQTT message to robot-compatible MQTT format.
    Converts BackendToGatewayMessage to GatewayToRobotsMessage.

    Args:
        mqtt_message: JSON string from backend containing BackendToGatewayMessage

    Returns:
        JSON string in robot-compatible format (GatewayToRobotsMessage)
    """
    try:
      backend_msg = BackendToGatewayMessage.model_validate_json(mqtt_message)
      commands = []

      # Store the current step from backend
      self.current_step = backend_msg.step

      for persona_id, movement in backend_msg.movements.persona.items():
        # Convert simulation coordinates to robot coordinates
        sim_coords = movement.movement
        robot_coords = self.coordinate_converter.convert_point(sim_coords)
        logging.info(f"Agent '{persona_id}': Converted sim coords {sim_coords} to robot coords {robot_coords}")
        fig = self.coordinate_visualizer.plot_coordinate_transformation(
          source_points=[sim_coords],
          # target_points=[robot_coords],
          title=f"Agent '{persona_id}' - Transformation",
        )
        fig.savefig(os.path.join(os.path.dirname(__file__), "img", f"agent_{persona_id}_transformation.png"))
        rounded_coords = (round(robot_coords[0]), round(robot_coords[1]))
        logging.info(f"Rounded robot coords to {rounded_coords}")

        command = RobotCommand(
          robot_id=persona_id,
          position=Position(x=rounded_coords[0], y=rounded_coords[1]),
        )
        commands.append(command)

      robot_msg = GatewayToRobotsMessage(commands=commands)
      return robot_msg.model_dump_json()

    except Exception as e:
      raise ValueError(f"Failed to convert backend message to robot format: {e}")

  def robots_to_backend(self, mqtt_message: str) -> str:
    """
    Convert robot MQTT message to backend-compatible format.
    Converts RobotsToGatewayMessage to GatewayToBackendMessage.

    Args:
        mqtt_message: JSON string from robots containing RobotsToGatewayMessage

    Returns:
        JSON string in backend-compatible format (GatewayToBackendMessage)
    """
    try:
      robots_msg = RobotsToGatewayMessage.model_validate_json(mqtt_message)
      environment = {}

      for robot in robots_msg.robots:
        # Convert robot coordinates to simulation coordinates
        robot_coords = (robot.position.x, robot.position.y)
        sim_coords = self.coordinate_converter.inverse_convert_point(robot_coords)
        logging.info(f"Robot '{robot.robot_id}': Converted robot coords {robot_coords} to sim coords {sim_coords}")
        fig = self.coordinate_visualizer.plot_inverse_transformation(
          target_points=[robot_coords],
          # source_points=[sim_coords],
          title=f"Robot '{robot.robot_id}' - Inverse Transformation",
        )
        fig.savefig(os.path.join(os.path.dirname(__file__), "img", f"robot_{robot.robot_id}_inverse_transformation.png"))
        rounded_coords = (round(sim_coords[0]), round(sim_coords[1]))
        logging.info(f"Rounded sim coords to {rounded_coords}")

        persona_env = PersonaEnvironment(
          x=rounded_coords[0],
          y=rounded_coords[1],
          perceived=robot.perceived,
          maze=self.current_maze,
        )
        environment[robot.robot_id] = persona_env

      # Increment step count for the next message to backend
      next_step = self.current_step + 1

      backend_msg = GatewayToBackendMessage(
        environment=environment,
        step=next_step,
      )
      return backend_msg.model_dump_json()

    except Exception as e:
      raise ValueError(f"Failed to convert robot message to backend format: {e}")

  @staticmethod
  def validate_message(message: str) -> bool:
    """
    Validate MQTT message format.

    Args:
        message: Message to validate

    Returns:
        True if message is valid JSON, False otherwise
    """
    try:
      json.loads(message)
      return True
    except json.JSONDecodeError:
      return False
