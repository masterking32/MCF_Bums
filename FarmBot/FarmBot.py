# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot
import sys
import os
import random
import time
import asyncio

from .core.HttpRequest import HttpRequest
from utilities import butils
from .core.MCFAPI import MCFAPI
from .core.Auth import Auth
from .core.Profile import Profile
from .core.Store import Store
from .core.Upgrades import Upgrades
from .core.City import City
from .core.Tasks import Tasks
from .core.Friends import Friends

MasterCryptoFarmBot_Dir = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__ + "/../../"))
)
sys.path.append(MasterCryptoFarmBot_Dir)

from utilities.utilities import getConfig


class FarmBot:
    def __init__(
        self,
        log,
        bot_globals,
        account_name,
        web_app_query,
        proxy=None,
        user_agent=None,
        isPyrogram=False,
        tgAccount=None,
    ):
        self.log = log
        self.bot_globals = bot_globals
        self.account_name = account_name
        self.web_app_query = web_app_query
        self.proxy = proxy
        self.user_agent = user_agent
        self.isPyrogram = isPyrogram
        self.tgAccount = tgAccount
        self.mcf_api = None

    async def run(self):
        try:
            self.log.info(
                f"<g>📦 Bums is starting for account <cyan>{self.account_name}</cyan>...</g>"
            )

            self.http = HttpRequest(
                self.log, self.proxy, self.user_agent, self.account_name
            )
            self.mcf_api = MCFAPI(
                self.log,
                self.bot_globals,
                self.account_name,
                self.proxy,
                self.tgAccount,
            )

            start_param = ""
            if self.tgAccount is not None and self.tgAccount.NewStart:
                start_param = "/?tgWebAppStartParam=" + self.tgAccount.ReferralToken

            auth = Auth(self.log, self.http, self.account_name, start_param)

            if not auth.authorize(self.web_app_query):
                return

            profile = Profile(self.log, self.http, self.account_name, self.tgAccount)

            if not profile.get_game_data():
                return

            await asyncio.sleep(random.randint(1, 2))

            store = Store(self.log, self.http, self.account_name, profile)

            profile.print_info()

            store.claim_blum_skin()

            if not profile.check_daily_checkin():
                return
            await asyncio.sleep(random.randint(1, 2))

            if not profile.perform_taps():
                return
            await asyncio.sleep(random.randint(1, 2))

            tasks = Tasks(
                self.log,
                self.http,
                self.bot_globals,
                self.tgAccount,
                self.account_name,
                profile,
                self.mcf_api,
            )
            await tasks.perform_tasks()
            await asyncio.sleep(random.randint(1, 2))

            friends = Friends(
                self.log,
                self.http,
                self.account_name,
                self.bot_globals,
                profile,
                self.mcf_api,
            )
            friends.get_friends()
            friends.get_balance()
            friends.clain_reward()

            city = City(
                self.log,
                self.http,
                self.account_name,
                self.bot_globals,
                profile,
                store,
                self.mcf_api,
            )
            city.get_free_expeditions()
            await asyncio.sleep(random.randint(1, 2))
            city.get_free_boxes()
            await asyncio.sleep(random.randint(1, 2))
            city.get_free_animas()
            await asyncio.sleep(random.randint(1, 2))
            city.do_daily_combo()
            await asyncio.sleep(random.randint(1, 2))

            upgrades = Upgrades(self.log, self.http, self.account_name, profile)
            upgrades.perform_upgrades()

        except Exception as e:
            self.log.error(
                f"⭕ <r>Failed to farm for account <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"❌ <r>{str(e)}</r>")
            return

        finally:
            delay_between_accounts = getConfig("delay_between_accounts", 60)
            random_sleep = random.randint(5, 15) + delay_between_accounts
            self.log.info(
                f"⌛ <g>Farming for account <c>{self.account_name}</c> completed. Waiting for <c>{random_sleep}</c> seconds before running the next account...</g>"
            )
            time.sleep(random_sleep)
