from dataclasses import dataclass, field
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T", bound="BaseModel")

@dataclass
class BaseModel:
    raw: Dict[str, Any]
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_data(cls: Type[T], data: Dict[str, Any]) -> T:
        known_fields = {f.name for f in cls.__dataclass_fields__.values() if f.name not in ("raw", "extra")}
        init_data = {k: data.get(k) for k in known_fields}
        extra_data = {k: v for k, v in data.items() if k not in known_fields}
        return cls(raw=data, extra=extra_data, **init_data)  # type: ignore
