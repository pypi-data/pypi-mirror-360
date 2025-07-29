from typing import Any, List
from logging import getLogger
import traceback
from pydantic import Field
import anonymization.client
from anonymization.exceptions import InvalidCredentials
import anonymization.basemodel
from anonymization.basemodel import BaseModel, AnonymizationBase
from typing import Dict

logger = getLogger(__name__)


class _UserEmail(BaseModel):
   verified: bool
   value: str 

class UserAnnotation(AnonymizationBase):
    """A custom User Subclass i.e., one that has only limited keys compared to 
    User from deeplabel.auth.users with only `email` and `user_id` keys.
    """

    email: _UserEmail
    user_id: str

class UserToken(anonymization.basemodel.AnonymizationBase):

    user: UserAnnotation = Field(None, alias='userId')
    hash: str
    expiry: str
    name: str
    tokenId: str

    @classmethod
    def from_root_secret_key(
        cls, root_secret_key: str, client: "anonymization.client.BaseClient"
    ):
        # Use client session so that non-default headers can be passed
        params = params={"name": "DEFAULT_TOKEN"}
        resp = client.session.get(
            client.infer_url.rstrip('/')+"/users/tokens",
            params=params,
            headers={"Authorization": f"Bearer {root_secret_key}"},
        )
        if resp.status_code > 200:
            logger.error(f"Couldn't fetch Token with params {params} and rsk: {root_secret_key}")
            logger.debug(traceback.format_exc())
            raise InvalidCredentials(f"failed fetching Tokens with rsk {root_secret_key}")
        return [cls(**token) for token in resp.json()["data"]["tokens"]][0]

    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "anonymization.client.BaseClient") -> List["UserToken"]:
        resp = client.get(
            client.infer_url + "/users/tokens", params=params
        )
        if resp.status_code > 200:
            logger.error(f"Couldn't fetch Token with params {params}")
            logger.debug(traceback.format_exc())
            raise InvalidCredentials(f"failed fetching Tokens with params {params}")
        return [cls(**token) for token in resp.json()["data"]["tokens"]]
