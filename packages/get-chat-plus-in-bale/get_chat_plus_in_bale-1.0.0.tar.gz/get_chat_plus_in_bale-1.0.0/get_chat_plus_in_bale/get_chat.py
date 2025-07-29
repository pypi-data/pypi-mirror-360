import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
from .chat_types import Chat_Types

def aiohttp_request(
        user_name : str,
        base_url : str,
        user_agent : str,
    ):
    async def send_request():
        async with aiohttp.ClientSession() as Client:
            async with Client.get(
                f"{base_url}/{user_name}",
                headers={'User-Agent' : user_agent}
            ) as HTML_Text:
                status_code = HTML_Text.status
                DataJson = json.loads(
                    BeautifulSoup(
                        await HTML_Text.text(),
                        "html.parser"
                    ).find(
                        "script" , id="__NEXT_DATA__" , type="application/json"
                    ).text
                )
        return {"status_code" : status_code , "json" : DataJson}
    return asyncio.run(send_request())


class Chat:
    def __init__(
            self,
            user_name : str,
            user_agent : str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            base_url : str = "https://ble.ir"
        ):
        self.user_name : str = user_name
        self.user_agent : str = user_agent
        self.base_url : str = base_url
        self.data_chat = {
            "chat_id" : None,
            "messages" : None,
            "title" : None,
            "description" : None,
            "avatarUrl" : None,
            "chat_type" : None
        }
        get_data = aiohttp_request(user_name , base_url , user_agent)
        self.json = get_data["json"]
        status_code , DataJson = get_data["status_code"] , get_data["json"]
        if status_code == 200:
            self.chat_id : str = DataJson["props"]["pageProps"]["peer"]["id"]
            if (DataJson["props"]["pageProps"]["group"] is None) and (DataJson["props"]["pageProps"]["user"] != None):
                self.messages = None
                self.nick : str = DataJson["props"]["pageProps"]["user"]["nick"]
                self.title : str = DataJson["props"]["pageProps"]["user"]["title"]
                self.description : str = DataJson["props"]["pageProps"]["user"]["description"]
                self.avatarUrl : str = DataJson["props"]["pageProps"]["user"]["avatarUrl"]
                if DataJson["props"]["pageProps"]["user"]["isBot"] == True:
                    self.chat_type : Chat_Types = Chat_Types.BOT
                else:
                    self.chat_type : Chat_Types = Chat_Types.PRIVATE
            elif (DataJson["props"]["pageProps"]["user"] is None) and (DataJson["props"]["pageProps"]["group"] != None):
                self.nick : str = user_name.strip("@")
                self.messages : tuple = DataJson["props"]["pageProps"]["messages"]
                self.title : str = DataJson["props"]["pageProps"]["group"]["title"]
                self.description : str = DataJson["props"]["pageProps"]["group"]["description"]
                self.avatarUrl : str = DataJson["props"]["pageProps"]["group"]["avatarUrl"]
                if DataJson["props"]["pageProps"]["group"]["isChannel"] == True:
                    self.chat_type : Chat_Types = Chat_Types.CHANNEL
                else:
                    self.chat_type : Chat_Types = Chat_Types.GROUP
            self.data_chat.update({
                "chat_id" : self.chat_id,
                "messages" : self.messages,
                "title" : self.title,
                "description" : self.description,
                "avatarUrl" : self.avatarUrl,
                "chat_type" : self.chat_type,
                "nick" : self.nick
            })