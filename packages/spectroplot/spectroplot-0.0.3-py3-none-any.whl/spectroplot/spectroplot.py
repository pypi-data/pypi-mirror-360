import pandas as pd
import matplotlib.pyplot as plt

class SpectroPlot:
    """
    A class to analyze and visualize frequency occupancy data across categories,
    including plotting overlap profiles and exporting occupied or unoccupied ranges.

    The class reads frequency ranges from an Excel file, cleans the data,
    and provides methods to:
        - plot overlaps per category
        - export occupied frequency intervals
        - export unoccupied frequency intervals

    Attributes:
        excel_file (str): Path to the Excel file containing frequency data.
        sheet_name (str): Sheet name in the Excel file.
        columns (list of str): Expected column names [Category, Start, Stop, Exclude].
        epsilon (float): Frequency resolution for merging events.
        df (pandas.DataFrame): Cleaned data loaded from the Excel file.
        categories (list of str): Unique categories found in the data.
        colormap (matplotlib Colormap): Colormap to use for plotting.
        min_freq (float): Minimum frequency in the dataset.
        max_freq (float): Maximum frequency in the dataset.
    """

    def __init__(self,
                 excel_file,
                 sheet_name='Sheet1',
                 columns=None,
                 epsilon=1e-6):
        """
        Initialize SpectroPlot with the Excel file and configuration.

        Parameters:
            excel_file (str): Path to the Excel file.
            sheet_name (str): Sheet name containing the frequency data.
            columns (list of str, optional): List of 4 column names [Category, Start, Stop, Exclude].
            epsilon (float): Tolerance for merging closely spaced frequency events.
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
        """
        Load, clean, and preprocess the Excel data, determining frequency bounds
        and unique categories.

        Raises:
            RuntimeError: If the file or sheet cannot be read.
            ValueError: If required columns are missing or data becomes invalid after cleaning.
        """
        try:
            df = pd.read_excel(
                io=self.excel_file,
                sheet_name=self.sheet_name,
                usecols=self.columns,
            )
        except Exception as e:
            raise RuntimeError(f"Could not read file '{self.excel_file}', sheet '{self.sheet_name}': {e}") from e

        # Ensure required columns exist
        missing_cols = [col for col in self.columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in the Excel sheet: {missing_cols}")

        # Strip whitespace in string columns
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].str.strip()

        # Drop rows missing start/end frequencies
        df.dropna(subset=[self.start_col, self.end_col], inplace=True)

        # Exclude rows marked with 'yes' in Exclude column
        df = df[df[self.exclude_col].fillna('').str.lower() != 'yes']

        # Convert start and end frequencies to numeric
        df[self.start_col] = pd.to_numeric(df[self.start_col], errors='coerce')
        df[self.end_col] = pd.to_numeric(df[self.end_col], errors='coerce')
        df.dropna(subset=[self.start_col, self.end_col], inplace=True)

        # Drop rows where start > end (invalid ranges)
        df = df[df[self.start_col] <= df[self.end_col]]
        if df.empty:
            raise ValueError("No valid data left after cleaning!")

        # Determine unique categories
        self.categories = df[self.category_col].unique()
        if len(self.categories) == 0:
            raise ValueError("No categories found after filtering!")

        # Assign color map for plots
        self.colormap = plt.colormaps.get_cmap('tab20')

        # Determine dataset frequency bounds
        self.min_freq = df[self.start_col].min()
        self.max_freq = df[self.end_col].max()

        self.df = df

    def _collect_merged_events(self, cat_df, min_bound, max_bound):
        """
        Collect start/end events for a category dataframe and merge close events.

        Parameters:
            cat_df (pandas.DataFrame): Dataframe containing rows for a single category.
            min_bound (float): Lower frequency bound.
            max_bound (float): Upper frequency bound.

        Returns:
            list of tuples: Merged events [(frequency, delta), ...].
        """
        events = []
        for _, row in cat_df.iterrows():
            start = max(row[self.start_col], min_bound)
            end = min(row[self.end_col], max_bound)
            if start > end:
                continue
            events.append((start, 1))
            events.append((end, -1))

        if not events:
            return []

        events.sort()
        merged_events = []
        i = 0
        while i < len(events):
            freq, delta = events[i]
            total_delta = delta
            j = i + 1
            # Merge events within epsilon
            while j < len(events) and abs(events[j][0] - freq) < self.epsilon:
                total_delta += events[j][1]
                j += 1
            merged_events.append((freq, total_delta))
            i = j

        return merged_events

    def _process_categories(self, min_bound, max_bound, callback):
        """
        Iterate over each category and process merged frequency events,
        calling the provided callback function.

        Parameters:
            min_bound (float): Lower frequency bound for processing.
            max_bound (float): Upper frequency bound for processing.
            callback (function): Function with signature callback(idx, category, merged_events),
                                 where merged_events is a list of (frequency, delta).
        """
        for idx, category in enumerate(self.categories):
            cat_df = self.df[self.df[self.category_col] == category]
            merged_events = self._collect_merged_events(cat_df, min_bound, max_bound)
            callback(idx, category, merged_events)

    def plot(self, min_freq=None, max_freq=None):
        """
        Plot frequency occupancy overlaps for each category as staircase plots.

        Parameters:
            min_freq (float, optional): Lower frequency limit for plotting.
                                        Defaults to the dataset's min frequency.
            max_freq (float, optional): Upper frequency limit for plotting.
                                        Defaults to the dataset's max frequency.

        Raises:
            RuntimeError: If data has not been loaded via load_data().
        """
        if self.df is None:
            raise RuntimeError("Data has not been loaded. Call load_data() first.")

        min_bound = min_freq if min_freq is not None else self.min_freq
        max_bound = max_freq if max_freq is not None else self.max_freq
        n_categories = len(self.categories)
        fig, axes = plt.subplots(n_categories, 1, figsize=(12, 4 * n_categories), sharex=True)
        if n_categories == 1:
            axes = [axes]

        def plot_callback(idx, category, merged_events):
            ax = axes[idx]
            if not merged_events:
                ax.text(0.5, 0.5, f"No valid data for category '{category}'",
                        ha='center', va='center', fontsize=14)
                ax.set_xlim(min_bound, max_bound)
                ax.set_ylim(bottom=0)
                ax.set_title(f"Category '{category}'")
                return

            freqs, overlaps, current_overlap = [], [], 0
            for freq, delta in merged_events:
                freqs.append(freq)
                current_overlap += delta
                overlaps.append(current_overlap)

            freqs = [min_bound] + freqs + [max_bound]
            overlaps = [0] + overlaps + [0]

            color = self.colormap(idx / max(n_categories - 1, 1))
            ax.step(freqs, overlaps, where='post', color=color, label=category)
            ax.fill_between(freqs, overlaps, step='post', alpha=0.4, color=color)
            ax.set_xlim(min_bound, max_bound)
            ax.set_ylim(bottom=0)
            ax.set_ylabel('Repeat Nbr')
            ax.grid(True)
            ax.legend(loc='upper right')

        self._process_categories(min_bound, max_bound, plot_callback)
        axes[-1].set_xlabel('Frequency')
        plt.tight_layout()
        plt.show()

    def occupied_ranges(self, output_file, min_freq=None, max_freq=None):
        """
        Export continuous occupied frequency ranges per category to an Excel file.

        Parameters:
            output_file (str): Path to the output Excel file.
            min_freq (float, optional): Lower frequency limit for exported ranges.
                                        Defaults to the dataset's min frequency.
            max_freq (float, optional): Upper frequency limit for exported ranges.
                                        Defaults to the dataset's max frequency.

        Raises:
            RuntimeError: If data has not been loaded via load_data().
            ValueError: If no valid occupied ranges are found.
        """
        if self.df is None:
            raise RuntimeError("Data has not been loaded. Call load_data() first.")

        min_bound = min_freq if min_freq is not None else self.min_freq
        max_bound = max_freq if max_freq is not None else self.max_freq
        export_rows = []

        def occupied_callback(idx, category, merged_events):
            current_overlap = 0
            range_start = None
            for freq, delta in merged_events:
                prev_overlap = current_overlap
                current_overlap += delta
                if prev_overlap == 0 and current_overlap > 0:
                    range_start = freq
                elif prev_overlap > 0 and current_overlap == 0:
                    export_rows.append({'Category': category, 'Start': range_start, 'Stop': freq})

        self._process_categories(min_bound, max_bound, occupied_callback)
        if not export_rows:
            raise ValueError("No valid occupied frequency ranges found.")

        pd.DataFrame(export_rows).to_excel(output_file, index=False, sheet_name='OccupiedRanges')

    def unoccupied_ranges(self, output_file, min_freq=None, max_freq=None):
        """
        Export continuous unoccupied frequency ranges per category to an Excel file.

        Parameters:
            output_file (str): Path to the output Excel file.
            min_freq (float, optional): Lower frequency limit for exported ranges.
                                        Defaults to the dataset's min frequency.
            max_freq (float, optional): Upper frequency limit for exported ranges.
                                        Defaults to the dataset's max frequency.

        Raises:
            RuntimeError: If data has not been loaded via load_data().
            ValueError: If no valid unoccupied ranges are found.
        """
        if self.df is None:
            raise RuntimeError("Data has not been loaded. Call load_data() first.")

        min_bound = min_freq if min_freq is not None else self.min_freq
        max_bound = max_freq if max_freq is not None else self.max_freq
        export_rows = []

        def unoccupied_callback(idx, category, merged_events):
            current_overlap = 0
            unoccupied_start = min_bound
            for freq, delta in merged_events:
                prev_overlap = current_overlap
                current_overlap += delta
                if prev_overlap == 0 and current_overlap > 0:
                    if unoccupied_start < freq:
                        export_rows.append({'Category': category, 'Start': unoccupied_start, 'Stop': freq})
                elif prev_overlap > 0 and current_overlap == 0:
                    unoccupied_start = freq
            if current_overlap == 0 and unoccupied_start < max_bound:
                export_rows.append({'Category': category, 'Start': unoccupied_start, 'Stop': max_bound})

        self._process_categories(min_bound, max_bound, unoccupied_callback)
        if not export_rows:
            raise ValueError("No unoccupied frequency ranges found.")

        pd.DataFrame(export_rows).to_excel(output_file, index=False, sheet_name='UnoccupiedRanges')
