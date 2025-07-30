from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
import os
import sys
import requests
from typing import Literal, Optional, Union, Any
from fastmcp.exceptions import ToolError
from fastmcp import Context
from ac_mcp_server.types import (
    ContactCreateParams,
    ContactTagParams,
    TagCreateParams,
    ContactCustomFieldCreateParams,
    FieldOptionBulkCreateParams,
    ContactFieldRelCreateParams,
    ContactStatus,
    ContactListParams,
    TagListParams,
    ContactCustomFieldListParams,
    ContactFieldValueCreateParams,
    ContactFieldValueUpdateParams,
    ContactFieldValueListParams,
    EmailActivityListParams,
    CampaignListParams,
    AutomationListParams,
    ContactAutomationListParams,
    ContactAutomationCreateParams,
    GroupListParams,
    ListListParams,
    ListCreateParams,
    ListGroupPermissionParams,
    ContactListUpdateParams,
    ListUpdateParams,
)
from ac_mcp_server.utils import get_package_info
from pydantic import BaseModel


@dataclass
class ACMCPHttpClientAuth:
    url: str
    header_name: str
    header_value: str


class ACMCPHttpClient:

    headers: dict[str, str] = {}
    base_url: str

    def __init__(
        self,
        auth: ACMCPHttpClientAuth,
    ):
        self.base_url = auth.url

        PACKAGE_NAME, PACKAGE_VERSION = get_package_info()
        self.headers = {
            "User-Agent": f"{PACKAGE_NAME}-{PACKAGE_VERSION}",
            auth.header_name: auth.header_value,
        }

    def _generate_query_param_value(self, value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        return value

    def _generate_query_params(self, params: BaseModel) -> dict[str, Any]:
        query_params = {}
        param_dict = params.model_dump(exclude_none=True, by_alias=True)
        for key, value in param_dict.items():
            if isinstance(value, dict):
                for dict_key, dict_value in value.items():
                    if isinstance(dict_value, dict):
                        for nested_key, nested_value in dict_value.items():
                            query_params[f"{key}[{dict_key}][{nested_key}]"] = (
                                self._generate_query_param_value(nested_value)
                            )
                    else:
                        query_params[f"{key}[{dict_key}]"] = (
                            self._generate_query_param_value(dict_value)
                        )
            else:
                query_params[key] = self._generate_query_param_value(value)
        return query_params

    def call_ac_api(
        self,
        endpoint: str,
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        data: dict[str, Any] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        try:
            if data:
                response = requests.request(
                    method, url, headers=self.headers, json=data, params=params
                )
            else:
                response = requests.request(
                    method, url, headers=self.headers, params=params
                )

            response.raise_for_status()

            try:
                return response.json()
            except ValueError:
                raise ToolError(
                    f"Invalid JSON response from ActiveCampaign API at {endpoint}. "
                    f"The server returned malformed data. Response content: {response.text[:200]}"
                )
        except requests.exceptions.ConnectionError:
            raise ToolError(
                f"Failed to connect to ActiveCampaign API at {url}. Please check your network connection and API URL."
            )
        except requests.exceptions.Timeout:
            raise ToolError(
                f"Request to ActiveCampaign API timed out. The server might be experiencing high load."
            )
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
            try:
                error_message = str(err.response.json())
            except ValueError:
                error_message = str(err)

            if status_code == 401:
                raise ToolError(
                    "Authentication failed. Please check your ActiveCampaign API token."
                )
            elif status_code == 403:
                raise ToolError(
                    "Access forbidden. Your API token doesn't have permission to perform this action."
                )
            elif status_code == 404:
                raise ToolError(
                    f"Resource not found at {endpoint}. Please check the endpoint path."
                )
            elif status_code == 429:
                raise ToolError("Rate limit exceeded. Please try again later.")
            elif 400 <= status_code < 500:
                raise ToolError(f"Client error: {error_message}")
            elif 500 <= status_code < 600:
                raise ToolError(
                    f"Server error: {error_message}. The ActiveCampaign server might be experiencing issues."
                )
            else:
                raise ToolError(f"HTTP error: {error_message}")
        except Exception as e:
            raise ToolError(
                f"Unexpected error when calling ActiveCampaign API: {str(e)}"
            )

    def list_contacts(self, filters: ContactListParams) -> dict[str, Any]:
        query_params = self._generate_query_params(filters)
        return self.call_ac_api("/api/3/contacts", params=query_params)

    def get_contact(self, contact_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/contacts/{contact_id}")

    def create_or_update_contact(self, params: ContactCreateParams) -> dict[str, Any]:
        data = {"contact": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/contact/sync", method="POST", data=data)

    def list_tags(self, params: TagListParams) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/tags", params=query_params)

    def get_tag(self, tag_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/tags/{tag_id}")

    def create_contact_tag(self, params: TagCreateParams) -> dict[str, Any]:
        data = {"tag": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/tags", method="POST", data=data)

    def add_tag_to_contact(self, params: ContactTagParams) -> dict[str, Any]:
        data = {"contactTag": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/contactTags", method="POST", data=data)

    def list_contact_custom_fields(
        self,
        params: ContactCustomFieldListParams,
    ) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/fields", params=query_params)

    def get_contact_custom_field(self, field_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/fields/{field_id}")

    def create_contact_custom_field(
        self,
        params: ContactCustomFieldCreateParams,
    ) -> dict[str, Any]:
        data = {"field": params.model_dump(exclude_none=True)}
        custom_field = self.call_ac_api("/api/3/fields", method="POST", data=data)
        # Always associate custom fields with the relid 0 to associate it with all lists
        # without this it is not visible in the UI
        self.create_contact_field_relationship(
            ContactFieldRelCreateParams(relid=0, field=custom_field["field"]["id"])
        )
        return custom_field

    def create_field_options(
        self, params: FieldOptionBulkCreateParams
    ) -> dict[str, Any]:
        field_options = [
            option.model_dump(exclude_none=True) for option in params.fieldOptions
        ]
        data = {"fieldOptions": field_options}
        return self.call_ac_api("/api/3/fieldOptions/bulk", method="POST", data=data)

    def create_contact_field_relationship(
        self,
        params: ContactFieldRelCreateParams,
    ) -> dict[str, Any]:
        data = {"fieldRel": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/fieldRels", method="POST", data=data)

    def list_contact_field_values(
        self,
        params: ContactFieldValueListParams,
    ) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/fieldValues", params=query_params)

    def get_contact_field_value(self, field_value_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/fieldValues/{field_value_id}")

    def create_contact_field_value(
        self,
        params: ContactFieldValueCreateParams,
    ) -> dict[str, Any]:
        data = {"fieldValue": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/fieldValues", method="POST", data=data)

    def update_contact_field_value(
        self, field_value_id: int, params: ContactFieldValueUpdateParams
    ) -> dict[str, Any]:
        data = {"fieldValue": params.model_dump(exclude_none=True)}
        return self.call_ac_api(
            f"/api/3/fieldValues/{field_value_id}", method="PUT", data=data
        )

    def list_email_activities(self, params: EmailActivityListParams) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/emailActivities", params=query_params)

    def list_campaigns(self, params: CampaignListParams) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/campaigns", params=query_params)

    def get_campaign(self, campaign_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/campaigns/{campaign_id}")

    def get_campaign_links(self, campaign_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/campaigns/{campaign_id}/links")

    def list_automations(self, params: AutomationListParams) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/automations", params=query_params)

    def list_contact_automations(
        self,
        params: ContactAutomationListParams,
    ) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/contactAutomations", params=query_params)

    def get_contact_automation(self, contact_automation_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/contactAutomations/{contact_automation_id}")

    def add_contact_to_automation(
        self,
        params: ContactAutomationCreateParams,
    ) -> dict[str, Any]:
        data = {"contactAutomation": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/contactAutomations", method="POST", data=data)

    def remove_contact_from_automation(
        self, contact_automation_id: int
    ) -> dict[str, Any]:
        return self.call_ac_api(
            f"/api/3/contactAutomations/{contact_automation_id}", method="DELETE"
        )

    def list_groups(self, params: GroupListParams) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/groups", params=query_params)

    def list_lists(self, params: ListListParams) -> dict[str, Any]:
        query_params = self._generate_query_params(params)
        return self.call_ac_api("/api/3/lists", params=query_params)

    def get_list(self, list_id: int) -> dict[str, Any]:
        return self.call_ac_api(f"/api/3/lists/{list_id}")

    def create_list(self, params: ListCreateParams) -> dict[str, Any]:
        data = {"list": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/lists", method="POST", data=data)

    def update_list(self, list_id: int, params: ListUpdateParams) -> dict[str, Any]:
        data = {"list": params.model_dump(exclude_none=True)}
        return self.call_ac_api(f"/api/3/lists/{list_id}", method="PUT", data=data)

    def create_list_group_permission(
        self,
        params: ListGroupPermissionParams,
    ) -> dict[str, Any]:
        data = {"listGroup": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/listGroups", method="POST", data=data)

    def add_contact_to_list(self, params: ContactListUpdateParams) -> dict[str, Any]:
        data = {"contactList": params.model_dump(exclude_none=True)}
        return self.call_ac_api("/api/3/contactLists", method="POST", data=data)
