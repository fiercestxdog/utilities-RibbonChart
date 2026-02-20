import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, List, Dict, Union

def get_sigmoid_curve(x1: float, y1: float, x2: float, y2: float, n_points: int = 30):
    """Generates a sigmoid curve between two points for smooth transitions."""
    x = np.linspace(0, 1, n_points)
    # Sigmoid function centered at 0.5 with steepness 10
    y = 1 / (1 + np.exp(-10 * (x - 0.5)))
    curve_x = x1 + x * (x2 - x1)
    curve_y = y1 + y * (y2 - y1)
    return curve_x, curve_y

def create_ribbon_chart(
    df: pd.DataFrame,
    x_col: str,
    category_col: str,
    value_col: str,
    title: str = "Ribbon Chart",
    gap: float = 2.0,
    bar_width: float = 0.4,
    colors: Optional[Union[Dict[str, str], List[str]]] = None,
    sort_ascending: bool = True,
    show_legend: bool = True,
    height: int = 600,
    hover_template: Optional[str] = None
) -> go.Figure:
    """
    Creates a robust ribbon chart from a long-form DataFrame.
    
    Args:
        df: Input DataFrame (long format).
        x_col: Column for the X-axis (e.g., 'Date', 'Week').
        category_col: Column for series identification (e.g., 'Employee').
        value_col: Column for numeric values.
        title: Chart title.
        gap: Vertical whitespace between ribbons.
        bar_width: Width of the bars at each period (0.0 to 1.0).
        colors: Optional dictionary mapping categories to colors, or a list of colors.
        sort_ascending: If True, smallest values are at the bottom.
        show_legend: Whether to display the legend.
        height: Chart height in pixels.
        hover_template: Custom hover template for Plotly traces.
    """
    # 1. Validation & Pre-processing
    required_cols = [x_col, category_col, value_col]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Ensure X-axis is sorted and categorical
    periods = sorted(df[x_col].unique())
    categories = sorted(df[category_col].unique())
    
    # 2. Color Setup
    if isinstance(colors, dict):
        color_map = colors
    elif isinstance(colors, list):
        color_map = {cat: colors[i % len(colors)] for i, cat in enumerate(categories)}
    else:
        # Default to a high-contrast palette
        palette = px.colors.qualitative.G10
        color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}

    fig = go.Figure()
    coords = {}

    # 3. Bar Generation (The Anchors)
    for p_idx, period in enumerate(periods):
        # Filter and sort for the current period
        period_df = df[df[x_col] == period].copy()
        period_df = period_df.sort_values(by=[value_col, category_col], ascending=[sort_ascending, True])
        
        current_y = 0
        coords[period] = {}
        
        for _, row in period_df.iterrows():
            cat, val = row[category_col], row[value_col]
            if pd.isna(val) or val <= 0:
                continue # Skip zeros or NaNs for clarity
                
            y_start, y_end = current_y, current_y + val
            coords[period][cat] = (y_start, y_end)
            
            # Default hover template if not provided
            h_temp = hover_template or f"<b>{cat}</b><br>{period}: {val}<extra></extra>"
            
            fig.add_trace(go.Bar(
                x=[period], y=[val], base=y_start,
                name=cat, marker_color=color_map[cat],
                width=bar_width, legendgroup=cat,
                showlegend=(p_idx == 0 and show_legend),
                hovertemplate=h_temp
            ))
            current_y += (val + gap)

    # 4. Ribbon Generation (The Flow)
    for i in range(len(periods) - 1):
        p1, p2 = periods[i], periods[i+1]
        for cat in categories:
            # Only draw ribbon if category exists in both adjacent periods
            if cat not in coords[p1] or cat not in coords[p2]:
                continue
                
            y1_b, y1_t = coords[p1][cat]
            y2_b, y2_t = coords[p2][cat]
            
            # Calculate connector start/end points
            x1, x2 = i + bar_width/2, (i+1) - bar_width/2
            
            # Sigmoid curves for smooth edges
            cx, _ = get_sigmoid_curve(x1, 0, x2, 1)
            _, cy_t = get_sigmoid_curve(x1, y1_t, x2, y2_t)
            _, cy_b = get_sigmoid_curve(x1, y1_b, x2, y2_b)
            
            fig.add_trace(go.Scatter(
                x=np.concatenate([cx, cx[::-1]]),
                y=np.concatenate([cy_t, cy_b[::-1]]),
                fill='toself', fillcolor=color_map[cat], opacity=0.3,
                line=dict(width=0.5, color='rgba(255,255,255,0.1)'),
                hoverinfo='skip', showlegend=False,
                legendgroup=cat, mode='lines'
            ))

    # 5. Layout Polish
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=f"{value_col} (Ranked)",
        barmode='overlay',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=height,
        hovermode='closest',
        xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', showticklabels=False) # Often ribbon charts hide Y values as they are ranks
    )
    
    return fig
