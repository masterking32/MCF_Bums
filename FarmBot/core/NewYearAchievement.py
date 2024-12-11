from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .MCFAPI import MCFAPI
import time, random
from logging import Logger
from utilities import utilities as utils
import asyncio


class NewYearAchievement:
    def __init__(
        self,
        log: Logger,
        httpRequest: HttpRequest,
        mcf_api: MCFAPI,
        profile: Profile,
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.profile: Profile = profile
        self.mcf_api: MCFAPI = mcf_api
        self.days = []

    def get_days(self):
        try:
            resp: dict = self.http.get(
                url="miniapps/api/active_christmas/get_lists?language=en",
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg",
                    "Unknown error occurred while getting new year achievements days.",
                )
                raise Exception(error_message)

            data = resp.get("data", {})
            days = data.get("lists", [])
            self.days = days

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to new year achievements days <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def open_day_card(self, id):
        try:
            payload = {
                "id": id,
            }

            resp: dict = self.http.post(
                url="miniapps/api/active_christmas/open",
                data=payload,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", f"Unknown error occurred while openning day {id}."
                )
                raise Exception(error_message)

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to open day {id} <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def finish_day(self, day):
        try:
            day_id = day.get("id", -1)
            payload = {
                "id": day_id,
            }

            resp: dict = self.http.post(
                url="miniapps/api/active_christmas/finish",
                data=payload,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", f"Unknown error occurred while finishing day <c>{id}</c>."
                )
                raise Exception(error_message)

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to finish day <c>{id}</c> <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    async def perform_days(self):
        if not self.days or len(self.days) <= 0:
            self.get_days()
        self.log.info(f"🟡 <g>Performing new year achievement days ... </g>")
        for day in self.days:
            is_finished = day.get("isFinish", -999)
            day_id = day.get("id", -1)
            day_name = day.get("name", "Unknown").strip()
            day_type = day.get("type", "Unknown")
            if is_finished == 1:
                # self.log.info(
                #     f"🟡 <g>Day <c>{day_id} - {day_name}</c> already openned ... </g>"
                # )
                continue
            if is_finished == -1:
                if self.open_day_card(day_id):
                    self.log.info(
                        f"✔️ <g>Day <c>{day_id}</c> - <y>{day_name}</y> openned ... </g>"
                    )
                    if day_type in ["ton", "star"]:
                        # self.log.info(
                        #     f"🟡 <y>You need to complete it manually in game ... </y>"
                        # )
                        continue
                    is_finished = 0
            if is_finished == 0:
                if day_type in ["ton", "star"]:
                    continue
                if day_id == 4:
                    if not self.mcf_api.tgAccount:
                        continue
                    if not utils.getConfig("auto_join_channels", True):
                        continue
                    await self.mcf_api.join_chat(day.get("jumpUrl"))
                    await asyncio.sleep(random.randint(1, 3))
                    if self.finish_day(day):
                        self.log.info(
                            f"✔️ <g>Day <c>{day_id}</c> - <y>{day_name}</y> finished ... </g>"
                        )
                        continue
                if day_id in [6, 11]:
                    if self.finish_day(day):
                        self.log.info(
                            f"✔️ <g>Day <c>{day_id}</c> - <y>{day_name}</y> finished ... </g>"
                        )
                        continue
                if "Invite friends" in day_name:
                    nums = []
                    for part in day_name.split():
                        clean_part = "".join(char for char in part if char.isdigit())
                        if clean_part:
                            nums.append(int(clean_part))
                    if len(nums) < 2:
                        continue
                    target = nums[0]
                    progress = nums[1]
                    if progress >= target:
                        if self.finish_day(day):
                            self.log.info(
                                f"✔️ <g>Day <c>{day_id}</c> - <y>{day_name}</y> finished ... </g>"
                            )
                            continue
