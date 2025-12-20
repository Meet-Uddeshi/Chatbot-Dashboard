from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Connection
from typing import Dict, Any, List
import uuid

from app.core.db import get_db
from app.services.query_exec import execute_parameterized_query, get_database_schema, fetch_dataframe
from app.services.viz_engine import render_viz
from app.schemas.query import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    ExecuteRequest, 
    JobResult, 
    VizSpec
)
from app.services.llm_engine import translate_nl_to_sql

router = APIRouter()

JOB_CACHE: Dict[str, Dict[str, Any]] = {} 

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(req: AnalyzeRequest, db_conn: Connection = Depends(get_db)):
    try:
        schema_context = get_database_schema(db_conn, req.context_tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Schema Error: {e}")

    llm_output = translate_nl_to_sql(req.prompt, schema_context)

    job_id = str(uuid.uuid4())
    generated_sql = llm_output.get("sql_query", "")
    sql_params = llm_output.get("params", {})
    viz_spec_data = llm_output.get("viz_spec", {})

    try:
        preview_rows = execute_parameterized_query(db_conn, generated_sql, sql_params, limit=5)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid SQL generated: {e}")

    JOB_CACHE[job_id] = {
        "sql": generated_sql,
        "params": sql_params,
        "viz_spec": viz_spec_data
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
    job_id = req.job_id
    
    if job_id not in JOB_CACHE:
        raise HTTPException(status_code=404, detail="Job ID not found in cache. Restart analysis.")
        
    job_data = JOB_CACHE[job_id]
    
    try:
        df = fetch_dataframe(db_conn, job_data["sql"], job_data["params"])
        chart_url = render_viz(job_data["viz_spec"], df)

        return JobResult(
            status="completed",
            chart_url=chart_url,
            data_summary={"total_rows": len(df)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Viz Error: {e}")