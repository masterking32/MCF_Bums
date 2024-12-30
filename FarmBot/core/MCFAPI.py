from mcf_utils.api import API
from logging import Logger
import time, json
from mcf_utils.tgAccount import tgAccount as TG


class MCFAPI:
    def __init__(
        self,
        log: Logger,
        bot_globals: dict,
        account_name,
        proxy,
        tgAccount,
        web_app_query,
    ):
        self.log = log
        self.bot_globals = bot_globals
        self.account_name = account_name
        self.proxy = proxy
        self.tgAccount = tgAccount
        self.web_app_query = web_app_query
        self.license_key = self.bot_globals.get("license", None)
        self.start_param = ""
        self.ref_code = ""

        if self.tgAccount is not None:
            self.ref_code = self.tgAccount.ReferralToken
            self.start_param = "/?tgWebAppStartParam=" + self.tgAccount.ReferralToken
            # if self.tgAccount.NewStart:

    def can_use(self, target_timestamp: int):
        if target_timestamp <= 0:
            return True
        
        current_timestamp = int(time.time())

        if current_timestamp >= target_timestamp:
            return False
        return True

    def _api_request(self, action: str, data: dict = {}):
        if self.license_key is None:
            return None
        apiObj = API(self.log)
        data["game_name"] = "bums"
        data["action"] = action
        response = apiObj.get_task_answer(self.license_key, data)
        time.sleep(3)
        if "error" in response:
            self.log.error(f"<r>⭕ API Error: {response['error']}</r>")
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
            self.log.error(f"<r>❌ Error getting lottery cards: {str(e)}</r>")
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
            self.log.error(f"<r>❌ Error getting task keyword: {str(e)}</r>")
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
            self.log.error(f"<r>❌ Error getting invite link: {str(e)}</r>")
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
            self.log.info(f"<g>✅ Bot <c>{bot_id}</c> started successfully!</g>")
            return True
        except Exception as e:
            self.log.error(f"<r>❌ Error starting bot <c>{bot_id}</c>: {str(e)}</r>")
            return False

    async def set_name(self, checkData):
        tgMe = self.tgAccount.me if self.tgAccount.me else None
        if tgMe is None:
            self.log.error("<r>❌ Telegram account not found</r>")
            return False
        try:
            tgMe.first_name = tgMe.first_name or ""
            tgMe.last_name = tgMe.last_name or ""
            if checkData not in tgMe.last_name and checkData not in tgMe.first_name:
                await self.tgAccount.setName(
                    tgMe.first_name, tgMe.last_name + checkData
                )
            self.log.info("<g>✅ Name set successfully!</g>")
            return True
        except Exception as e:
            self.log.error(f"<r>❌ Error setting name: {str(e)}</r>")
            return False

    async def join_chat(self, channel_url):
        try:
            channel_url = channel_url
            if "+" not in channel_url:
                channel_url = (
                    channel_url.replace("https://t.me/", "")
                    .replace("@", "")
                    .replace("boost/", "")
                )
            channel_url = (
                channel_url.split("/")[0]
                if "/" in channel_url
                else channel_url
            )
            await self.tgAccount.joinChat(channel_url)
            self.log.info(f"<g>✅ Joined chat: {channel_url}</g>")
            return True
        except Exception as e:
            self.log.error(f"<r>❌ Error joining chat: {str(e)}</r>")
            return False
