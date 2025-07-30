# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import json

from forge.api.utils import fetch_paginated_list
from ngcbase.util.utils import format_org_team

PAGE_SIZE = 100


class MachineAPI:  # noqa: D101
    def __init__(self, api_client):
        self.connection = api_client.connection
        self.client = api_client

    @staticmethod
    def _get_machine_endpoint(org_name=None, _team_name=None):
        # Forge doesn't have teams currently. Drop the 'team' part.
        org_team = format_org_team(org_name, None, plural_form=False)
        return "/".join(["v2", org_team, "forge", "machine"])

    def list(self, org_name, team_name, site, assigned, status):  # noqa: D102
        ep = self._get_machine_endpoint(org_name, team_name)
        params = []
        if site:
            params.append(f"siteId={site}")
        if assigned:
            params.append(f"hasInstanceType={assigned}")
        if status:
            params.append(f"status={status}")
        params.append("includeRelation=InfrastructureProvider")
        params.append("includeRelation=Site")
        params.append("includeRelation=InstanceType")
        params.append("orderBy=CREATED_ASC")
        params.append(f"pageSize={PAGE_SIZE}")
        query = "?".join([ep, "&".join(params)])
        return fetch_paginated_list(self.connection, query, org=org_name, operation_name="list_machine")

    def info(self, org_name, team_name, machine):  # noqa: D102
        ep = self._get_machine_endpoint(org_name, team_name)
        params = []
        params.append("includeRelation=InfrastructureProvider")
        params.append("includeRelation=Site")
        params.append("includeRelation=InstanceType")
        url = f"{ep}/{machine}"
        query = "?".join([url, "&".join(params)])
        resp = self.connection.make_api_request(
            "GET", query, auth_org=org_name, auth_team=team_name, operation_name="info_instance_type"
        )
        return resp

    def update(  # noqa: D102
        self,
        org_name,
        team_name,
        machine,
        instance_type=None,
        clear_instance_type=None,
        maintenance_mode=None,
        maintenance_message=None,
    ):
        if instance_type and clear_instance_type:
            raise TypeError("'instance_type' cannot be specified with 'clear_instance_type'.")
        ep = self._get_machine_endpoint(org_name, team_name)
        url = f"{ep}/{machine}"
        update_obj = {}
        if clear_instance_type:
            update_obj["clearInstanceType"] = clear_instance_type
        else:
            update_obj["instanceTypeId"] = instance_type
        update_obj["setMaintenanceMode"] = maintenance_mode
        update_obj["maintenanceMessage"] = maintenance_message
        resp = self.connection.make_api_request(
            "PATCH",
            url,
            auth_org=org_name,
            auth_team=team_name,
            payload=json.dumps(update_obj),
            operation_name="update_machine",
        )
        return resp


class GuestMachineAPI(MachineAPI):  # noqa: D101
    pass
