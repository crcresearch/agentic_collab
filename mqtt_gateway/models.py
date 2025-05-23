from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


### Backend to Gateway ###
class PersonaMovement(BaseModel):
  movement: Tuple[int, int]
  pronunciatio: str
  description: str
  chat: Optional[List[Tuple[str, str]]] = None


class Meta(BaseModel):
  curr_time: str


class Movements(BaseModel):
  persona: Dict[str, PersonaMovement]
  meta: Meta


class BackendToGatewayMessage(BaseModel):
  step: int
  movements: Movements


### Gateway to Robots ###
class Position(BaseModel):
  x: int
  y: int


class RobotCommand(BaseModel):
  robot_id: str
  position: Position


class GatewayToRobotsMessage(BaseModel):
  commands: List[RobotCommand]


### Robots to Gateway ###
class RobotEnvironment(BaseModel):
  robot_id: str
  position: Position
  perceived: str


class RobotsToGatewayMessage(BaseModel):
  robots: List[RobotEnvironment]


### Gateway to Backend ###
class PersonaEnvironment(BaseModel):
  x: int
  y: int
  perceived: str
  maze: str


class GatewayToBackendMessage(BaseModel):
  environment: Dict[str, PersonaEnvironment]
  step: int
