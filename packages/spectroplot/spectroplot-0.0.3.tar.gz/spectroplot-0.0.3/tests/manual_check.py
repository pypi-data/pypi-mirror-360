import sys
import os

# Add the src directory to Python path so Python can find spectroplot module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pandas as pd
import matplotlib.pyplot as plt
from spectroplot.spectroplot import SpectroPlot

sp = SpectroPlot(excel_file='data.xlsx')
sp.load_data()
sp.plot()  # checked. res=OK
# sp.plot(min_freq=110, max_freq=190)  # checked. res=OK
# sp.occupied_ranges(output_file='occupied.xlsx')  # checked. res=OK
# sp.occupied_ranges(output_file='occupied-limited.xlsx', min_freq=110, max_freq=190)  # checked. res=OK.
# sp.unoccupied_ranges(output_file='unoccupied.xlsx')  # checked. res=OK
sp.unoccupied_ranges(output_file='unoccupied-limited.xlsx', min_freq=110, max_freq=190)  # checked. res=OK