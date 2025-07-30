# MCP server for Blackduck Coverity

## Available MCP Tools

 * `get_issue_info`
 * `get_issue_diagnostics`
 * `triage_issue`

## Usage

### MCP server configuration

Ensure *uvx* is installed.

```json
"coverity": {
  "command": "/path/to/uvx",
  "args": [
    "coverity-mcp",
    "--base-url", "https://coverity.examples.com/api/v2",
    "--certificate-path", "optional-path-to-certificate",
    "--username", "user",
    "--key", "AABBCC",
    "--trim-path-prefix", "/",
    "run"
  ],
  "alwaysAllow": [
    "get_issue_diagnostics",
    "get_issue_info"
  ],
  "disabled": false
}
```

### Local MCP server configuration

```json
"coverity": {
  "cwd": "/full/path/to/coverity-mcp",
  "command": "/path/to/uv",
  "args": [
    "run", "./main.py",
    "--base-url", "https://coverity.example.com/api/v2",
    "--certificate-path", "optional-path-to-certificate",
    "--username", "user",
    "--key", "AABBCC",
    "--trim-path-prefix", "/",
    "run"
  ],
  "alwaysAllow": [
    "get_issue_diagnostics",
    "get_issue_info"
  ],
  "disabled": false
}
```
