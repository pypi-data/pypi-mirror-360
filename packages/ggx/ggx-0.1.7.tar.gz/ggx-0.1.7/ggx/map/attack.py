from ..client.game_client import GameClient
from loguru import logger





class Attack(GameClient):
    
    
    
    
    async def send_attack(
        self,
        kingdom: int,
        sx: int,
        sy: int,
        tx: int,
        ty: int,
        army: list,
        lord_id: int = 0,
        horses_type: int = -1,
        feathers: int = 0,
        slowdown: int = 0,
        boosters: list = [],
        support_tools: list = [],
        final_wave: list = [],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            
            await self.send_json_message(
                "cra",
                {
                    "SX": sx,
                    "SY": sy,
                    "TX": tx,
                    "TY": ty,
                    "KID": kingdom,
                    "LID": lord_id,
                    "WT": 0,
                    "HBW": horses_type,
                    "BPC": 0,
                    "ATT": 0,
                    "AV": 0,
                    "LP": 0,
                    "FC": 0,
                    "PTT": feathers,
                    "SD": slowdown,
                    "ICA": 0,
                    "CD": 99,
                    "A": army,
                    "BKS": boosters,
                    "AST": support_tools,
                    "RW": final_wave,
                    "ASCT": 0, 
                }
            )
            if sync:
                response = await self.wait_for_response("cra")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False