import re
import dataclasses  # type: ignore
from dataclasses import InitVar
from typing import Any, Dict, Optional, Union
import inspect
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from logging import getLogger

from anonymization.exceptions import InvalidAPIResponse
logger = getLogger(__name__)

@dataclasses.dataclass
class _MixinLogin:
    username: InitVar[str]
    password: InitVar[str]


@dataclasses.dataclass
class _MixinToken:
    token: str

@dataclasses.dataclass
class BaseClient:
    infer_url: str = 'https://anonymize.streamingo.ai/blur'
    owner_id: Optional[str] = None
    restriction: Union[bool, str] = True

    def __post_init__(self):
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        session.mount("http://", HTTPAdapter(max_retries=retry))
        session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session = session
        self.infer_url = self.infer_url.rstrip('/')

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}  # type: ignore

    def post(self, url: str, json: Dict[str, Any], headers:Optional[Dict[str, str]]=None):
        if not url.startswith("http"):
            url = self._get_url_by_caller(url)
        if self.restriction in ["false",False]:
            json["openRestriction"] = "true"
        json["sessionRestriction"] = "false"
        response = self.session.post(
            url, json=json, headers={**self.headers, **(headers if isinstance(headers, dict) else {})})
        if response.status_code > 300:
            logger.error(f"{response.status_code}  {url} failed. {response.text} ; data:{json}")
            raise InvalidAPIResponse(f"{response.status_code}  {url} {json} {response.text}")
        return response

    def _get_url_by_caller(self, suffix: str):
        """When client's get/post/put url is called, the passed suffix must me
        added to either label_url or infer_url. In order to determine which of
        these two should be the base url, use inspect.stack() to get the caller
        function's path and determine it.

        This func is generally called inside client's get/put/post methods which
        are called by the caller method in question. Hence callstack would be
        this_func -> get/post/put -> caller
        """
        caller_filename = inspect.stack()[2][1]  # 1 is for filename
        return self.infer_url + suffix
      

    def get(
        self,
        url: str,
        params: Dict[str, Any],
        headers: Optional[Dict[str,str]] = None
    ):
        """Get a anonymization get api

        Args:
            url (str): url to get. can be a suffix like /videos or full url
            params (Dict[str,Any]): query parameters

        Raises:
            InvalidAPIResponse: If the response code is > 200

        Returns:
            Response: requests.Response object
        """
        if self.restriction in ["false",False]:
            params["openRestriction"] = "true"
        params["sessionRestriction"] = "false"
        if not url.startswith("http"):
            url = self._get_url_by_caller(url)
        logger.debug(f"Fetching {url} params: {params}")
        response = self.session.get(
            url, params=params, headers={**self.headers, **(headers if isinstance(headers, dict) else {})})
        if response.status_code > 202:
            logger.error(f"{response.status_code}  {url} {params} failed. {response.text}")
            raise InvalidAPIResponse(f"{response.status_code} {url} {params} {response.text}")
        logger.debug(f"Received Response {response.text}")
        return response

    def put(self, url: str, json: Dict[str, Any], headers:Optional[Dict[str,str]]=None):
        if not url.startswith("http"):
            url = self._get_url_by_caller(url)
        if self.restriction in ["false",False]:
            json["openRestriction"] = "true"
        json["sessionRestriction"] = "false"
        response = self.session.put(url, json=json, headers={**self.headers, **(headers if isinstance(headers, dict) else {})})
        if response.status_code > 202:
            logger.error(f"{response.status_code}  {url} {json} failed. {response.text}")
            raise InvalidAPIResponse(f"{response.status_code}  {url} {json} {response.text}")
        return response
    
    def delete(self, url: str, json: Dict[str, Any], headers:Optional[Dict[str,str]]=None):
        if not url.startswith("http"):
            url = self._get_url_by_caller(url)
        if self.restriction in ["false",False]:
            json["openRestriction"] = "true"
        json["sessionRestriction"] = "false"
        response = self.session.delete(url, json=json, headers={**self.headers, **(headers if isinstance(headers, dict) else {})})
        if response.status_code > 202:
            logger.error(f"{response.status_code}  {url} {json} failed. {response.text}")
            raise InvalidAPIResponse(f"{response.status_code}  {url} {json} {response.text}")
        return response

@dataclasses.dataclass
class AnonymizationClient(BaseClient, _MixinToken):
    ...


@dataclasses.dataclass
class AnonymizationLoginClient(BaseClient, _MixinLogin):
    def __post_init__(self, email: str, password: str):  # type: ignore
        import anonymization.auth as auth
        # Get Session
        super().__post_init__()
        # Get user and token
        user: auth.users.User = auth.users.User.from_login(email, password, self)
        assert user.root_secret_key, f"No root secret key found in user"
        token = auth.tokens.UserToken.from_root_secret_key(user.root_secret_key, self)
        self.token = token.hash
