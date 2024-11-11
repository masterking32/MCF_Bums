from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .Store import Store
from .MCFAPI import MCFAPI
from .models.ProfileModel import ProfileModel
from .models.StoreModel import StoreModel
from .models.GangModel import GangModel
import time, random
from logging import Logger
from utilities import utilities as utils


class Gangs:
    def __init__(
        self,
        log: Logger,
        httpRequest: HttpRequest,
        account_name: str,
        bot_globals: dict,
        profile: Profile,
        store: Store,
        mcfapi: MCFAPI,
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.account_name: str = account_name
        self.bot_globals: dict = bot_globals
        self.profile: Profile = profile
        self.store: Store = store
        self.mcf_api = mcfapi
        self.gangs: list[GangModel.Gang] = None
        self.my_gang: GangModel.Gang = None

    def get_gangs_data(self, boost=5, power=95):
        try:
            payload = {
                "boostNum": boost,
                "powerNum": power,
            }
            resp: dict = self.http.post(
                url="miniapps/api/gang/gang_lists",
                data=payload,
            )
            if not resp or resp.get("code", -999) != 0 or resp.get("msg") != "OK":
                error_message = resp.get(
                    "msg", "Unknown error occurred while getting gangs."
                )
                raise Exception(error_message)

            data: dict = resp.get("data", {})
            self.gangs = [
                GangModel.Gang(gang) for gang in data.get("lists", []) if gang
            ]
            self.my_gang = GangModel.Gang(data.get("myGang", {}))
            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get gangs for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def join_gang(self, gang_name):
        try:
            payload = {
                "name": gang_name,
            }
            resp: dict = self.http.post(
                url="miniapps/api/gang/gang_join",
                data=payload,
            )
            if not resp or resp.get("code", -999) != 0 or resp.get("msg") != "OK":
                error_message = resp.get(
                    "msg", f"Unknown error occurred while joining gang <y>{gang_name}</y>."
                )
                raise Exception(error_message)

            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to join gang <y>{gang_name}</y> for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False
        
    def leave_gang(self):
        try:
            resp: dict = self.http.get(
                url="miniapps/api/gang/gang_leave"
            )
            if not resp or resp.get("code", -999) != 0 or resp.get("msg") != "OK":
                error_message = resp.get(
                    "msg", f"Unknown error occurred while leaving gang."
                )
                raise Exception(error_message)

            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to leave gang for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False