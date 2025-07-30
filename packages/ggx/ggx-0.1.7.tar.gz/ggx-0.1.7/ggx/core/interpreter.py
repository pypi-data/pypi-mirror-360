from ..client.game_client import GameClient
import asyncio
from typing import Callable, Dict, Any







class Interpreter(GameClient):
    
    
    async def _interpreter(
        self,
        action: Dict[str, Callable],
        interval: float = 0.5
        ) -> None:
        
        
        auto_tasks = []
        for prefix, handler in action.items():
            task = asyncio.create_task(self.process_data(prefix, handler, interval))
            auto_tasks.append(task)
            
        await asyncio.gather(*auto_tasks)  
            
    
    
            
    async def _autoset(
        self,
        msg: str,
        handler: Any,
        interval: float = 1.0
    ) -> asyncio.Task:
        
        _auto_task = asyncio.create_task(
            self.process_data(msg, handler, interval)
        )
        
        return _auto_task
    
 