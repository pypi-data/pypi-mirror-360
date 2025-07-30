# ActiveCampaign MCP Server

ActiveCampaign's MCP server is now available as a beta release. This enables AI clients to seamlessly take ActiveCampaign actions and interact with your ActiveCampaign data, opening up powerful new integration possibilities for our ecosystem. For more information and to provide feedback, visit https://www.activecampaign.com/mcp

## What is MCP?

MCP (Model Context Protocol) is an emerging standard that allows AI models to interact with applications through a consistent interface. It acts as an abstraction layer over HTTP, letting AI agents access application functionality without needing to understand specific API protocols.

## Beta Notice

The ActiveCampaign MCP Server is currently in beta. Features and functionality may change as we continue to improve the integration.

## Pre-requisites

You will need `uv`, a python package manager required to run the MCP server locally installed. We recommend installing through [Homebrew](https://brew.sh/) if you are on a Mac to make sure `uvx` is installed correctly on the system path for MCP clients.

To install `uvx` through homebrew, run these commands from your terminal:

```shell
# If you don't already have homebrew installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install uv
brew install uv
```

If you are not on a Mac, or prefer not to use Homebrew, visit [this link](https://docs.astral.sh/uv/getting-started/installation/) for detailed instructions on other ways to install uv.

### Finding your API token and URL in ActiveCampaign:

Reference [here](https://help.activecampaign.com/hc/en-us/articles/207317590-Getting-started-with-the-API) for instructions on finding your ActiveCampaign API token and URL.

## Using the MCP Server

### Claude Desktop

Download Claude Desktop [here](https://claude.ai/download).

Add the server configuration to your Claude Desktop config file. You can get to this file by opening the Claude settings and clicking on "Developer" and the "Edit Config". Claude will create an MCP configuration file for you and open your file explorer to show you where it is 
(usually located at `~/Library/Application Support/Claude/claude_desktop_config.json` in macOS). Copy in this configuration, replacing `<YOUR AC API TOKEN>` and `<YOUR AC API URL>` with the values from your account settings page:

```json
{
  "mcpServers": {
    "activecampaign": {
      "command": "uvx",
      "args": [
        "ac-mcp-server"
      ],
      "env": {
        "AC_API_TOKEN": "<YOUR AC API TOKEN>",
        "AC_API_URL": "<YOUR AC API URL>"
      }
    }
  }
}
```

Save the file and restart Claude. You should now be able to access all the tools!

Visit [this page](https://modelcontextprotocol.io/clients#claude-desktop) for more information and troubleshooting.

### Cursor

Create a `.cursor/mcp.json` file in your project:

```bash
mkdir -p .cursor && touch .cursor/mcp.json
```

Put the following configuration in the file:

```json
{
  "mcpServers": {
    "activecampaign": {
      "command": "uvx",
      "args": [
        "ac-mcp-server"
      ],
      "env": {
        "AC_API_TOKEN": "<YOUR AC API TOKEN>",
        "AC_API_URL": "<YOUR AC API URL>"
      }
    }
  }
}
```

Save the file and restart Cursor. You should now be able to access all the tools!

Visit [this page](https://docs.cursor.com/context/mcp) for more information and troubleshooting.

### Other MCP Clients

List of other popular MCP Clients are [here](https://modelcontextprotocol.io/clients).

### Troubleshooting

If you see an error like `Error: spawn uvx ENOENT`, you should be able to fix this by providing your client with the full path to `uvx`. Run this command in your terminal in and paste the full output into the `command` field in the JSON configuration:

```shell
which uvx
```

Your JSON configuration will then look something like this:
```json
{
  "mcpServers": {
    "activecampaign": {
      "command": "/Users/me/.local/bin/uvx",
      "args": [
        "ac-mcp-server"
      ],
      "env": {
        "AC_API_TOKEN": "<YOUR AC API TOKEN>",
        "AC_API_URL": "<YOUR AC API URL>"
      }
    }
  }
}
```

## Example Usage

Once set up, try these example prompts:

### Create and Modify Contacts
"Create a new contact in ActiveCampaign with email john@example.com, first name John, and last name Smith"

"Update ActiveCampaign contact john@example.com to change their phone number to 312-555-0123"

"Add contact sarah@company.com to the 'Newsletter Subscribers' list in ActiveCampaign"

"Set the ActiveCampaign custom field 'Company Size' to 'Enterprise' for John Smith"

### Get Insights from Your Campaign Data
"Show me my most recent email activities in ActiveCampaign"

"List all my ActiveCampaign campaigns and their performance metrics from this month"

"Get me the email activity for John Smith in ActiveCampaign"

"Give me details for my campaign 'Black Friday Sale 2024' in ActiveCampaign"

### Automation Management
"Show me all active automations in my ActiveCampaign account"

"Add Sarah Smith to the 'Welcome Series' automation in ActiveCampaign"

"List all ActiveCampaign automations that john@example.com is currently enrolled in"

"Remove John Smith from the 'Re-engagement Campaign' automation in ActiveCampaign"

### Tags and List Management
"Create a new tag called 'Webinar Attendee' in ActiveCampaign"

"Add the 'High Value Customer' tag to Sarah Smith in ActiveCampaign"

"Show me all ActiveCampaign contacts subscribed to the 'Monthly Newsletter' list"

"Update my 'Product Launch' list in ActiveCampaign to be 'Product Launch Updates'"

## Tools

This MCP server provides a set of tools for interacting with the ActiveCampaign API.

| Category | Tool Name | Description |
|----------|-----------|-------------|
| **Contacts** | list_contacts | Retrieve all contacts from your ActiveCampaign account, with basic filtering capabilities |
| **Contacts** | get_contact | Fetch details for a specific contact |
| **Contacts** | create_or_update_contact | Add a new contact to your account or update existing contact information |
| **Tags** | list_tags | Retrieve all available tags in your account |
| **Tags** | get_tag | Fetch details for a specific tag |
| **Tags** | create_contact_tag | Create a new tag for organizing contacts |
| **Tags** | add_tag_to_contact | Apply a tag to a specific contact |
| **Lists** | list_lists | Retrieve all contact lists in your account |
| **Lists** | get_list | Fetch details for a specific list |
| **Lists** | create_list | Create a new contact list |
| **Lists** | update_list | Modify existing list settings |
| **Lists** | add_contact_to_list | Change a contact's subscription status for specific lists |
| **Custom Fields** | list_contact_custom_fields | Retrieve all custom fields defined in your account |
| **Custom Fields** | get_contact_custom_field | Fetch details for a specific custom field |
| **Custom Fields** | create_contact_custom_field | Create a new custom field for contacts |
| **Custom Fields** | create_field_options | Create options for dropdown, listbox, radio, or checkbox custom fields |
| **Custom Fields** | create_contact_field_relationship | Associate a custom field with a contact list |
| **Custom Field Values** | list_contact_field_values | Retrieve custom field values for contacts |
| **Custom Field Values** | get_contact_field_value | Fetch a specific custom field value |
| **Custom Field Values** | create_contact_field_value | Set custom field values for contacts |
| **Custom Field Values** | update_contact_field_value | Modify existing custom field values |
| **Email Activities** | list_email_activities | Retrieve contact email engagement activities |
| **Campaigns** | list_campaigns | Retrieve all email campaigns in your account |
| **Campaigns** | get_campaign | Fetch details for a specific campaign |
| **Campaigns** | get_campaign_links | Get all tracked links from a specific campaign |
| **Automations** | list_automations | Retrieve all automations in your account |
| **Automations** | list_contact_automations | Show which automations a specific contact is enrolled in |
| **Automations** | get_contact_automation | Get details of a specific automation that a contact is enrolled in |
| **Automations** | add_contact_to_automation | Add a contact into an automation |
| **Automations** | remove_contact_from_automation | Remove a contact from an automation |
| **Groups** | list_groups | Retrieve all user groups from ActiveCampaign |
| **Groups** | create_list_group_permission | Associate a list with a user group for enhanced organization and visibility |

# Changelog

## 0.11.0

- Restructuring tool definitions to allow them to be mounted outside of FastMCP

## 0.10.1

- Some code cleanup

## 0.10.0

- Update create_contact_custom_field to make field visible by adding to all lists

## 0.9.1

- Update guidance on how to install and troubleshoot

## 0.9.0

- Relax required python version to >=3.10

## 0.8.1

 - Add `update_list` tool

## 0.8.0

 - Initial release