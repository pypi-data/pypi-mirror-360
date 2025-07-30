from typing import Any, Dict, List, Type, TypeVar
from .models.base import BaseModel

T = TypeVar("T", bound=BaseModel)

async def paginate(method: str, client: Any, key: str, model: Type[T], params: Dict[str, Any], pages: int = 1, subkey: str = None) -> List[T]:
    results: List[T] = []
    for page in range(1, pages + 1):
        data = await client.request(method, **params, page=page)
        block = data[subkey or method.split(".")[0]]
        items = block.get(key, [])
        if not isinstance(items, list): items = [items]
        for item in items:
            results.append(model.from_data(item))
    return results
