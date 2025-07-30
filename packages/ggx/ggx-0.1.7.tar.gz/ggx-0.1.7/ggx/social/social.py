from ..client.game_client import GameClient
from loguru import logger
from typing import Callable, Any
import asyncio




class Social(GameClient):
    
    
    
    
    async def send_player_sms(
        self,
        player_name: str,
        sms_title: str,
        sms_text: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "sms",
                {
                    "RN": player_name,
                    "MH": sms_title,
                    "TXT": sms_text
                }
            )
            if sync:
                response = await self.wait_for_response("sms")
                return response
            return True

        except Exception as e:
            logger.error(e)
            
            
    async def delete_message(self, message_id, sync = True):
        
        try:
            
            await self.send_json_message(
                "dms", {
                    "MID": message_id
                }
            )
            
            if sync:
                response = self.pending_get_status("dms")
                return response
            logger.info(f'Message {message_id} removed!')
            return True
            
        except Exception as e:
            logger.error(e) 
            return False
        
    
    
            
    async def inbox_watcher(
        self,
        handler,
    ) -> asyncio.Task:
        
        watcher_task = asyncio.create_task(
            self.process_data("sne", handler, interval= 0.5)
        )
        return watcher_task
        