from .HttpRequest import HttpRequest
from .MCFAPI import MCFAPI
from .Profile import Profile
from utilities import butils
from .models.ProfileModel import ProfileModel
import time, random
from logging import Logger
from utilities import utilities as utils


class Upgrades:
    def __init__(
        self, log: Logger, httpRequest: HttpRequest, mcf_api: MCFAPI, profile: Profile
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.mcf_api: MCFAPI = mcf_api
        self.profile: Profile = profile
        self.pph_upgrades: list[ProfileModel.MineData.MineUpgrade] = []
        self.tap_upgrades: list[ProfileModel.TapData.TapUpgrade] = (
            self.profile.tap_data.tap_upgrades
        )

        self.BuyCard = False

    def _get_upgrades(self):
        try:
            resp: dict = self.http.post(
                url="miniapps/api/mine/getMineLists",
                use_boundary=False,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (
                resp.get("code") != 0 or "data" not in resp or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", f"Unknown error occurred while getting upgrades."
                )
                raise Exception(error_message)

            upgrades_list = resp.get("data", {}).get("lists", [])
            if not upgrades_list or len(upgrades_list) < 1:
                raise Exception("Server upgrade list is empty")

            self.upgrades = [
                ProfileModel.MineData.MineUpgrade(upgrade) for upgrade in upgrades_list
            ]
            if not self.upgrades or len(self.upgrades) < 1:
                raise Exception("Local upgrade list is empty")

            self.log.info(
                f"<g>├─ ✅ Upgrades successfully acquired for <c>{self.mcf_api.account_name}</c>!</g>"
            )
            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get upgrades for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _buy_upgrade(
        self,
        skill,
        retries: int = 2,
    ):
        try:
            is_pph = isinstance(skill, ProfileModel.MineData.MineUpgrade)
            skill_desc = "pph" if is_pph else "tap"
            skill_type = "mineId" if is_pph else "type"
            url = (
                "miniapps/api/mine/upgrade"
                if is_pph
                else "miniapps/api/user_game_level/upgradeLeve"
            )
            payload = {skill_type: skill.id}
            resp: dict = self.http.post(
                url=url,
                data=payload,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                if "Insufficient balance" in resp.get("msg"):
                    time.sleep(random.randint(1, 2))
                    return self._buy_upgrade(skill=skill, retries=retries - 1)
                error_message = resp.get(
                    "msg",
                    f"Unknown error occurred while buying {skill_desc} upgrade {skill.id}",
                )
                raise Exception(error_message)

            self.log.info(
                f"<g>├─ ✅ Upgrade {skill_desc} skill {skill.id} succeeded for <c>{self.mcf_api.account_name}</c>!</g>"
            )

            self.BuyCard = True
            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to upgrade {skill_desc} skill {skill.id} for <c>{self.mcf_api.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _perform_pph_upgrades(self):
        self.BuyCard = False
        if not utils.getConfig("auto_buy_pph_upgrades", True):
            self.log.info(f"<y>Auto-buy PPH upgrades disabled.</y>")
            return True
        if not self._get_upgrades():
            return
        if not self.upgrades or len(self.upgrades) < 1:
            return
        self.log.info(
            f"<g>├─ ✅ Performing PPH skill upgrades for <c>{self.mcf_api.account_name}</c>!</g>"
        )
        self.upgrades.sort(key=lambda upgrade: upgrade.profit_diff)
        current_balance = self.profile.game_profile.current_balance
        total_upgrades_price = 0
        total_upgrades_profit = 0
        performing_upgrades: list[ProfileModel.MineData.MineUpgrade] = []

        for upgrade in self.upgrades:
            if (
                upgrade.next_lvl_price > 0
                and upgrade.status == 1
                and upgrade.req_profile_lvl <= self.profile.game_profile.current_level
                and upgrade.next_lvl_price < current_balance
                and upgrade.req_invites <= self.profile.user_profile.invites_count
                and total_upgrades_price + upgrade.next_lvl_price < current_balance
            ):
                performing_upgrades.append(upgrade)
                total_upgrades_price += upgrade.next_lvl_price
                total_upgrades_profit += upgrade.profit_diff

        for upgrade in performing_upgrades:
            if current_balance >= upgrade.next_lvl_price:
                if self._buy_upgrade(upgrade):
                    current_balance -= upgrade.next_lvl_price
            time.sleep(random.randint(1, 3))
        self.profile.game_profile.current_balance = current_balance

        try:
            if self.BuyCard:
                time.sleep(random.randint(1, 3))
                self._perform_pph_upgrades()
        except Exception as e:
            pass

    def _perform_tap_upgrades(self):
        if not utils.getConfig("auto_buy_tap_upgrades", True):
            self.log.info(f"<y>Auto-buy tap upgrades disabled.</y>")
            return True

        if not self.tap_upgrades or len(self.tap_upgrades) < 1:
            return

        self.log.info(
            f"<g>├─ ✅ Performing tap skill upgrades for <c>{self.mcf_api.account_name}</c>!</g>"
        )
        current_balance = self.profile.game_profile.current_balance
        total_upgrades_price = 0
        performing_upgrades: list[ProfileModel.TapData.TapUpgrade] = []
        self.tap_upgrades.sort(key=lambda upgrade: upgrade.next_lvl_price)

        for upgrade in self.tap_upgrades:
            if upgrade.next_lvl_price <= 0:
                continue
            lvl_price = upgrade.next_lvl_price
            if total_upgrades_price + lvl_price < current_balance:
                performing_upgrades.append(upgrade)
                total_upgrades_price += lvl_price

        for upgrade in performing_upgrades:
            if current_balance >= upgrade.next_lvl_price:
                if self._buy_upgrade(upgrade):
                    current_balance -= upgrade.next_lvl_price
            time.sleep(random.randint(1, 3))
        self.profile.game_profile.current_balance = current_balance

    def perform_upgrades(self):
        self._perform_pph_upgrades()
        self._perform_tap_upgrades()
