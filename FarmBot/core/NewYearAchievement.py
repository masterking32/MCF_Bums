from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .MCFAPI import MCFAPI
import time, random
from logging import Logger
from utilities import utilities as utils


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

    def perform_days(self):
        if not self.days or len(self.days) <= 0:
            self.get_days()
        self.log.info(
            f"🟡 <g>Performing new year achievement days ... </g>"
        )
        for day in self.days:
            is_finished = day.get("isFinish", -999)
            day_id = day.get("id", -1)
            day_name = day.get("name", "Unknown").strip()
            if is_finished in [0, 1]:
                # self.log.info(
                #     f"🟡 <g>Day <c>{day_id} - {day_name}</c> already openned ... </g>"
                # )
                continue
            if is_finished == -1:
                if self.open_day_card(day_id):
                    self.log.info(
                        f"✔️ <g>Day <c>{day_id}</c> - <y>{day_name}</y> openned ... </g>"
                    )
                    self.log.info(
                        f"🟡 <y>You need to complete it manually in game ... </y>"
                    )
