import enum

from biolib.typing_utils import TypedDict, Any


class Proxy(TypedDict):
    container: Any
    hostname: str
    ip: str


class DockerDiffKind(enum.Enum):
    CHANGED = 0
    ADDED = 1
    DELETED = 2
