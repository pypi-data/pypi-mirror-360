from typing import Union

import requests

from ..util.cheapdantic import BaseModel
from .http_client import OdpHttpClient
from odp.client.exc import OdpUnauthorizedError
from odp.dto.catalog.dataset import DatasetDto
from odp.dto.resource import ResourceDto


class OdpIamClient(BaseModel):
    http_client: OdpHttpClient

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def share_with_hubocean_internal(self, ref: Union[ResourceDto, DatasetDto]) -> str:
        """Share a resource with HubOcean Internal group as editor.

        Args:
            ref: Resource reference
            subject_id: Subject ID
            role: Role to assign to the subject
        """
        if not (isinstance(ref, ResourceDto) or isinstance(ref, DatasetDto)):
            raise ValueError("ref is not of type ResourceDto")

        role = "2"  # Editor
        subject_id = "0ee75a5a-6fcc-47db-8d0c-8f61f0641126"  # HubOcean Internal group ID
        params = {
            "object": {"id": str(ref.metadata.uuid), "kind": str(ref.get_kind())},
            "role": role,
            "subject": {"id": subject_id, "type": "group"},
        }
        path = "/api/permissions/v1/resources/relationships/"
        res = self.http_client.post(f"{path}", content=params)

        try:
            res.raise_for_status()
        except requests.HTTPError:
            if res.status_code == 409:
                return "The resource is already shared with HubOcean Internal group"
            elif res.status_code == 401:
                raise OdpUnauthorizedError("Unauthorized access")
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")
        return "Success"
