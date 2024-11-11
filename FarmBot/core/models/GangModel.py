class GangModel:
    def __init__(self):
        pass

    class Gang:
        def __init__(self, data: dict):
            self._data = data
            self._id = self._data.get("gangId", "")
            self._name = self._data.get("name", "")
            self._members_count = int(self._data.get("userCount", -1))
            self._power = int(self._data.get("power", -1))
            self._boost = self._data.get("boost", -1)
            self._rank = self._data.get("rank", -1)
            self._icon = self._data.get("icon", "")

        @property
        def data(self):
            return self._data

        @property
        def id(self):
            return self._id

        @property
        def name(self):
            return self._name

        @property
        def members_count(self):
            return self._members_count

        @property
        def power(self):
            return self._power

        @property
        def boost(self):
            return self._boost

        @property
        def rank(self):
            return self._rank

        @property
        def icon(self):
            return self._icon

    class Member:
        def __init__(self, data: dict):
            self._data = data
            self._full_name = self._data.get("name", "")
            self._first_name = self._data.get("firstName", "")
            self._last_name = self._data.get("lastName", "")
            self._avatar = self._data.get("avatar", "")
            self._boost = int(self._data.get("boost", -1))

        @property
        def data(self):
            return self._data

        @property
        def full_name(self):
            return self._full_name

        @property
        def first_name(self):
            return self._first_name

        @property
        def last_name(self):
            return self._last_name

        @property
        def avatar(self):
            return self._avatar

        @property
        def boost(self):
            return self._boost
