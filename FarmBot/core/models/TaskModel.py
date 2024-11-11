class TaskMgr:
    def __init__(self, data: dict):
        self._data = data
        self._tasks = [TaskMgr.Task(task) for task in self._data.get("lists")]
        self._new_count = self._data.get("newCount", -999)
        self._incomplete = self._data.get("notFinishCount", -999)

    @property
    def tasks(self):
        return self._tasks

    @property
    def new_count(self):
        return self._new_count

    @property
    def incomplete(self):
        return self._incomplete

    class Task:
        def __init__(self, data: dict):
            self._data = data
            self._id = int(self._data.get("id", -999))
            self._name = str(self._data.get("name", ""))
            self._type = str(self._data.get("type", ""))
            self._task_type = str(self._data.get("taskType", ""))
            self._url = str(self._data.get("jumpUrl", ""))
            self._is_finished = self._data.get("isFinish", 0) == 1
            self._class_name = str(self._data.get("classifyName", ""))
            self._reward_party = int(self._data.get("rewardParty", -999))
            self._reward_diamond = int(self._data.get("rewardDiamond"))
            self._copy_text = str(self._data.get("copyText", ""))
            self._invites_required = int(self._data.get("limitInviteCount", -999))
            self._invites_progress = int(self._data.get("InviteCount", -999))

        @property
        def id(self):
            return self._id

        @property
        def name(self):
            return self._name

        @property
        def type(self):
            return self._type

        @property
        def task_type(self):
            return self._task_type

        @property
        def url(self):
            return self._url

        @property
        def is_finished(self):
            return self._is_finished

        @property
        def class_name(self):
            return self._class_name

        @property
        def reward_patry(self):
            return self._reward_party

        @property
        def reward_diamond(self):
            return self._reward_diamond

        @property
        def copy_text(self):
            return self._copy_text

        @property
        def invites_required(self):
            return self._invites_required

        @property
        def invites_progress(self):
            return self._invites_progress
