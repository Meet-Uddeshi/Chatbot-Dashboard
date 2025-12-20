import os
import json
import google.generativeai as genai

# 1. Setup Gemini with your Free Key
# Ensure your key is in your environment or .env as GOOGLE_API_KEY
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def translate_nl_to_sql(user_prompt: str, schema_context: str):
    """Uses Google Gemini Free Tier to translate NL to SQL/VizSpec."""
    
    model = genai.GenerativeModel('gemini-2.5-flash')

    # UPDATED SYSTEM INSTRUCTION FOR 'sales_data'
    system_instruction = f"""
    You are a MySQL expert. Translate the USER REQUEST into JSON using this SCHEMA:
    {schema_context}

    IMPORTANT DATA DICTIONARY (Table: sales_data):
    - Table Name = 'sales_data'
    - Revenue / Sales / Money = 'total_amount'
    
    CRITICAL SQL RULES: 
    - When using SUM, AVG, or COUNT, you MUST use an alias matching the column name.
    - WRONG: SELECT category, SUM(total_amount)...
    - CORRECT: SELECT category, SUM(total_amount) AS total_amount...
    - The 'y' value in 'viz_spec' MUST match the alias used in the SQL.
    
    OUTPUT FORMAT (Strict JSON):
    {{
        "sql_query": "SELECT category, SUM(total_amount) FROM sales_data GROUP BY category",
        "params": {{}},
        "viz_spec": {{
            "type": "bar",
            "x": "category",
            "y": "total_amount",
            "title": "Total Sales by Category"
        }},
        "explanation": "Brief description of the query."
    }}
    """

    try:
        full_prompt = f"{system_instruction}\n\nUSER REQUEST: {user_prompt}"
        
        response = model.generate_content(
            full_prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        llm_data = json.loads(response.text)
        return llm_data

    except Exception as e:
        print(f"Gemini Engine Error: {e}")
        # Fallback query using your new table structure
        return {
            "sql_query": "SELECT * FROM sales_data LIMIT 5",
            "params": {},
            "viz_spec": {
                "type": "bar", 
                "x": "transaction_id", 
                "y": "total_amount", 
                "title": "Error - Fallback Data"
            },
            "explanation": f"The AI encountered an error: {str(e)}"
        }