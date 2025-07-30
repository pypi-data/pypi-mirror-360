# CBUAE MCP Server

A Model Context Protocol (MCP) server for querying and analyzing Central Bank of UAE (CBUAE) policies and regulations.

## Features

- **Policy Search**: Search through CBUAE policies using fuzzy matching
- **Web Integration**: Query the live CBUAE website (https://rulebook.centralbank.ae/) directly
- **Hybrid Search**: Search both local database and live website for comprehensive results
- **Gap Analysis**: Analyze gaps between bank policies and CBUAE regulations
- **Policy Listing**: List all available policies in the database
- **Caching**: Intelligent caching of web requests to improve performance

## Installation

### From PyPI (Recommended)

```bash
pip install cbuae-mcp
```

### From Source

```bash
git clone https://github.com/your-repo/cbuae-mcp.git
cd cbuae-mcp
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/your-repo/cbuae-mcp.git
cd cbuae-mcp
./scripts/install-dev.sh
```

## Quick Start

### Command Line Usage

```bash
# Start the MCP server
cbuae-mcp

# With debug logging
cbuae-mcp --debug
```

### Programmatic Usage

```python
from cbuae_mcp import create_server

# Create and run the server
server = create_server()
server.run()
```

## Available Tools

### Local Database Tools

#### 1. `query_cbuae_policy`
Search CBUAE policies using fuzzy matching in the local database.

**Parameters:**
- `query` (string): The search query to find relevant policies

**Returns:**
- Dictionary containing query results with matching policies

#### 2. `analyze_policy_gaps`
Analyze gaps between bank policies and CBUAE regulations.

**Parameters:**
- `bank_policy` (string): The bank's policy text to analyze
- `reg_id` (string): The CBUAE regulation ID to compare against

**Returns:**
- Dictionary containing identified gaps and recommendations

#### 3. `list_available_policies`
List all available CBUAE policies in the database.

**Returns:**
- Dictionary containing all available policies with their IDs, titles, and categories

### Web Integration Tools

#### 4. `search_cbuae_website`
Search for policies directly on the CBUAE website.

**Parameters:**
- `query` (string): The search query to find policies on the website

**Returns:**
- Dictionary containing search results from the CBUAE website

#### 5. `fetch_policy_from_website`
Fetch the full content of a specific policy from the CBUAE website.

**Parameters:**
- `policy_url` (string): The URL of the policy to fetch

**Returns:**
- Dictionary containing the policy content and metadata

#### 6. `get_cbuae_policy_categories`
Get available policy categories from the CBUAE website.

**Returns:**
- Dictionary containing available policy categories

#### 7. `hybrid_policy_search`
Search both local policy database and CBUAE website for comprehensive results.

**Parameters:**
- `query` (string): The search query to find policies

**Returns:**
- Dictionary containing combined search results from both sources

## Usage with MCP Clients

### Method 1: Using pip installation (Recommended)

After installing with `pip install cbuae-mcp`, add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "cbuae": {
      "command": "cbuae-mcp",
      "args": [],
      "description": "CBUAE Policy Agent - Search and analyze Central Bank of UAE policies and regulations"
    }
  }
}
```

### Method 2: Using Python module

```json
{
  "mcpServers": {
    "cbuae": {
      "command": "python",
      "args": ["-m", "cbuae_mcp.server"],
      "description": "CBUAE Policy Agent - Search and analyze Central Bank of UAE policies and regulations"
    }
  }
}
```

### Method 3: Development setup

```json
{
  "mcpServers": {
    "cbuae": {
      "command": "python",
      "args": ["-m", "cbuae_mcp.cli"],
      "cwd": "/path/to/cbuae-mcp",
      "description": "CBUAE Policy Agent - Search and analyze Central Bank of UAE policies and regulations"
    }
  }
}
```

## Testing

Run the test scripts to verify functionality:

**Local functionality:**
```bash
python test_mcp.py
```

**Web integration:**
```bash
python test_web_integration.py
```

**Complete test suite:**
```bash
python test_web_scraper.py
```

## Troubleshooting

### Common Issues

#### 1. "can't open file 'main.py': No such file or directory"
- **Solution**: Use the provided `start-server.sh` script or ensure `cwd` is set correctly in your MCP configuration
- **Check**: Verify the working directory path in your configuration

#### 2. "Module 'cbuae' not found"
- **Solution**: Ensure `PYTHONPATH` includes the server directory
- **Check**: Use the startup script which sets the Python path automatically

#### 3. Server disconnects immediately
- **Debug**: Check the MCP client logs for stderr output
- **Verify**: Run `./start-server.sh` manually to test server startup

#### 4. Web scraping returns no results
- **Note**: The CBUAE website may have access restrictions
- **Fallback**: The server automatically falls back to local database queries
- **Check**: Verify internet connection and website accessibility

### Debug Mode

Run the server manually to see debug output:
```bash
./start-server.sh
```

This will show:
- Python executable path
- Working directory
- Python path
- Import status
- Startup messages

### Log Output

The server outputs debugging information to stderr, which appears in MCP client logs:
- Import success/failure
- Server startup status
- Error messages with details

## Policy Database

The server loads policies from `policy_db.json` or falls back to mock data. To add real policies:

1. Place PDF files in the `docs/` directory
2. Update the mappings in `extract.py`
3. Run `python extract.py` to extract and store policy text

## Available Policies

### Local Database
- **AML_2018**: Anti-Money Laundering regulations
- **CAPITAL_2023**: Capital Adequacy Regulation
- **PTS_2024**: Payment Token Services Regulation
- **CBUAE_EN_1691_VER2**: Standards re Capital Adequacy of Banks in the UAE
- **CBUAE_EN_3934_VER1**: Regulations Re Capital Adequacy

### Web Integration
- Direct access to live CBUAE policies at https://rulebook.centralbank.ae/
- Real-time policy content retrieval
- Automatic caching for improved performance

## Web Integration Features

- **Real-time Access**: Query the live CBUAE website for the most current policies
- **Intelligent Caching**: Automatic caching of web requests with configurable duration
- **Error Handling**: Robust error handling for network issues and access restrictions
- **Hybrid Search**: Combine local database and web results for comprehensive coverage
- **Content Extraction**: Extract structured policy content from web pages

## Example Usage

```python
# Search locally
result = query_cbuae_policy("capital adequacy")

# Search website
web_result = search_cbuae_website("banking regulation")

# Fetch specific policy
policy = fetch_policy_from_website("https://rulebook.centralbank.ae/en/rulebook/capital-adequacy")

# Hybrid search (both local and web)
hybrid_result = hybrid_policy_search("anti-money laundering")
```

## License

This project is designed for compliance and regulatory analysis purposes.