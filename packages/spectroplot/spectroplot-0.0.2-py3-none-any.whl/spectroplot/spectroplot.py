import pandas as pd
import matplotlib.pyplot as plt

class SpectroPlot:
    def __init__(self,
                 excel_file,
                 sheet_name='Sheet1',
                 columns=None,
                 epsilon=1e-6):
        """Initialize SpectrumPlotter with configuration.

        Parameters:
            excel_file: path to the Excel file.
            sheet_name: sheet name in the Excel file.
            columns: list of 4 column names [category, start, end, exclude].
            epsilon: tolerance for merging close frequencies.
        """
        self.excel_file = excel_file
        self.sheet_name = sheet_name
        self.columns = columns or ['Category', 'Start', 'Stop', 'Exclude']
        if len(self.columns) != 4:
            raise ValueError("Expected exactly 4 columns: [Category, Start, Stop, Exclude]")

        # Map roles to columns
        self.category_col, self.start_col, self.end_col, self.exclude_col = self.columns

        self.epsilon = epsilon
        self.df = None
        self.categories = []
        self.colormap = None
        self.min_freq = None
        self.max_freq = None


    def load_data(self):
        """Load the Excel data, clean, determine min and max frequencies."""
        try:
            df = pd.read_excel(
                    io=self.excel_file,
                    sheet_name=self.sheet_name,
                    usecols=self.columns,
            )
        except Exception as e:
            raise RuntimeError(f"Could not read file '{self.excel_file}', sheet '{self.sheet_name}': {e}")

        # Check required columns
        missing_cols = [col for col in self.columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in the Excel sheet: {missing_cols}")

        # Strip whitespace in string columns
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].str.strip()

        # Drop rows with NaN in start/end frequencies
        df.dropna(subset=[self.start_col, self.end_col], inplace=True)

        # Remove rows with exclude='yes'
        df = df[df[self.exclude_col].fillna('').str.lower() != 'yes']

        # Convert frequencies to numeric (in place)
        df[self.start_col] = pd.to_numeric(df[self.start_col], errors='coerce')
        df[self.end_col] = pd.to_numeric(df[self.end_col], errors='coerce')

        # Drop rows with invalid (NaN) frequencies after conversion
        df.dropna(subset=[self.start_col, self.end_col], inplace=True)

        # Drop rows where start > end
        df = df[df[self.start_col] <= df[self.end_col]]
        if df.empty:
            raise ValueError("No valid data left after cleaning!")

        # Determine unique categories
        self.categories = df[self.category_col].unique()
        if len(self.categories) == 0:
            raise ValueError("No categories found after filtering!")

        # Create colormap for unique category colors
        self.colormap = plt.colormaps.get_cmap('tab20')

        # Determine default frequency bounds
        self.min_freq = df[self.start_col].min()
        self.max_freq = df[self.end_col].max()

        # Clean data
        self.df = df


    def plot(self, min_freq=None, max_freq=None):
        """Plot frequency overlaps per category.

        Parameters:
            min_freq: optional lower bound for plotting.
            max_freq: optional upper bound for plotting.
        """
        if self.df is None:
            raise RuntimeError("Data has not been loaded. Call load_data() first.")

        min_freq = min_freq if min_freq is not None else self.min_freq
        max_freq = max_freq if max_freq is not None else self.max_freq

        n_categories = len(self.categories)
        fig, axes = plt.subplots(n_categories, 1, figsize=(12, 4 * n_categories), sharex=True)
        if n_categories == 1:
            axes = [axes]  # make it iterable

        for idx, (ax, category) in enumerate(zip(axes, self.categories)):
            cat_df = self.df[self.df[self.category_col] == category]

            # Collect events: (frequency, delta)
            events = []
            for _, row in cat_df.iterrows():
                start = max(row[self.start_col], min_freq)
                end = min(row[self.end_col], max_freq)
                if start > end:
                    continue  # skip intervals outside plotting boundaries
                events.append((start, 1))
                events.append((end, -1))

            if not events:
                ax.text(0.5, 0.5, f"No valid data for category '{category}'",
                        ha='center', va='center', fontsize=14)
                ax.set_xlim(min_freq, max_freq)
                ax.set_ylim(bottom=0)
                ax.set_title(f"Category '{category}'")
                continue

            # Sort and merge close events
            events.sort()
            merged_events = []
            i = 0
            while i < len(events):
                freq, delta = events[i]
                total_delta = delta
                j = i + 1
                while j < len(events) and abs(events[j][0] - freq) < self.epsilon:
                    total_delta += events[j][1]
                    j += 1
                merged_events.append((freq, total_delta))
                i = j

            # Build staircase data
            freqs, overlaps, current_overlap = [], [], 0
            for freq, delta in merged_events:
                freqs.append(freq)
                current_overlap += delta
                overlaps.append(current_overlap)

            # Add boundary points
            freqs = [min_freq] + freqs + [max_freq]
            overlaps = [0] + overlaps + [0]

            # Plot
            color = self.colormap(idx / max(n_categories - 1, 1))  # normalize index to [0,1]
            # ax.step(freqs, overlaps, where='post', color=color, label={category})
            ax.step(freqs, overlaps, where='post', color=color, label=category)
            ax.fill_between(freqs, overlaps, step='post', alpha=0.4, color=color)

            ax.set_xlim(min_freq, max_freq)
            ax.set_ylim(bottom=0)
            # ax.set_title(f"Category '{category}'")
            ax.set_ylabel('Repeat Nbr')
            ax.grid(True)
            ax.legend(loc='upper right')

        axes[-1].set_xlabel('frequency')
        plt.tight_layout()
        plt.show()