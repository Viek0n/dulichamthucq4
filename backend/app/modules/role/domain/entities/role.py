from dataclasses import dataclass


@dataclass
class Role:
    id: str | None
    name: str
    permissions: list[str]
    priority: int
