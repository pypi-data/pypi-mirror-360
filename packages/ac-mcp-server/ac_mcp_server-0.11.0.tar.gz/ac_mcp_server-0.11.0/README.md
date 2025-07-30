# AC MCP Server

A simple, local mcp server to interact with the ActiveCampaign platform.

# Usage

## Setup
If you do not already have `uv` installed, do so:

```
brew install uv
```

If you don't already have `brew` installed, do that first:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Install the server in Claude Desktop

* Open Claude Desktop
* Go to Settings -> Developer
* Click "Edit Config"
* Open the file it points you to (`~/Library/Application Support/Claude/claude_desktop_config.json` on mac)
* Add the server. **NOTE:** You must change the `env` section to include your AC API URL and Token from your Settings -> Developer page:
    ```
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

# Development 

## Setup

Pull down this repository and install dependencies

```
git clone git@gitlab-ssh.devops.app-us1.com:ai/mcp/ac-mcp-server.git
uv sync
```

## Run the server

Change your Claude desktop configuration file to use your local server. Restart Claude desktop to pick up new changes.

```
{
    "mcpServers": {
        "activecampaign": {
            "command": "uv",
            "args": [
                "--directory",
                "/Users/<YOUR USER DIRECTORY>/dev/ac-mcp-server",
                "run",
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

## Testing

Run tests:

```
pytest 
```

# Publishing Changes

We publish this project publicly to the PyPI repository [ac-mcp-server](https://pypi.org/project/ac-mcp-server/). We are using the [hatchling build system](https://hatch.pypa.io/1.9/config/metadata/), see their docs if you need to modify anything about the information published with this project.

## Releaseing from CI

> These steps are currently manual as we work through any kinks. Publishing should be automatic once we trust it

1. Make sure the version field in `pyproject.toml` has been updated
2. Make sure you have updated the Changelog in `public/README.md`
3. Validate that build and publishing works on your branch by running the `publish-to-testpypi-manual` manual step on your branch pipeline
4. Once your change is merged, run the manual `publish-to-pypi-manual` manual step to release your changes

## Releasing manually

If there are any issues releasing the project from our Gitlab pipelines, you can 

1. Make sure the version field in `pyproject.toml` has been updated
2. Make sure you have updated the Changelog in `public/README.md`
2. Run `make publish-release` when publishing a final version you want all users to use

You will be prompted for a login. Credentials can be found in the 1Password AI Team vault, in `PyPI - AC MCP PyPI login`.
Username is `__token__`, and password can be found in the 1Password credentials.

# Troubleshooting
If you installed uv with pipx instead of brew, you will need to provide Claude with the binary path to uv.
Add this to the `env` section in your server config:

```
"PATH": "/Users/<YOUR USER DIRECTORY>/.local/bin:$PATH"
```