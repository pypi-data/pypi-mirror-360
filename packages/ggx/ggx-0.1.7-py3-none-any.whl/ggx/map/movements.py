from ..client.game_client import GameClient
from loguru import logger
import asyncio



class Movements(GameClient):
    
    
    async def get_movements(self, sync = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("gam", {})
            
            if sync:
                response = await self.wait_for_response("gam")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False


    async def tower_watch(
        self,
        handler,
    ) -> asyncio.Task:
        
        tower_task = asyncio.create_task(
            self.process_data("gam", handler, interval= 0.5)
        )
        return tower_task
        
        
    
    