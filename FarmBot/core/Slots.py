from .HttpRequest import HttpRequest
from .MCFAPI import MCFAPI
from .Profile import Profile
from utilities import butils
from .models.ProfileModel import ProfileModel
from .models.StoreModel import StoreModel
import time, random
from logging import Logger

from utilities import utilities as utils


class Slots:
    def __init__(
        self,
        log: Logger,
        httpRequest: HttpRequest,
        mcf_api: MCFAPI,
        profile: Profile,
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.mcf_api: MCFAPI = mcf_api
        self.profile: Profile = profile
        self.zombie_data = {}
        self.stamina_data = {}
        self.energy_options = [50, 10, 5, 3, 2, 1]

    def _get_zombie(self):
        try:
            resp: dict = self.http.get(
                url="miniapps/api/game_slot/zombie",
                valid_response_code=[200, 201],
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")

            if resp and (
                resp.get("code") != 0 or not resp.get("data") or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", "An unknown error occurred while getting slots zombie."
                )
                raise Exception(error_message)

            self.zombie_data = resp.get("data", {})

            return True
        except Exception as e:
            self.log.error(
                f"❌ <r>Failed to get slots zombie for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"❌ <r>{str(e)}</r>")
            return False

    def _get_stamina(self):
        try:
            resp: dict = self.http.get(
                url="miniapps/api/game_slot/stamina",
                valid_response_code=[200, 201],
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")

            if resp and (
                resp.get("code") != 0 or not resp.get("data") or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", "An unknown error occurred while getting slots stamina."
                )
                raise Exception(error_message)

            self.stamina_data = resp.get("data", {})

            return True
        except Exception as e:
            self.log.error(
                f"❌ <r>Failed to get slots stamina for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"❌ <r>{str(e)}</r>")
            return False

    def _spin_slots(self, count):
        try:

            payload = {
                "count": count,
            }
            resp: dict = self.http.post(
                url="miniapps/api/game_slot/start",
                data=payload,
                valid_response_code=[200, 201],
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")

            if resp and (
                resp.get("code") != 0 or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", "An unknown error occurred while getting slots stamina."
                )
                raise Exception(error_message)

            data = resp.get("data")
            if not data:
                self.log.info(f"<y>🟠 Energy not spended.</y>")
                return False
            rewards = data.get("rewardLists", {}).get("rewardList", [])
            for reward in rewards:
                name = reward.get("name")
                amount = reward.get("num")
                reward_msg = (
                    f"<c>{amount}</c> <y>{name}</y>"
                    if name == "Zombie"
                    else f"<c>{name}</c>"
                )
                self.log.info(f"<g>🎁 Reward: {reward_msg}</g>")

            return True
        except Exception as e:
            self.log.error(
                f"❌ <r>Failed to get slots stamina for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"❌ <r>{str(e)}</r>")
            return False

    def _get_data(self):
        if not self._get_zombie():
            return False
        if not self._get_stamina():
            return False
        return True

    def spin_slots(self):
        if not utils.getConfig("auto_spin_slots", True):
            self.log.info(f"<y>Auto spin slots disabled</y>")
            return False
        if not self._get_data():
            return False

        energy_max = self.stamina_data.get("staminaMax", -1)
        energy_crnt = self.stamina_data.get("staminaNow", -1)
        if energy_crnt <= 0:
            self.log.info(
                f"<g>🟠 <y>Not enough energy to spin slots.</y></g>"
                )
            return
        
        self.log.info(
            f"<g>🔋 Slots energy: <c>{butils.round_int(energy_crnt)}</c>/<y>{butils.round_int(energy_max)}</y></g>"
        )
        
        while energy_crnt > 0:
            spend = next(e for e in self.energy_options if e <= energy_crnt)
            energy_crnt -= spend
            self.log.info(
                f"<g>🔋 Spending <c>{butils.round_int(spend)}</c> energy. Remaining: {butils.round_int(energy_crnt)}</g>"
            )
            if not self._spin_slots(spend):
                return False
            time.sleep(random.randint(1, 3))
            if not self._get_data():
                return False
            energy_max = self.stamina_data.get("staminaMax", -1)
            energy_crnt = self.stamina_data.get("staminaNow", -1)
