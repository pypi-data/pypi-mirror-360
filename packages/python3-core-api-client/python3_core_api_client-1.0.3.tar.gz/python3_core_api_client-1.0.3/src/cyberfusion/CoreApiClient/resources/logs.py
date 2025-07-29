from cyberfusion.CoreApiClient import models
from typing import Optional

from cyberfusion.CoreApiClient.interfaces import Resource


class Logs(Resource):
    def list_access_logs(
        self,
        *,
        virtual_host_id: int,
        timestamp: Optional[str] = None,
        sort: Optional[models.LogAccessResource] = None,
        limit: Optional[int] = None,
    ) -> list[models.LogAccessResource]:
        return [
            models.LogAccessResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/logs/access/{virtual_host_id}",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "sort": sort,
                    "limit": limit,
                },
            ).json
        ]

    def list_error_logs(
        self,
        *,
        virtual_host_id: int,
        timestamp: Optional[str] = None,
        sort: Optional[models.LogErrorResource] = None,
        limit: Optional[int] = None,
    ) -> list[models.LogErrorResource]:
        return [
            models.LogErrorResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/logs/error/{virtual_host_id}",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "sort": sort,
                    "limit": limit,
                },
            ).json
        ]
