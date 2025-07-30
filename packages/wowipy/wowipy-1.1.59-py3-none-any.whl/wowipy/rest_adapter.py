import logging

import requests
import requests.packages
import requests.utils
import requests_cache
from typing import Dict
from wowipy.exceptions import WowiPyException
from wowipy.models import Result
from json import JSONDecodeError


class RestAdapter:
    logger = logging.getLogger(__name__)

    def __init__(self, hostname: str, user: str, password: str, api_key: str, version: str = 'v1.2',
                 logger: logging.Logger = None, user_agent: str = None):
        """
        Constructor for RestAdapter
        :param hostname: OPENWOWI-Hostname without trailing slash, e.g. customer.wowiport.de
        :type hostname: str
        :param user: Wowiport username (does not need any permissions)
        :type user: str
        :param password: Wowiport User password
        :type password: str
        :param api_key: OPENWOWI API-Key. Set permissions and scope in Wowiport!
        :type api_key: str
        :param version: OPENWOWI version. Defaults to the newest at the time of writing
        :type version: str
        :param logger: Logger Object
        :type logger: Logger
        """
        requests_cache.install_cache(backend='memory', expire_after=10800)
        if user_agent is None:
            self.user_agent = requests.utils.default_headers().get('User-Agent')
        else:
            self.user_agent = user_agent
        self._logger = logger or logging.getLogger(__name__)
        self.host_base = hostname
        self.url = f"https://{hostname}/openwowi/{version}/"
        self.user = user
        self.password = password
        self.api_key = api_key
        if len(hostname) > 0:
            self.token = self._create_token()

    def _create_token(self):
        full_url = f"https://{self.host_base}/oauth2/token"
        payload = f"grant_type=password&" \
                  f"username={self.user}&" \
                  f"password={self.password}"
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/plain',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", full_url, headers=headers, data=payload)

        if response.status_code != 200:
            errmsg = f"OPEN WOWI Auth Error. Status {response.status_code}:{response.text}"
            self.logger.error(errmsg)
            raise ConnectionError(errmsg)

        response_json = response.json()
        return response_json["access_token"]

    def get(self, endpoint: str, ep_params: Dict = None, force_refresh: bool = False) -> Result:
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params, force_refresh=force_refresh)

    def post(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        return self._do(http_method='POST', endpoint=endpoint, ep_params=ep_params, data=data)

    def delete(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        return self._do(http_method='DELETE', endpoint=endpoint, ep_params=ep_params, data=data)

    def _do(self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None,
            force_refresh: bool = False) -> Result:
        if ep_params is None:
            ep_params = {}

        if http_method.upper() == "GET":
            if "limit" not in ep_params.keys():
                ep_params["limit"] = 100

            if ep_params.get("limit") > 100 or ep_params.get("limit") < 1:
                raise WowiPyException("Wert für limit muss zwischen 1 und 100 liegen")
        ep_params["apiKey"] = self.api_key

        full_url = self.url + endpoint
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.token}'
        }
        log_line_pre = f"method={http_method}, url={full_url}"
        log_line_post = ', '.join((log_line_pre, "success={}, status_code={}, message={}, text={}"))
        response = None
        for _ in range(2):
            try:
                self._logger.debug(msg=log_line_pre)
                if force_refresh:
                    with requests_cache.disabled():
                        response = requests.request(method=http_method, url=full_url, headers=headers, params=ep_params,
                                                    json=data)
                else:
                    response = requests.request(method=http_method, url=full_url, headers=headers, params=ep_params,
                                                json=data)
            except requests.exceptions.RequestException as e:
                self._logger.error(msg=(str(e)))
                raise WowiPyException("Request failed") from e

            if 200 <= response.status_code < 300:
                break
            elif response.status_code == 401:
                self.token = self._create_token()
                headers['Authorization'] = f'Bearer {self.token}'
                continue

        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            self._logger.error(msg=log_line_post.format(False, None, f"{e} Response: {response.text}"))
            raise WowiPyException("Bad JSON in response") from e

        is_success = 200 <= response.status_code <= 299
        log_line = log_line_post.format(is_success, response.status_code, response.reason, response.text)
        if is_success:
            self._logger.debug(msg=log_line)
            return Result(response.status_code, message=response.reason, data=data_out)
        self._logger.error(msg=log_line)
        raise WowiPyException(f"{response.status_code}: {response.reason} -> {response.text}")
