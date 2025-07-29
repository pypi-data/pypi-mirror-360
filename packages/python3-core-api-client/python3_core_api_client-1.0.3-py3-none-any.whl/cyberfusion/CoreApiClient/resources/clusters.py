from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class Clusters(Resource):
    def get_common_properties(
        self,
    ) -> models.ClustersCommonProperties:
        return models.ClustersCommonProperties.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                "/api/v1/clusters/common-properties",
                data=None,
                query_parameters={},
            ).json
        )

    def create_cluster(
        self,
        request: models.ClusterCreateRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/clusters",
                data=request.dict(),
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def list_clusters(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.ClusterResource]:
        return [
            models.ClusterResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/clusters",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_cluster(
        self,
        *,
        id_: int,
    ) -> models.ClusterResource:
        return models.ClusterResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/clusters/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_cluster(
        self,
        request: models.ClusterUpdateRequest,
        *,
        id_: int,
    ) -> models.ClusterResource:
        return models.ClusterResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/clusters/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_cluster(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/clusters/{id_}", data=None, query_parameters={}
            ).json
        )

    def get_borg_ssh_key(
        self,
        *,
        id_: int,
    ) -> models.ClusterBorgSSHKey:
        return models.ClusterBorgSSHKey.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/clusters/{id_}/borg-ssh-key",
                data=None,
                query_parameters={},
            ).json
        )

    def list_ip_addresses_for_cluster(
        self,
        *,
        id_: int,
    ) -> models.ClusterIPAddresses:
        return models.ClusterIPAddresses.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/clusters/{id_}/ip-addresses",
                data=None,
                query_parameters={},
            ).json
        )

    def create_ip_address_for_cluster(
        self,
        request: models.ClusterIPAddressCreateRequest,
        *,
        id_: int,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/clusters/{id_}/ip-addresses",
                data=request.dict(),
                query_parameters={},
            ).json
        )

    def delete_ip_address_for_cluster(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/clusters/{id_}/ip-addresses/{ip_address}",
                data=None,
                query_parameters={},
            ).json
        )

    def enable_l3_ddos_protection_for_ip_address(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/clusters/{id_}/ip-addresses/{ip_address}/l3-ddos-protection",
                data=None,
                query_parameters={},
            ).json
        )

    def disable_l3_ddos_protection_for_ip_address(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/clusters/{id_}/ip-addresses/{ip_address}/l3-ddos-protection",
                data=None,
                query_parameters={},
            ).json
        )

    def get_ip_addresses_products_for_clusters(
        self,
    ) -> list[models.IPAddressProduct]:
        return [
            models.IPAddressProduct.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/clusters/ip-addresses/products",
                data=None,
                query_parameters={},
            ).json
        ]

    def list_cluster_deployments_results(
        self,
        *,
        id_: int,
        get_non_running: Optional[bool] = None,
    ) -> models.ClusterDeploymentResults:
        return models.ClusterDeploymentResults.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/clusters/{id_}/deployments-results",
                data=None,
                query_parameters={
                    "get_non_running": get_non_running,
                },
            ).json
        )

    def list_unix_users_home_directory_usages(
        self,
        *,
        cluster_id: int,
        timestamp: str,
        time_unit: Optional[models.UNIXUsersHomeDirectoryUsageResource] = None,
    ) -> list[models.UNIXUsersHomeDirectoryUsageResource]:
        return [
            models.UNIXUsersHomeDirectoryUsageResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/clusters/unix-users-home-directories/usages/{cluster_id}",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "time_unit": time_unit,
                },
            ).json
        ]
