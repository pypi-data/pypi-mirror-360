from ..client.game_client import GameClient
from loguru import logger
from ..utils.utils import Utils
import asyncio





## de adaugat soldier_replesnished cu cap








class Castle(GameClient):
    
    
    
    async def go_to_kingdom(
        self,
        loc_id: int,
        kid: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "jca",
                {
                    "CID": loc_id,
                    "KID": kid
                }
            )
            if sync:
                response = await self.wait_for_response("jaa")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    
    async def go_to_mains(
        self,
        px: int,
        py: int,
        kid: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "jaa",
                {
                    "PX": px,
                    "PY": py,
                    "KID": kid
                }
            )
            if sync:
                response = await self.wait_for_response("jaa")
                return response
            return True

        except Exception as e:
            logger.error(e)
            return False
    
    
    
    
    
    
    async def get_castles(self, sync: bool = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("gcl", {})
            if sync:
                response = await self.wait_for_response("gcl")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def get_detailed_castles(self, sync: bool = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("dcl", {})
            if sync:
                response = await self.wait_for_response("dcl")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def send_resources_to_kingdom(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        resources: list[list[str, int]],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "kgt",
                {
                   "SCID": id_sender,
                   "SKID": sender_kid,
                   "TKID": target_kid,
                   "G": resources
                }
            )
            if sync:
                response = await self.wait_for_response("kgt")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
    async def send_units_to_kingdom(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        units: list[list[int, int]],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "kut",
                {
                   "SCID": id_sender,
                   "SKID": sender_kid,
                   "TKID": target_kid,
                   "CID": -1,
                   "A": units
                }
            )
            if sync:
                response = await self.wait_for_response("kut")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def skip_kingdom_transfer(
        self,
        skip: str,
        target_kid: int,
        transfer_type: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "msk",
                {
                    "MST": skip,
                    "KID": target_kid,
                    "TT": transfer_type
                }
            )
            if sync:
                response = await self.wait_for_response("msk")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    
    async def auto_units_kingdom_transfer(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        units: list,
        skips: list = None,
        sync: bool = True  
    ) -> dict | bool:
        
        
        utils = Utils()
        send_units = await self.send_units_to_kingdom(id_sender, sender_kid, target_kid, units)
        if not isinstance(send_units, dict):
            logger.error(f"Failed to send units to kingdom: {target_kid}")
            return
        
        kpi = send_units.get("kpi", {})
        ut_list = kpi.get("UT")
        if not ut_list or not isinstance(ut_list, list):
            logger.error("Unknown transfer time data!")
            return
        
        time_to_transfer = ut_list[0].get("RS")
        if not isinstance(time_to_transfer, int):
            logger.error(f"Invalid time value: {ut_list[0]}")
            return
        
        skip_list = utils.skip_calculator(time_to_transfer, skips)
        for skip in skip_list:
            await self.skip_kingdom_transfer(skip, target_kid, transfer_type=1, sync=sync)
        
        logger.info(f"All units has been sent succesfully to kingdom {target_kid}!")
        
        
        
        
        
        
    async def auto_res_kingdom_transfer(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        resources: list,
        skips: list = None,
        sync: bool = True  
    ) -> dict | bool:
        
        
        utils = Utils()
        resources_sender = await self.send_resources_to_kingdom(id_sender, sender_kid, target_kid, resources)
        if not isinstance(resources_sender, dict):
            logger.error(f"Failed to send resources to kingdom: {target_kid}")
            return
        
        kpi = resources_sender.get("kpi", {})
        rt_list = kpi.get("RT")
        if not rt_list or not isinstance(rt_list, list):
            logger.error("Unknown transfer time data!")
            return
        
        time_to_transfer = rt_list[0].get("RS")
        if not isinstance(time_to_transfer, int):
            logger.error(f"Invalid time value: {rt_list[0]}")
            return

        skip_list = utils.skip_calculator(time_to_transfer, skips)
        for skip in skip_list:
            await self.skip_kingdom_transfer(skip, target_kid, transfer_type=2, sync=sync)
        
        logger.info(f"All resources has been sent succesfully to kingdom {target_kid}!")    
        
        
        
    async def kingdom_auto_feeder(
        self,
        target_kid: int,
        activator: bool,
        min_food: int,
        min_mead: int,
        skips: list = None,
        interval: float = 60.0,
        sync: bool = True
    ) -> None:
        
        
        while activator:
            
            try:
                castles_inventory = await self.get_detailed_castles(sync = sync)
                resource_inventory = castles_inventory["C"]
                
                potential_donors_food = {}
                potential_donors_mead = {}
                
            except TimeoutError:
                await asyncio.sleep(1)
                continue
            
            for items in resource_inventory:
                kid = items.get("KID")
                if kid == target_kid:
                    continue
                
                for ai_item in items.get("AI", []):
                    aid = ai_item.get("AID")
                    mead_value = ai_item.get("MEAD")
                    food_value = ai_item.get("F")
                    mead_prod = ai_item.get("gpa", {}).get("DMEAD")
                    food_prod = ai_item.get("gpa", {}).get("DF")
                    
                    if food_value > 100000 and food_prod > 0:
                        potential_donors_food[kid] = {"aid": aid, "food": food_value}
                    
                    if mead_value > 100000 and mead_prod > 0:
                        potential_donors_mead[kid] = {"aid": aid, "mead": mead_value}
                        
            
            for items in resource_inventory:
                kid = items.get("KID")
                if kid == target_kid:
                    for ai_item in items.get("AI", []):
                        food_value = ai_item.get("F")
                        mead_value = ai_item.get("MEAD")
                        food_cap = ai_item.get("gpa", {}).get("MRF")
                        mead_cap = ai_item.get("gpa", {}).get("MRMEAD")
                        fcap_var = int(food_cap - 5) - int(food_value)
                        mcap_var = int(mead_cap - 5) - int(mead_value)
                        
                        
                        if food_value < min_food:
                            logger.warning(f"Kingdom {kid} has low level of food: {food_value}. Searching for food...")
                            if potential_donors_food:
                                donor_kid = max(potential_donors_food, key=lambda k: potential_donors_food[k]["food"])
                                donor_info = potential_donors_food[donor_kid]
                                donor_aid = donor_info["aid"]
                                logger.info(f"Transfer from kingdom {donor_kid} (AID: {donor_aid}) to kingdom {kid}.")
                                await self.auto_res_kingdom_transfer(donor_aid, donor_kid, target_kid, [["F", fcap_var]], skips, sync)
                            
                            else:
                                logger.warning("No enough amount of food in your castles to refill!")
                        
                        
                        if mead_value < min_mead:
                            logger.warning(f"Kingdom {kid} has low level of mead: {mead_value}. Searching for...")
                            if potential_donors_mead:
                                donor_kid = max(potential_donors_mead, key=lambda k: potential_donors_mead[k]["mead"])
                                donor_info = potential_donors_mead[donor_kid]
                                donor_aid = donor_info["aid"]
                                logger.info(f"Transfer mead from kingdom {donor_kid} (AID: {donor_aid}) to kingdom {kid}.")
                                await self.auto_res_kingdom_transfer(donor_aid, donor_kid, target_kid, [["MEAD", mcap_var]], skips, sync)
                                
                            else:
                                logger.warning("No enough amount of mead in your castles to refill!")
            
            await asyncio.sleep(interval)
            
            
            
            
    async def units_replenish(
        self,
        target_kid: int,
        wod_id: int,
        amount: int
    ) -> None:
        
        
        try:
            
            account_inventory = await self.get_detailed_castles()
            inventory_data = account_inventory["C"]
            donors = []
            
            
            for kingdom in inventory_data:
                kid = kingdom.get("KID")
                if kid == target_kid:
                    continue
                
                for ai_block in kingdom.get("AI", []):
                    aid = ai_block.get("AID")
                    for wod, amt in ai_block.get("AC", []):
                        if wod == wod_id and amt > amount:
                            donors.append({"aid": aid, "kid":kid, "amount": amt})
                            break
                        
            if not donors:
                logger.warning("I can't find any eligible location!")
                return False
                            
            else:
                best = max(donors, key=lambda d: d["amount"])
                donor_aid = best["aid"]
                donor_amt = best["amount"]
                donor_kid = best["kid"]
                send_amt = min(donor_amt, amount)
                
                await self.auto_units_kingdom_transfer(donor_aid, donor_kid, target_kid, [[wod_id, send_amt]])
                logger.info(f"Kingdom {target_kid} refilled with {send_amt} units!")
                     
        except Exception as e:
            logger.error(e)
            return False