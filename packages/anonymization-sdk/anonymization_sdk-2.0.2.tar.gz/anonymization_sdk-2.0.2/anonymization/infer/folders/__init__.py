from typing import Any, Dict, List, Optional
from enum import Enum
from anonymization.exceptions import InvalidIdError
from anonymization.basemodel import AnonymizationBase
import anonymization.infer.videos
import anonymization.infer.images
import anonymization.infer.folders
import anonymization.client
import anonymization
from pydantic import conint, Field

class FolderType(Enum):
    VIDEO = "VIDEO"
    IMAGE = "IMAGE"


class RootFolder(AnonymizationBase):
    type: Optional[FolderType]
    folder_id: Optional[str]
    owner_id: str
    
    @property
    def videos(self) -> List["anonymization.infer.videos.Video"]:
        search_params = {
            "ownerId": self.owner_id,
            "limit": "-1",
        }
        if self.folder_id is not None:
            search_params["parentFolderId"] = self.folder_id
        return anonymization.infer.videos.Video.from_search_params(
            search_params, client=self.client
        )

    @property
    def images(self) -> List["anonymization.infer.images.Image"]:
        search_params = {
            "ownerId": self.owner_id,
            "limit": "-1",
        }
        if self.folder_id is not None:
            search_params["parentFolderId"] = self.folder_id
        return anonymization.infer.images.Image.from_search_params(
            search_params, self.client
        )


class Folder(RootFolder):
    description: Optional[str]
    name: str
    parent_folder_id: Optional[str]
    # ancestor_folder_ids: List[str]
    project_id:str
    organization_id:str
    
    @classmethod
    def create(
        cls,
        name: str,
        owner_id:str,
        project_id:str,
        client: "anonymization.client.BaseClient",
        type: FolderType = FolderType.VIDEO,
        description: str = "",
        parent_folder_id: str = "user",
    ):
        request_data = {
            "ownerId":owner_id,
            "name": name,
            "type": type.value,
            "parentFolderId": parent_folder_id,
            "description": description,
            "projectId": project_id
        }
        resp = client.post("/folders", request_data)
        return cls(**resp.json()["data"], client=client)

    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "anonymization.client.BaseClient"
    ) -> List["Folder"]:
        resp = client.get("/folders", params)
        folders = resp.json()["data"]["folders"]
        folders = [cls(**folder, client=client) for folder in folders]
        return folders  # type: ignore

    @classmethod
    def from_owner_id(
        cls, owner_id: str, client: "anonymization.client.BaseClient"
    ) -> List["Folder"]:
        folders = cls.from_search_params({"ownerId": owner_id}, client)
        return folders

    @classmethod
    def from_folder_id(
        cls, folder_id: str, client: "anonymization.client.BaseClient"
    ) -> "Folder":
        folders = cls.from_search_params({"folderId": folder_id}, client)
        if not folders:
            raise InvalidIdError(f"No Folder found with folderId: {folder_id}")
        return folders[0]
    
    def delete(self) -> bool:
        """ deletes a folder """
        data = {}
        data['folderId'] = self.folder_id
        resp = self.client.delete("/folders", data)
        if resp.status_code == 200:
            return True
        return False