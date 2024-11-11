import json
from .HttpRequest import HttpRequest
from utilities.utilities import getConfig
from urllib.parse import parse_qs, urlencode
from utilities import butils


class Auth:
    def __init__(self, log, httpRequest, account_name, start_param=""):
        self.log = log
        self.http: HttpRequest = httpRequest
        self.account_name: str = account_name
        self.auth_token: str = None
        self.start_param: str = start_param

    @property
    def token(self):
        return self.auth_token

    def authorize(self, web_app_query):
        try:
            self.log.info(
                f"<y>Authorizing user <c>{self.account_name}</c> to <c>Bums</c>...</y>"
            )

            ref_code = ""
            try:
                if self.start_param != "":
                    ref_code = self.start_param.split("=")[1]
                else:
                    self.start_param = "/"

                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                }

                self.http.get(
                    self.start_param,
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
                "initData": web_app_query,
            }
            if ref_code != "":
                payload["invitationCode"] = ref_code

            res: dict = self.http.post(
                url="miniapps/api/user/telegram_auth",
                data=payload,
                valid_response_code=[200, 201],
            )

            if (
                res is None
                or res.get("code", -1) != 0
                or "data" not in res
                or res.get("msg", False) != "OK"
            ):
                self.log.error(
                    f"<r>❌ Failed to authorize user <c>{self.account_name}</c>! RESPONSE_IS_NULL</r>"
                )
                return False

            self.auth_token = res.get("data", {}).get("token", None)
            self.http.auth_token = self.token

            self.log.info(
                f"<g>├─ ✅ Authorization complete for <c>{self.account_name}</c>!</g>"
            )
            return True
        except Exception as e:
            self.log.error(
                f"<r>❌ Failed to authorize user <c>{self.account_name}</c>!</r>"
            )
            self.log.error(f"<r>❌ {str(e)}</r>")
            return False
