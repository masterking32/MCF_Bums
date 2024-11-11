from utilities import butils


class ProfileModel:
    def __init__(self):
        pass

    class GameProfile:
        def __init__(self, data: dict):
            self._data = data
            self._current_exp = int(self._data.get("experience", -1))
            self._current_level = self._data.get("level", -1)
            self._current_level_exp = int(self._data.get("levelExperience", -1))
            self._required_exp = int(self._data.get("nextExperience", -1))
            self._current_energy = int(self._data.get("energySurplus", -1))
            self._current_balance = int(self._data.get("coin", -1))
            self._tapped_coins = self._data.get("todayCollegeCoin", -1)
            self._tapped_coins_limit = self._data.get("todayMaxCollegeCoin", -1)
            self._skin_id = int(self._data.get("skinId", -999))

        @property
        def current_exp(self):
            return self._current_exp

        @property
        def current_level(self):
            return self._current_level

        @property
        def current_exp_percents(self):
            lvl_percent = round(
                (self._current_exp - self._current_level_exp)
                / self._required_exp
                * 100,
                2,
            )
            return f"{lvl_percent}%"

        @property
        def current_energy(self):
            return self._current_energy

        @property
        def current_balance(self):
            return self._current_balance

        @current_balance.setter
        def current_balance(self, value):
            self._data["coins"] = value
            self._current_balance = value

        @property
        def tapped_coins(self):
            return self._tapped_coins

        @property
        def tapped_coins_limit(self):
            return self._tapped_coins_limit

        @property
        def skin_id(self):
            return self._skin_id

    class UserProfile:
        def __init__(self, data: dict):
            self._data = data
            self._uid = self._data.get("userId", None)
            self._tg_username = self._data.get("telegramUsername", None)
            self._nickname = self._data.get("nickName", None)
            self._days_in_game = self._data.get("daysInGame", -1)
            self._friends_count = self._data.get("invitedFriendsCount", -1)
            self._animals_count = self._data.get("animalInvitedFriendsCount", -1)
            self._upgrades_count = self._data.get("imprpvesCount", -1)
            self._can_claim_blum = self._data.get("blumClaim", False)

        @property
        def uid(self):
            return self._uid

        @property
        def tg_username(self):
            return self._tg_username

        @property
        def nickname(self):
            return self._nickname

        @property
        def days_in_game(self):
            return self._days_in_game

        @property
        def friends_count(self):
            return self._friends_count

        @property
        def animals_count(self):
            return self._animals_count

        @property
        def invites_count(self):
            return self._friends_count + self._animals_count

        @property
        def upgrades_count(self):
            return self._upgrades_count

        @property
        def can_claim_blum(self):
            return self._can_claim_blum

    class TapData:
        def __init__(self, data: dict):
            self._data = data
            self._energy = ProfileModel.TapData.TapUpgrade(
                self._data.get("energy", {}), "energy"
            )
            self._recovery = ProfileModel.TapData.TapUpgrade(
                self._data.get("recovery", {}), "recovery"
            )
            self._tap = ProfileModel.TapData.TapUpgrade(
                self._data.get("tap", {}), "tap"
            )
            self._bonus_chance = ProfileModel.TapData.TapUpgrade(
                self._data.get("bonusChance", {}), "bonusChance"
            )
            self._bonus_ratio = ProfileModel.TapData.TapUpgrade(
                self._data.get("bonusRatio", {}), "bonusRatio"
            )
            self._collect_seq_no = self._data.get("collectInfo", {}).get(
                "collectSeqNo", -1
            )
            self._collect_time = self._data.get("collectInfo", {}).get(
                "collectTime", -1
            )
            self._auto_collect_coin = int(self._data.get("autoCollectCoin", -1))
            self._tap_upgrades = [
                value
                for value in vars(self).values()
                if isinstance(value, ProfileModel.TapData.TapUpgrade)
            ]

        @property
        def energy(self):
            return self._energy

        @property
        def recovery(self):
            return self._recovery

        @property
        def tap(self):
            return self._tap

        @property
        def bonus_chance(self):
            return self._bonus_chance

        @property
        def bonus_ratio(self):
            return self._bonus_ratio

        @property
        def collect_seq_no(self):
            return self._collect_seq_no

        @property
        def collent_time(self):
            return self._collect_time

        @property
        def auto_collect_coin(self):
            return self._auto_collect_coin

        @property
        def tap_upgrades(self):
            return self._tap_upgrades

        class TapUpgrade:
            def __init__(self, data: dict, id: str):
                self._data = data
                self._id = id
                self._name = butils.normalize_name(self._id)
                self._level = self._data.get("level", -1)
                self._current_lvl_value = int(self._data.get("value", -1))
                self._next_lvl_price = int(self._data.get("nextCostCoin", -1))
                self._next_lvl_profit = int(self._data.get("nextIncrease", -1))

            @property
            def id(self):
                return self._id

            @property
            def name(self):
                return self._name

            @property
            def level(self):
                return self._level

            @property
            def current_lvl_value(self):
                return self._current_lvl_value

            @property
            def next_lvl_price(self):
                return self._next_lvl_price

            @property
            def next_lvl_profit(self):
                return self._next_lvl_profit

    class MineData:
        def __init__(self, data: dict):
            self._data = data
            self._mine_power = int(self._data.get("minePower", -1))
            self._mine_offline_coin = int(self._data.get("mineOfflineCoin", -1))

        @property
        def mine_power(self):
            return self._mine_power

        @property
        def mine_offline_coin(self):
            return self._mine_offline_coin

        class MineUpgrade:
            def __init__(self, data: dict):
                self._data = data
                self._id = self._data.get("mineId")
                self._level = self._data.get("level")
                self._next_lvl_price = int(self._data.get("nextLevelCost", -1))
                self._profit = int(self._data.get("perHourReward", -1))
                self._next_lvl_profit = int(self._data.get("nextPerHourReward", -1))
                self._profit_diff = int(self._data.get("distance", -1))
                self._status = self._data.get("status")
                self._category_id = self._data.get("cateId")
                self._req_mine_id = self._data.get("limitMineId")
                self._req_mine_lvl = self._data.get("limitMineLevel")
                self._req_description = self._data.get("limitText")
                self._req_profile_lvl = self._data.get("limitExperienceLevel")
                self._req_invites = self._data.get("limitInvite")

            @property
            def id(self):
                return self._id

            @property
            def level(self):
                return self._level

            @property
            def next_lvl_price(self):
                return self._next_lvl_price

            @property
            def profit(self):
                return self._profit

            @property
            def next_lvl_profit(self):
                return self._next_lvl_profit

            @property
            def profit_diff(self):
                return self._profit_diff

            @property
            def status(self):
                return self._status

            @property
            def category_id(self):
                return self._category_id

            @property
            def req_mine_id(self):
                return self._req_mine_id

            @property
            def req_mine_lvl(self):
                return self._req_mine_lvl

            @property
            def req_description(self):
                return self._req_description

            @property
            def req_profile_lvl(self):
                return self._req_profile_lvl

            @property
            def req_invites(self):
                return self._req_invites

    class UserProp:
        def __init__(self, data: dict):
            self._data = data
            self._props: list[ProfileModel.UserProp.PropObject] = (
                [ProfileModel.UserProp.PropObject(prop) for prop in data]
                if data
                else []
            )

        @property
        def props(self):
            return self._props

        class PropObject:
            def __init__(self, data: dict):
                self._data = data
                self._id = int(self._data.get("prop_id", -1))
                self._name = self._data.get("name", "")
                self._affect = self._data.get("affect", "")
                self._source = self._data.get("source", "")
                self._ratio = float(self._data.get("ratio", 0))
                self._remaining_time = int(self._data.get("times", -1))

            @property
            def id(self):
                return self._id

            @property
            def name(self):
                return self._name

            @property
            def affect(self):
                return self._affect

            @property
            def source(self):
                return self._source

            @property
            def ratio(self):
                return self._ratio

            @property
            def remaining_time(self):
                return self._remaining_time

    class CheckinDay:
        def __init__(self, data: dict):
            self._data = data
            self._day = self._data.get("days", -1)
            self._day_desc = self._data.get("daysDesc", "")
            self._normal_reward = self._data.get("normal", -1)
            self._premium_reward = self._data.get("premium", -1)
            self._status = self._data.get("status", -1) == 1
            self._ad_id = self._data.get("adId", -1)
            self._big_day = self._data.get("bigDay", -1) == 1

        @property
        def day(self):
            return self._day

        @property
        def day_desc(self):
            return self._day_desc

        @property
        def normal_reward(self):
            return self._normal_reward

        @property
        def premium_reward(self):
            return self._premium_reward

        @property
        def status(self):
            return self._status

        @property
        def ad_id(self):
            return self._ad_id

        @property
        def big_day(self):
            return self._big_day
