from dataclasses import dataclass

@dataclass
class KeyboardDevice:
    """Represents a keyboard device with its path and name."""
    path: str
    name: str