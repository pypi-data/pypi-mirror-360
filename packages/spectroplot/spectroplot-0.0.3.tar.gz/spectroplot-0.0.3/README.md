# SpectroPlot

**SpectroPlot** is a Python tool for analyzing, visualizing, and exporting 
frequency occupancy data across multiple categories. It provides:
- Overlap plots showing simultaneous frequency use
- Export of occupied ranges
- Export of unoccupied ranges

It’s designed for radio spectrum engineers, regulators, or analysts who want 
to visualize how frequency use stack up within different categories 
(e.g., services, technologies, operators, etc.).

![Example Plot](img/Figure_1.png)

---
## Features

- Load and clean frequency interval data from Excel file   
- Flexible category, frequency, and exclude handling  
- Handles near-identical frequencies with `epsilon` tolerance
- Configurable frequency bounds
- Plot frequency overlaps per category
- Export occupied and unoccupied frequency intervals to Excel
- Modular, reusable class design with tests

---
## Requirements

- Python 3.12+
- `pandas`
- `matplotlib`
- `openpyxl` (required by pandas to read `.xlsx`)

## Installation

```bash
# From PyPI
py -m pip install spectroplot  # on Windows
python3 -m pip install spectroplot  # on Unix/macOS

# From GitHub
py -m pip install git+https://github.com/murzabaevb/spectroplot.git  # on Windows 
python3 -m pip install git+https://github.com/murzabaevb/spectroplot.git  # on Unix/macOS
```

---
## Expected Excel file format

Your Excel sheet must contain **four columns**, for example:

| Category | Start  | Stop   | Exclude |
|----------|--------|--------|---------|
| LTE      | 700.0  | 720.0  |         |
| GSM      | 900.0  | 915.0  | yes     |
| 5G       | 3500.0 | 3700.0 |         |

- **Category**: name of the assignment category (e.g., LTE, GSM)  
- **Start**: start frequency (numeric)  
- **Stop**: end frequency (numeric)  
- **Exclude**: set to "yes" (case-insensitive) to exclude the row from plotting

*Note:* These four columns could be named differently in Excel file. If so, 
it is necessary to pass these headers when instantiating the object of the 
class as shown in the example below. Apart from these four columns, the Excel 
file may contain other columns which would be ignored during reading.

---
## Usage Examples

```python
from spectroplot import SpectroPlot

# Initialize with your Excel file, default sheet name and column headers:
# - default `sheet_name='Sheet1`,
# - default `columns=['Category', 'Start', 'Stop', 'Exclude']`
sp = SpectroPlot(excel_file='data.xlsx')

# Load and clean data
sp.load_data()

# Plot overlaps
sp.plot()
```

```python
from spectroplot import SpectroPlot

# Initialize with your Excel file and custom sheet/columns
sp = SpectroPlot(
    excel_file='assignments.xlsx',
    sheet_name='uhf',
    columns=['system', 'f_low', 'f_hi', 'excl'],
)

# Load and clean data
sp.load_data()

# Plot overlaps of entire data read
sp.plot()

# Or specify frequency bounds as per your requirement
sp.plot(min_freq=600, max_freq=4000)
```

```python
from spectroplot import SpectroPlot

# Initialize with your Excel file, default sheet name and column headers:
# - default `sheet_name='Sheet1`,
# - default `columns=['Category', 'Start', 'Stop', 'Exclude']`
sp = SpectroPlot(excel_file='data.xlsx')

# Load and clean data
sp.load_data()

# Export occupied frequency ranges
sp.occupied_ranges(output_file='occupied.xlsx')

# Or specify frequency bounds as per your requirement
sp.occupied_ranges(output_file='occupied.xlsx', min_freq=600, max_freq=4000)

# Export unoccupied frequency ranges
sp.unoccupied_ranges(output_file='unoccupied.xlsx')

# Or specify frequency bounds as per your requirement
sp.unoccupied_ranges(output_file='unoccupied.xlsx', min_freq=600, max_freq=4000)
```

---
## Output

- Generates a **matplotlib plot** with one subplot per category
- Each plot shows the number of overlapping frequency assignments as a staircase
- Colors are automatically assigned from the `tab20` colormap

---
## Parameters

`SpectroPlot` constructor:
- **excel_file**: Path to your Excel file  
- **sheet_name**: Name of the worksheet to read (default: `'Sheet1'`)  
- **columns**: List of four column names in order (default: `['Category', 'Start', 'Stop', 'Exclude']`)  
- **epsilon**: Tolerance for merging events with nearly identical frequencies (default: `1e-6`)  

`plot()` method:
- **min_freq**: Lower frequency bound of plotting (default: Min freq. in Excel file)
- **max_freq**: Upper frequency bound of plotting (default: Max freq. in Excel file)

`occupied_ranges()` method:
- **output_file**: Path to your Excel file
- **min_freq**: Lower frequency bound of export (default: Min freq. in Excel file)
- **max_freq**: Upper frequency bound of export (default: Max freq. in Excel file)

`unoccupied_ranges()` method:
- **output_file**: Path to your Excel file
- **min_freq**: Lower frequency bound of export (default: Min freq. in Excel file)
- **max_freq**: Upper frequency bound of export (default: Max freq. in Excel file)

---
## License

MIT License. Feel free to use, modify, and contribute!

---
## Project Links
- [GitHub Repository](https://github.com/murzabaevb/spectroplot.git)
- [GitHub Issues](https://github.com/murzabaevb/spectroplot/issues)
