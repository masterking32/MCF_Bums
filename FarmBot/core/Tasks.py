import json
import time
import random
import asyncio
import os
from .models.TaskModel import TaskMgr
from .MCFAPI import MCFAPI
from logging import Logger
from .Profile import Profile
from .HttpRequest import HttpRequest
from utilities import butils
from utilities import utilities as utils


class Tasks:
    def __init__(
        self,
        log: Logger,
        httpRequest: HttpRequest,
        bot_globals,
        tgAccount,
        account_name,
        profile: Profile,
        mcfapi: MCFAPI,
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.bot_globals = bot_globals
        self.tgAccount = tgAccount
        self.account_name = account_name
        self.profile: Profile = profile
        self.mcf_api: MCFAPI = mcfapi
        self.task_mgr: TaskMgr = None

    def _get_tasks(self):
        try:
            resp: dict = self.http.get(
                url="miniapps/api/task/lists",
            )
            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            elif resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", "Unknown error occurred while getting tasks."
                )
                raise Exception(error_message)

            data = resp.get("data", {})
            self.task_mgr = TaskMgr(data)
            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get tasks for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def log_task_reward(self, task: TaskMgr.Task):
        self.log.info(
            f"<g>Received <y>{butils.round_int(task.reward_patry)}</y> for completing task: <y>{task.name}</y></g>"
        )

    def _read_pwd_from_file(self, task: TaskMgr.Task):
        file_path = os.path.join(
            self.bot_globals["module_dir"], "youtube_keywords.json"
        )
        if os.path.isfile("youtube_keywords.json"):
            self.log.info(f"File youtube_keywords.json not exists ...")
            return None
        self.log.info(f"Checking in youtube_keywords.json")
        with open(file_path, "r") as file:
            answers = json.load(file)
        if not answers:
            self.log.info(f"Answers empty ...")
            return None
        answer = next(
            (answer for answer in answers if answer.get("id") == task.id), None
        )
        if answer:
            if answer.get("pwd"):
                return answer.get("pwd")
            else:
                self.log.info(
                    f"Youtube task <y>{answer.get("name")}</y> pwd is unknown."
                )
                self.log.info(
                    f"Find it in <y>{answer.get("url")}</y> and add it to youtube_keywords.json manually"
                )
                return None
        answers.append({"id": task.id, "name": task.name, "url": task.url, "pwd": None})
        answers.sort(key=lambda ans: ans.get("id"))
        with open(file_path, "w") as file:
            json.dump(answers, file, indent=4)
        self.log.info(
            f"Task <y>{task.name}</y> was added to the youtube_keywords.json without a password ..."
        )
        self.log.info(
            f"Find it in <y>{task.url}</y> and add it to youtube_keywords.json manually"
        )
        return None

    async def perform_tasks(self):
        if not utils.getConfig("auto_tasks", True):
            self.log.info("Auto tasks disabled.")
            return True
        self.log.info("<g>Performing tasks...</g>   ")
        if not self._get_tasks():
            return False
        try:
            incompleted_tasks = [
                task
                for task in self.task_mgr.tasks
                if not task.is_finished
                and (
                    "boost" not in task.name.lower()
                    and "?boost" not in task.url.lower()
                )
            ]

            for task in incompleted_tasks:
                try:
                    self.log.info(f"<g>Performing task: <y>{task.name}</y> ...</g>")
                    if "boost" in task.name.lower() or "?boost" in task.url.lower():
                        continue
                    elif task.task_type == "pwd":
                        if not utils.getConfig("auto_pwd_tasks", True):
                            self.log.info(f"Auto complete youtube tasks disabled ...")
                            await asyncio.sleep(random.randint(1, 2))
                            continue
                        pwd = self.mcf_api.get_task_keyword(task.id, task.name)
                        if not pwd:
                            self.log.info(
                                f"Password for task <y>{task.name}</y> not found on API ..."
                            )
                            continue
                        # pwd = self._read_pwd_from_file(task)
                        # if not pwd:
                        #     await asyncio.sleep(random.randint(1, 2))
                        #     continue
                        await asyncio.sleep(random.randint(1, 2))
                        if self.finish_task(task, pwd):
                            self.log_task_reward(task)

                    if task.name == "Like and repost the latest news":
                        if self.finish_task(task):
                            self.log_task_reward(task)
                    elif (
                        "t.me" in task.url
                        and "boost/" in task.url
                        and utils.getConfig("auto_join_channels", True)
                    ):
                        if not self.tgAccount:
                            continue
                        channel_url = task.url
                        if "+" not in channel_url:
                            channel_url = (
                                channel_url.replace("https://t.me/", "")
                                .replace("@", "")
                                .replace("boost/", "")
                            )
                        channel_url = (
                            channel_url.split("/")[0]
                            if "/" in channel_url
                            else channel_url
                        )
                        self.log.info(
                            f"<g>📝 Attempting to join the <c>{channel_url}</c> channel to complete the <c>{task.name}</c> task</g>"
                        )
                        await self.mcf_api.join_chat(channel_url)
                        await asyncio.sleep(random.randint(1, 2))
                        if self.finish_task(task):
                            self.log_task_reward(task)
                    elif task.url is not None and task.url != "":
                        if "t.me" not in task.url:
                            if self.finish_task(task):
                                self.log_task_reward(task)
                            continue

                        if not self.tgAccount:
                            continue

                        if (
                            "+" not in task.url
                            and task.url.lower()
                            .replace("/", "")
                            .split("?")[0]
                            .endswith("bot")
                            or "?" in task.url
                        ):
                            if not utils.getConfig("auto_start_bots", True):
                                self.log.info(f"Auto start bot disabled ...")
                                continue

                            api_resp = self.mcf_api.get_invite_link(task.url)
                            if not api_resp:
                                self.log.info(
                                    f"Failed to get invite link for <y>{task.name}</y> ..."
                                )
                                continue

                            ref_link = api_resp.get("referral")
                            bot_id = api_resp.get("bot_id")
                            await self.mcf_api.start_bot(bot_id, ref_link)
                            await asyncio.sleep(random.randint(1, 2))
                            if self.finish_task(task):
                                self.log_task_reward(task)

                            continue

                        if not utils.getConfig("auto_join_channels", True):
                            self.log.info(f"Auto join channels disabled ...")
                            continue

                        channel_url = task.url
                        if "+" not in channel_url:
                            channel_url = (
                                channel_url.replace("https://t.me/", "")
                                .replace("@", "")
                                .replace("boost/", "")
                            )
                        channel_url = (
                            channel_url.split("/")[0]
                            if "/" in channel_url
                            else channel_url
                        )
                        self.log.info(
                            f"<g>📝 Attempting to join the <c>{channel_url}</c> channel to complete the <c>{task.name}</c> task</g>"
                        )

                        await self.mcf_api.join_chat(channel_url)
                        await asyncio.sleep(random.randint(3, 5))
                        if self.finish_task(task):
                            self.log_task_reward(task)

                    elif task.task_type == "level" and task.type == "index":
                        req_level = int(task.name.strip()[-1])
                        user_level = self.profile.game_profile.current_level
                        if not req_level and req_level <= 0:
                            await asyncio.sleep(random.randint(1, 2))
                            continue
                        if user_level >= req_level:
                            if self.finish_task(task):
                                self.log_task_reward(task)
                        else:
                            self.log.info(
                                f"<g>Insufficient level to accomplish the task. Requires <y>{req_level}</y>, yours is <y>{user_level}</y>.</g>"
                            )
                    elif task.task_type == "tap_coin" and task.type == "upgrade":
                        if self.profile.tap_data.collect_seq_no > 0:
                            if self.finish_task(task):
                                self.log_task_reward(task)
                    elif task.task_type == "invite_group":
                        if (
                            task.invites_required > 0
                            and task.invites_progress >= task.invites_required
                        ):
                            if self.finish_task(task):
                                self.log_task_reward(task)
                        else:
                            self.log.info(
                                f"<g>Insufficient frens to accomplish the task. Requires <y>{task.invites_required}</y>, yours is <y>{task.invites_progress}</y>.</g>"
                            )
                            await asyncio.sleep(random.randint(1, 2))
                            continue
                    elif task.task_type == "nickname_check" and utils.getConfig(
                        "auto_change_name", True
                    ):
                        if not self.tgAccount:
                            continue
                        if task.copy_text not in self.profile.user_profile.nickname:
                            if await self.mcf_api.set_name(task.copy_text):
                                self.log.info(
                                    f"<g>✅ Added <c>{task.copy_text}</c> to last name to complete the <c>{task.name}</c> task</g>"
                                )
                                self.log.info(
                                    f"<g>✅ <c>{task.name}</c> will be completed on the next run!</g>"
                                )
                            else:
                                self.log.warning("Failed to set name.")
                        else:
                            if self.finish_task(task):
                                self.log_task_reward(task)

                    self.profile.get_game_data()
                    await asyncio.sleep(random.randint(1, 2))
                except Exception as e:
                    self.log.error(f"❌ <r>{str(e)}</r>")
                    await asyncio.sleep(random.randint(1, 2))
                    continue

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to get tasks for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False

    def finish_task(self, task: TaskMgr.Task, pwd: str = None):
        try:
            payload = {"id": f"{task.id}"}
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            if pwd:
                payload["pwd"] = pwd

            resp: dict = self.http.post(
                url="miniapps/api/task/finish_task",
                headers=headers,
                use_boundary=False,
                data=payload,
            )
            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            elif resp and (resp.get("code") != 0 or resp.get("msg") != "OK"):
                error_message = resp.get(
                    "msg", f"Unknown error occurred while finishing task {task.id}"
                )
                raise Exception(error_message + ", pwd may be wrond." if pwd else "")

            return True

        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to finish task {task.id} for <c>{self.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False
