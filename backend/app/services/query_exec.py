import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging

# Configure Logger
logger = logging.getLogger(__name__)

# --- 1. CORE SECURITY FUNCTION: Parameterized Execution ---

def execute_parameterized_query(
    db: Session,  # CHANGED: Type hint is now Session (matches FastAPI)
    sql_query: str, 
    params: Dict[str, Any], 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    
    # 1. Apply Limit Logic
    final_sql = sql_query
    # Simple check to avoid double limits if the LLM already added one
    if limit is not None and "LIMIT" not in final_sql.upper():
        final_sql = f"SELECT * FROM ({sql_query}) AS sub_query_alias LIMIT {limit}"
        
    stmt = text(final_sql).bindparams(**params)
    
    try:
        # 2. Execute using the Session
        result = db.execute(stmt)
        columns = result.keys()
        
        rows = []
        for row in result.all():
            # Create a dictionary for the row
            row_dict = dict(zip(columns, row))
            
            # 3. FIX: Convert Decimal/Date objects to JSON-serializable types
            for key, value in row_dict.items():
                # Handle Decimals/Floats
                if hasattr(value, '__float__') and not isinstance(value, (int, float, str)):
                    row_dict[key] = float(value)
                # Handle Dates/Times
                elif hasattr(value, 'isoformat'): 
                    row_dict[key] = value.isoformat()
            
            rows.append(row_dict)
            
        return rows
        
    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        print(f"CRITICAL SQL ERROR: {e}") # Visible in terminal
        raise ValueError(f"Database query failed. Error: {e}")

# --- 2. PANDAS EXECUTION ---

def fetch_dataframe(db: Session, sql_query: str, params: Dict[str, Any]) -> pd.DataFrame:
    """Fetches full results into a Pandas DataFrame safely."""
    try:
        stmt = text(sql_query).bindparams(**params)
        
        # CRITICAL FIX: Pandas needs the ENGINE (db.bind), not the Session
        df = pd.read_sql(stmt, db.bind)
        
        return df
    except Exception as e:
        logger.error(f"Pandas Read Error: {e}")
        print(f"CRITICAL PANDAS ERROR: {e}")
        raise e

# --- 3. MYSQL SCHEMA INTROSPECTION ---

def get_database_schema(db: Session, tables: List[str]) -> str:
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
        
        # Use the session to execute
        result = db.execute(schema_query, {"table_name": table_name})
        
        columns_data = [f"{row[0]} ({row[1]})" for row in result.all()]
        
        if not columns_data:
            schema_parts.append(f"Table: {table_name} (NOT FOUND or EMPTY)")
            continue

        schema_parts.append(
            f"Table: {table_name}\nColumns: {', '.join(columns_data)}"
        )
            
    return "\n---\n".join(schema_parts)