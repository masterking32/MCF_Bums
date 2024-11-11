from mcf_utils.api import API
from logging import Logger
import time, json
from mcf_utils.tgAccount import tgAccount as TG


class MCFAPI:
    def __init__(self, log: Logger, bot_globals: dict, account_name, proxy, tgAccount):
        self.log = log
        self.bot_globals = bot_globals
        self.account_name = account_name
        self.proxy = proxy
        self.tgAccount = tgAccount
        self.license_key = self.bot_globals.get("license", None)

    def _api_request(self, action: str, data: dict = {}):
        if self.license_key is None:
            return None
        apiObj = API(self.log)
        data["game_name"] = "bums"
        data["action"] = action
        response = apiObj.get_task_answer(self.license_key, data)
        time.sleep(3)
        if "error" in response:
            self.log.error(f"<y>⭕ API Error: {response['error']}</y>")
            return None
        elif response.get("status") == "success":
            return response
        elif response.get("status") == "error" and response.get("message"):
            self.log.info(f"<y>🟡 {response.get('message')}</y>")
            return None
        else:
            self.log.error(
                f"<y>🟡 Unable to get task answer, please try again later</y>"
            )
            return None

    def get_lottery_cards(self):
        try:
            resp = self._api_request("get_lottery")
            if not resp or not resp.get("cards"):
                return None
            return resp.get("cards")
        except Exception as e:
            return None

    def get_task_keyword(self, task_id, task_title):
        try:
            data = {
                "task_type": "keyword",
                "task_id": task_id,
                "task_name": task_title,
            }
            resp = self._api_request("get_task", data)
            if not resp or not resp.get("answer"):
                return None
            return resp.get("answer")
        except Exception as e:
            return None

    def get_invite_link(self, url):
        try:
            data = {
                "task_type": "invite",
                "task_data": url,
            }
            resp = self._api_request("get_task", data)
            if resp is None or "status" not in resp or resp["status"] != "success":
                return None
            return resp
        except Exception as e:
            return None

    async def start_bot(self, bot_id, ref_link):
        try:
            tg = TG(
                bot_globals=self.bot_globals,
                log=self.log,
                accountName=self.account_name,
                proxy=self.proxy,
                BotID=bot_id,
                ReferralToken=ref_link,
                MuteBot=True,
            )
            await tg.getWebViewData()
            self.log.info(f"<g>✅ Bot <c>{bot_id}</c> started!</g>")
            return True
        except Exception as e:
            return False

    async def set_name(self, checkData):
        tgMe = self.tgAccount.me if self.tgAccount.me else None
        if tgMe is None:
            return False
        try:
            tgMe.first_name = tgMe.first_name or ""
            tgMe.last_name = tgMe.last_name or ""
            if checkData not in tgMe.last_name and checkData not in tgMe.first_name:
                await self.tgAccount.setName(
                    tgMe.first_name, tgMe.last_name + checkData
                )
            return True
        except Exception as e:
            return False

    async def join_chat(self, channel_url):
        try:
            await self.tgAccount.joinChat(channel_url)
            return True
        except Exception as e:
            return False
