# backend/app/services/viz_engine.py
import matplotlib
matplotlib.use('Agg') # CRITICAL: Non-interactive backend for server environments
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import uuid
import os
from typing import Dict

# Ensure the output directory exists relative to the backend app root
CHART_OUTPUT_DIR = "static/charts"

if not os.path.exists(CHART_OUTPUT_DIR):
    os.makedirs(CHART_OUTPUT_DIR)

def render_viz(viz_spec: Dict, df: pd.DataFrame, output_dir: str = CHART_OUTPUT_DIR) -> str:
    """
    Renders a visualization based on the VizSpec and a DataFrame, saves it as PNG,
    and returns the local path segment for the FastAPI static file server.
    """
    plt.clf() # Clear previous figures to prevent memory/state bleed
    
    # Check for empty data before proceeding
    if df.empty:
        raise ValueError("Cannot render chart: DataFrame is empty.")

    # Configuration extraction
    chart_type = viz_spec.get('type', 'line')
    x_col = viz_spec.get('x')
    y_col = viz_spec.get('y')
    title = viz_spec.get('title', 'Generated Visualization')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    try:
        # --- Conditional Plotting Logic ---
        if chart_type == 'bar':
            # Check if x_col and y_col exist in the DataFrame
            if x_col not in df.columns or y_col not in df.columns:
                 raise ValueError(f"Bar chart failed: Column(s) '{x_col}' or '{y_col}' not found in data.")
            sns.barplot(data=df, x=x_col, y=y_col, ax=ax)
        
        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
        
        # Add more logic for line/heatmap as needed, default to line for basic implementation
        elif chart_type == 'line' or True:
            sns.lineplot(data=df, x=x_col, y=y_col, ax=ax)
            
        # --- Formatting ---
        ax.set_title(title, fontsize=14)
        ax.set_xlabel(x_col.replace('_', ' ').title())
        ax.set_ylabel(y_col.replace('_', ' ').title())
        plt.tight_layout() # Adjust layout to prevent labels cutting off
        
        # Save the figure
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight')
        
        # CRITICAL MEMORY MANAGEMENT: Close the figure object
        plt.close(fig) 
        
        # Return the URL segment that FastAPI serves via the /static mount
        return f"/static/charts/{filename}"
        
    except Exception as e:
        # Ensure figure is closed on error
        plt.close(fig) 
        # Re-raise the error to be caught by the /execute endpoint
        raise ValueError(f"Visualization rendering failed for type '{chart_type}': {e}")