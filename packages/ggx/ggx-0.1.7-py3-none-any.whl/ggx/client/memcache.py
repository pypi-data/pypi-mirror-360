
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, Dict, Union
import asyncio




class GGSCache(MutableMapping):
    
    def __init__(
        self,
        default_ttl: float = 5.0,
        on_expire: Optional[Callable[[Any, Any], None]] = None
    ):
        self._default_ttl = default_ttl
        self._on_expire = on_expire
        
        self._data: Dict[Any, Any] = {}
        self._tasks: Dict[Any, asyncio.Task] = {}
        
    
    def __getitem__(self, key: Any):
        return self._data[key]
    
    
    def __setitem__(self, key: Any, value: Any) -> None:
        
        self.set_with_ttl(key, value, self._default_ttl)
    
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __iter__(self):
        return iter(self._data)
    
    
        
    def set_with_ttl(self, key: Any, value: Any, ttl: float) -> None:
        
        if key in self._tasks:
            self._tasks[key].cancel()
        self._data[key] = value
        self._tasks[key] = asyncio.create_task(self._expire_later(key, ttl))
 
    
    def __delitem__(self, key):
        
        if key in self._tasks:
            self._tasks[key].cancel()
            del self._tasks[key]
 
        del self._data[key]
 
    async def _expire_later(self, key: Any, ttl: float) -> None:
        
        try:
            await asyncio.sleep(ttl)
            val = self._data.pop(key, None)
            self._tasks.pop(key, None)
            if self._on_expire and val is not None:
                self._on_expire(key, val)
 
        except asyncio.CancelledError:
            return
 
 
    def find_by_prefix(self, prefix: str) -> Dict[Any, Any]:
        
        result: Dict[Any, Any] = {}
        for k, v in self._data.items():
            if str(k).startswith(prefix):
                result[k] = v
        
        return result

        
    def find_by_value(self, target: Any) -> list[Any]:
        return [k for k, v in self._data.items() if v == target]
    
    
    def clear(self) -> None:
        for t in self._tasks.values():
            t.cancel()
        
        self._data.clear()
        self._tasks.clear()
        
        
    def get_keys_data(self, prefix: str) -> Dict[Any, Any]:
        
        result: Dict[Any, Any] = {}
        for key, val in self._data.items():
            if str(key).startswith(prefix):
                if not isinstance(val, dict):
                    result[key] = None
                    continue
            
                payload = val.get("payload")
                if not isinstance(payload, dict):
                    result[key] = None
                    continue
            
                result[key] = payload.get("data")
        
        return result
        
        
    def get_key_status(self, prefix: str) -> Optional[int]:
        
        for key, val in self._data.items():
            if str(key).startswith(prefix):
                if not isinstance(val, dict):
                    return None
                payload = val.get("payload")
                if not isinstance(payload, dict):
                    return None
                status = payload.get("status")
                return status if isinstance(status, int) else None
        
        return None
    
    def get_data_by_status(self, prefix: str, expected_status: int = 0) -> Dict[Any, Any]:
        
        for key, val in self._data.items():
            if str(key).startswith(prefix):
                if not isinstance(val, dict):
                    return None
                payload = val.get("payload")
                if not isinstance(payload, dict):
                    return None
                status = payload.get("status")
                data = payload.get("data")
                return data if status == expected_status else None
        
        return None
    
    
    ## special function for game
    
    def process_by_status(
        self,
        prefix: str, 
        expected_status: int = 0               
        ) -> Union[Dict[Any, Any], bool]:
        
        for key, val in self._data.items():
            if str(key).startswith(prefix):
                if not isinstance(val, dict):
                    return None
                payload = val.get("payload")
                if not isinstance(payload, dict):
                    return None
                status = payload.get("status")
                data = payload.get("data")
                
                if status == expected_status:
                    return True
                
                if status == 20:
                    return False
                
                if status == 453:
                    return data
        
        return None
        
        
        