# MCP MS SQL Server

A Model Context Protocol (MCP) server for Microsoft SQL Server that provides tools for database operations, data analysis, and visualization generation.

## Installation

```bash
pip install mcp-mssql-server

## Features

This MCP server provides 8 powerful tools:

1. **sql_query** - Execute SQL queries with permission controls
2. **get_database_info** - Get server and database information
3. **show_tables** - List all tables in the database
4. **describe_table** - Get detailed table structure information
5. **show_indexes** - Display table indexes
6. **generate_analysis_notebook** - Create Jupyter notebooks for data analysis
7. **generate_visualization** - Create interactive visualizations (bar, scatter, pie, line, heatmap, table)
8. **generate_powerbi_visualization** - Generate Power BI compatible data exports

## Installation

1. Clone this repository
2. Install dependencies using uv:

```bash
cd mcp-mssql-server
uv pip install -e .
```

## Configuration
use uv pip install -r requirements.txt to install all the requirements.

1. Copy the `.env` file and update with your database credentials:

```bash
# Database Type (mssql)
DB_TYPE=mssql

# SQL Server Configuration
MSSQL_SERVER=tcp:your-server.database.windows.net
MSSQL_PORT=1433
MSSQL_USER=your-username
MSSQL_PASSWORD=your-password
MSSQL_DATABASE=your-database
MSSQL_ENCRYPT=true
MSSQL_TRUST_SERVER_CERTIFICATE=true

# Security Settings
ALLOW_WRITE_OPERATIONS=false
ALLOW_INSERT_OPERATION=false
ALLOW_UPDATE_OPERATION=false
ALLOW_DELETE_OPERATION=false

# Performance Settings
CONNECTION_POOL_MIN=1
CONNECTION_POOL_MAX=10
QUERY_TIMEOUT=30000
```

2. Update the password field with your actual password.

## Usage

### Running the MCP Server

```bash
uv run python main.py
```

Or with logging:

```bash
uv run python main.py --log
uv run python mssql.py --log
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcp-mssql-server": {
    "command": "uv",
    "args": ["run", "python", "/path/to/mcp-mssql-server/mssql.py"]
  }
}
```

## Tools Documentation

### 1. sql_query
Execute any SQL query on the database.

```json
{
  "query": "SELECT TOP 10 * FROM users"
}
```

### 2. get_database_info
Get information about the SQL Server instance and available databases.

### 3. show_tables
List all tables in the current database.

```json
{
  "schema": "dbo"  // optional
}
```

### 4. describe_table
Get detailed information about a table's columns and structure.

```json
{
  "table_name": "users",
  "schema": "dbo"
}
```

### 5. show_indexes
Display indexes for a specific table or all tables.

```json
{
  "table_name": "users",  // optional
  "schema": "dbo"
}
```

### 6. generate_analysis_notebook
Create a Jupyter notebook with automated data analysis code.

```json
{
  "query": "SELECT * FROM sales_data",
  "output_file": "sales_analysis.ipynb"  // optional
}
```

### 7. generate_visualization
Create interactive visualizations from query results.

```json
{
  "query": "SELECT category, SUM(amount) as total FROM sales GROUP BY category",
  "viz_type": "bar",  // auto, bar, scatter, pie, line, heatmap, table
  "title": "Sales by Category"
}
```

### 8. generate_powerbi_visualization
Export data in Power BI compatible format.

```json
{
  "query": "SELECT * FROM sales_data",
  "viz_type": "auto"
}
```

## Security

- All write operations (INSERT, UPDATE, DELETE) are disabled by default
- Enable specific operations by setting the corresponding environment variables to `true`
- Connection uses encryption by default
- Credentials are stored in `.env` file (not committed to version control)

## Output Files

The tools generate various output files:

- **Jupyter Notebooks**: `.ipynb` files with analysis code
- **Visualizations**: `.html` files with interactive charts
- **Power BI Data**: `.csv` and `.json` files for Power BI import

## Troubleshooting

### Connection Issues

1. Verify your server address format (use `tcp:` prefix for Azure SQL)
2. Check firewall rules allow connections from your IP
3. Ensure SQL Server authentication is enabled
4. Verify credentials in `.env` file

### Permission Errors

- Check `ALLOW_*_OPERATIONS` settings in `.env`
- Ensure database user has appropriate permissions

### Visualization Errors

- Ensure query returns data suitable for the visualization type
- Check that numeric columns exist for scatter/line charts
- Verify categorical columns exist for bar/pie charts

## Development

To modify or extend the server:

1. All database tools are implemented in `mssql.py`
2. MCP server interface is in `main.py`
3. Add new tools by:
   - Creating a method in `MSSQLTools` class
   - Adding tool definition in `list_tools()`
   - Adding handler in `call_tool()`

## License

MIT