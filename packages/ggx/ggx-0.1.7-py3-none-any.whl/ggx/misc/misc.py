from ..client.game_client import GameClient
from loguru import logger
import random
import asyncio






class Misc(GameClient):
    


    
    async def cooldown(self, min_time: int, max_time: int) -> None:
        
        try:
            
            random_time = random.randint(min_time, max_time)
            await asyncio.sleep(random_time)
            
        except Exception as e:
            logger.error(e)   
        
    