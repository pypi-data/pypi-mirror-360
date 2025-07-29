from logging import getLogger

import anonymization.client
from anonymization.exceptions import InvalidCredentials, InvalidIdError
import anonymization.basemodel
from pydantic import BaseModel
from typing import Optional
from anonymization.utils import encryption

logger = getLogger(__name__)

class _UserEmail(BaseModel):
   verified: bool
   value: str 

class User(anonymization.basemodel.AnonymizationBase):
    """A Login User.
    Raises InvalidCredentials if login failed or not able to fetch rsk or token.
    """

    name: str
    email: _UserEmail
    role: str
    user_id: str
    root_secret_key:Optional[str]

    @classmethod
    def from_login(cls, email: str, password: str, client: "anonymization.client.BaseClient")->"User": #type: ignore
        # encrypt password
        password = encryption.encrypt(password, key='bGnJiPnHUiPlKJUL', iv='bGnJiPnHUiPlKJUL')
        res = client.session.post(
            client.infer_url.rstrip('/')+"/users/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
        )
        if res.status_code > 200:
            raise InvalidCredentials(res.text)
        return cls(**res.json()['data'])
    
    @classmethod
    def from_user_id(cls, user_id:str, client: "anonymization.client.BaseClient") -> "User":
        res = client.get(
            "/users",
            {"userId": user_id},
        )
        if res.status_code > 200:
            raise InvalidIdError(res.text)
        return cls(**res.json()['data']['users'][0])
