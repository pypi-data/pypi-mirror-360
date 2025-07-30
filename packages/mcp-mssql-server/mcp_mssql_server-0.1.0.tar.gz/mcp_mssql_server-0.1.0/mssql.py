


from typing import Any, Dict, List, Optional
import os
import pymssql
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import nbformat as nbf
from contextlib import contextmanager
import json

load_dotenv()

# Initialize the FastMCP sever
mcp = FastMCP("mcp-mssql-server")


class MSSQLConnection:
    def __init__(self):
        self.server = os.getenv('MSSQL_SERVER', 'localhost')
        self.port = int(os.getenv('MSSQL_PORT', '1433'))
        self.user = os.getenv('MSSQL_USER', 'sa')
        self.password = os.getenv('MSSQL_PASSWORD', '')
        self.database = os.getenv('MSSQL_DATABASE', 'master')
        self.encrypt = os.getenv('MSSQL_ENCRYPT', 'true').lower() == 'true'
        self.trust_server_certificate = os.getenv('MSSQL_TRUST_SERVER_CERTIFICATE', 'true').lower() == 'true'

        self.allow_write = os.getenv('ALLOW_WRITE_OPERATIONS', 'false').lower() == 'true'
        self.allow_insert = os.getenv('ALLOW_INSERT_OPERATION', 'false').lower() == 'true'
        self.allow_update = os.getenv('ALLOW_UPDATE_OPERATION', 'false').lower() == 'true'
        self.allow_delete = os.getenv('ALLOW_DELETE_OPERATION', 'false').lower() == 'true'

        self.query_timeout = int(os.getenv('QUERY_TIMEOUT', '30000')) // 1000

    @contextmanager
    def get_connection(self):
        server_parts = self.server.replace('tcp:', '').split('.')
        if len(server_parts) > 1 and 'database.windows.net' in self.server:
            server = self.server.replace('tcp:', '')
        else:
            server = f"{self.server},{self.port}"

        conn = pymssql.connect(
            server=server,
            user=self.user,
            password=self.password,
            database=self.database,
            timeout=self.query_timeout,
            login_timeout=self.query_timeout,
            as_dict=True
        )
        try:
            yield conn
        finally:
            conn.close()

    def is_write_query(self, query: str) -> bool:
        query_upper = query.upper().strip()
        write_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        return any(query_upper.startswith(keyword) for keyword in write_keywords)

    def check_permissions(self, query: str) -> bool:
        if not self.is_write_query(query):
            return True

        query_upper = query.upper().strip()

        if not self.allow_write:
            return False

        if query_upper.startswith('INSERT') and not self.allow_insert:
            return False
        elif query_upper.startswith('UPDATE') and not self.allow_update:
            return False
        elif query_upper.startswith('DELETE') and not self.allow_delete:
            return False

        return True

# Initialize connection
db_connection = MSSQLConnection()

@mcp.tool()
def sql_query(query: str) -> Dict[str, Any]:
    """Execute a SQL query on the MS SQL Server database"""
    if not db_connection.check_permissions(query):
        return {
            "success": False,
            "error": "Permission denied for this operation"
        }

    try:
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)

            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                return {
                    "success": True,
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
            else:
                conn.commit()
                return {
                    "success": True,
                    "rows_affected": cursor.rowcount
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_database_info() -> Dict[str, Any]:
    """Get information about the database server and available databases"""
    query = """
    SELECT
        @@VERSION AS version,
        @@SERVERNAME AS server_name,
        DB_NAME() AS current_database,
        SUSER_SNAME() AS current_user
    """

    try:
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            info = cursor.fetchone()

            cursor.execute("SELECT name FROM sys.databases ORDER BY name")
            databases = [row['name'] for row in cursor.fetchall()]

            return {
                "success": True,
                "server_info": info,
                "databases": databases
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def show_tables(schema_name: Optional[str] = None) -> Dict[str, Any]:
    """Show all tables in the current database"""
    if schema_name:
        query = """
        SELECT
            TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        params = (schema_name,)
    else:
        query = """
        SELECT
            TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        params = None

    try:
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            tables = cursor.fetchall()

            return {
                "success": True,
                "tables": tables,
                "count": len(tables)
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def describe_table(table_name: str, schema_name: str = 'dbo') -> Dict[str, Any]:
    """Get detailed information about a table's structure"""
    query = """
    SELECT
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.CHARACTER_MAXIMUM_LENGTH,
        c.NUMERIC_PRECISION,
        c.NUMERIC_SCALE,
        c.IS_NULLABLE,
        c.COLUMN_DEFAULT,
        pk.CONSTRAINT_TYPE AS IS_PRIMARY_KEY
    FROM INFORMATION_SCHEMA.COLUMNS c
    LEFT JOIN (
        SELECT
            ccu.COLUMN_NAME,
            tc.CONSTRAINT_TYPE
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu
            ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = ccu.TABLE_SCHEMA
        WHERE tc.TABLE_NAME = %s
            AND tc.TABLE_SCHEMA = %s
            AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
    ) pk ON c.COLUMN_NAME = pk.COLUMN_NAME
    WHERE c.TABLE_NAME = %s AND c.TABLE_SCHEMA = %s
    ORDER BY c.ORDINAL_POSITION
    """

    try:
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (table_name, schema_name, table_name, schema_name))
            columns = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) as row_count
                FROM [{0}].[{1}]
            """.format(schema_name, table_name))
            row_count = cursor.fetchone()['row_count']

            return {
                "success": True,
                "table_name": table_name,
                "schema": schema_name,
                "columns": columns,
                "row_count": row_count
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def show_indexes(table_name: Optional[str] = None, schema_name: str = 'dbo') -> Dict[str, Any]:
    """Show indexes for a table or all tables"""
    if table_name:
        query = """
        SELECT
            t.name AS table_name,
            i.name AS index_name,
            i.type_desc AS index_type,
            i.is_unique,
            i.is_primary_key,
            STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS columns
        FROM sys.indexes i
        INNER JOIN sys.tables t ON i.object_id = t.object_id
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE t.name = %s AND s.name = %s AND i.type > 0
        GROUP BY t.name, i.name, i.type_desc, i.is_unique, i.is_primary_key
        ORDER BY t.name, i.name
        """
        params = (table_name, schema_name)
    else:
        query = """
        SELECT
            t.name AS table_name,
            i.name AS index_name,
            i.type_desc AS index_type,
            i.is_unique,
            i.is_primary_key
        FROM sys.indexes i
        INNER JOIN sys.tables t ON i.object_id = t.object_id
        WHERE i.type > 0
        ORDER BY t.name, i.name
        """
        params = None

    try:
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            indexes = cursor.fetchall()

            return {
                "success": True,
                "indexes": indexes,
                "count": len(indexes)
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def generate_analysis_notebook(query: str, output_file: Optional[str] = None) -> Dict[str, Any]:
    """Generate a Jupyter notebook with Python code to analyze SQL query results"""
    if output_file is None:
        output_file = "sql_analysis.ipynb"

    try:
        result = sql_query(query)
        if not result["success"]:
            return result

        nb = nbf.v4.new_notebook()

        cells = []

        cells.append(nbf.v4.new_markdown_cell("# SQL Data Analysis\n\nThis notebook analyzes data from SQL Server query."))

        cells.append(nbf.v4.new_code_cell("""import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            import plotly.express as px
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            plt.style.use('seaborn-v0_8-darkgrid')
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', 100)"""))

        data_dict = {
            'columns': result['columns'],
            'data': result['rows']
        }
        cells.append(nbf.v4.new_code_cell(f"""# Load data from SQL query
        data = {json.dumps(data_dict, indent=2)}
        df = pd.DataFrame(data['data'])
        print(f"Data shape: {{df.shape}}")
        print(f"Columns: {{list(df.columns)}}")"""))

        cells.append(nbf.v4.new_markdown_cell("## Data Overview"))
        cells.append(nbf.v4.new_code_cell("""# Display first few rows
df.head(10)"""))

        cells.append(nbf.v4.new_code_cell("""# Data types and basic info
df.info()"""))

        cells.append(nbf.v4.new_code_cell("""# Statistical summary
df.describe(include='all')"""))

        cells.append(nbf.v4.new_code_cell("""# Check for missing values
missing_data = df.isnull().sum()
if missing_data.any():
    print("Missing values per column:")
    print(missing_data[missing_data > 0])
else:
    print("No missing values found")"""))

        cells.append(nbf.v4.new_markdown_cell("## Data Analysis"))

        cells.append(nbf.v4.new_code_cell("""# Identify numeric and categorical columns
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

print(f"Numeric columns: {numeric_cols}")
print(f"Categorical columns: {categorical_cols}")"""))

        cells.append(nbf.v4.new_code_cell("""# Correlation analysis for numeric columns
if len(numeric_cols) > 1:
    plt.figure(figsize=(10, 8))
    correlation_matrix = df[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.show()"""))

        cells.append(nbf.v4.new_markdown_cell("## Automated Visualizations"))

        cells.append(nbf.v4.new_code_cell("""# Distribution plots for numeric columns
if numeric_cols:
    fig, axes = plt.subplots(nrows=(len(numeric_cols) + 1) // 2, ncols=2, figsize=(12, 4 * ((len(numeric_cols) + 1) // 2)))
    axes = axes.flatten() if len(numeric_cols) > 1 else [axes]

    for i, col in enumerate(numeric_cols):
        if i < len(axes):
            df[col].hist(ax=axes[i], bins=30, edgecolor='black')
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')

    for i in range(len(numeric_cols), len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    plt.show()"""))

        cells.append(nbf.v4.new_code_cell("""# Value counts for categorical columns
if categorical_cols:
    for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
        print(f"\\nValue counts for {col}:")
        print(df[col].value_counts().head(10))

        if df[col].nunique() <= 10:
            plt.figure(figsize=(10, 6))
            df[col].value_counts().plot(kind='bar')
            plt.title(f'Distribution of {col}')
            plt.xlabel(col)
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()"""))

        cells.append(nbf.v4.new_markdown_cell("## Interactive Visualizations"))

        cells.append(nbf.v4.new_code_cell("""# Create interactive scatter plot if we have numeric columns
if len(numeric_cols) >= 2:
    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                     title=f'{numeric_cols[0]} vs {numeric_cols[1]}',
                     hover_data=df.columns)
    fig.show()"""))

        cells.append(nbf.v4.new_code_cell("""# Create interactive bar chart for top categorical values
if categorical_cols:
    col = categorical_cols[0]
    top_values = df[col].value_counts().head(10)

    fig = go.Figure(data=[
        go.Bar(x=top_values.index, y=top_values.values)
    ])
    fig.update_layout(
        title=f'Top 10 {col} Values',
        xaxis_title=col,
        yaxis_title='Count'
    )
    fig.show()"""))

        cells.append(nbf.v4.new_markdown_cell("## Custom Analysis\n\nAdd your custom analysis code below:"))
        cells.append(nbf.v4.new_code_cell("# Add your custom analysis here\n"))

        nb['cells'] = cells

        with open(output_file, 'w') as f:
            nbf.write(nb, f)

        return {
            "success": True,
            "message": f"Analysis notebook created: {output_file}",
            "file_path": output_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def generate_visualization(query: str, viz_type: str = "auto", title: Optional[str] = None) -> Dict[str, Any]:
    """Generate visualizations (bar, scatter, pie, line, heatmap, table) from SQL query results"""
    try:
        result = sql_query(query)
        if not result["success"]:
            return result

        df = pd.DataFrame(result['rows'])

        if df.empty:
            return {
                "success": False,
                "error": "No data to visualize"
            }

        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        fig = None

        if viz_type == "auto":
            if len(numeric_cols) >= 2:
                viz_type = "scatter"
            elif len(numeric_cols) == 1 and len(categorical_cols) >= 1:
                viz_type = "bar"
            elif len(categorical_cols) >= 1:
                viz_type = "pie"
            else:
                viz_type = "table"

        if viz_type == "bar":
            if categorical_cols and numeric_cols:
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]

                grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(20)

                fig = go.Figure(data=[
                    go.Bar(x=grouped.index, y=grouped.values)
                ])
                fig.update_layout(
                    title=title or f'{y_col} by {x_col}',
                    xaxis_title=x_col,
                    yaxis_title=y_col
                )

        elif viz_type == "scatter" and len(numeric_cols) >= 2:
            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                           title=title or f'{numeric_cols[0]} vs {numeric_cols[1]}',
                           hover_data=df.columns)

        elif viz_type == "pie" and categorical_cols:
            col = categorical_cols[0]
            value_counts = df[col].value_counts().head(10)

            fig = go.Figure(data=[
                go.Pie(labels=value_counts.index, values=value_counts.values)
            ])
            fig.update_layout(title=title or f'Distribution of {col}')

        elif viz_type == "line" and numeric_cols:
            if len(df) > 1:
                fig = go.Figure()
                for col in numeric_cols[:3]:
                    fig.add_trace(go.Scatter(
                        x=list(range(len(df))),
                        y=df[col],
                        mode='lines',
                        name=col
                    ))
                fig.update_layout(
                    title=title or 'Line Chart',
                    xaxis_title='Index',
                    yaxis_title='Value'
                )

        elif viz_type == "heatmap" and len(numeric_cols) > 1:
            correlation = df[numeric_cols].corr()

            fig = go.Figure(data=go.Heatmap(
                z=correlation.values,
                x=correlation.columns,
                y=correlation.columns,
                colorscale='RdBu',
                zmid=0
            ))
            fig.update_layout(title=title or 'Correlation Heatmap')

        elif viz_type == "table":
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns),
                          fill_color='paleturquoise',
                          align='left'),
                cells=dict(values=[df[col] for col in df.columns],
                         fill_color='lavender',
                         align='left'))
            ])
            fig.update_layout(title=title or 'Data Table')

        if fig:
            html_file = "visualization.html"
            fig.write_html(html_file)

            return {
                "success": True,
                "visualization_type": viz_type,
                "file_path": html_file,
                "message": f"Visualization saved to {html_file}"
            }
        else:
            return {
                "success": False,
                "error": f"Could not create visualization of type '{viz_type}'"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def generate_powerbi_visualization(query: str, viz_type: str = "auto") -> Dict[str, Any]:
    """Generate Power BI compatible data and visualization metadata"""
    try:
        result = sql_query(query)
        if not result["success"]:
            return result

        df = pd.DataFrame(result['rows'])

        powerbi_data = {
            "data": df.to_dict('records'),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "visualization_type": viz_type,
            "row_count": len(df)
        }

        csv_file = "powerbi_data.csv"
        df.to_csv(csv_file, index=False)

        json_file = "powerbi_data.json"
        with open(json_file, 'w') as f:
            json.dump(powerbi_data, f, indent=2)

        return {
            "success": True,
            "message": "Power BI compatible data generated",
            "csv_file": csv_file,
            "json_file": json_file,
            "data_summary": {
                "rows": len(df),
                "columns": list(df.columns),
                "numeric_columns": df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                "text_columns": df.select_dtypes(include=['object']).columns.tolist()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }



# @mcp.tool()
# def construct_knowledge_graph(query: str, node_columns: List[str], relationship_column: Optional[str] =
#   None, graph_name: str = "sql_knowledge_graph") -> Dict[str, Any]:
#       """Construct a knowledge graph in Neo4j from SQL query results"""
#       try:
#           # Execute SQL query first
#           result = sql_query(query)
#           if not result["success"]:
#               return result

#           df = pd.DataFrame(result['rows'])

#           if df.empty:
#               return {
#                   "success": False,
#                   "error": "No data to create knowledge graph"
#               }

#           # Neo4j connection
#           neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
#           neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
#           neo4j_password = os.getenv('NEO4J_PASSWORD', '')

#           if not neo4j_password or neo4j_password == 'your_neo4j_password':
#               return {
#                   "success": False,
#                   "error": "Neo4j password not configured in .env file"
#               }

#           driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))       

#           with driver.session() as session:
#               # Clear existing graph with same name
#               session.run(f"MATCH (n:{graph_name}) DETACH DELETE n")

#               nodes_created = 0
#               relationships_created = 0

#               # Create nodes
#               for _, row in df.iterrows():
#                   for node_col in node_columns:
#                       if node_col in df.columns and pd.notna(row[node_col]):
#                           # Create node with properties
#                           properties = {k: v for k, v in row.items() if pd.notna(v)}        

#                           cypher = f"""
#                           MERGE (n:{graph_name} {{name: $name}})
#                           SET n += $properties
#                           """

#                           session.run(cypher, name=str(row[node_col]), properties=properties)
#                           nodes_created += 1

#               # Create relationships if relationship column is specified
#               if relationship_column and relationship_column in df.columns:
#                   for _, row in df.iterrows():
#                       if len(node_columns) >= 2:
#                           source = str(row[node_columns[0]])
#                           target = str(row[node_columns[1]])
#                           rel_type = str(row[relationship_column]).upper().replace(' ', '_')

#                           cypher = f"""
#                           MATCH (a:{graph_name} {{name: $source}})
#                           MATCH (b:{graph_name} {{name: $target}})
#                           MERGE (a)-[r:{rel_type}]->(b)
#                           SET r += $properties
#                           """

#                           properties = {k: v for k, v in row.items() if pd.notna(v)}        
#                           session.run(cypher, source=source, target=target, properties=properties)
#                           relationships_created += 1

#           driver.close()

#           return {
#               "success": True,
#               "message": f"Knowledge graph '{graph_name}' created successfully",
#               "nodes_created": nodes_created,
#               "relationships_created": relationships_created,
#               "graph_name": graph_name,
#               "neo4j_uri": neo4j_uri
#           }

#       except Exception as e:
#           return {
#               "success": False,
#               "error": str(e)
#           }

# @mcp.tool()
# def query_knowledge_graph(cypher_query: str, graph_name: str = "sql_knowledge_graph") -> Dict[str, Any]:
#       """Query the knowledge graph using Cypher"""
#       try:
#           neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
#           neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
#           neo4j_password = os.getenv('NEO4J_PASSWORD', '')

#           if not neo4j_password or neo4j_password == 'your_neo4j_password':
#               return {
#                   "success": False,
#                   "error": "Neo4j password not configured in .env file"
#               }

#           driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))       

#           with driver.session() as session:
#               result = session.run(cypher_query)
#               records = [record.data() for record in result]

#           driver.close()

#           return {
#               "success": True,
#               "results": records,
#               "count": len(records)
#           }

#       except Exception as e:
#           return {
#               "success": False,
#               "error": str(e)
#           }

# @mcp.tool()
# def visualize_knowledge_graph(graph_name: str = "sql_knowledge_graph", limit: int = 100) -> Dict[str,
#   Any]:
#       """Create a visual representation of the knowledge graph"""
#       try:
#           neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
#           neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
#           neo4j_password = os.getenv('NEO4J_PASSWORD', '')

#           if not neo4j_password or neo4j_password == 'your_neo4j_password':
#               return {
#                   "success": False,
#                   "error": "Neo4j password not configured in .env file"
#               }

#           driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))       

#           with driver.session() as session:
#               # Get nodes
#               nodes_query = f"MATCH (n:{graph_name}) RETURN n LIMIT {limit}"
#               nodes_result = session.run(nodes_query)

#               # Get relationships
#               rels_query = f"MATCH (a:{graph_name})-[r]->(b:{graph_name}) RETURN a, r, b LIMIT {limit}"
#               rels_result = session.run(rels_query)

#               nodes_data = []
#               edges_data = []

#               # Process nodes
#               for record in nodes_result:
#                   node = record['n']
#                   nodes_data.append({
#                       'id': node.element_id,
#                       'label': node.get('name', 'Unknown'),
#                       'properties': dict(node)
#                   })

#               # Process relationships
#               for record in rels_result:
#                   source = record['a']
#                   target = record['b']
#                   rel = record['r']

#                   edges_data.append({
#                       'source': source.element_id,
#                       'target': target.element_id,
#                       'relationship': rel.type,
#                       'properties': dict(rel)
#                   })

#           driver.close()

#           # Create a simple network visualization using plotly
#           G = nx.Graph()

#           # Add nodes
#           for node in nodes_data:
#               G.add_node(node['id'], label=node['label'])

#           # Add edges
#           for edge in edges_data:
#               G.add_edge(edge['source'], edge['target'])

#           # Get layout
#           pos = nx.spring_layout(G)

#           # Create traces
#           edge_trace = []
#           for edge in edges_data:
#               x0, y0 = pos[edge['source']]
#               x1, y1 = pos[edge['target']]
#               edge_trace.append(go.Scatter(
#                   x=[x0, x1, None],
#                   y=[y0, y1, None],
#                   mode='lines',
#                   line=dict(width=2, color='gray'),
#                   showlegend=False
#               ))

#           node_trace = go.Scatter(
#               x=[pos[node['id']][0] for node in nodes_data],
#               y=[pos[node['id']][1] for node in nodes_data],
#               mode='markers+text',
#               marker=dict(size=20, color='lightblue'),
#               text=[node['label'] for node in nodes_data],
#               textposition="middle center",
#               showlegend=False
#           )

#           fig = go.Figure(data=edge_trace + [node_trace])
#           fig.update_layout(
#               title=f'Knowledge Graph: {graph_name}',
#               showlegend=False,
#               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
#           )

#           html_file = f"knowledge_graph_{graph_name}.html"
#           fig.write_html(html_file)

#           return {
#               "success": True,
#               "nodes_count": len(nodes_data),
#               "edges_count": len(edges_data),
#               "visualization_file": html_file,
#               "message": f"Knowledge graph visualization saved to {html_file}"
#           }

#       except Exception as e:
#           return {
#               "success": False,
#               "error": str(e)
#           }


def main():
    """Main entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()