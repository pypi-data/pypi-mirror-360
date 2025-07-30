# Daydream Contribution Guide

We welcome contributions to improve the Daydream project!

We are happy to receive pull requests and issues. Issues are helpful for talking through a more time consuming change ahead of time.

Contributions to this project are released to the public under the project's open source license, which is specified in the LICENSE file.

## Setup a Dev environment

You'll need [uv](https://github.com/astral-sh/uv) to develop locally.

On macOS:

```
brew install uv
```

### Linting & Formatting

This project uses [pre-commit](https://pre-commit.com/) to manage linting and formatting via pre-commit hooks. To set it up:

```
uv run pre-commit install
```

Going forward, linters and formatters will run automatically before each commit.

### MCP Logs on macOS

* `~/Library/Logs/Claude/mcp.log`
* `~/Library/Logs/Claude/mcp-server-aptible.log`
