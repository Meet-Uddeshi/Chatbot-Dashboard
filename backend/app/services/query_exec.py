# backend/app/services/query_exec.py
import pandas as pd
from sqlalchemy import text, Connection
from typing import Dict, Any, List, Optional
import io

# --- 1. CORE SECURITY FUNCTION: Parameterized Execution ---

def execute_parameterized_query(
    db_connection: Connection,
    sql_query: str, 
    params: Dict[str, Any], 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    # ... (keep existing LIMIT logic)
    final_sql = sql_query
    if limit is not None:
        final_sql = f"SELECT * FROM ({sql_query}) AS sub_query_alias LIMIT {limit}"
        
    stmt = text(final_sql).bindparams(**params)
    
    try:
        result = db_connection.execute(stmt)
        columns = result.keys()
        
        rows = []
        for row in result.all():
            # Create a dictionary for the row
            row_dict = dict(zip(columns, row))
            # FIX: Convert Decimal/Date objects to JSON-serializable types
            for key, value in row_dict.items():
                if hasattr(value, '__float__') and not isinstance(value, (int, float)):
                    row_dict[key] = float(value)
                elif hasattr(value, 'isoformat'): # Handles Dates
                    row_dict[key] = value.isoformat()
            rows.append(row_dict)
            
        return rows
        
    except Exception as e:
        print(f"SQL Error Detail: {e}") # This helps you see the error in your terminal
        raise ValueError(f"Database query failed. Error: {e}")
def fetch_dataframe(db_connection: Connection, sql_query: str, params: Dict[str, Any]) -> pd.DataFrame:
    """Fetches full results into a Pandas DataFrame."""
    stmt = text(sql_query).bindparams(**params)
    
    # Using pandas read_sql directly with the connection object is the cleanest way
    df = pd.read_sql(stmt, db_connection)
    return df

# --- 3. MYSQL SCHEMA INTROSPECTION ---

def get_database_schema(db_connection: Connection, tables: List[str]) -> str:
    """Introspects the DB schema for MySQL and formats it for the LLM."""
    schema_parts = []
    
    for table_name in tables:
        # Query MySQL's INFORMATION_SCHEMA
        schema_query = text("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION;
        """)
        
        # Use safe parameterization for the table name lookup
        result = db_connection.execute(schema_query, {"table_name": table_name})
        
        columns_data = [f"{row[0]} ({row[1]})" for row in result.all()]
        
        if not columns_data:
            # If table is specified but not found (critical for LLM guidance)
            schema_parts.append(f"Table: {table_name} (NOT FOUND or EMPTY)")
            continue

        schema_parts.append(
            f"Table: {table_name}\nColumns: {', '.join(columns_data)}"
        )
            
    return "\n---\n".join(schema_parts)