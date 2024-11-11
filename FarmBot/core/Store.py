from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .models.ProfileModel import ProfileModel
from .models.StoreModel import StoreModel
import time, random
from logging import Logger


class Store:
    def __init__(
        self, log: Logger, httpRequest: HttpRequest, account_name: str, profile: Profile
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.account_name: str = account_name
        self.profile: Profile = profile

    def _get_props(self, page_type, page_num: int = 1, page_size: int = 10):
        try:
            res: dict = self.http.get(
                url=f"miniapps/api/prop_shop/Lists?showPages={page_type}&page={page_num}&pageSize={page_size}",
            )

            if (
                res is None
                or res.get("code", -1) != 0
                or "data" not in res
                or res.get("msg", False) != "OK"
            ):
                error_message = res.get(
                    "msg", "Unknown error occurred while fetching prop data."
                )
                raise Exception(error_message)

            return res.get("data", None)

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
                self.log.info(f"<g>Successfully</g> ordered <y>{prop.desc}</y> ...")
                time.sleep(random.randint(1, 2))
                if not self._apply_prop(
                    prop.prop_id, True if prop_name == "spin" else False
                ):
                    continue
                self.log.info(f"<g>Successfully</g> applyed <y>{prop.desc}</y> ...")
                time.sleep(random.randint(1, 2))

            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get free boxes for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def _make_prop_order(self, sell_id: int):
        try:
            payload = {
                "num": 1,
                "propShopSellId": sell_id,
            }
            res: dict = self.http.post(
                url="miniapps/api/prop_shop/CreateGptPayOrder",
                data=payload,
            )

            if not res:
                error_message = res.get(
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

            res: dict = self.http.post(
                url=url,
                data=payload,
            )

            if res is None or (
                (not is_box and (res.get("code") != 0 or res.get("msg") != "OK"))
                or (is_box and not res.get("rewardLists"))
            ):
                error_message = res.get(
                    "msg", "Unknown error occurred while applying prop."
                )
                raise Exception(error_message)

            if is_box:
                reward_list = res.get("rewardLists", [])
                if reward_list:
                    reward = reward_list[0].get("name", "")
                    self.log.error(
                        f"<g>Box reward <y>{reward}</y> for <c>{self.account_name}</c>!</g>"
                    )

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to apply prop for <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def get_skins(self):
        try:
            skins = []
            for i in range(3):
                # paid_skin_{i+1},notcoin_skin_{i+1}
                # paid_skin_{i+1},notcoin_skin_{i+1},halloween_paid_skin_{i+1},durov_paid_skin_{i+1},blum_skin_{i+1}
                resp = self._get_props(
                    f"paid_skin_{i+1},notcoin_skin_{i+1},halloween_paid_skin_{i+1},durov_paid_skin_{i+1},blum_skin_{i+1}"
                )
                if resp:
                    skins.extend(resp)

            return skins

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get skins for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return None

    def claim_blum_skin(self): # TODO: need to find how to check if skin already claimed
        if not self.profile.user_profile.can_claim_blum:
            # self.log.info(f"Cannot claim blum reward right now")
            return
        try:
            payload = {
                "userId": self.profile.user_profile.uid,
                "blumInvitationCode": butils.generate_md5("9TOkLN1L"), #"c95ebdec8c444b604bb21ae73c3912c4",  # 9TOkLN1L = blum_ref_code.split("_")[1] to md5 32 -
            }
            res: dict = self.http.post(
                url="miniapps/api/linkage/claim_skin_blum",
                data=payload,
            )

            if res is None or res.get("code") != 0 or res.get("msg") != "OK":
                error_message = res.get(
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
