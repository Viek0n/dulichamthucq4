from dataclasses import dataclass


@dataclass
class Role:
    id: str | None
    slug: str
    name: str
    permissions: list[str]
    priority: int
