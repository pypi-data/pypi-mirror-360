from ..client.game_client import GameClient
from loguru import logger


## de adaugat movements checks la functia de select lords
## functia de gasit coms dupa skill




class Lords(GameClient):
    
    
    async def get_lords(self, sync = True) -> dict | bool:
        
        
        try:
            
            await self.send_json_message("gli", {})
            
            if sync:
                response = await self.wait_for_response("gli")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
    
    

    
    
    
    
    
    async def select_lord(
        self,
        lord_index: int,
        lord_list: list,    
    ) -> int:
        
        if not hasattr(self, 'lord_index'):
            self.lord_index = 0
            
        if not isinstance(lord_list, list):
            logger.error("No selected lords available!")
            return None
        
        n = len(lord_list)
        for _ in range(n):
            lord = lord_list[lord_index]
            lord_index = (lord_index + 1) % n
            return lord
        
        
        
        
    async def list_lords_id(
        self,
        lord_list: list,
    ) -> list:
        
        if not isinstance(lord_list, list):
            lord_list = []
        
        lords_data = await self.get_lords()
        all_lords = lords_data.get("C", [])
        
        for lord_obj in all_lords:
            lord_id = lord_obj.get("ID")
            eq_list = lord_obj.get("EQ")
            if len(eq_list) >= 5:
                lord_list.append(lord_id)
        
        