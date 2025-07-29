import logging

import numpy as np
from shapely.geometry import Point, LineString
from typing import Literal
import pandas as pd

from .PyTranslate import _
from .drawing_obj import Element_To_Draw
from .PyVertexvectors import Triangulation, vector,Zones, zone
from .wolf_array import WolfArray, header_wolf

class Array_analysis_onepolygon():
    """ Class for values analysis of an array based on a polygon.

    This class select values insides a polygon and plot statistics of the values.

    The class is designed to be used with the WolfArray class and the vector class from the PyVertexvectors module.

    Plots of the values distribution can be generated using seaborn or plotly.
    """

    def __init__(self, wa:WolfArray, polygon:vector):

        self._wa = wa
        self._polygon = polygon

        self._selected_cells = None
        self._values = None

    def values(self, which:Literal['Mean', 'Std', 'Median', 'Sum', 'Volume', 'Values']) -> pd.DataFrame | float:
        """ Get the values as a pandas DataFrame

        :param which: Mean, Std, Median, Sum, Volume, Values
        """

        authrorized = ['Mean', 'Std', 'Median', 'Sum', 'Volume', 'Values']
        if which not in authrorized:
            raise ValueError(f"Invalid value for 'which'. Must be one of {authrorized}.")

        if self._values is None:
            self.compute_values()

        if self._values is None:
            raise ValueError("No values computed. Please call compute_values() first.")

        if which == 'Values':
            return pd.DataFrame(self._values[_(which)], columns=[which])
        else:
            return self._values[which]

    def select_cells(self, mode:Literal['polygon', 'buffer'] = 'polygon', **kwargs):
        """ Select the cells inside the polygon """

        if mode == 'polygon':
            if 'polygon' in kwargs:
                self._polygon = kwargs['polygon']
                self._select_cells_polygon(self._polygon)
            else:
                raise ValueError("No polygon provided. Please provide a polygon to select cells.")
        elif mode == 'buffer':
            if 'buffer' in kwargs:
                self._select_cells_buffer(kwargs['buffer'])
            else:
                raise ValueError("No buffer size provided. Please provide a buffer size to select cells.")
        else:
            raise ValueError("Invalid mode. Please use 'polygon' or 'buffer'.")

    def _select_cells_polygon(self, selection_poly:vector):
        """ Select the cells inside the polygon """

        self._polygon = selection_poly
        self._selected_cells = self._wa.get_xy_inside_polygon(self._polygon)

    def _select_cells_buffer(self, buffer_size:float = 0.0):
        """ Select the cells inside the buffer of the polygon """

        self._polygon = self._polygon.buffer(buffer_size, inplace=False)
        self._selected_cells = self._wa.get_xy_inside_polygon(self._polygon)

    def compute_values(self):
        """ Get the values of the array inside the polygon """

        if self._selected_cells is None:
            if self._polygon is None:
                raise ValueError("No polygon provided. Please provide a polygon to select cells.")

        self._values = self._wa.statistics(self._polygon)

    def plot_values(self, show:bool = True, bins:int = 100,
                    engine:Literal['seaborn', 'plotly'] = 'seaborn'):
        """ Plot a histogram of the values """

        if engine == 'seaborn':
            return self.plot_values_seaborn(show=show, bins=bins)
        elif engine == 'plotly':
            return self.plot_values_plotly(show=show, bins=bins)

    def plot_values_seaborn(self, bins:int = 100, show:bool = True):
        """ Plot a histogram of the values """

        import seaborn as sns
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        sns.histplot(self.values('Values'), bins=bins,
                     kde=True, ax=ax,
                     stat="density")

        # Add mean, std, median values on plot
        mean = self.values('Mean')
        # std = self.values('Std').values[0]
        median = self.values('Median')

        # test noen and masked value
        if mean is not None and mean is not np.ma.masked:
            ax.axvline(mean, color='r', linestyle='--', label=f'Mean: {mean:.2f}')
        if median is not None and median is not np.ma.masked:
            ax.axvline(median, color='b', linestyle='--', label=f'Median: {median:.2f}')

        ax.legend()
        ax.set_xlabel('Values')
        ax.set_ylabel('Frequency')
        ax.set_title('Values distribution')

        if show:
            plt.show()

        return (fig, ax)

    def plot_values_plotly(self, bins:int = 100, show:bool = True):
        """ Plot a histogram of the values """

        import plotly.express as px

        fig = px.histogram(self.values('Values'), x='Values',
                           nbins=bins, title='Values distribution',
                           histnorm='probability density')

        # Add mean, std, median values on plot
        mean = self.values('Mean')
        median = self.values('Median')

        if mean is not None and mean is not np.ma.masked:
            fig.add_vline(x=mean, line_color='red', line_dash='dash', annotation_text=f'Mean: {mean:.2f}')
        if median is not None and median is not np.ma.masked:
            fig.add_vline(x=median, line_color='blue', line_dash='dash', annotation_text=f'Median: {median:.2f}')

        fig.update_layout(xaxis_title='Values', yaxis_title='Frequency')

        if show:
            fig.show(renderer='browser')

        return fig


class Array_analysis_polygons():
    """ Class for values analysis of an array based on a polygon.

    This class select values insides a polygon and plot statistics of the values.

    The class is designed to be used with the WolfArray class and the vector class from the PyVertexvectors module.

    Plots of the values distribution can be generated using seaborn or plotly.
    """

    def __init__(self, wa:WolfArray, polygons:zone):
        """ Initialize the class with a WolfArray and a zone of polygons """

        self._wa = wa
        self._polygons = polygons

        self._zone = {polygon.myname: Array_analysis_onepolygon(self._wa, polygon) for polygon in self._polygons.myvectors}

    def __getitem__(self, key):
        """ Get the polygon by name """
        if key in self._zone:
            return self._zone[key]
        else:
            raise KeyError(f"Polygon {key} not found in zone.")

    def plot_values(self, show:bool = True, bins:int = 100,
                    engine:Literal['seaborn', 'plotly'] = 'seaborn'):
        """ Plot a histogram of the values """

        if engine == 'seaborn':
            return self.plot_values_seaborn(show=show, bins=bins)
        elif engine == 'plotly':
            return self.plot_values_plotly(show=show, bins=bins)

    def plot_values_seaborn(self, bins:int = 100, show:bool = True):
        """ Plot a histogram of the values """
        return {key: pol.plot_values_seaborn(bins=bins, show=show) for key, pol in self._zone.items()}

    def plot_values_plotly(self, bins:int = 100, show:bool = True):
        """ Plot a histogram of the values """

        return {key: pol.plot_values_plotly(bins=bins, show=show) for key, pol in self._zone.items()}

class Slope_analysis:
    """ Class for slope analysis of in an array based on a trace vector.

    This class allows to select cells inside a polygon or a buffer around a trace vector
    and compute the slope of the dike. The slope is computed as the difference in elevation
    between the trace and the cell divided by the distance to the trace.

    The slope is computed for each cell inside the polygon or buffer and accessed in a Pandas Dataframe.

    Plots of the slope distribution can be generated using seaborn or plotly.

    The class is designed to be used with the WolfArray class and the vector class from the PyVertexvectors module.
    """

    def __init__(self, wa:WolfArray, trace:vector):

        self._wa = wa
        self._trace = trace

        self._selection_poly = None
        self._buffer_size = 0.0

        self._selected_cells = None
        self._slopes = None

    @property
    def slopes(self) -> pd.DataFrame:
        """ Get the slopes as a pandas DataFrame """

        if self._slopes is None:
            self.compute_slopes()

        if self._slopes is None:
            raise ValueError("No slopes computed. Please call compute_slopes() first.")

        return pd.DataFrame(self._slopes, columns=['Slope [m/m]'])

    def select_cells(self, mode:Literal['polygon', 'buffer'] = 'polygon', **kwargs):
        """ Select the cells inside the trace """

        if mode == 'polygon':
            if 'polygon' in kwargs:
                self._selection_poly = kwargs['polygon']
                self._select_cells_polygon(self._selection_poly)
            else:
                raise ValueError("No polygon provided. Please provide a polygon to select cells.")
        elif mode == 'buffer':
            if 'buffer' in kwargs:
                self._buffer_size = kwargs['buffer']
                self._select_cells_buffer(self._buffer_size)
            else:
                raise ValueError("No buffer size provided. Please provide a buffer size to select cells.")
        else:
            raise ValueError("Invalid mode. Please use 'polygon' or 'buffer'.")

    def _select_cells_buffer(self, buffer_size:float = 0.0):
        """ Select the cells inside the buffer of the trace """

        self._buffer_size = buffer_size
        self._selection_poly = self._trace.buffer(self._buffer_size, inplace=False)
        self._select_cells_polygon(self._selection_poly)

    def _select_cells_polygon(self, selection_poly:vector):
        """ Select the cells inside the polygon """

        self._selection_poly = selection_poly
        self._selected_cells = self._wa.get_xy_inside_polygon(self._selection_poly)

    def compute_slopes(self):
        """ Get the slope of the dike """

        if self._selected_cells is None:
            self.select_cells()
        if self._selected_cells is None:
            raise ValueError("No cells selected. Please call select_cells() first.")

        trace_ls = self._trace.linestring

        def compute_cell_slope(curxy):
            i, j = self._wa.get_ij_from_xy(curxy[0], curxy[1])
            pt = Point(curxy[0], curxy[1])
            distance_to_trace = trace_ls.distance(pt)
            elevation_on_trace = trace_ls.interpolate(trace_ls.project(pt, normalized=True), normalized=True).z
            if distance_to_trace == 0.0:
                return 0.0
            if elevation_on_trace == -99999.0:
                return 0.0

            return (elevation_on_trace - self._wa.array[i, j]) / distance_to_trace

        self._slopes = [compute_cell_slope(curxy) for curxy in self._selected_cells]

    def plot_slopes(self, show:bool = True, bins:int = 100,
                    engine:Literal['seaborn', 'plotly'] = 'seaborn'):
        """ Plot a histogram of the slopes """

        if engine == 'seaborn':
            return self.plot_slopes_seaborn(show=show, bins=bins)
        elif engine == 'plotly':
            return self.plot_slopes_plotly(show=show, bins=bins)

    def plot_slopes_seaborn(self, bins:int = 100, show:bool = True):
        """ Plot a histogram of the slopes """

        import seaborn as sns
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        sns.histplot(self.slopes, bins=bins,
                     kde=True, ax=ax,
                     stat="density")

        ax.set_xlabel('Slope [m/m]')
        ax.set_ylabel('Frequency')
        ax.set_title('Slope distribution')

        if show:
            plt.show()

        return (fig, ax)

    def plot_slopes_plotly(self, bins:int = 100, show:bool = True):
        """ Plot a histogram of the slopes """

        import plotly.express as px

        fig = px.histogram(self.slopes, x='Slope [m/m]',
                           nbins=bins, title='Slope distribution',
                           histnorm='probability density')

        fig.update_layout(xaxis_title='Slope [m/m]', yaxis_title='Frequency')

        if show:
            fig.show(renderer='browser')

        return fig