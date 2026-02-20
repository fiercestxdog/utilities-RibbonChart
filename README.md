# Power BI Ribbon Chart for Python (Plotly)

This project provides a robust implementation of the **Power BI Ribbon Chart** using Python and Plotly. It mimics the core behavior of Power BI by dynamically re-sorting categories at every time point to reflect ranking changes, while connecting them with smooth, flowing ribbons.

## 🚀 Features
- **Dynamic Ranking**: Categories are automatically sorted at each X-axis point (highest value at the top).
- **Smooth Flow**: Uses Sigmoid curves to create organic transitions between data points.
- **Vertical Spacing**: Configurable `gap` parameter to add whitespace between ribbons for better clarity.
- **Full Interactivity**: Supports Plotly's legend toggling, hovering, and zooming.
- **Lifecycle Handling**: Correctlty handles series that start late (entry), drop out (exit), or hit zero (tapering).

## 🛠️ Prerequisites
Ensure you have the following libraries installed:
```bash
pip install pandas numpy plotly
```

## 📖 How to Use

### 1. Basic Implementation
The core function is `create_ribbon_chart`. It expects a "long-form" Pandas DataFrame.

```python
from ribbon_chart import create_ribbon_chart
import pandas as pd

# 1. Prepare your data (Long format)
data = {
    'Year': [2023, 2023, 2024, 2024],
    'Category': ['A', 'B', 'A', 'B'],
    'Value': [10, 20, 30, 15]
}
df = pd.DataFrame(data)

# 2. Generate the chart
fig = create_ribbon_chart(
    df, 
    x_col='Year', 
    category_col='Category', 
    value_col='Value', 
    title="My Ribbon Chart",
    gap=2  # Optional: Vertical space between ribbons
)

# 3. Show or Save
fig.show()
fig.write_html("my_chart.html")
```

### 2. Parameter Reference
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `df` | `pd.DataFrame` | The data in long format (one row per category/period). |
| `x_col` | `str` | Name of the column for the X-axis (e.g., 'Year', 'Month'). |
| `category_col`| `str` | Name of the column identifying the series (e.g., 'Company'). |
| `value_col` | `str` | Name of the column containing the numeric values. |
| `title` | `str` | The title of the chart. |
| `gap` | `int/float` | Vertical whitespace between ribbons in the stack (default: 2). |

## 🧪 Running the Tests
You can run the script directly to generate an interactive gallery of test cases:
```bash
python projects/ribbon_chart/ribbon_chart.py
```
This will produce `ribbon_gallery.html`, which includes a dropdown menu to switch between different data scenarios (Market Trends, High Volatility, Random Data).

## 📂 Project Structure
- `ribbon_chart.py`: Main logic containing the plotting function and curve generator.
- `README.md`: This documentation.
- `*.html`: Generated interactive chart examples.
