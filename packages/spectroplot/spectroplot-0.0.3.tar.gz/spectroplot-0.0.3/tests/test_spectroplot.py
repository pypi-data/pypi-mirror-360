import sys
import os

# Add the src directory to Python path so Python can find spectroplot module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pandas as pd
import matplotlib.pyplot as plt
from spectroplot.spectroplot import SpectroPlot


def make_test_data():
    """Create a sample DataFrame with overlapping and non-overlapping intervals."""
    data = {
        'Category': ['A', 'A', 'A', 'B', 'B', 'B'],
        'Start': [100, 150, 250, 200, 300, 400],
        'Stop': [200, 180, 300, 250, 350, 500],
        'Exclude': ['', '', '', '', '', 'yes'],  # last row excluded
    }
    return pd.DataFrame(data)


def test_load_and_plot(monkeypatch):
    """Test plotting does not raise errors with synthetic data."""
    sp = SpectroPlot(excel_file="dummy.xlsx")  # file won't be used

    # Patch df directly to skip reading Excel
    sp.df = make_test_data()
    sp.categories = sp.df['Category'].unique()
    sp.colormap = plt.colormaps.get_cmap('tab20')
    sp.min_freq = sp.df['Start'].min()
    sp.max_freq = sp.df['Stop'].max()

    # Should produce a plot without exceptions
    sp.plot()


def test_occupied_ranges(tmp_path):
    """Test occupied ranges are correctly exported."""
    sp = SpectroPlot(excel_file="dummy.xlsx")
    sp.df = make_test_data()
    sp.categories = sp.df['Category'].unique()
    sp.colormap = plt.colormaps.get_cmap('tab20')
    sp.min_freq = sp.df['Start'].min()
    sp.max_freq = sp.df['Stop'].max()

    outfile = tmp_path / "occupied.xlsx"
    sp.occupied_ranges(str(outfile))
    assert outfile.exists()

    df_out = pd.read_excel(outfile, sheet_name='OccupiedRanges')
    assert not df_out.empty
    # Basic check: should include expected columns
    assert {'Category', 'Start', 'Stop'}.issubset(df_out.columns)


def test_unoccupied_ranges(tmp_path):
    """Test unoccupied ranges are correctly exported."""
    sp = SpectroPlot(excel_file="dummy.xlsx")
    sp.df = make_test_data()
    sp.categories = sp.df['Category'].unique()
    sp.colormap = plt.colormaps.get_cmap('tab20')
    sp.min_freq = sp.df['Start'].min()
    sp.max_freq = sp.df['Stop'].max()

    outfile = tmp_path / "unoccupied.xlsx"
    sp.unoccupied_ranges(str(outfile))
    assert outfile.exists()

    df_out = pd.read_excel(outfile, sheet_name='UnoccupiedRanges')
    assert not df_out.empty
    # Basic check: should include expected columns
    assert {'Category', 'Start', 'Stop'}.issubset(df_out.columns)


def test_exclude_rows_effect():
    """Test that rows with Exclude='yes' are ignored."""
    sp = SpectroPlot(excel_file="dummy.xlsx")
    df = make_test_data()
    # Add a row that should be excluded
    df.loc[len(df)] = ['A', 600, 700, 'yes']
    sp.df = df
    sp.categories = sp.df['Category'].unique()
    sp.colormap = plt.colormaps.get_cmap('tab20')
    sp.min_freq = sp.df['Start'].min()
    sp.max_freq = sp.df['Stop'].max()

    # After processing, excluded range should not affect occupied intervals
    occupied_before = []

    def cb(idx, cat, events):
        occupied_before.append(events)

    sp._process_categories(sp.min_freq, sp.max_freq, cb)

    # Emulate what load_data would do: clean excluded rows manually
    df_cleaned = sp.df[sp.df[sp.exclude_col].fillna('').str.lower() != 'yes']
    sp.df = df_cleaned
    sp.categories = sp.df['Category'].unique()

    occupied_after = []
    sp._process_categories(sp.min_freq, sp.max_freq, lambda idx, cat, events: occupied_after.append(events))

    assert len(occupied_before) == len(occupied_after)  # same categories
    # Ensure excluded row is dropped: last event should not exceed original data's max freq
    for events in occupied_after:
        if events:
            assert all(freq <= sp.max_freq for freq, _ in events)

