from enum import Enum

WORKDIR = "./workdir"

class Command(Enum):
	MAIN = 0
	SPLIT = 1

COMMAND_TABLE: dict[str, Command] = {
	"接龙": Command.MAIN,
	"split": Command.SPLIT
}