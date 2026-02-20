import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import argparse
import os

def get_sigmoid_curve(x1, y1, x2, y2, n_points=30):
    """Generates a sigmoid curve between two points for smooth transitions."""
    x = np.linspace(0, 1, n_points)
    # Sigmoid function centered at 0.5
    y = 1 / (1 + np.exp(-10 * (x - 0.5)))
    curve_x = x1 + x * (x2 - x1)
    curve_y = y1 + y * (y2 - y1)
    return curve_x, curve_y

def generate_fake_data():
    """Generates fake time series data for employee hours."""
    weeks = [f"Week {i+1}" for i in range(12)]
    employees = ["Alice", "Bob", "Charlie", "David", "Eve"]
    data = []
    
    for week in weeks:
        # Randomly vary hours slightly each week
        for emp in employees:
            hours = np.random.randint(30, 50)
            data.append({"Week": week, "Employee": emp, "Hours": hours})
            
    return pd.DataFrame(data)

def read_excel_data(file_path):
    """Reads employee hours data from an Excel file."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    try:
        # Expects columns: 'Week', 'Employee', 'Hours'
        df = pd.read_excel(file_path)
        required_cols = ['Week', 'Employee', 'Hours']
        if not all(col in df.columns for col in required_cols):
            print(f"Error: Excel file must contain columns: {required_cols}")
            return None
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def create_ribbon_chart(df, x_col='Week', category_col='Employee', value_col='Hours', gap=2):
    """Creates a ribbon chart from the provided DataFrame."""
    fig = go.Figure()
    
    periods = df[x_col].unique()
    categories = df[category_col].unique()
    
    # Use a fixed color map
    color_palette = px.colors.qualitative.Prism
    colors = {cat: color_palette[i % len(color_palette)] for i, cat in enumerate(categories)}
    
    coords = {}
    bar_width = 0.4
    
    # 1. Plot Bars at each period
    for period_idx, period in enumerate(periods):
        period_df = df[df[x_col] == period].sort_values(by=value_col, ascending=True)
        current_y = 0
        coords[period] = {}
        
        for _, row in period_df.iterrows():
            cat, val = row[category_col], row[value_col]
            y_start, y_end = current_y, current_y + val
            coords[period][cat] = (y_start, y_end)
            
            # Add Bar
            fig.add_trace(go.Bar(
                x=[period], y=[val], base=y_start,
                name=cat, marker_color=colors[cat],
                width=bar_width, legendgroup=cat,
                showlegend=(period_idx == 0),
                hovertemplate=f"<b>{cat}</b><br>{period}: {val} hours<extra></extra>"
            ))
            current_y += (val + gap)

    # 2. Plot Ribbons between periods
    for i in range(len(periods) - 1):
        p1, p2 = periods[i], periods[i+1]
        for cat in categories:
            if cat not in coords[p1] or cat not in coords[p2]:
                continue
                
            y1_b, y1_t = coords[p1][cat]
            y2_b, y2_t = coords[p2][cat]
            
            x1, x2 = i + bar_width/2, (i+1) - bar_width/2
            
            # Generate sigmoid curves for top and bottom edges
            cx, _ = get_sigmoid_curve(x1, 0, x2, 1) # Normalizing X axis index
            _, cy_t = get_sigmoid_curve(x1, y1_t, x2, y2_t)
            _, cy_b = get_sigmoid_curve(x1, y1_b, x2, y2_b)
            
            # Map normalized X back to period labels if necessary, 
            # but plotly handles categorical X with indices 0, 1, 2...
            
            fig.add_trace(go.Scatter(
                x=np.concatenate([cx, cx[::-1]]),
                y=np.concatenate([cy_t, cy_b[::-1]]),
                fill='toself', fillcolor=colors[cat], opacity=0.3,
                line=dict(width=0), hoverinfo='skip', showlegend=False,
                legendgroup=cat, mode='lines'
            ))

    fig.update_layout(
        title="Employee Weekly Hours (Ribbon Chart)",
        xaxis_title="Week",
        yaxis_title="Total Hours (Stacked with Gaps)",
        barmode='overlay',
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='white',
        height=600,
        legend_title="Employees"
    )
    
    return fig

def main():
    parser = argparse.ArgumentParser(description="Plot Employee Hours Time Series.")
    parser.add_argument("--excel", type=str, help="Path to an Excel file with 'Week', 'Employee', and 'Hours' columns.")
    parser.add_argument("--output", type=str, default="employee_hours_ribbon.html", help="Output HTML file name.")
    args = parser.parse_args()

    if args.excel:
        print(f"Reading data from {args.excel}...")
        df = read_excel_data(args.excel)
        if df is None:
            return
    else:
        print("No Excel file provided. Generating fake data...")
        df = generate_fake_data()

    print("Creating Ribbon Chart...")
    fig = create_ribbon_chart(df)
    
    output_path = args.output
    fig.write_html(output_path)
    print(f"Chart saved to {output_path}")
    
    # Try to open in browser if possible (optional)
    # fig.show()

if __name__ == "__main__":
    main()
