from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .Store import Store
from .MCFAPI import MCFAPI
from .models.ProfileModel import ProfileModel
from .models.StoreModel import StoreModel
import time, random
from logging import Logger
from utilities import utilities as utils


class City:
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

    def get_free_expeditions(self):
        if not utils.getConfig("auto_free_expeditions", True):
            self.log.info(f"Auto check free expeditions disabled.")
            return True
        try:
            self.log.info(f"Checking for free expeditions ...")
            if not self.store._get_free_prop("expedition"):
                return False

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get free expeditions for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def get_free_boxes(self):
        if not utils.getConfig("auto_free_boxes", True):
            self.log.info(f"Auto check free boxes disabled.")
            return True
        try:
            self.log.info(f"Checking for free boxes ...")
            if not self.store._get_free_prop("box"):
                return False
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get free boxes for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def get_free_animas(self):
        if not utils.getConfig("auto_free_animals", True):
            self.log.info(f"Auto check free animals disabled.")
            return True
        try:
            self.log.info(f"Checking for free animals ...")
            if not self.store._get_free_prop("animals"):
                return False
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get free animals for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def do_daily_combo(self):
        # Not supported in the API at the moment
        return
        if not utils.getConfig("auto_dily_combo", False):
            self.log.info("Daily combo disabled.")
            return True
        try:
            cards = self.mcf_api.get_lottery_cards()
            if not cards:
                raise Exception("Failed to get combo cards from api.")

            payload = {
                "cardIdStr": cards,  # mast be: 106,220,303
            }
            res: dict = self.http.post(
                url="miniapps/api/mine_active/JoinMineAcctive",
                data=payload,
            )
            if not res:
                raise Exception("RESPONSE_IS_NULL")
            elif res and (res.get("code") != 0 or res.get("msg") != "OK"):
                error_message = res.get(
                    "msg", "Unknown error occurred while solving daily combo."
                )
                raise Exception(error_message)
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to solve daily combo for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False
