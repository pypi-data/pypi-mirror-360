import wx
import wx.grid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PandasGrid(wx.Dialog):
    
    def __init__(self, parent, id, df: pd.DataFrame):
        super().__init__(parent, title=f"DataFrame characteristics: {id}", size=(600, 400))

        self.df = df

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create the grid
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(df.shape[0], df.shape[1])

        # Set column labels
        for col, colname in enumerate(df.columns):
            self.grid.SetColLabelValue(col, str(colname))

        # Fill grid and make cells read-only
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                val = str(df.iloc[row, col])
                self.grid.SetCellValue(row, col, val)
                self.grid.SetReadOnly(row, col, True)

        vbox.Add(self.grid, 1, wx.EXPAND | wx.ALL, 10)

        # Add a button to show histogram
        self.hist_button = wx.Button(self, label="Histogram")
        self.hist_button.Bind(wx.EVT_BUTTON, self.OnShowHistogram)
        vbox.Add(self.hist_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        self.SetSizer(vbox)

    def OnShowHistogram(self, event):
        selected_cols = self.grid.GetSelectedCols()
        if not selected_cols:
            wx.MessageBox("Please select a column to plot.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        col_idx = selected_cols[0]
        colname = self.df.columns[col_idx]
        data = pd.to_numeric(self.df[colname], errors='coerce').dropna()

        if data.empty:
            wx.MessageBox(f"No numeric data in column '{colname}'", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        # Calcul de l'histogramme sans affichage
        counts, bins = np.histogram(data, bins=20)
        probabilities = counts / counts.sum()*100  # Normalisation

        # Plot manuel
        plt.figure(figsize=(6, 4))
        plt.bar(bins[:-1], probabilities, width=np.diff(bins), align='edge',
                color='skyblue', edgecolor='black')
        plt.title(f"Histogram of {colname}")
        plt.xlabel(colname)
        plt.ylabel("Probability [%]")
        plt.grid(visible=True)
        plt.tight_layout()
        plt.show()