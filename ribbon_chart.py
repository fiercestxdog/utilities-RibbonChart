import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def get_sigmoid_curve(x1, y1, x2, y2, n_points=30):
    """Generates a sigmoid curve between two points."""
    x = np.linspace(0, 1, n_points)
    y = 1 / (1 + np.exp(-10 * (x - 0.5)))
    curve_x = x1 + x * (x2 - x1)
    curve_y = y1 + y * (y2 - y1)
    return curve_x, curve_y

def generate_scenario_data(type="random"):
    """Generates various data scenarios."""
    periods = np.arange(2020, 2026)
    categories = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon']
    data = []
    
    if type == "market_share":
        vals = {
            'Alpha': [40, 35, 30, 25, 20, 15],
            'Beta':  [20, 25, 30, 35, 40, 45],
            'Gamma': [10, 15, 10, 15, 10, 15],
            'Delta': [20, 10, 20, 10, 20, 10],
            'Epsilon':[10, 15, 10, 15, 10, 15]
        }
        for p_idx, p in enumerate(periods):
            for cat in categories:
                data.append({'Year': p, 'Category': cat, 'Value': vals[cat][p_idx]})
    elif type == "volatile":
        for p in periods:
            vals = np.random.randint(10, 100, size=len(categories))
            for cat, val in zip(categories, vals):
                data.append({'Year': p, 'Category': cat, 'Value': val})
    else: # Default random
        for p in periods:
            vals = np.random.randint(5, 50, size=len(categories))
            for cat, val in zip(categories, vals):
                data.append({'Year': p, 'Category': cat, 'Value': val})
                
    return pd.DataFrame(data)

def add_ribbon_scenario(fig, df, x_col, category_col, value_col, scenario_name, visible=False, gap=2):
    """Adds a set of traces (bars + ribbons) for a specific scenario."""
    periods = sorted(df[x_col].unique())
    categories = sorted(df[category_col].unique())
    
    # Normalize
    full_index = pd.MultiIndex.from_product([periods, categories], names=[x_col, category_col])
    df_norm = df.set_index([x_col, category_col]).reindex(full_index, fill_value=0).reset_index()
    
    # Use a fixed color map for consistency across scenarios
    color_palette = px.colors.qualitative.D3
    colors = {cat: color_palette[i % len(color_palette)] for i, cat in enumerate(categories)}
    
    coords = {}
    bar_width = 0.35
    traces_added = 0
    
    # Track which categories have been added to the legend for THIS scenario
    seen_categories = set()
    
    # 1. Bars
    for period in periods:
        period_df = df_norm[df_norm[x_col] == period].sort_values(by=[value_col, category_col], ascending=[True, True])
        current_y = 0
        coords[period] = {}
        for _, row in period_df.iterrows():
            cat, val = row[category_col], row[value_col]
            y_start, y_end = current_y, current_y + val
            coords[period][cat] = (y_start, y_end)
            
            if val > 0:
                is_first = cat not in seen_categories
                fig.add_trace(go.Bar(
                    x=[period], y=[val], name=cat, marker_color=colors[cat],
                    legendgroup=cat, offsetgroup=0, base=y_start, width=bar_width,
                    visible=visible, meta=scenario_name,
                    showlegend=is_first, # ONLY SHOW ONCE PER SCENARIO
                    hovertemplate=f"<b>{cat}</b><br>{scenario_name}<br>{period}: {val}<extra></extra>"
                ))
                if is_first:
                    seen_categories.add(cat)
                traces_added += 1
            current_y += (val + gap if val > 0 else 0)

    # 2. Ribbons
    for i in range(len(periods) - 1):
        p1, p2 = periods[i], periods[i+1]
        for cat in categories:
            y1_b, y1_t = coords[p1][cat]
            y2_b, y2_t = coords[p2][cat]
            if (y1_t - y1_b) == 0 and (y2_t - y2_b) == 0: continue
            
            x1, x2 = p1 + bar_width/2, p2 - bar_width/2
            cx, _ = get_sigmoid_curve(x1, 0, x2, 1)
            _, cy_t = get_sigmoid_curve(x1, y1_t, x2, y2_t)
            _, cy_b = get_sigmoid_curve(x1, y1_b, x2, y2_b)
            
            fig.add_trace(go.Scatter(
                x=np.concatenate([cx, cx[::-1]]), y=np.concatenate([cy_t, cy_b[::-1]]),
                fill='toself', fillcolor=colors[cat], opacity=0.3, visible=visible,
                line=dict(width=0.5, color='rgba(255,255,255,0.1)'),
                hoverinfo='skip', showlegend=False, legendgroup=cat, mode='lines',
                meta=scenario_name
            ))
            traces_added += 1
            
    return traces_added

def create_interactive_gallery():
    fig = go.Figure()
    scenarios = ["Market Trends", "High Volatility", "Random A", "Random B", "Random C"]
    types = ["market_share", "volatile", "random", "random", "random"]
    
    trace_counts = []
    for i, (name, stype) in enumerate(zip(scenarios, types)):
        df = generate_scenario_data(stype)
        count = add_ribbon_scenario(fig, df, 'Year', 'Category', 'Value', name, visible=(i==0))
        trace_counts.append(count)
    
    # Create buttons for the dropdown
    buttons = []
    start_idx = 0
    for i, name in enumerate(scenarios):
        # Create a visibility list for all traces
        visibility = [False] * len(fig.data)
        for j in range(start_idx, start_idx + trace_counts[i]):
            visibility[j] = True
        
        buttons.append(dict(
            label=name,
            method="update",
            args=[{"visible": visibility}, {"title": f"Ribbon Chart: {name}"}]
        ))
        start_idx += trace_counts[i]

    fig.update_layout(
        updatemenus=[dict(active=0, buttons=buttons, x=0.1, y=1.15, xanchor='left', yanchor='top')],
        title="Ribbon Chart: Market Trends",
        xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
        barmode='overlay', plot_bgcolor='white', paper_bgcolor='white',
        height=750, margin=dict(t=120)
    )
    
    fig.write_html("ribbon_gallery.html")
    print("Interactive gallery generated: ribbon_gallery.html")

if __name__ == "__main__":
    create_interactive_gallery()
