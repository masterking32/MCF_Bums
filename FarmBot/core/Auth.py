import json
from .HttpRequest import HttpRequest
from .MCFAPI import MCFAPI
from utilities.utilities import getConfig
from urllib.parse import parse_qs, urlencode
from utilities import butils
from logging import Logger


class Auth:
    def __init__(self, log: Logger, httpRequest: HttpRequest, mcf_api: MCFAPI):
        self.log: Logger = log
        self.http: HttpRequest = httpRequest
        self.mcf_api: MCFAPI = mcf_api
        self.account_name: str = self.mcf_api.account_name
        self.auth_token: str = None

    def authorize(self):
        try:
            self.log.info(
                f"🔐 <y>Authorizing user <c>{self.account_name}</c> to <c>Bums</c>...</y>"
            )

            try:
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                }

                self.http.get(
                    self.mcf_api.start_param,
                    domain="app",
                    headers=headers,
                    send_option_request=False,
                    auth_header=False,
                    only_json_response=False,
                )
            except Exception as e:
                pass

            payload = {
                "invitationCode": "",
                "initData": self.mcf_api.web_app_query,
            }
            if self.mcf_api.ref_code != "":
                ref_code = self.mcf_api.tgAccount.ReferralToken
                payload["invitationCode"] = (
                    ref_code.split("_")[1] if "_" in ref_code else ref_code
                )

            resp: dict = self.http.post(
                url="miniapps/api/user/telegram_auth",
                data=payload,
                valid_response_code=[200, 201],
            )

            if not resp:
                raise Exception("RESPONSE_IS_NULL")

            if resp and (
                resp.get("code") != 0 or not resp.get("data") or resp.get("msg") != "OK"
            ):
                error_message = resp.get(
                    "msg", "An unknown error occurred during user authorization."
                )
                raise Exception(error_message)

            self.auth_token = resp.get("data", {}).get("token", None)
            self.http.auth_token = self.auth_token

            self.log.info(
                f"✅ <g>Authorization complete for user <c>{self.account_name}</c>!</g>"
            )
            return True
        except Exception as e:
            self.log.error(
                f"❌ <r>Failed to authorize user <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"❌ <r>{str(e)}</r>")
            return False
