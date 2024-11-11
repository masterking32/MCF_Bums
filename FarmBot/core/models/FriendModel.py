class FriendModel:
    def __init__(self):
        pass

    class Friend:
        def __init__(self, data: dict):
            self._data = data
            self._nickname = self._data.get("nickName", "")
            self._level = int(self._data.get("level", -1))
            self._is_premium = bool(self._data.get("isPremium", False))
            self._amount = int(self._data.get("amount", -1))
            self._ton_reward = int(self._data.get("tonReward", -1))
            self._avatar_id = self._data.get("avatarId", -1)

        @property
        def data(self):
            return self._data

        @property
        def nickname(self):
            return self._nickname

        @property
        def level(self):
            return self._level

        @property
        def is_premium(self):
            return self._is_premium

        @property
        def amount(self):
            return self._amount

        @property
        def ton_reward(self):
            return self._ton_reward

        @property
        def avatar_id(self):
            return self._avatar_id

    class Balance:
        def __init__(self, data: dict):
            self._data = data
            self._id = self._data.get("id", -1)
            self._title = self._data.get("title", "")
            self._freezed_amount = self._data.get("freezeAmount", -1)
            self._available_amount = self._data.get("availableAmount", -1)
            self._total_expenditure = self._data.get("totalExpenditure", -1)

        @property
        def data(self):
            return self._data

        @property
        def id(self):
            return self._id

        @property
        def title(self):
            return self._title

        @property
        def freezed_amount(self):
            return self._freezed_amount

        @property
        def available_amount(self):
            return self._available_amount

        @property
        def total_expenditure(self):
            return self._total_expenditure
