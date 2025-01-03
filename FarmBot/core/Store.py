from .HttpRequest import HttpRequest
from .MCFAPI import MCFAPI
from .Profile import Profile
from utilities import butils
from .models.ProfileModel import ProfileModel
from .models.StoreModel import StoreModel
import time, random
from logging import Logger

from utilities import utilities as utils


class Store:
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
        self.account_name: str = self.mcf_api.account_name
        self.all_skins: list[StoreModel.StoreProp] = []
        self.have_notcoin_reward = False
        self.have_blum_reward = False

    def _get_props(self, page_type, page_num: int = 1, page_size: int = 10):
        try:
            resp: dict = self.http.get(
                url=f"miniapps/api/prop_shop/Lists?showPages={page_type}&page={page_num}&pageSize={page_size}",
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (
                resp.get("code") != 0 or "data" not in resp or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", "Unknown error occurred while fetching prop data."
                )
                raise Exception(error_message)

            return resp.get("data", None)

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get {page_type} store data for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return None

    def _get_free_prop(self, prop_name: str):
        try:
            if prop_name == "box":
                prop_name = "spin"
            elif prop_name == "animals":
                prop_name = "teddy_Bear"

            raw_props = self._get_props(prop_name)
            props: list[StoreModel.StoreProp] = []

            if not raw_props:
                return False

            props = [
                StoreModel.StoreProp(prop) for prop in raw_props if prop is not None
            ]

            if not props:
                return False

            free_props = [
                prop
                for prop in props
                if any(sell.new_amount == 0 for sell in prop.sell_lists)
                and prop.today_used < prop.today_max_use
            ]

            if not free_props:
                return False

            for prop in free_props:
                if prop.prop_id < 0:
                    continue

                if prop.today_used >= prop.today_max_use:
                    continue

                if (
                    prop_name == "expedition"
                    and not utils.getConfig("cheating_mode", False)
                    and prop.title != "Rocket Expedition Team"
                ):
                    continue

                sell_id = next(
                    (
                        sell.id
                        for sell in prop.sell_lists
                        if sell.id > 0 and sell.new_amount == 0
                    )
                )
                if not sell_id:
                    continue
                if not self._make_prop_order(sell_id):
                    continue
                self.log.info(f"<g>✅ Successfully</g> ordered <y>{prop.desc}</y> ...")
                time.sleep(random.randint(1, 2))
                if not self._apply_prop(
                    prop.prop_id, True if prop_name == "spin" else False
                ):
                    continue
                self.log.info(f"<g>✅ Successfully</g> applied <y>{prop.desc}</y> ...")
                time.sleep(random.randint(1, 2))

            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get free boxes for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _get_advent_box(self):
        raw_props = self._get_props("spin")
        props: list[StoreModel.StoreProp] = []

        if not raw_props:
            return False

        props = [StoreModel.StoreProp(prop) for prop in raw_props if prop is not None]
        if not props:
            return False

        advent_box = next(
            prop
            for prop in props
            if prop.title == "Advent Rewards" and prop.desc == "Advent Rewards"
        )
        return advent_box

    def _open_advent_box(self):
        try:
            payload = {
                "count": 10,
            }
            resp: dict = self.http.post(
                url=f"miniapps/api/active/christmas_spin",
                data=payload,
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (
                resp.get("code") != 0 or "data" not in resp or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", "Unknown error occurred while fetching prop data."
                )
                raise Exception(error_message)

            return resp.get("data", None)

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to open advent box for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return None

    def _make_prop_order(self, sell_id: int):
        try:
            payload = {
                "num": 1,
                "propShopSellId": sell_id,
            }
            resp: dict = self.http.post(
                url="miniapps/api/prop_shop/CreateGptPayOrder",
                data=payload,
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", "Unknown error occurred while making prop order."
                )
                raise Exception(error_message)

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to make prop order for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _apply_prop(self, prop_id: int, is_box: bool = False):
        try:
            payload = {}
            if is_box:
                payload["count"] = 1
            payload["propId"] = prop_id
            url = "miniapps/api/user_prop/UseProp"
            if is_box:
                url = "miniapps/api/game_spin/Start"

            resp: dict = self.http.post(
                url=url,
                data=payload,
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and (
                (not is_box and (resp.get("code") != 0 or resp.get("msg") != "OK"))
                or (is_box and not resp.get("rewardLists"))
            ):
                error_message = resp.get(
                    "msg", "Unknown error occurred while applying prop."
                )
                raise Exception(error_message)

            if is_box:
                reward_list = resp.get("rewardLists", [])
                if reward_list:
                    reward = reward_list[0].get("name", "")
                    self.log.info(
                        f"<g>🎁 Box reward <y>{reward}</y> for <c>{self.account_name}</c>!</g>"
                    )

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to apply prop for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _get_all_skins(self):
        if self.all_skins and len(self.all_skins) > 0:
            self.all_skins.clear()
        try:
            skins: list[StoreModel.StoreProp] = []
            for i in range(1, 4):
                skins_list = [
                    f"paid_skin_{i}",
                    f"notcoin_skin_{i}",
                    f"halloween_paid_skin_{i}",
                    f"durov_paid_skin_{i}",
                ]
                if i == 2:
                    skins_list.append(f"blum_skin_{i}")
                endpoint = ",".join(skins_list)
                resp = self._get_props(endpoint)
                if resp:
                    skins.extend(StoreModel.StoreProp(item) for item in resp)

            self.all_skins = skins

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get skins for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return None

    def _claim_blum_skin(self):
        if not self.profile.user_profile.can_claim_blum:
            return
        try:
            payload = {
                "userId": self.profile.user_profile.uid,
                "blumInvitationCode": butils.generate_md5("9TOkLN1L"),
            }
            resp: dict = self.http.post(
                url="miniapps/api/linkage/claim_skin_blum",
                data=payload,
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp and resp.get("status") is False:
                error_message = resp.get(
                    "msg", "Unknown error occurred while getting blum reward skin."
                )
                raise Exception(error_message)

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get blum reward skin for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _get_existing_skins(self):
        self._get_all_skins()
        if not self.all_skins or len(self.all_skins) <= 0:
            self.log.info(f"<y>All skins local data is empty ...</y>")
            return
        existing_skins = [skin for skin in self.all_skins if skin.stock > 0]
        return existing_skins

    def check_reward_skins(self):
        existing_skins = self._get_existing_skins()
        skins_names = {skin.title for skin in existing_skins}
        notcoin_skin_names = {"NOT a toy", "Glitch Bum", "Pixeloid"}
        blum_skin_names = {"Blumbum"}
        self.have_notcoin_reward = any(
            skin in skins_names for skin in notcoin_skin_names
        )
        self.have_blum_reward = any(skin in skins_names for skin in blum_skin_names)
        if not self.have_notcoin_reward:
            if self.mcf_api.tgAccount:
                # TODO: GET NOTCOIN REF CODE FROM API???
                # self.mcf_api.start_bot("notcoin_bot", "")
                # need to get available skin by notcoin level or other things before claim
                pass
        if not self.have_blum_reward:
            # TODO: need to implement skin receiving
            # im not sure if its right and safe way to do it in same loop with other ref code
            # self.profile.get_game_data(True) # TODO
            # self._claim_blum_skin()
            pass
