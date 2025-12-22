import matplotlib
# Force non-interactive backend to prevent server crashes
matplotlib.use('Agg') 
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import seaborn as sns
import pandas as pd
import uuid
import os
from typing import Dict

# Ensure output directory exists
CHART_OUTPUT_DIR = "static/charts"
if not os.path.exists(CHART_OUTPUT_DIR):
    os.makedirs(CHART_OUTPUT_DIR)

def render_viz(viz_spec: Dict, df: pd.DataFrame, output_dir: str = CHART_OUTPUT_DIR) -> str:
    """
    Renders visualization with aggressive error handling and auto-correction.
    """
    
    # 1. DEBUG: Print what the database actually returned
    print(f"\n--- VIZ ENGINE DEBUG ---")
    print(f"Columns in DataFrame: {df.columns.tolist()}")
    if not df.empty:
        print(f"First Row Data: {df.iloc[0].to_dict()}")
    print(f"AI Requested: X='{viz_spec.get('x')}', Y='{viz_spec.get('y')}'")
    print(f"------------------------\n")

    # 2. Safety Check: Empty Data
    if df.empty:
        raise ValueError("The query returned 0 rows. Cannot generate chart.")

    # 3. Setup Configuration
    chart_type = viz_spec.get('type', 'line').lower()
    x_col = viz_spec.get('x')
    y_col = viz_spec.get('y')
    title = viz_spec.get('title', 'Data Visualization')

    # --- AGGRESSIVE AUTO-CORRECTION (The Fix) ---
    
    # Fix Y-Axis (The Metric)
    if y_col not in df.columns:
        # Check 1: Case insensitive match
        match = next((c for c in df.columns if c.lower() == y_col.lower()), None)
        # Check 2: Substring match (e.g., 'total_amount' matches 'SUM(total_amount)')
        if not match:
            match = next((c for c in df.columns if y_col in c), None)
        # Check 3: Last Column Fallback (The numeric value is usually the last column)
        if not match:
            match = df.columns[-1]
            print(f"DEBUG: Y-column '{y_col}' not found. Defaulting to '{match}'")
        
        y_col = match

    # Fix X-Axis (The Label)
    if x_col not in df.columns:
        # Fallback to the first column (usually the category/date)
        x_col = df.columns[0]
        print(f"DEBUG: X-column '{viz_spec.get('x')}' not found. Defaulting to '{x_col}'")

    # 4. Data Type Conversion (Fixes MySQL Decimal Issues)
    # Convert Y column to Float (Seaborn crashes on Decimals)
    try:
        df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
    except Exception as e:
        print(f"Warning: Could not convert {y_col} to numeric: {e}")

    # Convert X column to DateTime if it looks like a date
    if 'date' in x_col.lower() or 'time' in x_col.lower():
        try:
            df[x_col] = pd.to_datetime(df[x_col])
            df = df.sort_values(by=x_col)
        except:
            pass # Keep as string if conversion fails

    # 5. Plotting (Object-Oriented Style)
    fig = Figure(figsize=(10, 6), dpi=100)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    try:
        if chart_type == 'bar':
            # Rotate labels if there are many bars
            if len(df) > 10:
                ax.tick_params(axis='x', rotation=45, labelsize=9)
            sns.barplot(data=df, x=x_col, y=y_col, ax=ax, palette="viridis")
        
        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax, s=100)
        elif chart_type == 'pie':
            # Matplotlib Pie Chart Implementation
            # y_col = Numerical Values (Size of slice)
            # x_col = Labels (Category name)
            
            # Use a Seaborn palette to keep colors consistent with other charts
            colors = sns.color_palette('pastel')[0:len(df)]
            
            wedges, texts, autotexts = ax.pie(
                df[y_col], 
                labels=df[x_col], 
                autopct='%1.1f%%',  # Show percentage with 1 decimal
                startangle=90,      # Start vertical for better aesthetics
                colors=colors,
                wedgeprops={'edgecolor': 'white'} # Clean separator lines
            )
            
            # Formatting text size for clarity
            plt.setp(texts, size=10, weight="bold")
            plt.setp(autotexts, size=9, color="white", weight="bold")
            
            # Ensure the pie is drawn as a circle, not an oval
            ax.axis('equal') 
            
            # Pie charts typically don't need XY axis labels, so we clear them
            ax.set_xlabel('')
            ax.set_ylabel('')

        elif chart_type == 'heatmap':
            numeric_df = df.select_dtypes(include=['float64', 'int64'])
            sns.heatmap(numeric_df.corr(), annot=True, ax=ax, cmap='coolwarm', fmt=".2f")
            ax.set_title("Correlation Heatmap")    
        
        else:
            sns.lineplot(data=df, x=x_col, y=y_col, ax=ax, marker='o')

        # Formatting
        ax.set_title(title, fontsize=14, fontweight='bold')
        if chart_type != 'pie':
            ax.set_xlabel(x_col.replace('_', ' ').title())
            ax.set_ylabel(y_col.replace('_', ' ').title())
        fig.tight_layout()

        # 6. Save File
        filename = f"chart_{uuid.uuid4()}.png"
        filepath = os.path.join(output_dir, filename)
        canvas.print_figure(filepath)
        
        print(f"SUCCESS: Chart saved to {filepath}")
        return f"/static/charts/{filename}"

    except Exception as e:
        print(f"CRITICAL VIZ ERROR: {str(e)}")
        # Return a fallback error image or re-raise
        raise ValueError(f"Rendering failed: {str(e)}")