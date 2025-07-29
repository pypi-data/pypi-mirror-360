from typing import Any, Dict, List, Optional
from anonymization.exceptions import InvalidIdError
from anonymization.basemodel import AnonymizationBase, MixinConfig
import anonymization.client
import anonymization


class _ProjectProgress(MixinConfig):
    total: int
    completed: int


class _ProjectOwner(MixinConfig):
    name: str
    user_id: str


class Project(AnonymizationBase):
    project_id: str
    title: str
    description: Optional[str]
    organization_id: str
    progress: Optional[_ProjectProgress]
    owner_name: str
    owner_email:str
    is_archive: Optional[bool]
    bucket_policy: int

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "anonymization.client.BaseClient"
    ) -> List["Project"]:
        resp = client.get(client.infer_url+ "/projects", params)
        projects = resp.json()["data"]["projects"]
        projects = [cls(**project, client=client) for project in projects]
        return projects

    @classmethod
    def from_project_id(
        cls, project_id: str, client: "anonymization.client.BaseClient"
    ) -> "Project":
        projects = cls._from_search_params({"projectId": project_id}, client)
        if not projects:
            raise InvalidIdError(f"No Project found with projectId: {project_id}")
        return projects[0]

    # @property
    # def image_datasets(self):
    #     return anonymization.label.folders.RootFolder(
    #         project_id=self.project_id,
    #         type=anonymization.label.folders.FolderType.GALLERY,
    #         client=self.client
    #     )

    # @property
    # def video_datasets(self):
    #     return anonymization.label.folders.RootFolder(
    #         project_id=self.project_id,
    #         type=anonymization.label.folders.FolderType.VIDEO,
    #         client=self.client
    #     )
    
    # @property
    # def label_map(self)->List["anonymization.label.label_maps.LabelMap"]:
    #     return anonymization.label.label_maps.LabelMap.from_search_params({'projectId':self.project_id}, self.client)
