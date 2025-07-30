import websockets
import asyncio
import json
import re
from loguru import logger
from typing import Any, Callable, Dict, List, Union, Awaitable
import uuid
from .memcache import GGSCache
import inspect
import aiohttp

HandlerType = Callable[[Any], Union[Any, Awaitable[Any]]]
version_url = "https://empire-html5.goodgamestudios.com/default/items/ItemsVersion.properties"




class GameClient:
    
    def __init__(self, url: str, server_header: str, username: str, password: str):
        
        self.url = url
        self.server_header = server_header
        self.username = username
        self.password = password
        self._pending = GGSCache()
        self.connected = asyncio.Event()
        
        
    
    
    
    
        
    async def connect(self) -> None:
        async with websockets.connect(self.url) as ws:
            self.ws = ws
            self.connected.set()
            listener_task = asyncio.create_task(self.listen_messages())
            keep_alive_task = asyncio.create_task(self.keep_alive())
            connected = await self.init()
            if not connected:
                await self.disconnect()
            
            
            runner_task = asyncio.create_task(self.run_jobs())
            await asyncio.gather(listener_task, runner_task, keep_alive_task)




    async def init(self) -> bool:
        await self.init_socket()
        return await self.login(self.username, self.password)



    async def run_jobs(self):
        pass # va fi suprapusa cu o functie custom 
    
    
    
    
    async def send(self, message):
        
        try:
            await self.ws.send(message)
        except Exception as e:
            logger.error(f"Error occured: {e}")    
       
           
            
    async def send_message(self, parts: List[str]) -> None:
        await self.send("%".join(["", *parts, ""]))



    async def send_raw_message(self, command: str, data: List[Any]) -> None:
        json_parts = [json.dumps(item) if isinstance(item, (dict, list)) else item for item in data]
        await self.send_message(["xt", self.server_header, command, "1", *json_parts])



    async def send_json_message(self, command: str, data: Dict[str, Any]) -> None:
        await self.send_message(["xt", self.server_header, command, "1", json.dumps(data)])



    async def send_xml_message(self, t: str, action: str, r: str, data: str) -> None:
        await self.send(f"<msg t='{t}'><body action='{action}' r='{r}'>{data}</body></msg>") 





    async def listen_messages(self):
        try:
            async for message in self.ws:
                await self.handle_message(message)
        except websockets.ConnectionClosed:
            logger.error("Connection closed. Reconnecting...")
            await asyncio.sleep(5)
            await self.connect()




    async def handle_message(self, message):
        if isinstance(message, bytes):
            message = message.decode('utf-8')
            self._message_parser(message)
            
            




    def _message_parser(self, message: str, caching: bool = True) -> Dict[str, Any]:
        
        if message.startswith("<"):
            
            xml_pattern = r"<msg t='(.*?)'><body action='(.*?)' r='(.*?)'>(.*?)</body></msg>"
            m = re.search(xml_pattern, message)
            t_value, action_value, r_value, data_value = m.groups()
            
            
            msg = {
                "type": "xml",
                "payload": {
                    "t": t_value,
                    "action": action_value,
                    "r": int(r_value),
                    "data": data_value
                }     
            }
             
            if caching:
                self._add_pending('xml', msg)
                
            return msg
          
            
            
        else:
            
            message = message.strip("%").split("%")
            message = {
                "type": "json",
                "payload": {
                    "command": message[1],
                    "status": int(message[3]),
                    "data": "%".join(message[4:]) if len(message) > 4 else None
                }
            }
            if message["payload"]["data"] and message["payload"]["data"].startswith("{"):
                message["payload"]["data"] = json.loads(message["payload"]["data"])
            
            if caching:
                self._add_pending('json', message)
             
            return message
                

    def _add_pending(self, type: str, parsed_message: Dict[str, Any]) -> None:
        
        if type == "json":
            
            try:

                key_uuid = f'{parsed_message["payload"]["command"]}_{str(uuid.uuid4())}'
                self._pending.set_with_ttl(key_uuid, parsed_message, 5.0)
                
            
            except Exception as e:
                logger.error(e)
        
        
        else:
            
            try:
                key_uuid = f'{parsed_message["payload"]["action"]}_{str(uuid.uuid4())}'
                self._pending.set_with_ttl(key_uuid, parsed_message, 5.0)
                

            except Exception as e:
                logger.error(e)



    async def disconnect(self) -> None:
        
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        
        for task in tasks:
            task.cancel()
            
        await asyncio.gather(*tasks, return_exceptions=True)
        
        try:
            await self.ws.close()
            logger.info("Connection closed succesfully!")
        
        except Exception as e:
            logger.error(f"Error occured: {e}")        

    
    async def pending_get_status(self,
                                 prefix: str,
                                 status: int = 0,
                                 timeout: float = 5.0,
                                 interval: float = 0.5) -> bool:
        
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            result_status = self._pending.get_key_status(prefix)
            if result_status is not None:
                return result_status == status
            await asyncio.sleep(interval)
        
        return False
                
    async def pending_match_xml(self,
                                prefix: str,
                                expected: dict,
                                timeout: float = 5.0,
                                interval: float = 0.1) -> bool:
        
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            pending_entries = self._pending.find_by_prefix(prefix)
            for msg in pending_entries.values():
                if isinstance(msg, dict):
                    payload = msg.get("payload", {})
                    if payload == expected:
                        return True
            await asyncio.sleep(interval)
            
        return False                       

     
        
    async def init_socket(self):
        
        try:
            await self.send_xml_message("sys", "verChk", "0", "<ver v='166' />")
            await self.send_xml_message("sys", "login", "0", 
                                        f"<login z='{self.server_header}'><nick><![CDATA[]]></nick><pword><![CDATA[1123010%fr%0]]></pword></login>")
            await self.send_xml_message("sys", "autoJoin", "-1", "")
            await self.send_xml_message("sys", "roundTrip", "1", "")
            
        except Exception as e:
            logger.error(e)
            return False
    
    
    
    
    
    
    
    
    
    
    async def ping(self):
        
        try:
            await self.send_raw_message("pin", ["<RoundHouseKick>"])
            return True
        
        except Exception as e:
            logger.error(e)
            return False


    async def keep_alive(self, interval: int = 60):
        
        await self.connected.wait()
        while self.connected.is_set():
            try:
                await asyncio.sleep(interval)
                await self.ping()
            except asyncio.CancelledError:
                logger.info("keep_alive task has been canceled!.")
        
            except Exception as e:
                logger.error(f"keep_alive error: {e}")
                raise
                
          



    async def process_data(
        self,
        prefix: str,
        handler: HandlerType,
        interval: float = 0.5
    ) -> None:
        
        while self.connected.is_set():
            key_map = self._pending.get_keys_data(prefix)
            for key, data in list(key_map.items()):
                try:
                    result = handler(data)
                    if inspect.isawaitable(result):
                        await result
        
                except Exception as e:
                    logger.error(e)

                finally:
                    self._pending.pop(key, None)
            await asyncio.sleep(interval)




    async def wait_for_response(self,
                                prefix: str,
                                interval: float = 0.5,
                                timeout: float = 5.0):
        
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            result_data = self._pending.get_data_by_status(prefix, 0)
            if result_data is not None:
                return result_data
            await asyncio.sleep(interval)
        
        return None    
        
    
    
    async def process_response_status(
        self,
        prefix: str,
        expected_status: int,
        interval: float = 0.5,
        timeout: float = 5.0
    ):
        
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            result_data = self._pending.process_by_status(prefix, expected_status)
            if result_data is not None:
                return result_data
            await asyncio.sleep(interval)
        
        return None   
            
    
    
    
    
    
    
    
    
    async def login(
        self,
        username: str,
        password: str
    ) -> bool:
        
        if not self.connected.is_set():
            logger.error("Not connected yet!")
            return False
        self._pending.clear()   
            
        try:
            await self.send_json_message(
                "lli",
                {
                    "CONM": 175,
                    "RTM": 24,
                    "ID": 0,
                    "PL": 1,
                    "NOM": username,
                    "PW": password,
                    "LT": None,
                    "LANG": "fr",
                    "DID": "0",
                    "AID": "1674256959939529708",
                    "KID": "",
                    "REF": "https://empire.goodgamestudios.com",
                    "GCI": "",
                    "SID": 9,
                    "PLFID": 1
                },
            )
            response_status = await self.process_response_status("lli", 0, 0.3, 5.0)
            if isinstance(response_status, bool):
                if response_status:
                    return response_status
                else:
                    logger.error("Login failed, check your details!")
                    return False
                
            if isinstance(response_status, dict):
                cd_value = response_status["CD"]
                logger.debug(f'Connection locked by the server! Reconnect in {cd_value} sec!')
                await asyncio.sleep(cd_value)
                return await self.login(username, password)
                    
        except Exception as e:
            logger.error(e) 
            return False
        
        logger.error("Unexpected response in login status!")
        return False
    
    
    async def fetch_game_db(self) -> dict:
        
        async with aiohttp.ClientSession() as session:
            async with session.get(version_url) as resp:
                resp.raise_for_status()
                text = await resp.text()
                _, version = text.strip().split("=", 1)
                version = version.strip()
            
            db_url = f"https://empire-html5.goodgamestudios.com/default/items/items_v{version}.json"
            async with session.get(db_url) as db_resp:
                db_resp.raise_for_status()
                data = await db_resp.json()
                return data
        