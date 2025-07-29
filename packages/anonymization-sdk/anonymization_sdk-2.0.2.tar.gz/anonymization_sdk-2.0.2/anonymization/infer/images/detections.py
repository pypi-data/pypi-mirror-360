from enum import Enum
from typing import Any, List, Optional, Dict
from pydantic import Field, root_validator
from anonymization.basemodel import AnonymizationBase
from anonymization.exceptions import InvalidIdError
import anonymization
import anonymization.client
from anonymization.types.bounding_box import BoundingBox

class DetectionType(Enum):
    BOUNDING_BOX = "image_bounding_box"

class Detection(AnonymizationBase):
    is_reviewed: Optional[bool]
    type: DetectionType
    bounding_box: Optional[BoundingBox]
    detection_id: Optional[str] = None  # SO user creating Detection to insert doesn't has detectionId
    # These 2 are optional since they are skipped when detections are implicitly added to images.detections
    image_id: Optional[str]
    track_id:Optional[str]
    probability:Optional[float]
    label:Optional[str]

    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "anonymization.client.BaseClient"
    ) -> List["Detection"]:
        """Make a get request for detections using the passed params. This
        is a private method used internally by other class methods

        Returns:
            List[Detection]: Returns a list of Detection objects
        """
        detections = []
        if 'limit' in params and params['limit'] == -1:
            page = 1
            limit = 500
            while True:
                params['limit'] = limit
                params['page'] = page
                resp = client.get("/images/detections", params=params)
                data = resp.json()["data"]["detections"]
                if not len(data):
                    break
                detections.extend(data)
                page += 1
        else:
            resp = client.get("/images/detections", params=params)
            detections = resp.json()["data"]["detections"]
        # don't check for empty list in this generic class method. returns empty list if no detections were found
        detections = [cls(**det, client=client) for det in detections]
        return detections #type: ignore

    @classmethod
    def from_detection_id(cls, detection_id: str, client: "anonymization.client.BaseClient"):
        """Get the Detection object for a certail detection_id

        Args:
            detection_id (str): detection Id to search for
            client (deeplabel.client.BaseClient): client to call the api from

        Raises:
            InvalidIdError: If no detections are returned, raise InvalidIdError

        Returns:
            Detection: returns a Detection object or raises InvalidIdError if not found
        """
        detections = cls.from_search_params({"detectionId": detection_id}, client)
        if not len(detections):
            raise InvalidIdError(
                f"Failed to fetch detections with detectionId  : {detection_id}"
            )
        # since detectionId should fetch only 1 detection, return that detection instead of a list
        return detections[0]

    @classmethod
    def from_image_id_and_project_id(
        cls, image_id: str, project_id: str, client: "anonymization.client.BaseClient"
    ) -> List["Detection"]:
        """Get all the detection of a imageTaskId

        Returns:
            List[Detection]: List of detections for the given imageTaskId
        """
        return cls.from_search_params({"imageId": image_id, "projectId": project_id, 'limit':'-1'}, client)