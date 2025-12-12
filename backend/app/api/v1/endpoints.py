from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Connection
from typing import Dict, Any, List
import uuid
import os
import shutil # For cleaning up static files if necessary

# Import core components and services
from app.core.db import get_db
from app.services.query_exec import execute_parameterized_query, get_database_schema, fetch_dataframe
from app.services.viz_engine import render_viz # <-- NEW: The Visualization Engine
from app.schemas.query import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    ExecuteRequest, 
    JobResult, 
    VizSpec # Used for type hinting
)

router = APIRouter()

# --- TEMPORARY CACHE (In-Memory Dictionary for MVP) ---
# In production, replace this with Redis or a dedicated job store.
JOB_CACHE: Dict[str, Dict[str, Any]] = {} 

# --- MOCK LLM SERVICE (For NL -> SQL/VizSpec Translation) ---
def mock_llm_translation(prompt: str, schema: str) -> dict:
    """Mocks the LLM translating NL into parameterized SQL and VizSpec."""
    
    # Simple logic based on keywords
    if 'sales by category' in prompt.lower() and 'sales' in schema:
        mock_sql = "SELECT category, SUM(amount) AS total_sales FROM sales GROUP BY category ORDER BY total_sales DESC"
        mock_params = {}
        mock_viz = {"type": "bar", "x": "category", "y": "total_sales", "title": "Total Sales by Category", "aggregation": "sum"}
    elif 'daily revenue' in prompt.lower() and 'order_date' in schema:
        mock_sql = "SELECT order_date, SUM(amount) AS daily_revenue FROM sales GROUP BY order_date ORDER BY order_date ASC"
        mock_params = {}
        mock_viz = {"type": "line", "x": "order_date", "y": "daily_revenue", "title": "Daily Revenue Trend", "aggregation": "sum"}
    elif 'recent' in prompt.lower():
        return {
            "error": True,
            "missing_info_question": "Clarification needed: Please specify the exact date range (e.g., 'last 30 days') or the relevant date column."
        }
    else:
        mock_sql = "SELECT 'default' AS placeholder, 100 AS count"
        mock_params = {}
        mock_viz = {"type": "bar", "x": "placeholder", "y": "count", "title": "Default Chart (Query Not Recognized)", "aggregation": "none"}

    return {
        "sql_query": mock_sql,
        "params": mock_params,
        "viz_spec": mock_viz
    }
# --- END MOCK LLM SERVICE ---


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(req: AnalyzeRequest, db_conn: Connection = Depends(get_db)):
    """Phase 1: Accepts NL, generates SQL/VizSpec, returns safety preview and clarification check."""
    
    # 1. Get Schema Context
    try:
        # Use only tables requested by the user for efficiency
        schema_context = get_database_schema(db_conn, req.context_tables)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database schema introspection failed: {e}")

    # 2. Translate NL to SQL and VizSpec
    llm_output = mock_llm_translation(req.prompt, schema_context)

    if "missing_info_question" in llm_output:
        return AnalyzeResponse(
            job_id=str(uuid.uuid4()),
            generated_sql="",
            sql_params={},
            viz_spec=VizSpec(type="text", x="", y="", title="Clarification", aggregation="none"),
            preview_rows=[],
            needs_clarification=True
        )

    generated_sql = llm_output["sql_query"]
    sql_params = llm_output["params"]
    viz_spec_data = llm_output["viz_spec"]
    job_id = str(uuid.uuid4()) 

    # 3. Safe Dry Run (LIMIT 5)
    try:
        preview_rows = execute_parameterized_query(
            db_conn, generated_sql, sql_params, limit=5
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"LLM generated invalid query or column: {e}")

    # 4. Cache the Job details for Phase 2 execution
    JOB_CACHE[job_id] = {
        "sql": generated_sql,
        "params": sql_params,
        "viz_spec": viz_spec_data,
        "status": "preview_ready"
    }

    return AnalyzeResponse(
        job_id=job_id,
        generated_sql=generated_sql,
        sql_params=sql_params,
        viz_spec=viz_spec_data,
        preview_rows=preview_rows,
        needs_clarification=False
    )


@router.post("/execute", response_model=JobResult)
async def execute_job(req: ExecuteRequest, db_conn: Connection = Depends(get_db)):
    """Phase 2: Executes the confirmed query, generates the chart, and returns the URL."""
    
    job_id = req.job_id
    if job_id not in JOB_CACHE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job ID not found or expired.")
        
    job_data = JOB_CACHE[job_id]
    
    if not req.confirmed:
        # User explicitly rejected the preview, although our Vue client doesn't support this path yet.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Execution rejected by client.")

    generated_sql = job_data["sql"]
    sql_params = job_data["params"]
    viz_spec = job_data["viz_spec"]
    
    try:
        # 1. Execute Full Query and Fetch DataFrame
        df = fetch_dataframe(db_conn, generated_sql, sql_params)
        
        if df.empty:
             raise ValueError("Query executed successfully but returned zero rows. Cannot generate chart.")
             
        # Guardrail: Limit the size of the result set for plotting and memory safety
        if len(df) > 5000:
            df = df.head(5000)
            print(f"Warning: Dataframe truncated to 5000 rows for rendering.")
            
        total_rows = len(df)
        
        # 2. Render Visualization
        # output_dir="static/charts" corresponds to the StaticFiles mount in main.py
        chart_url = render_viz(viz_spec, df, output_dir="static/charts")

        # 3. Clean Cache (Optional: To prevent re-running heavy jobs)
        # del JOB_CACHE[job_id]

        return JobResult(
            status="completed",
            chart_url=chart_url,
            data_summary={"total_rows": total_rows}
        )

    except Exception as e:
        # 500 Error for general execution/rendering failure
        JOB_CACHE[job_id]["status"] = "failed"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Execution or Rendering Failed: {e}")

# Note: The GET /api/v1/job/{job_id} endpoint for status checking is omitted
# for MVP simplicity but would be necessary for long-running, asynchronous jobs.