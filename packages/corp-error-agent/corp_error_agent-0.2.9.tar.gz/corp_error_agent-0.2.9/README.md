# Corp Error Agent
A lightweight runtime agent that captures uncaught exceptions and environment snapshots.

Install this in your project to capture errors and send them to a backend for further processing and fix suggestions.

## Backend URL Configuration

The backend URL defaults to `http://127.0.0.1:8000`, but you can change it in two ways:

1. **Environment Variable (recommended for quick changes):**
   - Set the environment variable `ERROR_AGENT_URL` to your backend URL before running your Python process.
     - On Windows (cmd): `set ERROR_AGENT_URL=http://your-backend:port`
     - On PowerShell: `$env:ERROR_AGENT_URL="http://your-backend:port"`
     - On Unix/bash: `export ERROR_AGENT_URL=http://your-backend:port`

2. **Persistent CLI Configuration:**
   - Use the provided CLI helper to set the backend URL once per machine:
     ```sh
     python -m corp_error_agent.cli configure --url http://your-backend:port
     ```
   - This stores the URL in a user config file for persistent use.

## Telemetry Server

You can use or further customize the [corp_error_agent_server](https://github.com/arielfayol37/corp_error_agent_server) Django REST project as a telemetry server for this package.

---
