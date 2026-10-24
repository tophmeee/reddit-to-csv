# Installing the ProLevelMax MCP server

This is a remote server, so there is nothing to download or build.

1. Add this entry to the MCP settings:

```json
{
  "mcpServers": {
    "prolevelmax": {
      "url": "https://prolevelmax.com/mcp"
    }
  }
}
```

2. On first use the client opens a browser window to sign in to ProLevelMax (OAuth 2.1). New accounts can sign up on that page.
3. Test it by calling `procli_balance`, then `procli_discover` with a query such as "reddit search".

No API key or environment variable is needed.
