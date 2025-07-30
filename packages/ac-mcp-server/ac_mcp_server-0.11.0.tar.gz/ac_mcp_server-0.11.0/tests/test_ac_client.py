import os
import pytest
import json
import requests
from unittest.mock import patch
import requests_mock
from fastmcp.exceptions import ToolError
from ac_mcp_server.ac_client import ACMCPHttpClient, ACMCPHttpClientAuth
from ac_mcp_server.types import (
    ContactCreateParams,
    TagCreateParams,
    ContactTagParams,
    ContactListParams,
    ContactStatus,
    TagListParams,
    TagOrderMethod,
    ContactCustomFieldListParams,
    ContactCustomFieldCreateParams,
    FieldOptionBulkCreateParams,
    FieldOptionCreateParams,
    ContactFieldRelCreateParams,
    ContactFieldValueListParams,
    ContactFieldValueCreateParams,
    ContactFieldValueUpdateParams,
    EmailActivityListParams,
    CampaignListParams,
    CampaignFilterField,
    AutomationListParams,
    AutomationFilterField,
    ContactAutomationListParams,
    ContactAutomationFilters,
    ContactAutomationDateFilter,
    ContactAutomationCreateParams,
    GroupListParams,
    ListListParams,
    ListCreateParams,
    ListGroupPermissionParams,
    ContactListUpdateParams,
    ListFilters,
    ListUpdateParams,
)
from datetime import date


@pytest.fixture
def ac_client():
    auth = ACMCPHttpClientAuth(
        url="https://test-api.example.com",
        header_name="Api-Token",
        header_value="fake-token",
    )
    return ACMCPHttpClient(auth=auth)


@pytest.fixture(autouse=True)
def mock_package_info():
    with patch(
        "ac_mcp_server.ac_client.get_package_info",
        return_value=("test-package", "1.0.0"),
    ):
        yield


class TestContactFunctions:
    def test_list_contacts_success(self, requests_mock, ac_client):
        mock_response = {
            "contacts": [
                {"id": 1, "email": "contact1@example.com"},
                {"id": 2, "email": "contact2@example.com"},
            ]
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/contacts",
            json=mock_response,
            status_code=200,
        )

        filters = ContactListParams()
        result = ac_client.list_contacts(filters)

        assert result == mock_response
        assert requests_mock.called

        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/contacts"
        )

    def test_list_contacts_with_parameters(self, requests_mock, ac_client):
        mock_response = {"contacts": [{"id": 5, "email": "filtered@example.com"}]}
        requests_mock.get(
            "https://test-api.example.com/api/3/contacts",
            json=mock_response,
            status_code=200,
        )

        test_date = date(2023, 1, 15)

        filters = ContactListParams(
            segmentid=123,
            formid=456,
            listid=789,
            tagid=101,
            limit=25,
            offset=10,
            search="somename",
            orders={"email": "DESC", "first_name": "ASC"},
            filters={"created_after": test_date, "updated_before": "2023-12-31"},
            id_greater=1000,
            seriesid=202,
            waitid=303,
            status=ContactStatus.ACTIVE,
        )
        result = ac_client.list_contacts(filters)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        print(last_request_url)
        assert "segmentid=123" in last_request_url
        assert "formid=456" in last_request_url
        assert "listid=789" in last_request_url
        assert "tagid=101" in last_request_url
        assert "limit=25" in last_request_url
        assert "offset=10" in last_request_url
        assert "search=somename" in last_request_url
        assert "orders%5Bemail%5D=DESC" in last_request_url
        assert "orders%5Bfirst_name%5D=ASC" in last_request_url
        assert f"filters%5Bcreated_after%5D={test_date.isoformat()}" in last_request_url
        assert "filters%5Bupdated_before%5D=2023-12-31" in last_request_url
        assert "id_greater=1000" in last_request_url
        assert "seriesid=202" in last_request_url
        assert "waitid=303" in last_request_url
        assert "status=1" in last_request_url

    def test_get_contact_success(self, requests_mock, ac_client):
        contact_id = 123
        mock_response = {
            "contact": {
                "id": str(contact_id),
                "email": "test@example.com",
                "firstName": "Test",
                "lastName": "User",
            }
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/contacts/{contact_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_contact(contact_id)
        assert result == mock_response
        assert requests_mock.called

    def test_create_or_update_contact_success(self, requests_mock, ac_client):
        mock_response = {
            "contact": {
                "id": "999",
                "email": "new@example.com",
                "firstName": "New",
                "lastName": "Contact",
                "phone": "555-1234",
            },
            "fieldValues": [
                {
                    "contact": "999",
                    "field": "123",
                    "value": "Custom Value 1",
                    "id": "456",
                },
                {"contact": "999", "field": "124", "value": "2023-01-15", "id": "457"},
            ],
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/contact/sync",
            json=mock_response,
            status_code=201,
        )

        params = ContactCreateParams(
            email="new@example.com",
            firstName="New",
            lastName="Contact",
            phone="555-1234",
        )
        result = ac_client.create_or_update_contact(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "contact": {
                "email": "new@example.com",
                "firstName": "New",
                "lastName": "Contact",
                "phone": "555-1234",
            }
        }


class TestTagFunctions:
    def test_list_tags(self, requests_mock, ac_client):
        mock_response = {
            "tags": [
                {
                    "tagType": "contact",
                    "tag": "Lead",
                    "description": "Potential customer",
                    "cdate": "2020-01-01T00:00:00-06:00",
                    "id": "1",
                },
                {
                    "tagType": "contact",
                    "tag": "Customer",
                    "description": "Paying customer",
                    "cdate": "2020-01-01T00:00:00-06:00",
                    "id": "2",
                },
            ]
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/tags",
            json=mock_response,
            status_code=200,
        )

        params = TagListParams()
        result = ac_client.list_tags(params)

        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url == "https://test-api.example.com/api/3/tags"
        )

    def test_list_tags_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "tags": [
                {
                    "tagType": "contact",
                    "tag": "Lead",
                    "description": "Potential customer",
                    "cdate": "2020-01-01T00:00:00-06:00",
                    "id": "1",
                }
            ]
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/tags",
            json=mock_response,
            status_code=200,
        )

        params = TagListParams(
            search_filters={"contains": "Lead"},
            order_method="weight",
            limit=50,
            offset=10,
        )
        result = ac_client.list_tags(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        assert "filters%5Bsearch%5D%5Bcontains%5D=Lead" in last_request_url
        assert "orders%5Bsearch%5D=weight" in last_request_url
        assert "limit=50" in last_request_url
        assert "offset=10" in last_request_url

    def test_get_tag_success(self, requests_mock, ac_client):
        tag_id = 123
        mock_response = {
            "tag": {
                "tagType": "contact",
                "tag": "Lead",
                "description": "Potential customer",
                "cdate": "2020-01-01T00:00:00-06:00",
                "id": str(tag_id),
            }
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/tags/{tag_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_tag(tag_id)
        assert result == mock_response
        assert requests_mock.called

    def test_create_contact_tag_success(self, requests_mock, ac_client):
        mock_response = {
            "tag": {
                "tagType": "contact",
                "tag": "New Tag",
                "description": "Test description",
                "cdate": "2020-01-01T00:00:00-06:00",
                "id": "100",
            }
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/tags",
            json=mock_response,
            status_code=201,
        )

        params = TagCreateParams(tag="New Tag", description="Test description")
        result = ac_client.create_contact_tag(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "tag": {
                "tagType": "contact",
                "tag": "New Tag",
                "description": "Test description",
            }
        }

    def test_add_tag_to_contact_success(self, requests_mock, ac_client):
        mock_response = {
            "contactTag": {
                "contact": "123",
                "tag": "456",
                "cdate": "2020-01-01T00:00:00-06:00",
                "id": "789",
            }
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/contactTags",
            json=mock_response,
            status_code=201,
        )

        params = ContactTagParams(contact=123, tag=456)
        result = ac_client.add_tag_to_contact(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "contactTag": {"contact": 123, "tag": 456}
        }


class TestContactCustomFieldFunctions:
    def test_list_contact_custom_fields(self, requests_mock, ac_client):
        mock_response = {
            "fields": [
                {
                    "title": "Test Field",
                    "descript": "Test description",
                    "type": "text",
                    "id": "1",
                },
                {
                    "title": "Test Dropdown",
                    "descript": "Test dropdown",
                    "type": "dropdown",
                    "id": "2",
                },
            ],
            "meta": {
                "total": "2",
            },
            "fieldOptions": [],
            "fieldRels": [],
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/fields",
            json=mock_response,
            status_code=200,
        )

        params = ContactCustomFieldListParams()
        result = ac_client.list_contact_custom_fields(params)

        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/fields"
        )

    def test_list_contact_custom_fields_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "fields": [
                {
                    "title": "Test Field",
                    "descript": "Test description",
                    "type": "text",
                    "id": "1",
                },
            ],
            "meta": {
                "total": "1",
            },
            "fieldOptions": [],
            "fieldRels": [],
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/fields",
            json=mock_response,
            status_code=200,
        )

        params = ContactCustomFieldListParams(limit=25, offset=10)
        result = ac_client.list_contact_custom_fields(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        assert "limit=25" in last_request_url
        assert "offset=10" in last_request_url

    def test_get_contact_custom_field_success(self, requests_mock, ac_client):
        field_id = 123
        mock_response = {
            "field": {
                "id": str(field_id),
                "title": "Test Field",
                "descript": "Test description",
                "type": "text",
                "visible": 1,
                "perstag": "TEST_FIELD",
            }
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/fields/{field_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_contact_custom_field(field_id)
        assert result == mock_response
        assert requests_mock.called

    def test_create_contact_custom_field_success(self, requests_mock, ac_client):
        mock_field_response = {
            "field": {
                "id": "999",
                "title": "New Custom Field",
                "descript": "A new custom field",
                "type": "text",
                "perstag": "NEW_FIELD",
                "visible": 1,
            }
        }

        mock_field_rel_response = {
            "fieldRel": {
                "field": "999",
                "relid": "0",
                "id": "123",
            }
        }

        # Mock the custom field creation endpoint
        requests_mock.post(
            "https://test-api.example.com/api/3/fields",
            json=mock_field_response,
            status_code=201,
        )
        
        # Mock the field relationship creation endpoint  
        requests_mock.post(
            "https://test-api.example.com/api/3/fieldRels",
            json=mock_field_rel_response,
            status_code=201,
        )

        params = ContactCustomFieldCreateParams(
            title="New Custom Field",
            descript="A new custom field",
            type="text",
            perstag="NEW_FIELD",
            visible=1,
        )
        result = ac_client.create_contact_custom_field(params)

        # Verify the response structure matches expected
        assert result["field"]["id"] == "999"
        assert result["field"]["title"] == "New Custom Field"
        assert result["field"]["type"] == "text"

        # Verify both API calls were made
        assert len(requests_mock.request_history) == 2

        # Verify the field creation call
        field_request = requests_mock.request_history[0]
        assert field_request.url == "https://test-api.example.com/api/3/fields"
        assert field_request.method == "POST"
        assert field_request.json() == {
            "field": {
                "title": "New Custom Field",
                "descript": "A new custom field",
                "type": "text",
                "perstag": "NEW_FIELD",
                "visible": 1,
            }
        }

        # Verify the field relationship creation call
        field_rel_request = requests_mock.request_history[1]
        assert field_rel_request.url == "https://test-api.example.com/api/3/fieldRels"
        assert field_rel_request.method == "POST"
        assert field_rel_request.json() == {
            "fieldRel": {
                "field": "999",
                "relid": 0,
            }
        }

    def test_create_field_options_success(self, requests_mock, ac_client):
        mock_response = {
            "fieldOptions": [
                {
                    "orderid": 1,
                    "value": "Option A",
                    "label": "Option A",
                    "isdefault": 0,
                    "field": "123",
                    "id": "1",
                },
                {
                    "orderid": 2,
                    "value": "Option B",
                    "label": "Option B",
                    "isdefault": 0,
                    "field": "123",
                    "id": "2",
                },
            ]
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/fieldOptions/bulk",
            json=mock_response,
            status_code=201,
        )

        params = FieldOptionBulkCreateParams(
            fieldOptions=[
                FieldOptionCreateParams(
                    orderid=1,
                    value="Option A",
                    label="Option A",
                    isdefault=False,
                    field="123",
                ),
                FieldOptionCreateParams(
                    orderid=2,
                    value="Option B",
                    label="Option B",
                    isdefault=False,
                    field="123",
                ),
            ]
        )
        result = ac_client.create_field_options(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "fieldOptions": [
                {
                    "orderid": 1,
                    "value": "Option A",
                    "label": "Option A",
                    "isdefault": False,
                    "field": "123",
                },
                {
                    "orderid": 2,
                    "value": "Option B",
                    "label": "Option B",
                    "isdefault": False,
                    "field": "123",
                },
            ]
        }

    def test_create_contact_field_relationship_success(self, requests_mock, ac_client):
        mock_response = {
            "fieldRel": {
                "field": "123",
                "relid": "456",
                "id": "789",
            }
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/fieldRels",
            json=mock_response,
            status_code=201,
        )

        params = ContactFieldRelCreateParams(field="123", relid=456)
        result = ac_client.create_contact_field_relationship(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "fieldRel": {"field": "123", "relid": 456}
        }


class TestContactFieldValueFunctions:
    def test_list_contact_field_values(self, requests_mock, ac_client):
        mock_response = {
            "fieldValues": [
                {
                    "contact": "123",
                    "field": "456",
                    "value": "Test Value",
                    "id": "1",
                },
                {
                    "contact": "123",
                    "field": "457",
                    "value": "Test Value 2",
                    "id": "2",
                },
            ],
            "meta": {
                "total": 2,
            },
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/fieldValues",
            json=mock_response,
            status_code=200,
        )

        params = ContactFieldValueListParams()
        result = ac_client.list_contact_field_values(params)

        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/fieldValues"
        )

    def test_list_contact_field_values_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "fieldValues": [
                {
                    "contact": "123",
                    "field": "456",
                    "value": "Test Value",
                    "id": "1",
                },
            ],
            "meta": {
                "total": 1,
            },
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/fieldValues",
            json=mock_response,
            status_code=200,
        )

        params = ContactFieldValueListParams(
            filters={"fieldid": 456},
            limit=25,
            offset=10,
        )
        result = ac_client.list_contact_field_values(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        assert "filters%5Bfieldid%5D=456" in last_request_url
        assert "limit=25" in last_request_url
        assert "offset=10" in last_request_url

    def test_get_contact_field_value_success(self, requests_mock, ac_client):
        field_value_id = 123
        mock_response = {
            "fieldValue": {
                "id": str(field_value_id),
                "contact": "456",
                "field": "789",
                "value": "Test Value",
            }
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/fieldValues/{field_value_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_contact_field_value(field_value_id)
        assert result == mock_response
        assert requests_mock.called

    def test_create_contact_field_value_success(self, requests_mock, ac_client):
        mock_response = {
            "fieldValue": {
                "id": "999",
                "contact": "123",
                "field": "456",
                "value": "Test Value",
            }
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/fieldValues",
            json=mock_response,
            status_code=201,
        )

        params = ContactFieldValueCreateParams(
            contact=123,
            field=456,
            value="Test Value",
        )
        result = ac_client.create_contact_field_value(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "fieldValue": {
                "contact": 123,
                "field": 456,
                "value": "Test Value",
            }
        }

    def test_create_contact_field_value_with_usedefaults(
        self, requests_mock, ac_client
    ):
        mock_response = {
            "fieldValue": {
                "id": "999",
                "contact": "123",
                "field": "456",
                "value": "Test Value",
            }
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/fieldValues",
            json=mock_response,
            status_code=201,
        )

        params = ContactFieldValueCreateParams(
            contact=123,
            field=456,
            value="Test Value",
            useDefaults=True,
        )
        result = ac_client.create_contact_field_value(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "fieldValue": {
                "contact": 123,
                "field": 456,
                "value": "Test Value",
                "useDefaults": True,
            },
        }

    def test_update_contact_field_value_success(self, requests_mock, ac_client):
        field_value_id = 123
        mock_response = {
            "fieldValue": {
                "id": str(field_value_id),
                "contact": "456",
                "field": "789",
                "value": "Updated Value",
            }
        }
        requests_mock.put(
            f"https://test-api.example.com/api/3/fieldValues/{field_value_id}",
            json=mock_response,
            status_code=200,
        )

        params = ContactFieldValueUpdateParams(value="Updated Value")
        result = ac_client.update_contact_field_value(field_value_id, params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "fieldValue": {"value": "Updated Value"}
        }

    def test_update_contact_field_value_with_usedefaults(
        self, requests_mock, ac_client
    ):
        field_value_id = 123
        mock_response = {
            "fieldValue": {
                "id": str(field_value_id),
                "contact": "456",
                "field": "789",
                "value": "Updated Value",
            }
        }
        requests_mock.put(
            f"https://test-api.example.com/api/3/fieldValues/{field_value_id}",
            json=mock_response,
            status_code=200,
        )

        params = ContactFieldValueUpdateParams(value="Updated Value", useDefaults=True)
        result = ac_client.update_contact_field_value(field_value_id, params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "fieldValue": {"value": "Updated Value", "useDefaults": True},
        }


class TestCallACAPI:
    def test_success(self, requests_mock, ac_client):
        mock_response = {"data": "test-data"}
        requests_mock.get(
            "https://test-api.example.com/api/3/test-endpoint",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.call_ac_api("/api/3/test-endpoint")

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.headers["Api-Token"] == "fake-token"
        assert requests_mock.last_request.headers["User-Agent"] == "test-package-1.0.0"

    def test_custom_method_and_data(self, requests_mock, ac_client):
        mock_response = {"result": "success"}
        requests_mock.post(
            "https://test-api.example.com/api/3/custom-endpoint",
            json=mock_response,
            status_code=200,
        )

        test_data = {"key": "value"}
        result = ac_client.call_ac_api(
            "/api/3/custom-endpoint", method="POST", data=test_data
        )

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == test_data

    def test_http_errors(self, requests_mock, ac_client):
        requests_mock.get(
            "https://test-api.example.com/api/3/test-endpoint",
            status_code=401,
            json={"message": "Unauthorized access"},
        )
        with pytest.raises(ToolError) as excinfo:
            ac_client.call_ac_api("/api/3/test-endpoint")
        assert "Authentication failed" in str(excinfo.value)

        requests_mock.get(
            "https://test-api.example.com/api/3/test-endpoint",
            status_code=404,
            json={"message": "Resource not found"},
        )
        with pytest.raises(ToolError) as excinfo:
            ac_client.call_ac_api("/api/3/test-endpoint")
        assert "Resource not found" in str(excinfo.value)

        requests_mock.get(
            "https://test-api.example.com/api/3/test-endpoint",
            status_code=500,
            json={"message": "Internal server error"},
        )
        with pytest.raises(ToolError) as excinfo:
            ac_client.call_ac_api("/api/3/test-endpoint")
        assert "Server error" in str(excinfo.value)

    def test_connection_error(self, requests_mock, ac_client):
        requests_mock.get(
            "https://test-api.example.com/api/3/test-endpoint",
            exc=requests.exceptions.ConnectionError,
        )
        with pytest.raises(ToolError) as excinfo:
            ac_client.call_ac_api("/api/3/test-endpoint")
        assert "Failed to connect" in str(excinfo.value)

    def test_invalid_json_response(self, requests_mock, ac_client):
        requests_mock.get(
            "https://test-api.example.com/api/3/test-endpoint",
            text="This is not JSON",
            status_code=200,
        )
        with pytest.raises(ToolError) as excinfo:
            ac_client.call_ac_api("/api/3/test-endpoint")
        assert "Invalid JSON response" in str(excinfo.value)


class TestEmailActivityFunctions:
    def test_list_email_activities(self, requests_mock, ac_client):
        mock_response = {
            "emailActivities": [
                {
                    "subscriberid": "1641",
                    "userid": "1",
                    "d_id": "0",
                    "account": None,
                    "reltype": "Log",
                    "relid": "12",
                    "from_name": "Test User",
                    "fromAddress": "test@example.com",
                    "toAddress": "recipient@example.com",
                    "subject": "Test Subject",
                    "message": "Test message content",
                    "tstamp": "2023-01-01T10:00:00-05:00",
                    "links": {
                        "contact": "https://test-api.example.com/api/3/emailActivities/1/contact",
                        "user": "https://test-api.example.com/api/3/emailActivities/1/user",
                    },
                    "id": "1",
                    "contact": "1641",
                    "user": "1",
                }
            ]
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/emailActivities",
            json=mock_response,
            status_code=200,
        )

        params = EmailActivityListParams()
        result = ac_client.list_email_activities(params)

        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/emailActivities"
        )

    def test_list_email_activities_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "emailActivities": [
                {
                    "subscriberid": "1641",
                    "userid": "1",
                    "d_id": "0",
                    "account": None,
                    "reltype": "Log",
                    "relid": "12",
                    "from_name": "Test User",
                    "fromAddress": "test@example.com",
                    "toAddress": "recipient@example.com",
                    "subject": "Test Subject",
                    "message": "Test message content",
                    "tstamp": "2023-01-01T10:00:00-05:00",
                    "links": {
                        "contact": "https://test-api.example.com/api/3/emailActivities/1/contact",
                        "user": "https://test-api.example.com/api/3/emailActivities/1/user",
                    },
                    "id": "1",
                    "contact": "1641",
                    "user": "1",
                }
            ]
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/emailActivities",
            json=mock_response,
            status_code=200,
        )

        params = EmailActivityListParams(
            limit=25,
            offset=0,
            orders={"tstamp": "DESC"},
            filters={"subscriberid": "1641"},
        )
        result = ac_client.list_email_activities(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        print(last_request_url)
        assert "limit=25" in last_request_url
        assert "offset=0" in last_request_url
        assert "orders%5Btstamp%5D=DESC" in last_request_url
        assert "filters%5Bsubscriberid%5D=1641" in last_request_url


class TestCampaignFunctions:
    def test_list_campaigns(self, requests_mock, ac_client):
        mock_response = {
            "campaigns": [
                {
                    "type": "single",
                    "userid": "1",
                    "segmentid": "0",
                    "bounceid": "0",
                    "realcid": "0",
                    "sendid": "0",
                    "threadid": "0",
                    "seriesid": "0",
                    "formid": "0",
                    "basetemplateid": "0",
                    "visible": "1",
                    "cdate": "2023-01-01T10:00:00-05:00",
                    "name": "Test Campaign",
                    "status": "1",
                    "public": "1",
                    "links": {
                        "user": "https://test-api.example.com/api/3/campaigns/1/user"
                    },
                    "id": "1",
                    "user": "1",
                }
            ]
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/campaigns",
            json=mock_response,
            status_code=200,
        )

        params = CampaignListParams()
        result = ac_client.list_campaigns(params)

        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/campaigns"
        )

    def test_list_campaigns_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "campaigns": [
                {
                    "type": "single",
                    "userid": "1",
                    "segmentid": "0",
                    "bounceid": "0",
                    "realcid": "0",
                    "sendid": "0",
                    "threadid": "0",
                    "seriesid": "0",
                    "formid": "0",
                    "basetemplateid": "0",
                    "visible": "1",
                    "cdate": "2023-01-01T10:00:00-05:00",
                    "name": "Test Campaign",
                    "status": "1",
                    "public": "1",
                    "links": {
                        "user": "https://test-api.example.com/api/3/campaigns/1/user"
                    },
                    "id": "1",
                    "user": "1",
                }
            ]
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/campaigns",
            json=mock_response,
            status_code=200,
        )

        campaign_filters = CampaignFilterField(
            type="single",
            list_id=123,
            automation=True,
            willrecur=False,
            seriesid="456",
            label_name="test-label",
            name="Newsletter",
            id=789,
            status="1,2,3",
        )

        params = CampaignListParams(
            limit=25,
            offset=10,
            orders={"sdate": "DESC", "ldate": "ASC"},
            filters=campaign_filters,
            has_message=True,
            has_message_content=True,
            has_form=False,
            campaignListing=1,
            status="scheduled",
            excludeTypes="reminder,special",
        )

        result = ac_client.list_campaigns(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        print(last_request_url)

        assert "limit=25" in last_request_url
        assert "offset=10" in last_request_url

        assert "orders%5Bsdate%5D=DESC" in last_request_url
        assert "orders%5Bldate%5D=ASC" in last_request_url

        assert "filters%5Btype%5D=single" in last_request_url
        assert "filters%5Blist_id%5D=123" in last_request_url
        assert "filters%5Bautomation%5D=True" in last_request_url
        assert "filters%5Bwillrecur%5D=False" in last_request_url
        assert "filters%5Bseriesid%5D=456" in last_request_url
        assert "filters%5Blabel_name%5D=test-label" in last_request_url
        assert "filters%5Bname%5D=Newsletter" in last_request_url
        assert "filters%5Bid%5D=789" in last_request_url
        assert "filters%5Bstatus%5D=1%2C2%2C3" in last_request_url  # URL-encoded comma

        assert "has_message=True" in last_request_url
        assert "has_message_content=True" in last_request_url
        assert "has_form=False" in last_request_url

        assert "campaignListing=1" in last_request_url
        assert "status=scheduled" in last_request_url
        assert "excludeTypes=reminder%2Cspecial" in last_request_url

    def test_get_campaign_success(self, requests_mock, ac_client):
        campaign_id = 123
        mock_response = {
            "campaign": {
                "type": "single",
                "userid": "1",
                "segmentid": "0",
                "bounceid": "0",
                "realcid": "0",
                "sendid": "0",
                "threadid": "0",
                "seriesid": "0",
                "formid": "0",
                "basetemplateid": "0",
                "visible": "1",
                "cdate": "2023-01-01T10:00:00-05:00",
                "name": "Test Campaign",
                "status": "1",
                "public": "1",
                "links": {
                    "user": "https://test-api.example.com/api/3/campaigns/123/user"
                },
                "id": str(campaign_id),
                "user": "1",
            }
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/campaigns/{campaign_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_campaign(campaign_id)
        assert result == mock_response
        assert requests_mock.called

    def test_get_campaign_links_success(self, requests_mock, ac_client):
        campaign_id = 123
        mock_response = {
            "links": [
                {
                    "campaignid": str(campaign_id),
                    "messageid": "3",
                    "link": "open",
                    "name": "Read Tracker",
                    "ref": "",
                    "tracked": "1",
                    "links": {
                        "campaign": "https://test-api.example.com/api/3/links/1/campaign",
                        "message": "https://test-api.example.com/api/3/links/1/message",
                    },
                    "id": "1",
                    "campaign": str(campaign_id),
                    "message": "3",
                },
                {
                    "campaignid": str(campaign_id),
                    "messageid": "0",
                    "link": "open",
                    "name": "Read Tracker",
                    "ref": "",
                    "tracked": "1",
                    "links": {
                        "campaign": "https://test-api.example.com/api/3/links/2/campaign",
                        "message": "https://test-api.example.com/api/3/links/2/message",
                    },
                    "id": "2",
                    "campaign": str(campaign_id),
                    "message": None,
                },
            ]
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/campaigns/{campaign_id}/links",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_campaign_links(campaign_id)
        assert result == mock_response
        assert requests_mock.called


class TestAutomationFunctions:
    def test_list_automations(self, requests_mock, ac_client):
        mock_response = {
            "automations": [
                {
                    "name": "Test Automation",
                    "cdate": "2023-01-01T10:00:00-05:00",
                    "mdate": "2023-01-02T10:00:00-05:00",
                    "userid": "1",
                    "status": "1",
                    "entered": "5",
                    "exited": "2",
                    "hidden": "0",
                    "defaultscreenshot": "",
                    "screenshot": "",
                    "links": {
                        "campaigns": "https://test-api.example.com/api/3/automations/1/campaigns",
                        "contactGoals": "https://test-api.example.com/api/3/automations/1/contactGoals",
                        "contactAutomations": "https://test-api.example.com/api/3/automations/1/contactAutomations",
                        "blocks": "https://test-api.example.com/api/3/automations/1/blocks",
                        "goals": "https://test-api.example.com/api/3/automations/1/goals",
                        "sms": "https://test-api.example.com/api/3/automations/1/sms",
                        "sitemessages": "https://test-api.example.com/api/3/automations/1/sitemessages",
                    },
                    "id": "1",
                }
            ],
            "meta": {
                "total": "1",
                "starts": [],
                "filtered": False,
                "smsLogs": [],
            },
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/automations",
            json=mock_response,
            status_code=200,
        )

        params = AutomationListParams()
        result = ac_client.list_automations(params)

        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/automations"
        )

    def test_list_automations_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "automations": [
                {
                    "name": "Email Marketing Automation",
                    "cdate": "2023-01-01T10:00:00-05:00",
                    "mdate": "2023-01-02T10:00:00-05:00",
                    "userid": "1",
                    "status": "1",
                    "entered": "10",
                    "exited": "3",
                    "hidden": "0",
                    "defaultscreenshot": "",
                    "screenshot": "",
                    "links": {
                        "campaigns": "https://test-api.example.com/api/3/automations/2/campaigns",
                        "contactGoals": "https://test-api.example.com/api/3/automations/2/contactGoals",
                        "contactAutomations": "https://test-api.example.com/api/3/automations/2/contactAutomations",
                        "blocks": "https://test-api.example.com/api/3/automations/2/blocks",
                        "goals": "https://test-api.example.com/api/3/automations/2/goals",
                        "sms": "https://test-api.example.com/api/3/automations/2/sms",
                        "sitemessages": "https://test-api.example.com/api/3/automations/2/sitemessages",
                    },
                    "id": "2",
                }
            ],
            "meta": {
                "total": "1",
                "starts": [],
                "filtered": True,
                "smsLogs": [],
            },
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/automations",
            json=mock_response,
            status_code=200,
        )

        automation_filters = AutomationFilterField(
            name="Email",
            status="1",
            ids="1,2,3",
            tag=123,
            triggers="form_submit,date_added",
            actions="send_email,wait",
            label_name="Marketing",
        )

        params = AutomationListParams(
            limit=50,
            offset=5,
            filters=automation_filters,
            orders={"name": "ASC", "cdate": "DESC"},
            label=456,
            search="marketing",
            active=True,
            has_message=True,
            enhance=True,
        )

        result = ac_client.list_automations(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        print(last_request_url)

        assert "limit=50" in last_request_url

        assert "orders%5Bname%5D=ASC" in last_request_url
        assert "orders%5Bcdate%5D=DESC" in last_request_url
        assert "filters%5Bname%5D=Email" in last_request_url
        assert "filters%5Bstatus%5D=1" in last_request_url
        assert "filters%5Bids%5D=1%2C2%2C3" in last_request_url
        assert "filters%5Btag%5D=123" in last_request_url
        assert "filters%5Btriggers%5D=form_submit%2Cdate_added" in last_request_url
        assert "filters%5Bactions%5D=send_email%2Cwait" in last_request_url
        assert "filters%5Blabel_name%5D=Marketing" in last_request_url
        assert "label=456" in last_request_url
        assert "search=marketing" in last_request_url
        assert "active=True" in last_request_url
        assert "has_message=True" in last_request_url
        assert "enhance=True" in last_request_url


class TestContactAutomationFunctions:
    def test_list_contact_automations(self, requests_mock, ac_client):
        mock_response = {
            "contactAutomations": [
                {
                    "contact": "10003",
                    "seriesid": "1",
                    "startid": "0",
                    "status": "2",
                    "batchid": None,
                    "adddate": "2018-11-16T02:32:33-06:00",
                    "remdate": "2018-11-16T02:32:33-06:00",
                    "timespan": "0",
                    "lastblock": "1",
                    "lastlogid": "0",
                    "lastdate": "2018-11-16T02:32:33-06:00",
                    "completedElements": 0,
                    "totalElements": 1,
                    "completed": 1,
                    "completeValue": 100,
                    "links": {
                        "automation": "https://test-api.example.com/api/3/contactAutomations/1/automation",
                        "contact": "https://test-api.example.com/api/3/contactAutomations/1/contact",
                        "contactGoals": "https://test-api.example.com/api/3/contactAutomations/1/contactGoals",
                        "automationLogs": "https://test-api.example.com/api/3/contactAutomations/1/automationLogs",
                        "subscriberSeriesEnd": "https://test-api.example.com/api/3/contactAutomations/1/subscriberSeriesEnd",
                    },
                    "id": "1",
                    "automation": "1",
                }
            ],
            "meta": {
                "total": "1",
                "showcase_stats": [],
            },
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/contactAutomations",
            json=mock_response,
            status_code=200,
        )

        params = ContactAutomationListParams()
        result = ac_client.list_contact_automations(params)

        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/contactAutomations"
        )

    def test_list_contact_automations_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "contactAutomations": [
                {
                    "contact": "10003",
                    "seriesid": "1",
                    "startid": "0",
                    "status": "1",
                    "batchid": None,
                    "adddate": "2018-11-16T02:32:33-06:00",
                    "remdate": "2018-11-16T02:32:33-06:00",
                    "timespan": "0",
                    "lastblock": "1",
                    "lastlogid": "0",
                    "lastdate": "2018-11-16T02:32:33-06:00",
                    "completedElements": 0,
                    "totalElements": 1,
                    "completed": 0,
                    "completeValue": 0,
                    "links": {
                        "automation": "https://test-api.example.com/api/3/contactAutomations/2/automation",
                        "contact": "https://test-api.example.com/api/3/contactAutomations/2/contact",
                        "contactGoals": "https://test-api.example.com/api/3/contactAutomations/2/contactGoals",
                        "automationLogs": "https://test-api.example.com/api/3/contactAutomations/2/automationLogs",
                        "subscriberSeriesEnd": "https://test-api.example.com/api/3/contactAutomations/2/subscriberSeriesEnd",
                    },
                    "id": "2",
                    "automation": "1",
                }
            ],
            "meta": {
                "total": "1",
                "showcase_stats": [],
            },
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/contactAutomations",
            json=mock_response,
            status_code=200,
        )

        params = ContactAutomationListParams(limit=25, offset=10)
        result = ac_client.list_contact_automations(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        print(last_request_url)

        assert "limit=25" in last_request_url
        assert "offset=10" in last_request_url

    def test_list_contact_automations_with_comprehensive_parameters(
        self, requests_mock, ac_client
    ):
        mock_response = {
            "contactAutomations": [
                {
                    "contact": "10003",
                    "seriesid": "1",
                    "startid": "0",
                    "status": "1",
                    "batchid": None,
                    "adddate": "2018-11-16T02:32:33-06:00",
                    "remdate": "2018-11-16T02:32:33-06:00",
                    "timespan": "0",
                    "lastblock": "1",
                    "lastlogid": "0",
                    "lastdate": "2018-11-16T02:32:33-06:00",
                    "completedElements": 0,
                    "totalElements": 1,
                    "completed": 0,
                    "completeValue": 0,
                    "links": {
                        "automation": "https://test-api.example.com/api/3/contactAutomations/3/automation",
                        "contact": "https://test-api.example.com/api/3/contactAutomations/3/contact",
                        "contactGoals": "https://test-api.example.com/api/3/contactAutomations/3/contactGoals",
                        "automationLogs": "https://test-api.example.com/api/3/contactAutomations/3/automationLogs",
                        "subscriberSeriesEnd": "https://test-api.example.com/api/3/contactAutomations/3/subscriberSeriesEnd",
                    },
                    "id": "3",
                    "automation": "1",
                }
            ],
            "meta": {
                "total": "1",
                "showcase_stats": [],
            },
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/contactAutomations",
            json=mock_response,
            status_code=200,
        )

        from ac_mcp_server.types import (
            ContactAutomationFilters,
            ContactAutomationDateFilter,
        )

        # Test with comprehensive parameters including nested date filters
        date_filter = ContactAutomationDateFilter(gte="2023-01-01", lt="2023-12-31")

        filters = ContactAutomationFilters(
            seriesid=123, adddate=date_filter, status=1, lastblock=5, subscriberid=456
        )

        params = ContactAutomationListParams(
            limit=50,
            offset=20,
            filters=filters,
            orders={"name": "ASC", "adddate": "DESC"},
            q="test search",
            min_time=3600,
            max_time=7200,
            tags=[1, 2, 3],
            g_tagid=10,
            g_tags=[11, 12],
            lists=[100, 200],
            g_listid=300,
            g_lists=[400, 500],
            g_id=999,
            g_status=1,
            g_min_time=1800,
            g_max_time=3600,
            scoreid=777,
            include="contact,automation",
        )

        result = ac_client.list_contact_automations(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        print(last_request_url)

        # Basic pagination
        assert "limit=50" in last_request_url
        assert "offset=20" in last_request_url

        # Filters
        assert "filters%5Bseriesid%5D=123" in last_request_url
        assert "filters%5Badddate%5D%5Bgte%5D=2023-01-01" in last_request_url
        assert "filters%5Badddate%5D%5Blt%5D=2023-12-31" in last_request_url
        assert "filters%5Bstatus%5D=1" in last_request_url
        assert "filters%5Blastblock%5D=5" in last_request_url
        assert "filters%5Bsubscriberid%5D=456" in last_request_url

        # Orders
        assert "orders%5Bname%5D=ASC" in last_request_url
        assert "orders%5Badddate%5D=DESC" in last_request_url

        # Search
        assert "q=test+search" in last_request_url

        # Time filters
        assert "min_time=3600" in last_request_url
        assert "max_time=7200" in last_request_url

        # Tag filters
        assert "tags%5B%5D=1" in last_request_url
        assert "tags%5B%5D=2" in last_request_url
        assert "tags%5B%5D=3" in last_request_url
        assert "g_tagid=10" in last_request_url
        assert "g_tags%5B%5D=11" in last_request_url
        assert "g_tags%5B%5D=12" in last_request_url

        # List filters
        assert "lists%5B%5D=100" in last_request_url
        assert "lists%5B%5D=200" in last_request_url
        assert "g_listid=300" in last_request_url
        assert "g_lists%5B%5D=400" in last_request_url
        assert "g_lists%5B%5D=500" in last_request_url

        # Goal parameters
        assert "g_id=999" in last_request_url
        assert "g_status=1" in last_request_url
        assert "g_min_time=1800" in last_request_url
        assert "g_max_time=3600" in last_request_url

        # Score and include
        assert "scoreid=777" in last_request_url
        assert "include=contact%2Cautomation" in last_request_url

    def test_get_contact_automation_success(self, requests_mock, ac_client):
        contact_automation_id = 123
        mock_response = {
            "contactAutomation": {
                "contact": "110",
                "seriesid": "2",
                "startid": "0",
                "status": "2",
                "batchid": None,
                "adddate": "2018-09-19T09:44:26-05:00",
                "remdate": "2018-09-19T09:44:26-05:00",
                "timespan": "0",
                "lastblock": "5",
                "lastlogid": "2",
                "lastdate": "2018-09-19T09:44:26-05:00",
                "completedElements": 1,
                "totalElements": 2,
                "completed": 1,
                "completeValue": 100,
                "links": {
                    "automation": "https://test-api.example.com/api/3/contactAutomations/123/automation",
                    "contact": "https://test-api.example.com/api/3/contactAutomations/123/contact",
                    "contactGoals": "https://test-api.example.com/api/3/contactAutomations/123/contactGoals",
                    "automationLogs": "https://test-api.example.com/api/3/contactAutomations/123/automationLogs",
                    "subscriberSeriesEnd": "https://test-api.example.com/api/3/contactAutomations/123/subscriberSeriesEnd",
                },
                "id": str(contact_automation_id),
                "automation": "2",
            }
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/contactAutomations/{contact_automation_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_contact_automation(contact_automation_id)
        assert result == mock_response
        assert requests_mock.called

    def test_add_contact_to_automation_success(self, requests_mock, ac_client):
        mock_response = {
            "contacts": [
                {
                    "cdate": "2018-09-19T09:44:26-05:00",
                    "email": "test@example.com",
                    "phone": "",
                    "firstName": "Test",
                    "lastName": "Contact",
                    "orgid": "0",
                    "orgname": "",
                    "segmentio_id": "",
                    "bounced_hard": "0",
                    "bounced_soft": "0",
                    "bounced_date": None,
                    "ip": "0",
                    "ua": "",
                    "hash": "abc123",
                    "socialdata_lastcheck": None,
                    "email_local": "test",
                    "email_domain": "example.com",
                    "sentcnt": "0",
                    "rating_tstamp": None,
                    "gravatar": "0",
                    "deleted": "0",
                    "anonymized": "0",
                    "adate": None,
                    "udate": "2018-09-19T09:44:26-05:00",
                    "edate": None,
                    "deleted_at": None,
                    "created_utc_timestamp": "2018-09-19 14:44:26",
                    "updated_utc_timestamp": "2018-09-19 14:44:26",
                    "created_timestamp": "2018-09-19 09:44:26",
                    "updated_timestamp": "2018-09-19 09:44:26",
                    "created_by": None,
                    "updated_by": None,
                    "mpp_tracking": "0",
                    "last_click_date": None,
                    "last_open_date": None,
                    "last_mpp_open_date": None,
                    "best_send_hour": None,
                    "contactAutomations": ["3"],
                    "contactLists": [],
                    "fieldValues": [],
                    "geoIps": [],
                    "deals": [],
                    "sentiment": None,
                    "accountContacts": [],
                    "scoreValues": [],
                    "links": {
                        "bounceLogs": "https://test-api.example.com/api/3/contacts/64/bounceLogs",
                        "contactAutomations": "https://test-api.example.com/api/3/contacts/64/contactAutomations",
                        "contactData": "https://test-api.example.com/api/3/contacts/64/contactData",
                        "contactGoals": "https://test-api.example.com/api/3/contacts/64/contactGoals",
                        "contactLists": "https://test-api.example.com/api/3/contacts/64/contactLists",
                        "contactLogs": "https://test-api.example.com/api/3/contacts/64/contactLogs",
                        "contactTags": "https://test-api.example.com/api/3/contacts/64/contactTags",
                        "contactDeals": "https://test-api.example.com/api/3/contacts/64/contactDeals",
                        "deals": "https://test-api.example.com/api/3/contacts/64/deals",
                        "fieldValues": "https://test-api.example.com/api/3/contacts/64/fieldValues",
                        "geoIps": "https://test-api.example.com/api/3/contacts/64/geoIps",
                        "notes": "https://test-api.example.com/api/3/contacts/64/notes",
                        "organization": "https://test-api.example.com/api/3/contacts/64/organization",
                        "plusAppend": "https://test-api.example.com/api/3/contacts/64/plusAppend",
                        "trackingLogs": "https://test-api.example.com/api/3/contacts/64/trackingLogs",
                        "scoreValues": "https://test-api.example.com/api/3/contacts/64/scoreValues",
                        "automationEntryCounts": "https://test-api.example.com/api/3/contacts/64/automationEntryCounts",
                    },
                    "id": "64",
                    "organization": None,
                }
            ],
            "contactAutomation": {
                "contact": "64",
                "seriesid": "2",
                "startid": "0",
                "status": "1",
                "batchid": None,
                "adddate": "2018-09-19T09:44:26-05:00",
                "remdate": "2018-09-19T09:44:26-05:00",
                "timespan": "0",
                "lastblock": "4",
                "lastlogid": "0",
                "lastdate": "2018-09-19T09:44:26-05:00",
                "in_als": "0",
                "completedElements": 1,
                "totalElements": 2,
                "completed": 0,
                "completeValue": 50,
                "links": {
                    "automation": "https://test-api.example.com/api/3/contactAutomations/3/automation",
                    "contact": "https://test-api.example.com/api/3/contactAutomations/3/contact",
                    "contactGoals": "https://test-api.example.com/api/3/contactAutomations/3/contactGoals",
                    "automationLogs": "https://test-api.example.com/api/3/contactAutomations/3/automationLogs",
                    "subscriberSeriesEnd": "https://test-api.example.com/api/3/contactAutomations/3/subscriberSeriesEnd",
                },
                "id": "3",
                "automation": "2",
            },
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/contactAutomations",
            json=mock_response,
            status_code=201,
        )

        params = ContactAutomationCreateParams(contact=64, automation=2)
        result = ac_client.add_contact_to_automation(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "contactAutomation": {"contact": 64, "automation": 2}
        }

    def test_remove_contact_from_automation_success(self, requests_mock, ac_client):
        contact_automation_id = 123
        mock_response = {}  # DELETE typically returns empty response
        requests_mock.delete(
            f"https://test-api.example.com/api/3/contactAutomations/{contact_automation_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.remove_contact_from_automation(contact_automation_id)
        assert result == mock_response
        assert requests_mock.called


class TestGroupFunctions:
    def test_list_groups_success(self, requests_mock, ac_client):
        mock_response = {
            "groups": [
                {
                    "title": "Admin Group",
                    "descript": "Administrator group with full permissions",
                    "id": "7",
                }
            ],
            "meta": {"total": "1"},
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/groups",
            json=mock_response,
            status_code=200,
        )

        params = GroupListParams()
        result = ac_client.list_groups(params)
        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url
            == "https://test-api.example.com/api/3/groups"
        )

    def test_list_groups_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "groups": [
                {
                    "title": "Limited Group",
                    "descript": "Group with limited permissions",
                    "id": "8",
                }
            ],
            "meta": {"total": "1"},
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/groups",
            json=mock_response,
            status_code=200,
        )

        params = GroupListParams(limit=10, offset=5)
        result = ac_client.list_groups(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        assert "limit=10" in last_request_url
        assert "offset=5" in last_request_url

    def test_list_groups_empty_response(self, requests_mock, ac_client):
        mock_response = {"groups": [], "meta": {"total": "0"}}
        requests_mock.get(
            "https://test-api.example.com/api/3/groups",
            json=mock_response,
            status_code=200,
        )

        params = GroupListParams()
        result = ac_client.list_groups(params)
        assert result == mock_response
        assert requests_mock.called

    def test_list_groups_api_error(self, requests_mock, ac_client):
        requests_mock.get(
            "https://test-api.example.com/api/3/groups",
            json={"error": "Unauthorized"},
            status_code=401,
        )

        with pytest.raises(ToolError, match="Authentication failed"):
            ac_client.list_groups(GroupListParams())


class TestListFunctions:
    def test_list_lists_success(self, requests_mock, ac_client):
        mock_response = {
            "lists": [
                {
                    "stringid": "email-subscription",
                    "userid": "1",
                    "name": "Email Subscription",
                    "cdate": "2018-08-06T16:30:41-05:00",
                    "p_use_tracking": "1",
                    "p_use_analytics_read": "0",
                    "p_use_analytics_link": "0",
                    "p_use_twitter": "0",
                    "p_use_facebook": "0",
                    "p_embed_image": "1",
                    "p_use_captcha": "1",
                    "send_last_broadcast": "0",
                    "private": "0",
                    "analytics_domains": None,
                    "analytics_source": "",
                    "analytics_ua": "",
                    "twitter_token": "",
                    "twitter_token_secret": "",
                    "facebook_session": None,
                    "carboncopy": None,
                    "subscription_notify": None,
                    "unsubscription_notify": None,
                    "require_name": "0",
                    "get_unsubscribe_reason": "0",
                    "to_name": "Subscriber",
                    "optinoptout": "1",
                    "sender_name": "",
                    "sender_addr1": "",
                    "sender_addr2": "",
                    "sender_city": "",
                    "sender_state": "",
                    "sender_zip": "",
                    "sender_country": "",
                    "sender_phone": "",
                    "sender_url": "http://www.activecampaign.com",
                    "sender_reminder": "You signed up for my mailing list.",
                    "fulladdress": "",
                    "optinmessageid": "0",
                    "optoutconf": "0",
                    "deletestamp": None,
                    "udate": None,
                    "links": {
                        "contactGoalLists": "https://test-api.example.com/api/3/lists/1/contactGoalLists",
                        "user": "https://test-api.example.com/api/3/lists/1/user",
                        "addressLists": "https://test-api.example.com/api/3/lists/1/addressLists",
                    },
                    "id": "1",
                    "user": "1",
                },
                {
                    "stringid": "newsletter-list",
                    "userid": "1",
                    "name": "Newsletter List",
                    "cdate": "2018-09-07T08:56:49-05:00",
                    "p_use_tracking": "1",
                    "p_use_analytics_read": "0",
                    "p_use_analytics_link": "0",
                    "p_use_twitter": "0",
                    "p_use_facebook": "0",
                    "p_embed_image": "1",
                    "p_use_captcha": "1",
                    "send_last_broadcast": "0",
                    "private": "0",
                    "analytics_domains": None,
                    "analytics_source": "",
                    "analytics_ua": "",
                    "twitter_token": "",
                    "twitter_token_secret": "",
                    "facebook_session": None,
                    "carboncopy": None,
                    "subscription_notify": None,
                    "unsubscription_notify": None,
                    "require_name": "0",
                    "get_unsubscribe_reason": "0",
                    "to_name": "Subscriber",
                    "optinoptout": "1",
                    "sender_name": "",
                    "sender_addr1": "",
                    "sender_addr2": "",
                    "sender_city": "",
                    "sender_state": "",
                    "sender_zip": "",
                    "sender_country": "",
                    "sender_phone": "",
                    "sender_url": "http://www.activecampaign.com",
                    "sender_reminder": "Test reminder",
                    "fulladdress": "",
                    "optinmessageid": "0",
                    "optoutconf": "0",
                    "deletestamp": None,
                    "udate": None,
                    "links": {
                        "contactGoalLists": "https://test-api.example.com/api/3/lists/2/contactGoalLists",
                        "user": "https://test-api.example.com/api/3/lists/2/user",
                        "addressLists": "https://test-api.example.com/api/3/lists/2/addressLists",
                    },
                    "id": "2",
                    "user": "1",
                },
            ],
            "meta": {"total": "2"},
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/lists",
            json=mock_response,
            status_code=200,
        )

        params = ListListParams()
        result = ac_client.list_lists(params)
        assert result == mock_response
        assert requests_mock.called
        assert (
            requests_mock.last_request.url == "https://test-api.example.com/api/3/lists"
        )

    def test_list_lists_with_parameters(self, requests_mock, ac_client):
        mock_response = {
            "lists": [
                {
                    "stringid": "newsletter-list",
                    "userid": "1",
                    "name": "Newsletter List",
                    "cdate": "2018-09-07T08:56:49-05:00",
                    "p_use_tracking": "1",
                    "p_use_analytics_read": "0",
                    "p_use_analytics_link": "0",
                    "p_use_twitter": "0",
                    "p_use_facebook": "0",
                    "p_embed_image": "1",
                    "p_use_captcha": "1",
                    "send_last_broadcast": "0",
                    "private": "0",
                    "analytics_domains": None,
                    "analytics_source": "",
                    "analytics_ua": "",
                    "twitter_token": "",
                    "twitter_token_secret": "",
                    "facebook_session": None,
                    "carboncopy": None,
                    "subscription_notify": None,
                    "unsubscription_notify": None,
                    "require_name": "0",
                    "get_unsubscribe_reason": "0",
                    "to_name": "Subscriber",
                    "optinoptout": "1",
                    "sender_name": "",
                    "sender_addr1": "",
                    "sender_addr2": "",
                    "sender_city": "",
                    "sender_state": "",
                    "sender_zip": "",
                    "sender_country": "",
                    "sender_phone": "",
                    "sender_url": "http://www.activecampaign.com",
                    "sender_reminder": "Test reminder",
                    "fulladdress": "",
                    "optinmessageid": "0",
                    "optoutconf": "0",
                    "deletestamp": None,
                    "udate": None,
                    "links": {
                        "contactGoalLists": "https://test-api.example.com/api/3/lists/2/contactGoalLists",
                        "user": "https://test-api.example.com/api/3/lists/2/user",
                        "addressLists": "https://test-api.example.com/api/3/lists/2/addressLists",
                    },
                    "id": "2",
                    "user": "1",
                }
            ],
            "meta": {"total": "1"},
        }
        requests_mock.get(
            "https://test-api.example.com/api/3/lists",
            json=mock_response,
            status_code=200,
        )

        params = ListListParams(
            limit=10, offset=5, filters=ListFilters(name="newsletter")
        )
        result = ac_client.list_lists(params)

        assert result == mock_response
        assert requests_mock.called

        last_request_url = requests_mock.last_request.url
        assert "limit=10" in last_request_url
        assert "offset=5" in last_request_url
        assert "filters%5Bname%5D=newsletter" in last_request_url

    def test_get_list_success(self, requests_mock, ac_client):
        list_id = 123
        mock_response = {
            "list": {
                "stringid": "test-list",
                "userid": "1",
                "name": "Test List",
                "cdate": "2018-08-06T16:30:41-05:00",
                "p_use_tracking": "1",
                "p_use_analytics_read": "0",
                "p_use_analytics_link": "0",
                "p_use_twitter": "0",
                "p_use_facebook": "0",
                "p_embed_image": "1",
                "p_use_captcha": "1",
                "send_last_broadcast": "0",
                "private": "0",
                "analytics_domains": None,
                "analytics_source": "",
                "analytics_ua": "",
                "twitter_token": "",
                "twitter_token_secret": "",
                "facebook_session": None,
                "carboncopy": None,
                "subscription_notify": None,
                "unsubscription_notify": None,
                "require_name": "0",
                "get_unsubscribe_reason": "0",
                "to_name": "Subscriber",
                "optinoptout": "1",
                "sender_name": "Test Sender",
                "sender_addr1": "123 Test St",
                "sender_addr2": "",
                "sender_city": "Test City",
                "sender_state": "TS",
                "sender_zip": "12345",
                "sender_country": "US",
                "sender_phone": "555-1234",
                "sender_url": "http://www.example.com",
                "sender_reminder": "You signed up for our test list.",
                "fulladdress": "123 Test St, Test City, TS 12345, US",
                "optinmessageid": "0",
                "optoutconf": "0",
                "deletestamp": None,
                "udate": None,
                "links": {
                    "contactGoalLists": f"https://test-api.example.com/api/3/lists/{list_id}/contactGoalLists",
                    "user": f"https://test-api.example.com/api/3/lists/{list_id}/user",
                    "addressLists": f"https://test-api.example.com/api/3/lists/{list_id}/addressLists",
                },
                "id": str(list_id),
                "user": "1",
            }
        }
        requests_mock.get(
            f"https://test-api.example.com/api/3/lists/{list_id}",
            json=mock_response,
            status_code=200,
        )

        result = ac_client.get_list(list_id)
        assert result == mock_response
        assert requests_mock.called

    def test_create_list_success(self, requests_mock, ac_client):
        mock_response = {
            "list": {
                "name": "Test Newsletter",
                "stringid": "test-newsletter",
                "channel": "email",
                "cdate": "2023-01-01T10:00:00-05:00",
                "udate": "2023-01-01T10:00:00-05:00",
                "userid": "1",
                "sender_url": "http://example.com",
                "sender_reminder": "You subscribed to our newsletter",
                "send_last_broadcast": "0",
                "carboncopy": "",
                "subscription_notify": "",
                "unsubscription_notify": "",
                "private": "0",
                "analytics_domains": None,
                "analytics_source": "",
                "analytics_ua": "",
                "twitter_token": "",
                "twitter_token_secret": "",
                "facebook_session": None,
                "require_name": "0",
                "get_unsubscribe_reason": "0",
                "to_name": "Subscriber",
                "optinoptout": "1",
                "sender_name": "",
                "sender_addr1": "",
                "sender_addr2": "",
                "sender_city": "",
                "sender_state": "",
                "sender_zip": "",
                "sender_country": "",
                "sender_phone": "",
                "fulladdress": "",
                "optinmessageid": "0",
                "optoutconf": "0",
                "deletestamp": None,
                "links": {
                    "contactGoalLists": "https://test-api.example.com/api/3/lists/123/contactGoalLists",
                    "user": "https://test-api.example.com/api/3/lists/123/user",
                    "addressLists": "https://test-api.example.com/api/3/lists/123/addressLists",
                },
                "id": "123",
                "user": "1",
            }
        }
        requests_mock.post(
            "https://test-api.example.com/api/3/lists",
            json=mock_response,
            status_code=201,
        )

        params = ListCreateParams(
            name="Test Newsletter",
            channel="email",
            sender_url="http://example.com",
            sender_reminder="You subscribed to our newsletter",
        )
        result = ac_client.create_list(params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "list": {
                "name": "Test Newsletter",
                "channel": "email",
                "sender_url": "http://example.com",
                "sender_reminder": "You subscribed to our newsletter",
                "send_last_broadcast": 0,
                "carboncopy": "",
                "subscription_notify": "",
                "unsubscription_notify": "",
            }
        }

    def test_create_list_group_permission_success(self, requests_mock, ac_client):
        mock_response = {
            "listGroup": {
                "list": "19",
                "group": "1",
                "links": {
                    "list": "https://account.api-us1.com/api/3/listGroups/55/list",
                    "group": "https://account.api-us1.com/api/3/listGroups/55/group",
                },
                "id": "55",
            }
        }

        requests_mock.post(
            "https://test-api.example.com/api/3/listGroups",
            json=mock_response,
            status_code=201,
        )

        params = ListGroupPermissionParams(list=19, group=1)
        result = ac_client.create_list_group_permission(params)

        assert result["listGroup"]["list"] == "19"
        assert result["listGroup"]["group"] == "1"
        assert result["listGroup"]["id"] == "55"
        assert requests_mock.last_request.json() == {
            "listGroup": {"list": 19, "group": 1}
        }

    def test_add_contact_to_list_success(self, requests_mock, ac_client):
        mock_response = {
            "contacts": [
                {
                    "cdate": "2017-07-24T12:09:52-05:00",
                    "email": "john@example.com",
                    "phone": "",
                    "firstName": "John",
                    "lastName": "Doe",
                    "orgid": "0",
                    "segmentio_id": "",
                    "bounced_hard": "0",
                    "bounced_soft": "0",
                    "bounced_date": "0000-00-00",
                    "ip": "0",
                    "ua": "",
                    "hash": "abc123",
                    "socialdata_lastcheck": None,
                    "email_local": "john",
                    "email_domain": "example.com",
                    "sentcnt": "0",
                    "rating_tstamp": None,
                    "gravatar": "0",
                    "deleted": "0",
                    "anonymized": "0",
                    "adate": None,
                    "udate": "2017-07-24T12:09:52-05:00",
                    "edate": None,
                    "deleted_at": None,
                    "created_utc_timestamp": "2017-07-24 17:09:52",
                    "updated_utc_timestamp": "2017-07-24 17:09:52",
                    "created_timestamp": "2017-07-24 12:09:52",
                    "updated_timestamp": "2017-07-24 12:09:52",
                    "created_by": None,
                    "updated_by": None,
                    "links": {
                        "bounceLogs": "https://test-api.example.com/api/3/contacts/123/bounceLogs",
                        "contactAutomations": "https://test-api.example.com/api/3/contacts/123/contactAutomations",
                        "contactData": "https://test-api.example.com/api/3/contacts/123/contactData",
                        "contactGoals": "https://test-api.example.com/api/3/contacts/123/contactGoals",
                        "contactLists": "https://test-api.example.com/api/3/contacts/123/contactLists",
                        "contactLogs": "https://test-api.example.com/api/3/contacts/123/contactLogs",
                        "contactTags": "https://test-api.example.com/api/3/contacts/123/contactTags",
                        "contactDeals": "https://test-api.example.com/api/3/contacts/123/contactDeals",
                        "deals": "https://test-api.example.com/api/3/contacts/123/deals",
                        "fieldValues": "https://test-api.example.com/api/3/contacts/123/fieldValues",
                        "geoIps": "https://test-api.example.com/api/3/contacts/123/geoIps",
                        "notes": "https://test-api.example.com/api/3/contacts/123/notes",
                        "organization": "https://test-api.example.com/api/3/contacts/123/organization",
                        "plusAppend": "https://test-api.example.com/api/3/contacts/123/plusAppend",
                        "trackingLogs": "https://test-api.example.com/api/3/contacts/123/trackingLogs",
                        "scoreValues": "https://test-api.example.com/api/3/contacts/123/scoreValues",
                    },
                    "id": "123",
                    "organization": None,
                }
            ],
            "contactList": {
                "contact": "123",
                "list": "456",
                "form": None,
                "seriesid": "0",
                "sdate": "2017-07-24T12:09:52-05:00",
                "status": 1,
                "responder": "1",
                "sync": "0",
                "unsubreason": "",
                "campaign": None,
                "message": None,
                "first_name": "John",
                "last_name": "Doe",
                "ip4Sub": "0",
                "sourceid": "0",
                "autosyncLog": None,
                "ip4_last": "0",
                "ip4Unsub": "0",
                "unsubscribeAutomation": None,
                "links": {
                    "automation": None,
                    "list": "https://test-api.example.com/api/3/contactLists/789/list",
                    "contact": "https://test-api.example.com/api/3/contactLists/789/contact",
                    "form": None,
                    "autosyncLog": None,
                    "campaign": None,
                    "unsubscribeAutomation": None,
                    "message": None,
                },
                "id": "789",
                "automation": None,
            },
        }

        requests_mock.post(
            "https://test-api.example.com/api/3/contactLists",
            json=mock_response,
            status_code=201,
        )

        params = ContactListUpdateParams(contact=123, list=456, status=1)
        result = ac_client.add_contact_to_list(params)

        assert result["contactList"]["contact"] == "123"
        assert result["contactList"]["list"] == "456"
        assert result["contactList"]["status"] == 1
        assert requests_mock.last_request.json() == {
            "contactList": {"contact": 123, "list": 456, "status": 1}
        }

    def test_update_list_success(self, requests_mock, ac_client):
        list_id = 123
        mock_response = {
            "list": {
                "name": "Updated Newsletter",
                "stringid": "updated-newsletter",
                "cdate": "2023-01-01T10:00:00-05:00",
                "udate": "2023-01-02T10:00:00-05:00",
                "userid": "1",
                "sender_url": "http://updated-example.com",
                "sender_reminder": "You subscribed to our updated newsletter",
                "send_last_broadcast": "0",
                "carboncopy": "",
                "subscription_notify": "",
                "unsubscription_notify": "",
                "private": "0",
                "analytics_domains": None,
                "analytics_source": "",
                "analytics_ua": "",
                "twitter_token": "",
                "twitter_token_secret": "",
                "facebook_session": None,
                "require_name": "0",
                "get_unsubscribe_reason": "0",
                "to_name": "Subscriber",
                "optinoptout": "1",
                "sender_name": "",
                "sender_addr1": "",
                "sender_addr2": "",
                "sender_city": "",
                "sender_state": "",
                "sender_zip": "",
                "sender_country": "",
                "sender_phone": "",
                "fulladdress": "",
                "optinmessageid": "0",
                "optoutconf": "0",
                "deletestamp": None,
                "links": {
                    "contactGoalLists": f"https://test-api.example.com/api/3/lists/{list_id}/contactGoalLists",
                    "user": f"https://test-api.example.com/api/3/lists/{list_id}/user",
                    "addressLists": f"https://test-api.example.com/api/3/lists/{list_id}/addressLists",
                },
                "id": str(list_id),
                "user": "1",
            }
        }
        requests_mock.put(
            f"https://test-api.example.com/api/3/lists/{list_id}",
            json=mock_response,
            status_code=200,
        )

        params = ListUpdateParams(
            name="Updated Newsletter",
            sender_url="http://updated-example.com",
            sender_reminder="You subscribed to our updated newsletter",
        )
        result = ac_client.update_list(list_id, params)

        assert result == mock_response
        assert requests_mock.called
        assert requests_mock.last_request.json() == {
            "list": {
                "name": "Updated Newsletter",
                "sender_url": "http://updated-example.com",
                "sender_reminder": "You subscribed to our updated newsletter",
                "send_last_broadcast": 0,
                "carboncopy": "",
                "subscription_notify": "",
                "unsubscription_notify": "",
            }
        }

    def test_create_list_group_permission_success(self, requests_mock, ac_client):
        mock_response = {
            "listGroup": {
                "list": "19",
                "group": "1",
                "links": {
                    "list": "https://account.api-us1.com/api/3/listGroups/55/list",
                    "group": "https://account.api-us1.com/api/3/listGroups/55/group",
                },
                "id": "55",
            }
        }

        requests_mock.post(
            "https://test-api.example.com/api/3/listGroups",
            json=mock_response,
            status_code=201,
        )

        params = ListGroupPermissionParams(listid=19, groupid=1)
        result = ac_client.create_list_group_permission(params)

        assert result["listGroup"]["list"] == "19"
        assert result["listGroup"]["group"] == "1"
        assert result["listGroup"]["id"] == "55"
        assert requests_mock.last_request.json() == {
            "listGroup": {"listid": 19, "groupid": 1}
        }
