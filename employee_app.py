import pandas as pd
import numpy as np
import plotly.express as px
import argparse
import os
import ribbon_engine as re

def get_employee_data(source_path: str = None) -> pd.DataFrame:
    """Gets employee data from either a file (CSV/Excel) or generates synthetic data."""
    if source_path and os.path.exists(source_path):
        ext = os.path.splitext(source_path)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(source_path)
            elif ext in ('.xlsx', '.xls'):
                df = pd.read_excel(source_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
                
            # Basic validation
            required = ['Week', 'Employee', 'Hours']
            if not all(col in df.columns for col in required):
                raise ValueError(f"Missing columns. File must contain: {required}")
            return df
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
            
    # Synthetic Data Generator
    weeks = [f"Week {i+1:02d}" for i in range(12)]
    employees = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
    data = []
    
    # Generate shifting patterns to show off the ribbon flow
    for week in weeks:
        for emp in employees:
            # Random hours with some base consistency per employee
            base = 35 + hash(emp) % 10
            var = np.random.randint(-10, 15)
            data.append({"Week": week, "Employee": emp, "Hours": max(0, base + var)})
            
    return pd.DataFrame(data)

def main():
    parser = argparse.ArgumentParser(description="Employee Hours Dashboard Generator")
    parser.add_argument("--input", type=str, help="Path to CSV or Excel file.")
    parser.add_argument("--output", type=str, default="employee_report.html", help="Output HTML file.")
    parser.add_argument("--top", type=int, help="Filter to show only top N employees by total hours.")
    parser.add_argument("--gap", type=float, default=2.0, help="Vertical gap between ribbons (default: 2.0).")
    parser.add_argument("--title", type=str, default="Employee Performance Flow (Weekly Hours)", help="Chart title.")
    args = parser.parse_args()

    # 1. Fetch & Prepare Data
    df = get_employee_data(args.input)
    if df is None: return

    # 2. Advanced Capability: Top N Filtering
    if args.top:
        print(f"Filtering top {args.top} employees...")
        top_emps = df.groupby("Employee")["Hours"].sum().sort_values(ascending=False).head(args.top).index
        df = df[df["Employee"].isin(top_emps)]

    # 3. Increase Robustness: Data Cleaning
    # Remove NaNs, ensure numeric Hours, ensure categorical Week/Employee
    df = df.dropna(subset=["Week", "Employee", "Hours"])
    df["Hours"] = pd.to_numeric(df["Hours"], errors='coerce').fillna(0)
    
    # 4. Custom Formatting (Robustness/Flexibility)
    # Define a custom hover template to make it look professional
    hover_fmt = "<b>%{name}</b><br>Period: %{x}<br>Value: %{y} hours<extra></extra>"

    # 5. Generate Chart via Helper Module
    print("Generating ribbon chart visualization...")
    try:
        fig = re.create_ribbon_chart(
            df,
            x_col='Week',
            category_col='Employee',
            value_col='Hours',
            title=args.title,
            gap=args.gap,
            hover_template=hover_fmt,
            # Using a custom color scheme (optional)
            colors=px.colors.qualitative.Prism
        )
        
        # 6. Save results
        fig.write_html(args.output)
        print(f"Success! Report saved to: {os.path.abspath(args.output)}")
        
    except Exception as e:
        print(f"Failed to generate chart: {e}")

if __name__ == "__main__":
    main()
