import pandas as pd
import numpy as np
import random  # for lists of tuples

np.random.seed(42)  # reproducibility

# Configuration
n_rows = 200
categories = [
    ('DVB-T UHF', 470, 862),  # DVB-T UHF band
    ('GSM-900', 880, 915),  # GSM900 UL band
    ('GSM-900', 925, 960),  # GSM900 DL band
    ('LTE-800', 791, 821),  # LTE800 DL band
    ('LTE-800', 832, 862),  # LTE800 UL band
]
regions = ['North', 'South', 'East', 'West']
system_types = ['Fixed', 'Mobile', 'Satellite']

data = []

for _ in range(n_rows):
    cat_name, band_min, band_max = random.choice(categories)  # <-- FIXED!

    start_freq = np.random.uniform(band_min, band_max - 1)  # leave space for interval
    bandwidth = np.random.uniform(0.1, 10)  # 0.1 MHz – 10 MHz bandwidth
    end_freq = start_freq + bandwidth

    # Clamp end frequency to stay within band
    end_freq = min(end_freq, band_max)

    exclude = np.random.choice(['yes', 'no'], p=[0.05, 0.95])  # 5% excluded
    description = f"{cat_name} assignment from {start_freq:.1f} to {end_freq:.1f} MHz"
    region = np.random.choice(regions)
    system_type = np.random.choice(system_types)

    data.append({
        'Category': cat_name,
        'Start': round(start_freq, 3),
        'Stop': round(end_freq, 3),
        'Exclude': exclude,
        'Description': description,
        'Region': region,
        'System type': system_type
    })

df = pd.DataFrame(data)

# Save to Excel
excel_path = 'data.xlsx'
df.to_excel(excel_path, index=False, sheet_name='Sheet1')
print(f"Generated {n_rows} telecom frequency assignments and saved to {excel_path}")