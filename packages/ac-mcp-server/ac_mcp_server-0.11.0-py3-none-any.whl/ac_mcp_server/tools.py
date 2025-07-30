import os
from typing import Literal, Optional, Union, Any, List
from ac_mcp_server.ac_client import ACMCPHttpClient, ACMCPHttpClientAuth
from ac_mcp_server.types import (
    ContactCreateParams,
    ContactTagParams,
    TagCreateParams,
    ContactCustomFieldCreateParams,
    FieldOptionBulkCreateParams,
    ContactFieldRelCreateParams,
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
    ListGroupPermissionParams,
    ContactListUpdateParams,
    ListCreateParams,
    ListUpdateParams,
)

default_auth = ACMCPHttpClientAuth(
    url=os.getenv("AC_API_URL"),
    header_name="Api-Token",
    header_value=os.getenv("AC_API_TOKEN"),
)


def list_contacts(
    params: ContactListParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Get contacts with filtering and pagination options

    Parameters:
    - params: ContactListParams object containing:
      - segmentid: Filter by segment ID
      - formid: Filter by form ID
      - listid: Filter by list ID
      - tagid: Filter by tag ID
      - limit: Number of results to return (default 20)
      - offset: Offset for pagination
      - search: Partial string to match in email, first_name, last_name, or account name
      - orders: Dictionary for ordering results by specific fields. Valid fields are:
        "id", "cdate" (created date), "email", "first_name", "last_name", "name" (full name), "score"
        Example: {"email": "ASC"} to sort by email ascending
      - filters: Dictionary for time-based filtering. Valid filters are:
        "created_before", "created_after", "updated_before", "updated_after"
        Values can be strings in ISO format or datetime/date objects
        Example: {"created_after": "2023-01-01", "updated_before": "2023-12-31"}
      - id_greater: Return contacts with ID greater than this (recommended for pagination)
      - seriesid: Filter by series ID
      - waitid: Filter by wait ID
      - status: Contact status (ANY=-1, UNCONFIRMED=0, ACTIVE=1, UNSUBSCRIBED=2, BOUNCED=3)
    """
    return ACMCPHttpClient(auth).list_contacts(params)


def get_contact(
    contact_id: int, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """Get a contact by ID"""
    return ACMCPHttpClient(auth).get_contact(contact_id)


def create_or_update_contact(
    params: ContactCreateParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Create or update a contact, using the email as the unique identifier
    fieldValues fieldIds can be found or created by using the list_contact_custom_fields and create_contact_custom_field tools.
    Always try to find a similar field name or perstag to the one you want to create, even if it isn't exactly the same. Stop and prompt
    the user if you can't find it to ask if they want to create a new field.
    """
    return ACMCPHttpClient(auth).create_or_update_contact(params)


def list_tags(
    params: TagListParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    List, search, and filter tags

    Parameters:
    - params: TagListParams object containing:
      - search_filters: Dictionary of operators and values to filter tags by name
        Valid operators: "eq", "neq", "lt", "lte", "gt", "gte", "contains", "starts_with"
        Example: {"contains": "lead"} to find tags containing "lead"
      - order_method: How to order results - "weight", "asc", or "desc"
        - weight: Exact matches first, then matches starting with search term, then others
        - asc/desc: Ascending or descending alphabetical order
      - limit: Number of results to return (default 100)
      - offset: Offset for pagination
    """
    return ACMCPHttpClient(auth).list_tags(params)


def get_tag(tag_id: int, auth: ACMCPHttpClientAuth = default_auth) -> dict[str, Any]:
    """
    Get a tag by ID

    Parameters:
    - tag_id: The ID of the tag to retrieve
    """
    return ACMCPHttpClient(auth).get_tag(tag_id)


def create_contact_tag(
    params: TagCreateParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Create a new contact tag

    Parameters:
    - params: TagCreateParams object containing:
      - tag: The name of the tag
      - description: Optional description of the tag (default empty string)
    """
    return ACMCPHttpClient(auth).create_contact_tag(params)


def add_tag_to_contact(
    params: ContactTagParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Add a tag to a contact

    Parameters:
    - params: ContactTagParams object containing:
      - contact: The ID of the contact
      - tag: The ID of the tag to add to the contact
    """
    return ACMCPHttpClient(auth).add_tag_to_contact(params)


def list_contact_custom_fields(
    params: ContactCustomFieldListParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    List all contact custom fields with pagination options

    Parameters:
    - params: ContactCustomFieldListParams object containing:
      - limit: Number of results to return
      - offset: Offset for pagination
    """
    return ACMCPHttpClient(auth).list_contact_custom_fields(params)


def get_contact_custom_field(
    field_id: int, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Get a contact custom field by ID

    Parameters:
    - field_id: The ID of the custom field to retrieve
    """
    return ACMCPHttpClient(auth).get_contact_custom_field(field_id)


def create_contact_custom_field(
    params: ContactCustomFieldCreateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Create a contact custom field. Always create field options after creating fields of type "dropdown", "listbox", "radio", or "checkbox".

    Parameters:
    - params: ContactCustomFieldCreateParams object containing:
      - title: The name of the custom field
      - descript: Optional description of the field
      - type: The type of field (e.g., "text", "textarea", "date", "listbox", "radio", "checkbox", "hidden", "datetime")
      - perstag: Optional personalization tag name
      - defval: Optional default value
      - visible: Whether this field is visible in forms
      - ordernum: The order of this field relative to others
    """
    return ACMCPHttpClient(auth).create_contact_custom_field(params)


def create_field_options(
    params: FieldOptionBulkCreateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Create options for a dropdown, listbox, radio, or checkbox contact custom field

    Parameters:
    - params: FieldOptionBulkCreateParams object containing a list of:
      - orderid: The order in which to display the option
      - value: The value of the option
      - label: The label to display for the option
      - isdefault: Whether this option is selected by default
      - field: The ID of the custom field these options belong to
    """
    return ACMCPHttpClient(auth).create_field_options(params)


def create_contact_field_relationship(
    params: ContactFieldRelCreateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Associate a contact custom field with a contact list

    Parameters:
    - params: ContactFieldRelCreateParams object containing:
      - relid: The ID of the contact list
      - field: The ID of the custom field
    """
    return ACMCPHttpClient(auth).create_contact_field_relationship(params)


def list_contact_field_values(
    params: ContactFieldValueListParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    List all contact custom field values

    Parameters:
    - params: ContactFieldValueListParams object containing:
      - filters: Optional dictionary to filter by fieldid conditions (e.g., {"fieldid": 123})
      - limit: Number of results to return
      - offset: Offset for pagination
    """
    return ACMCPHttpClient(auth).list_contact_field_values(params)


def get_contact_field_value(
    field_value_id: int, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Get a contact custom field value by ID

    Parameters:
    - field_value_id: The ID of the field value to retrieve
    """
    return ACMCPHttpClient(auth).get_contact_field_value(field_value_id)


def create_contact_field_value(
    params: ContactFieldValueCreateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Create a contact custom field value. Contact field values can also be set in bulk in the payload to create or update a contact.

    Parameters:
    - params: ContactFieldValueCreateParams object containing:
      - contact: The ID of the contact
      - field: The ID of the custom field
      - value: The value to store in the field. Format depends on field type:
        - text/textarea/hidden: Simple string value
        - dropdown/radio: Exact option value
        - date: "YYYY-MM-DD" format
        - datetime: ISO format "YYYY-MM-DDThh:mm:ssZ"
        - checkbox (multiple): "||Option 1||Option 3||" format
        - checkbox (single): "||Option 2||" format
      - useDefaults: Optional boolean to set default values for required fields on the contact record
    """
    return ACMCPHttpClient(auth).create_contact_field_value(params)


def update_contact_field_value(
    field_value_id: int,
    params: ContactFieldValueUpdateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Update a contact custom field value

    Parameters:
    - field_value_id: The ID of the field value to update
    - params: ContactFieldValueUpdateParams object containing:
      - value: The new value for the field. Format depends on field type:
        - text/textarea/hidden: Simple string value
        - dropdown/radio: Exact option value
        - date: "YYYY-MM-DD" format
        - datetime: ISO format "YYYY-MM-DDThh:mm:ssZ"
        - checkbox (multiple): "||Option 1||Option 3||" format
        - checkbox (single): "||Option 2||" format
      - useDefaults: Optional boolean to set default values for required fields on the contact record
    """
    return ACMCPHttpClient(auth).update_contact_field_value(field_value_id, params)


def list_email_activities(
    params: EmailActivityListParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    List email activities from ActiveCampaign.

    For best results, only single records should be requested rather than running the call unfiltered.

    Parameters:
    - params: EmailActivityListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "subscriberid", "fieldid", "tstamp", "id" - subscriberid is a contact id
        Example: {"tstamp": "DESC"} to sort by timestamp descending
      - filters: Optional dictionary for filtering by specific fields. Valid filters are:
        "subscriberid", "fieldid"
        Example: {"subscriberid": "1641"} to filter by subscriber ID
    """
    return ACMCPHttpClient(auth).list_email_activities(params)


def list_campaigns(
    params: CampaignListParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    List all campaigns from ActiveCampaign with comprehensive filtering options.

    Parameters:
    - params: CampaignListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "sdate" (scheduled send date), "mdate" (modifed date), "ldate" (last sent date), "status"
        Example: {"sdate": "DESC"} to sort by scheduled send date descending
      - filters: Optional CampaignFilterField object containing:
        - type: Campaign type ("single", "recurring", "split", "responder", "reminder", "special", "activerss", "text")
        - list_id: Filter by specific list ID
        - automation: Filter by automation flag
        - willrecur: Filter by recurring campaign flag
        - seriesid: Filter by series ID
        - label_name: Filter by label name
        - name: Filter by campaign name (partial match)
        - id: Filter by campaign ID
        - status: Filter by comma-separated list of status integers (e.g., "1,2,3")
      - Boolean filters:
        - has_message: Filter for campaigns with messages
        - has_message_content: Filter for campaigns with message content
        - has_form: Filter for campaigns with forms
      - Other filters:
        - campaignListing: Filter by campaign listing ID
        - status: Filter by campaign status name ("drafts", "scheduled", "currently-sending", etc.)
        - excludeTypes: Comma-separated list of campaign types to exclude
    """
    return ACMCPHttpClient(auth).list_campaigns(params)


def get_campaign(
    campaign_id: int, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Get a campaign by ID from ActiveCampaign.

    Parameters:
    - campaign_id: The ID of the campaign to retrieve
    """
    return ACMCPHttpClient(auth).get_campaign(campaign_id)


def get_campaign_links(
    campaign_id: int, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Retrieve links associated with a campaign from ActiveCampaign.

    Parameters:
    - campaign_id: The ID of the campaign to retrieve links for
    """
    return ACMCPHttpClient(auth).get_campaign_links(campaign_id)


def list_automations(
    params: AutomationListParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    List all automations from ActiveCampaign with comprehensive filtering and ordering options.

    Parameters:
    - params: AutomationListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - filters: Optional AutomationFilterField object containing:
        - name: Filter by automation name (partial match)
        - status: Filter by exact status (1 - active, 2 - inactive)
        - ids: Comma-separated list of automation IDs
        - tag: Tag ID to filter by
        - triggers: Comma-separated list of start trigger types
        - actions: Comma-separated list of action block types
        - label_name: Filter by label/folder name
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "name", "status", "entered (number of contacts that have entered the automation)", "cdate" (created date), "mdate" (modified date), "revisions"
        Example: {"name": "ASC", "cdate": "DESC"} to sort by name ascending, then created date descending
      - label: Filter by label/folder ID (integer)
      - search: String search in automation name
      - active: Filter by active status (true/false)
      - has_message: Filter automations that have messages (true/false)
      - enhance: Add enhanced data including blocks, goals, campaigns, counts, and labels (true/false)
    """
    return ACMCPHttpClient(auth).list_automations(params)


def list_contact_automations(
    params: ContactAutomationListParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Get information about automation runs, for use when a user wants to know more about which automations a contact was in, which contacts went through which automation,
     or just generally more information about how an automation performs.

    Parameters:
    - params: ContactAutomationListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
      - filters: Optional ContactAutomationFilters object containing:
        - seriesid: Filter by automation ID (exact match)
        - adddate: Filter by date added (string or ContactAutomationDateFilter object with eq/gt/gte/lt/lte operators)
        - status: Filter by status (1 - autlmation in progress, 2 - automation has completed/ended)
        - subscriberid: Filter by contact ID (exact match)
      - orders: Optional dictionary for ordering results by specific fields. Valid fields are:
        "seriesid", "adddate", "status", "lastblock", "subscriberid", "name", "first_name", "last_name", "email", "cdate", "score", "goal_completion"
        Example: {"name": "ASC", "adddate": "DESC"} to sort by contact name ascending, then date added descending
      - q: Search term across contact fields (email, first_name, last_name, customer_acct_name, phone)
      - min_time: Filter by minimum timespan in automation (seconds)
      - max_time: Filter by maximum timespan in automation (seconds, 0 for immediately completed)
      - tags: List of tag IDs to filter by
      - g_tags: Goal-specific tag filter (list of tag IDs)
      - lists: List of list IDs to filter by
      - g_lists: Goal-specific list filter (list of list IDs)
      - g_id: Filter by goal ID
      - g_status: Goal completion status (0=incomplete, 1=complete)
      - g_min_time: Minimum goal completion time (seconds)
      - g_max_time: Maximum goal completion time (seconds)
      - scoreid: Score ID (required for score-based ordering)
      - include: Include related models in response
    """
    return ACMCPHttpClient(auth).list_contact_automations(params)


def get_contact_automation(
    contact_automation_id: int, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Retrieve a specific contact automation record by ID.

    This provides detailed information about a specific automation run for a contact,
    including status, progress, completion details, and timing information.

    Parameters:
    - contact_automation_id: The ID of the contact automation record to retrieve
    """
    return ACMCPHttpClient(auth).get_contact_automation(contact_automation_id)


def add_contact_to_automation(
    params: ContactAutomationCreateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Add a contact to an automation.

    This will start the automation for the specified contact. The contact will begin
    at the first step of the automation sequence.

    Parameters:
    - params: ContactAutomationCreateParams object containing:
      - contact: The ID of the contact to add to the automation
      - automation: The ID of the automation to add the contact to
    """
    return ACMCPHttpClient(auth).add_contact_to_automation(params)


def remove_contact_from_automation(
    contact_automation_id: int, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Remove a contact from an automation.

    This will stop the automation for the contact and remove them from the automation sequence.
    The contact will no longer receive any further communications from this automation.

    Parameters:
    - contact_automation_id: The ID of the contact automation record to remove/delete
    """
    return ACMCPHttpClient(auth).remove_contact_from_automation(contact_automation_id)


def list_groups(
    params: GroupListParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    List all user groups from ActiveCampaign.

    This tool is essential for list management workflows as it provides the available groups
    that can be associated with lists. When creating a new list, you must assign it to a group
    for it to be visible in the ActiveCampaign user interface.

    Parameters:
    - params: GroupListParams object containing:
      - limit: Optional number of results to return
      - offset: Optional offset for pagination
    """
    return ACMCPHttpClient(auth).list_groups(params)


def list_lists(
    params: ListListParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    List all lists from ActiveCampaign with filtering and pagination options.

    This tool allows you to retrieve and filter lists in your ActiveCampaign account.
    Lists are used to organize contacts and manage email campaigns.

    Parameters:
    - params: ListListParams object containing:
      - limit: Optional number of results to return (default 20)
      - offset: Optional offset for pagination
      - filters: Optional ListFilters object for filtering:
        - name (str): Filters lists where the name field is like the provided value
        - id: Filters lists where the id field is like the provided value
        - channel ("email", "sms", "all"): Filters by channel. Defaults to "email". "all" removes channel filtering.

      - orders: Optional ListOrders object for ordering results:
        - name: Optional[ListNameOrderSetting ("ASC", "DESC", "weight")] - Special "weight" case, then sorts by name ASC as secondary.
        - id: Optional[ListSortDirection ("ASC", "DESC")]
        - channel: Optional[ListSortDirection ("ASC", "DESC")]
        - userid: Optional[ListSortDirection ("ASC", "DESC")]
        - created_timestamp: Optional[ListSortDirection ("ASC", "DESC")]
        - active_subscribers: Optional[ListSortDirection ("ASC", "DESC")]

    Usage:
    Use this tool to browse available lists, search for specific lists by name,
    or get an overview of your list organization before creating new lists or
    managing existing ones.
    """
    return ACMCPHttpClient(auth).list_lists(params)


def get_list(list_id: int, auth: ACMCPHttpClientAuth = default_auth) -> dict[str, Any]:
    """
    Retrieve a single list by ID from ActiveCampaign.

    This tool fetches detailed information about a specific list, including all
    configuration settings, tracking options, and metadata.

    Parameters:
    - list_id: The ID of the list to retrieve
    """
    return ACMCPHttpClient(auth).get_list(list_id)


def create_list(
    params: ListCreateParams, auth: ACMCPHttpClientAuth = default_auth
) -> dict[str, Any]:
    """
    Create a new list in ActiveCampaign.

    This tool creates a new list for organizing contacts and managing email campaigns.

    Parameters:
    - params: ListCreateParams object containing:
      - name: Required name of the list
      - channel: Optional channel type ("sms" or "email", default: "email")
      - sender_url: Required sender URL for compliance
      - sender_reminder: Required reminder text for subscribers
      - send_last_broadcast: Optional flag for sending last broadcast (default: 0)
      - carboncopy: Optional carbon copy email address
      - subscription_notify: Optional email for subscription notifications
      - unsubscription_notify: Optional email for unsubscription notifications

    Usage:
    Use this tool to create new lists for organizing contacts. Consider using
    list_groups() to see available groups if you want to associate the new list
    with a group for better organization using create_list_group_permission().

    Note: For a list to be visible in the ActiveCampaign user interface for non-administrators,
    it may need to be associated with a user group.
    """
    return ACMCPHttpClient(auth).create_list(params)


def update_list(
    list_id: int,
    params: ListUpdateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Update an existing list in ActiveCampaign. You must provide all required fields, you cannot do a partial update.

    Parameters:
    - list_id: The ID of the list to update.
    - params: ListUpdateParams object containing the fields to update.
      - name: Name of the list
      - sender_url: Sender URL for compliance
      - sender_reminder: Seminder text for subscribers
      - send_last_broadcast: Optional flag for sending last broadcast
      - carboncopy: Optional carbon copy email address
      - subscription_notify: Optional email for subscription notifications
      - unsubscription_notify: Optional email for unsubscription notifications
    """
    return ACMCPHttpClient(auth).update_list(list_id, params)


def create_list_group_permission(
    params: ListGroupPermissionParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Associate a list with a user group for enhanced organization and visibility.

    This tool creates a list group permission, which associates a specific list with a user group
    in ActiveCampaign. This association enables group-based permissions and makes lists visible
    in the appropriate sections of the ActiveCampaign interface.

    Parameters:
    - params: ListGroupPermissionParams object containing:
      - list: The ID of the list to associate with the group
      - group: The ID of the group to associate with the list

    Note: This is typically used after creating a list to ensure it appears in the correct
    sections of the ActiveCampaign interface for the appropriate user groups.
    """
    return ACMCPHttpClient(auth).create_list_group_permission(params)


def add_contact_to_list(
    params: ContactListUpdateParams,
    auth: ACMCPHttpClientAuth = default_auth,
) -> dict[str, Any]:
    """
    Subscribe a contact to a list or update their subscription status.

    This tool allows you to add a contact to a list with a specific status, enabling
    contact list management and subscription control. Use this to subscribe contacts
    to lists for email campaigns and marketing automation.

    Parameters:
    - params: ContactListUpdateParams object containing:
      - contact: The ID of the contact to add to the list
      - list: The ID of the list to add the contact to
      - status: The subscription status for the contact:
        - 1 = Active (subscribed)
        - 2 = Unsubscribed
        - 0 = Unconfirmed

    Important Notes:
    - Setting status from unsubscribed (2) to active (1) may require additional confirmation
    - Use status 1 for normal subscription workflows
    - Status 0 is used for double opt-in processes
    - The contact and list must already exist in ActiveCampaign

    Use Cases:
    - Subscribe new contacts to marketing lists
    - Update subscription status for existing contacts
    """
    return ACMCPHttpClient(auth).add_contact_to_list(params)
