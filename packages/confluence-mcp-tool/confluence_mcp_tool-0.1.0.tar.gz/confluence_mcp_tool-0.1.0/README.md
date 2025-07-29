# Confluence Tool

A Python-based tool for retrieving and processing Confluence page content via the Atlassian API, with specialized support for extracting PlantUML diagrams and related page references.

## Features

- Retrieve Confluence page content using page urls
- Extract and decode PlantUML diagrams from Confluence macros, including:
  - Automatic filename detection
  - Support for compressed PlantUML data
  - URL-encoded content handling
- Parse and extract related page references with support for:
  - Full Confluence URLs
  - Shortened Confluence URLs (x/ format)
- REST API endpoint for accessing Confluence content
- Pydantic models for type-safe data handling

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Confluence API access credentials
- pipx for package

## Build Targets

This project comprises of 2 targets, each of which will have its corresponding configuration and installation steps:

1. MCP server
2. FastAPI server

## 1. MCP Server

### Deployment Options

#### a. Using Docker (Recommended)

The simplest way to run the service is using Docker Compose:

```bash
docker build -t confluence-mcp .
```

#### MCP client tool configuration

Here is an example of the configuration:

```json
{
    "mcpServers": {
        "confluence_mcp": {
            "command": "docker",
            "args": [
                "run",
                "--name", "confluence-mcp",
                "--interactive",
                "-e", "ATLASSIAN_USERNAME",
                "-e", "ATLASSIAN_API_KEY",
                "confluence-mcp:latest"
            ],
            "env": {
                "ATLASSIAN_USERNAME": "<your-username>",
                "ATLASSIAN_API_KEY": "<your-api-key>"
            }
        }
    }
}
```

#### b. Local Development Setup

If you want to run the service directly on your machine:

1. Install Python 3.11 or higher

2. Install Poetry for dependency management

3. Install pipx

   ```
   brew install pipx && pipx ensurepath
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Build for distribution:

   ```
   poetry build
   pipx install dist/*.whl --force
   ```



#### MCP tool configuration

Here is an example of the configuration:

```json
{
    "mcpServers": {
        "confluence_mcp": {
            "command": "<path-to-confluence-mcp>",
            "env": {
                "ATLASSIAN_USERNAME": "<your-username>",
                "ATLASSIAN_API_KEY": "<your-api-key>"
            }
        }
    }
}
```

Replace the following:
- **command**: execute shell command `which confluence-mcp` and use this value.
- **ATLASSIAN_USERNAME**: the [Atlassian username](https://id.atlassian.com/manage-profile/profile-and-visibility) which is usually the email address used for accessing Atlassian.
- **ATLASSIAN_API_KEY**: the [Atlassian API token](https://id.atlassian.com/manage-profile/security/api-tokens) generated.

Once updated, copy the JSON and use it with your **Claude desktop client's [config json file]($HOME/Library/Application Support/Claude/claude_desktop_config.json)** or **any MCP client's configuration file**. 



## 2. FastAPI server

### Configuration

Before running the service (using either method below), create a `.env` file in the root directory. You can copy the provided `.env.example` file as a template:

```bash
cp .env.example .env
```

Then edit the `.env` file with your specific values:

```env
ATLASSIAN_USERNAME=your-username       # Your Atlassian account email
ATLASSIAN_API_KEY=your-api-key        # API token from Atlassian account settings
```

### Deployment Options

#### 1. Using Docker Compose (Recommended)

The simplest way to run the service is using Docker Compose:

```bash
docker compose -f docker-compose.api.yml up --build
```

The service will be available at `http://localhost:8000`

#### 2. Local Development Setup

If you want to run the service directly on your machine:

1. Install Python 3.11 or higher

2. Install Poetry for dependency management

3. Install pipx

   ```
   brew install pipx && pipx ensurepath
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Build for distribution:

   ```
   poetry build
   pipx install dist/*.whl --force
   ```

6. Start the FastAPI service:

   ```bash
   poetry run confluence-tool
   OR
   confluence-tool
   ```

The service will be available at `http://localhost:8000`



###  API Documentation

#### Endpoints

- POST `/tool/confluence_reader/run`
  - Request Body: 
    ```json
    {
        "input": "https://scbtechx.atlassian.net/wiki/spaces/CP/pages/11136044830/Payment+Domain+Deployment",  // Confluence page URL
        "args": {}            // Optional additional arguments
    }
    ```
  - Response:
    ```json
    {
        "output": {
            "title": "Page Title",
            "content": "HTML content",
            "plant_uml": {
                "filename": "diagram.puml",
                "plant_uml": "PlantUML content"
            },
            "related_pages_page_ids": ["123456", "789012"]
        }
    }
    ```



## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information about contributing to this repository.

## Authors

- Michael Tan <michael.tan@scbtechx.io>
- Sathish Kumar <sathishkumar.gunasekaran@scbtechx.io>