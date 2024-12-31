from .HttpRequest import HttpRequest
from utilities import butils
from .Profile import Profile
from .MCFAPI import MCFAPI
from logging import Logger
from utilities import utilities as utils


class Town:
    def __init__(
        self,
        log: Logger,
        httpRequest: HttpRequest,
        mcf_api: MCFAPI,
        profile: Profile,
    ):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.profile: Profile = profile
        self.mcf_api: MCFAPI = mcf_api

    def get_my_town(self):
        try:
            resp: dict = self.http.get(
                url="/miniapps/api/town/my_town",
                display_errors=True,
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")
            if resp.get("code") == -1:
                pass
                # self.log.info("🟡 <y>You don't have your own town yet.</y>")

            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to own town for <c>{self.mcf_api.account_name}</c> ...</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False
