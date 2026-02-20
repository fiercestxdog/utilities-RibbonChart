# Ribbon Chart Refactored

This version of the project splits the logic into a reusable engine and a specific use case application.

## 📂 Project Structure
- `ribbon_engine.py`: The "core" library. It contains `create_ribbon_chart()`, which is agnostic to the data type. It handles sigmoid math, trace stacking, and ranking logic.
- `employee_app.py`: The "UI/App" layer. It handles file I/O (CSV/Excel), data cleaning, filtering (Top N), and specific formatting for employee hours.

## 🚀 Capabilities

### 1. Robustness
- **Validation**: Both files check for required columns and data types.
- **Fail-Safe**: Handles missing categories or periods gracefully without breaking the ribbon flow.
- **Data Cleaning**: Automatically handles NaNs and non-numeric values.

### 2. Simplicity
- **Abstraction**: You don't need to know how sigmoid curves work. Just pass a long-form DataFrame to `create_ribbon_chart`.
- **Automatic Ranking**: The engine automatically sorts categories at every X-axis point to ensure the "ribbons" flow according to rank.

### 3. Optional Features
- **Top N Filtering**: Show only the most significant contributors.
- **Custom Tooltips**: Pass standard Plotly hover templates for professional-looking popups.
- **Custom Aesthetics**: Easily change color schemes, gap sizes, and bar widths.
- **Multi-Format Support**: Reads `.csv`, `.xlsx`, and `.xls`.

## 🛠️ Usage

```bash
# Generate a report with fake data, filtering for top 5 employees, and wide gaps
python employee_app.py --top 5 --gap 8 --output my_report.html

# Run with your own Excel file
python employee_app.py --input data.xlsx
```
