from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .Store import Store
from .MCFAPI import MCFAPI
from .models.ProfileModel import ProfileModel
from .models.FriendModel import FriendModel
import time, random
from logging import Logger
from utilities import utilities as utils


class Friends:
    def __init__(
        self,
        log: Logger,
        httpRequest: HttpRequest,
        account_name: str,
        bot_globals: dict,
        profile: Profile,
        mcfapi: MCFAPI,
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.account_name: str = account_name
        self.bot_globals: dict = bot_globals
        self.profile: Profile = profile
        self.mcf_api = mcfapi
        self.friends: list[FriendModel.Friend] = None
        self.friends_count = -1
        self.balances: list[FriendModel.Balance] = None

    def get_friends(self, page=1, page_size=10):
        self.log.info(f"Getting friends ...")
        try:
            payload = {
                "page": page,
                "pageSize": page_size,
            }
            resp: dict = self.http.post(
                url="miniapps/api/user_game/friends",
                data=payload,
            )
            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            elif resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", "Unknown error occurred while getting friends."
                )
                raise Exception(error_message)

            data: dict = resp.get("data", {})
            self.friends = [
                FriendModel.Friend(fren) for fren in data.get("lists", []) if fren
            ]
            self.friends = len(self.friends)
            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get friends for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def get_balance(self):
        self.log.info(f"Getting friends reward ...")
        try:
            resp: dict = self.http.get(
                url="miniapps/api/wallet/balance",
            )
            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            elif resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", "Unknown error occurred while getting friends balance."
                )
                raise Exception(error_message)

            data: dict = resp.get("data", {})
            self.balances = [FriendModel.Balance(b) for b in data.get("lists", []) if b]
            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get friends balance for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def clain_reward(self):
        self.log.info(f"Claiming friends reward ...")
        try:
            # TODO: figureout
            # W     - ID with lowest amount ?
            # To    - ID with greater amount ?
            # url is hardcoded or generated in page load?
            # function vZe(e) {
            #     return an({
            #         url: "/miniapps/api/wallet/W70001To80001",
            #         method: "post",
            #         data: Kr(e)
            #     })
            # }

            if not self.balances or len(self.balances) <= 0:
                return True

            is_claim_available = any(
                b.id < 80001 and b.total_expenditure > 0 and b.available_amount > 0
                for b in self.balances
            )

            if not is_claim_available:
                self.log.info(f"Nothing to claim ...")
                return True
            # min_id = min(item.id for item in self.balances)
            # max_id = max(item.id for item in self.balances)
            payload = {
                "": "undefined",
            }
            resp: dict = self.http.post(
                url="miniapps/api/wallet/W70001To80001",
                # url=f"miniapps/api/wallet/W{min_id}To{max_id}", # Not found
                data=payload,
            )
            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            elif resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", "Unknown error occurred while claiming balance."
                )
                raise Exception(error_message)
            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to claim balance for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False
