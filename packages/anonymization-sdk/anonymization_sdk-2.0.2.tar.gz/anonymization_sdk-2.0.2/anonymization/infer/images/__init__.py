import os
import json
import wget
from typing import Any, Dict, List, Optional
from pydantic import Field
import anonymization.client
import anonymization
from anonymization.exceptions import InvalidIdError
from anonymization.basemodel import AnonymizationBase, MixinConfig
from urllib.parse import urlparse, parse_qs
from enum import Enum
from pydantic import conint

class ImageResolution(MixinConfig):
    height: Optional[int]
    width: Optional[int]


class ImageTaskStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"
    RETRY = "RETRY"
    HOLD = "HOLD"

class _BaseStatus(MixinConfig):
    status: ImageTaskStatus
    start_time: float
    end_time: float
    error: Optional[str] = None


class _InferenceStatus(_BaseStatus):
    progress: float

class _ReviewStatus(_BaseStatus):
    progress: float
class _DownloadStatus(_BaseStatus):
    pass

class _ImageStatus(MixinConfig):
    download: _DownloadStatus
    inference: _InferenceStatus
    # review: _ReviewStatus


class Image(AnonymizationBase):
    image_id: str
    image_url: str
    name: str
    owner_id: str
    inferred_url: str
    parent_folder_id: Optional[str]
    ancestor_folder_ids: List[str] = []
    resolution: ImageResolution = Field(default_factory=ImageResolution)  # type: ignore
    status: _ImageStatus
    toggle_hairblur: bool
    log_file: Optional[str]
    organization_id:str
    project_id:str
    
    @classmethod
    def create(
        cls,
        image_url: str,
        name: str,
        height: int,
        width: int,
        project_id:str,
        organization_id:str,
        client: "anonymization.client.BaseClient",
        parent_folder_id: Optional[str] = None,
        toggle_hairblur=False,

    )-> "Image":
        json = dict(
            batch=True,
            data = [
                dict(
                    displayed=True,
                    imageUrl=image_url,
                    name=name,
                    # ownerId='64b12904cfd05a00127c7b20',#remove
                    resolution=dict(
                        height=height,
                        width=width
                    ),
                    toggleHairblur=toggle_hairblur,
                    parentFolderId=parent_folder_id,
                    projectId=project_id,
                    organizationId=organization_id
                )
            ],
            # userId='64b12904cfd05a00127c7b20'
        )
            
        resp = client.post('/images', json=json)
        return cls(**resp.json()['data'][0], client=client)

    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "anonymization.client.BaseClient"
    ) -> List["Image"]:
        resp = client.get("/images", params=params)
        images = resp.json()["data"]["images"]
        images = [cls(**image, client=client) for image in images]
        return images  # type: ignore

    @classmethod
    def from_image_id(
        cls, image_id: str, client: "anonymization.client.BaseClient"
    ) -> "Image":
        image = cls.from_search_params({"imageId": image_id}, client=client)
        if not len(image):
            raise InvalidIdError(f"Failed to fetch image with imageId: {image_id}")
        return image[0]
    
    @classmethod
    def from_folder_id(
        cls, folder_id: str, client: "anonymization.client.BaseClient"
    ) -> List["Image"]:
        images = cls.from_search_params({"folderId": folder_id}, client=client)
        if not len(images):
            raise InvalidIdError(f"Failed to fetch image with folderId: {folder_id}")
        return images
    
    @property
    def infer(
        self
    ):
        """Send image for Inference"""
        data = {}
        data['imageId'] = self.image_id
        resp = self.client.post("/images/infer",data)
        print(resp.status_code)
        if resp.status_code == 200:
            return True
        return False
        
    def update_status(self, inference_status:Optional[_InferenceStatus]=None, download_status:Optional[_DownloadStatus]=None) -> "Image": # type: ignore
        """update status of the video and return new video object from it
        Returns:
            Image: New Image object of returned data
        """
        data={"status":{}}
        if inference_status:
            data['status']['inference'] = json.loads(inference_status.json())
        if download_status:
            data['status']['download'] = json.loads(download_status.json()) 
        # print(data)
        # if status is not None:
        #     data["status"] = json.loads(status.json())
        if not data['status']:
            raise ValueError("No valid arguments passed to update. All args are None.")
        data["imageId"] = self.image_id
        updated_task = self.client.put("/images/status", json=data).json()["data"]
        for key, val in updated_task.items():
            if key in self.__fields__:
                setattr(self, key, val)
        return self
    
    
    # def update_metadata(self, data: Dict[str, Any]) -> "Video":
    #     """Update metadata of this video and return new Video object from it
    #     Since update might not work for all fields, do check in the returned
    #     Video object if the desired change has taken effect.

    #     Returns:
    #         Video: New Video object of the returned data
    #     """
    #     data["videoId"] = self.video_id
    #     res = self.client.put("/videos/metadata", json=data)
    #     video = res.json()["data"]
    #     return Video(**video)
