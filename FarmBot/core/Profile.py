from .HttpRequest import HttpRequest
from .MCFAPI import MCFAPI
from utilities import butils
from .models.ProfileModel import ProfileModel
from .models.StoreModel import StoreModel
import time, random
from logging import Logger
from utilities import utilities as utils


class Profile:
    def __init__(self, log: Logger, httpRequest: HttpRequest, mcf_api: MCFAPI):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.mcf_api: MCFAPI = mcf_api
        self.account_name = self.mcf_api.account_name
        self.tgAccount = self.mcf_api.tgAccount
        self._data: dict = {}
        self._user_profile: ProfileModel.UserProfile = None
        self._game_profile: ProfileModel.GameProfile = None
        self._tap_data: ProfileModel.TapData = None
        self._mine_info: ProfileModel.MineData = None
        self._user_prop: ProfileModel.UserProp = None
        self._not_coin_rewards: list[ProfileModel.UserProp.PropObject] = None

    @property
    def data(self):
        return self._data

    @property
    def user_profile(self):
        return self._user_profile

    @property
    def game_profile(self):
        return self._game_profile

    @property
    def tap_data(self):
        return self._tap_data

    @property
    def mine_info(self):
        return self._mine_info

    @property
    def user_prop(self):
        return self._user_prop

    @property
    def not_coin_rewards(self):
        return self._not_coin_rewards

    def print_info(self, logged=True):
        if logged:
            self.log.info(
                f"<g>├─ ✅ Logged in as: <y>{self.user_profile.nickname}</y></g>"
            )
        self.log.info(
            f"<g>├─ 📈 Level: <y>{self.game_profile.current_level}</y> - Exp: <y>{self.game_profile.current_exp_percents}%</y></g>"
        )
        self.log.info(
            f"<g>├─ 💰 Balance: <y>{butils.round_int(self.game_profile.current_balance)}</y></g>"
        )
        self.log.info(
            f"<g>├─ 💵 Offline income: <y>{butils.round_int(self.mine_info.mine_offline_coin)}</y></g>"
        )
        self.log.info(
            f"<g>├─ 🔋 Energy: <y>{butils.round_int(self.game_profile.current_energy)}</y>/<y>{butils.round_int(self.tap_data.energy.current_lvl_value)}</y></g>"
        )

    def get_game_data(self, blum=False):
        try:
            url = "miniapps/api/user_game_level/getGameInfo?blumInvitationCode="
            if blum:
                url += "9TOkLN1L"
            elif self.tgAccount and not blum:
                ref_code = self.tgAccount.ReferralToken
                url += ref_code.split("_")[1] if "_" in ref_code else ref_code

            resp: dict = self.http.get(
                url=url,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (
                resp.get("code") != 0 or "data" not in resp or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", "Unknown error occurred while getting game data."
                )
                raise Exception(error_message)

            self._data = resp.get("data", {})
            self._user_profile = ProfileModel.UserProfile(self.data.get("userInfo", {}))
            self._game_profile = ProfileModel.GameProfile(self.data.get("gameInfo", {}))
            self._tap_data = ProfileModel.TapData(self.data.get("tapInfo", {}))
            self._mine_info = ProfileModel.MineData(self.data.get("mineInfo", {}))
            self._user_prop = ProfileModel.UserProp(self.data.get("propInfo", []))

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to acquire game data for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def check_daily_checkin(self):
        if not utils.getConfig("daily_checking", True):
            self.log.info(f"<g>├─ ⚙️ Auto daily check-in disabled.</g>")
            return True
        try:
            resp: dict = self.http.get(
                url="miniapps/api/sign/getSignLists",
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (
                resp.get("code") != 0
                or "data" not in resp
                or resp.get("msg", False) != "OK"
            ):
                error_message = resp.get(
                    "msg", "Unknown error occurred while checking daily check-in."
                )
                raise Exception(error_message)

            checkin_data: dict = resp.get("data", {})
            is_checked_in = checkin_data.get("signStatus") == 1
            checkin_streak = checkin_data.get("signNum", -1)  # TODO: check if it wrong
            days = checkin_data.get("lists", [])
            today_data = [day for day in days if day["status"] == 1]
            today = ProfileModel.CheckinDay(today_data[-1]) if today_data else None

            next_day_data = [day for day in days if day["status"] == 2]
            next_day = (
                ProfileModel.CheckinDay(next_day_data[0]) if next_day_data else None
            )

            if not is_checked_in and next_day:
                if not self._do_daily_checkin(next_day):
                    return False
                time.sleep(random.randint(1, 3))
                return self.check_daily_checkin()

            self.log.info(
                f'<g>├─ ✔️ Daily check-in: {f"<y>Yes</y>" if is_checked_in else "<r>No</r>"}</g>'
            )

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to check daily check-in for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _do_daily_checkin(self, today: ProfileModel.CheckinDay):
        try:
            payload = {
                "": "undefined",
            }
            resp: dict = self.http.post(
                url="miniapps/api/sign/sign",
                data=payload,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", "Unknown error occurred while performing daily check-in."
                )
                raise Exception(error_message)

            day_desc = today.day_desc
            normal_reward = butils.round_int(today.normal_reward)
            premium_reward = butils.round_int(today.premium_reward)
            premium_text = (
                f" +{premium_reward} for premium." if today.premium_reward > 0 else ""
            )

            self.log.info(
                f"<g>├─ ✔️ Daily check-in success, <y>{day_desc}</y>. "
                f"Reward: {normal_reward}{premium_text}</g>"
            )

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to perform daily check-in for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _tap_request(self, collect_amount):
        const_value = "7be2a16a82054ee58398c5edb7ac4a5a"
        collectSeqNo = self.tap_data.collect_seq_no
        collectAmount = int(collect_amount)
        preHash = f"{collectAmount}{collectSeqNo}{const_value}"
        hashCode = butils.generate_md5(preHash)
        payload = {
            "hashCode": hashCode,
            "collectSeqNo": collectSeqNo,
            "collectAmount": collectAmount,
        }
        resp: dict = self.http.post(
            url="miniapps/api/user_game/collectCoin",
            data=payload,
        )
        if not resp:
            raise Exception("RESPONSE_IS_NULL")
        if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
            error_message = resp.get(
                "msg", "Unknown error occurred while performing taps."
            )
            raise Exception(error_message)
        self.log.info(
            f"<g>├─ ✔️ Spent tap energy {butils.round_int(collectAmount)} for <c>{self.account_name}</c></g>"
        )
        time.sleep(random.uniform(0.5, 1.0))
        self.get_game_data()
        time.sleep(random.uniform(0.5, 1.0))

    def perform_taps(self):
        if not utils.getConfig("auto_taps", True):
            self.log.info(f"<g>├─ ⚙️ Auto taps disabled.</g>")
            return True
        try:
            tapped_coins = self.game_profile.tapped_coins
            limit_coins = self.game_profile.tapped_coins_limit
            if tapped_coins >= limit_coins:
                return True

            self.log.info(
                f"<g>├─ 👆 Performing taps for <c>{self.account_name}</c></g>"
            )

            energy = self.game_profile.current_energy
            max_energy = self.tap_data.energy.current_lvl_value
            self.log.info(
                f"<g>├─ 🔋 Current energy <c>{butils.round_int(energy)}</c></g>"
            )
            if energy < int(max_energy * 0.05):
                self.log.info(f"<g>├─ ⚠️ Low energy, skipping taps ...</g>")
                return True

            if utils.getConfig("auto_taps_human_like", False):
                while energy > int(max_energy * 0.26):
                    collect_amount = int(max_energy * random.uniform(0.10, 0.25))
                    self._tap_request(collect_amount)
                    energy = self.game_profile.current_energy
                    time.sleep(random.uniform(1.0, 2.0))
            else:
                collect_amount = int(energy * random.uniform(0.90, 0.95))
                self._tap_request(collect_amount)

            self.log.info(
                f"<g>├─ ✔️ Successfully performed taps for <c>{self.account_name}</c>, balance <y>{butils.round_int(self.game_profile.current_balance)}</y></g>"
            )

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to perform taps for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False
