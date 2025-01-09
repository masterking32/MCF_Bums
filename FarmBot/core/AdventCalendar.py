from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Tuple
from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .MCFAPI import MCFAPI
import time, random
from logging import Logger
from utilities import utilities as utils
import asyncio


@dataclass
class DayMdl:
    id: Optional[int] = None
    type: Optional[str] = None
    auth_type: Optional[str] = None
    prop_sell_id: Optional[str] = None
    jump_url: Optional[str] = None
    date: Optional[str] = None
    name: Optional[str] = None
    target_num: Optional[int] = None
    finish_num: Optional[int] = None
    gift: Optional[int] = None
    is_finished: Optional[bool] = None
    is_openned: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]):
        if data is None or not isinstance(data, dict):
            return None
        return cls(
            id=data.get("id", -1),
            type=data.get("type", ""),
            auth_type=data.get("authType", ""),
            prop_sell_id=data.get("propSellId", ""),
            jump_url=data.get("jumpUrl", ""),
            date=data.get("date", ""),
            name=data.get("name", ""),
            target_num=data.get("num", -1),
            finish_num=data.get("finishNum", -1),
            gift=data.get("gift", -1),
            is_finished=data.get("isFinish", -1) == 1,
            is_openned=data.get("isFinish", -1) == 0,
        )


class AdventCalendar:
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
        self.days: list[DayMdl] = []

    def get_days(self, date: int):
        try:
            payload = {
                "month": date,
            }
            resp: dict = self.http.post(
                url="miniapps/api/active_advent/get_lists",
                data=payload,
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg",
                    "Unknown error occurred while getting advent calendar days.",
                )
                raise Exception(error_message)

            data = resp.get("data", {})
            days = data.get("lists", [])
            self.days = [DayMdl.from_dict(day) for day in days]
            time.sleep(random.randint(1, 2))

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get advent calendar days for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def open_day(self, day: DayMdl, date: int):
        try:
            payload = {
                "id": day.id,
                "month": date,
            }

            resp: dict = self.http.post(
                url="miniapps/api/active_advent/open",
                data=payload,
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", f"Unknown error occurred while openning day {day.id}."
                )
                raise Exception(error_message)

            self.log.info(f"🟢 <g>Advent calendar day <c>{day.id}</c> openned</g>")
            time.sleep(random.randint(1, 2))

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to open advent calendar day {day.id} for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def finish_day(self, day: DayMdl, date: int):
        try:
            payload = {
                "id": day.id,
                "month": date,
            }

            resp: dict = self.http.post(
                url="miniapps/api/active_advent/finish",
                data=payload,
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg",
                    f"Unknown error occurred while finishing day <c>{day.id}</c>.",
                )
                raise Exception(error_message)

            self.log.info(f"🟢 <g>Advent calendar day <c>{day.id}</c> finished.</g>")
            time.sleep(random.randint(1, 2))

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to finish advent calendar day <c>{day.id}</c> for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def perform_advent_calendar(self, date: int):
        if not self.days or len(self.days) <= 0:
            self.get_days(date)
        self.log.info(f"🟡 <g>Performing advent calendar days ... </g>")
        for day in self.days:
            if day.is_finished:
                continue
            if not day.is_openned:
                if self.open_day(day, date):
                    day.is_openned = True
                    if day.auth_type not in ["send_prop_shop", "invite"]:
                        continue
            if day.is_openned and not day.is_finished:
                if day.auth_type == "send_prop_shop":
                    self.finish_day(day, date)
                    continue
                if day.auth_type == "invite":
                    if day.finish_num >= day.target_num:
                        self.finish_day(day, date)
                        continue
                continue
