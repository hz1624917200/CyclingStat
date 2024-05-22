from enum import Enum
from os import remove
import logging


WORKDIR = "./workdir"
GROUP_NAME = "北大车队23-24秋季正式队员群"
INDOOR_RIDING_RATE = 32
CROSS_DIS_LIMIT = 100
DUMP_RECORD = False
DUMP_CSV = True
UPDATE_DB = False

# remove(WORKDIR + "/log.txt")
# logging.basicConfig(filename=WORKDIR + "/log.txt", level=logging.DEBUG, encoding="utf-8")
logging.basicConfig(level=logging.INFO)

class Command(Enum):
	MAIN = 0
	SPLIT = 1

COMMAND_TABLE: dict[str, Command] = {
	"接龙": Command.MAIN,
	"split": Command.SPLIT
}

class Stat:
	def __init__(self, name: str, distance: int = 0, duration: int = 0):
		self.name = name
		self.distance = distance
		self.duration = duration
	
	def __str__(self):
		return f"{self.name}: {self.distance} km, {self.duration} h - converted {self.convert()} km"
	
	def append(self, distance: int, duration: int):
		self.distance += distance
		self.duration += duration
	
	def convert(self):
		duration_dis = self.duration * INDOOR_RIDING_RATE
		if duration_dis > self.distance:
			self.distance = duration_dis
		return self.distance + duration_dis

	def __lt__(self, other):
		return self.convert() < other.convert()
	
	def __eq__(self, other):
		return self.convert() == other.convert()