"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

import geopandas as gpd
from pathlib import Path
from typing import List, Union
from shapely.geometry import Polygon, Point
import logging
import wx

from .PyTranslate import _
from .PyVertexvectors import Zones, zone, vector, wolfvertex
from .PyVertex import cloud_vertices, getRGBfromI, getIfromRGB
from .drawing_obj import Element_To_Draw

class Picc_data(Element_To_Draw):
    """
    Read and show PICC data -- see https://geoportail.wallonie.be/georeferentiel/PICC

    """

    def __init__(self,
                 idx:str = '',
                 plotted:bool = True,
                 mapviewer = None,
                 need_for_wx:bool = False,
                 data_dir:Path = Path(r'./data/PICC'),
                 bbox:Union[Polygon, list[float]] = None) -> None:

        super().__init__(idx = idx, plotted = plotted, mapviewer = mapviewer, need_for_wx= need_for_wx)

        self.data_dir = data_dir
        self._filename_vector = 'Wallonie.gdb' #'PICC_Vesdre.shp'
        self._filename_points = 'PICC_Vesdre_points.shp'
        self.zones = None
        self.cloud = None
        self._colors = {'Habitation': [255, 0, 0], 'Annexe': [0, 255, 0], 'Culture, sport ou loisir': [0, 0, 255], 'Autre': [10, 10, 10]}

        self.active_vector = None
        self.active_zone = None

        return None

    def read_data(self, data_dir:Path = None, bbox:Union[Polygon, list[float]] = None, colorize:bool = True) -> None:
        """
        Read data from PICC directory

        :param data_dir: directory where PICC data are stored
        :param bbox: bounding box to select data

        """
        if data_dir is None:
            data_dir = self.data_dir

        datafile = data_dir / self._filename_vector

        if datafile.exists():
            self.zones = Zones(data_dir / self._filename_vector, bbox = bbox, mapviewer=self.mapviewer, colors= self._colors)
        else:
            logging.info(_('File not found : {}').format(datafile))

            if self.mapviewer is not None:
                dlg = wx.SingleChoiceDialog(None, _('Would you like to select a Shape file or a GDB database ?'), _('Choose data source'), ['Shape file/GPKG', 'GDB database'], wx.CHOICEDLG_STYLE)
                ret = dlg.ShowModal()

                if ret == wx.ID_CANCEL:
                    dlg.Destroy()

                choice = dlg.GetStringSelection()
                dlg.Destroy()

                if choice == 'Shape file/GPKG':
                    with wx.FileDialog(None, _('Select a file'), wildcard="Shapefile (*.shp)|*.shp|Gpkg (*.gpkg)|*.gpkg", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                        if fileDialog.ShowModal() == wx.ID_CANCEL:
                            return

                        pathname = fileDialog.GetPath()

                        try:
                            self.data_dir = Path(pathname).parent
                            data_dir = self.data_dir
                            self._filename_vector = Path(pathname).name
                            self.zones = Zones(pathname, bbox = bbox, mapviewer=self.mapviewer, parent=self, colors=self._colors)
                        except:
                            logging.error(_('File not found : {}').format(pathname))

                elif choice == 'GDB database':
                    with wx.DirDialog(None, _("Choose a directory"), style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:
                        if dirDialog.ShowModal() == wx.ID_CANCEL:
                            return

                        pathname = dirDialog.GetPath()

                        try:
                            self.data_dir = Path(pathname).parent
                            data_dir = self.data_dir
                            self._filename_vector = ''
                            self.zones = Zones(pathname, bbox = bbox, mapviewer=self.mapviewer, parent=self, colors= self._colors)

                        except:
                            logging.error(_('Dirrectory not a gdb : {}').format(pathname))

        if self._filename_points != '':
            pointfile = data_dir / self._filename_points

            if pointfile.exists():
                self.cloud = cloud_vertices(data_dir / self._filename_points, bbox = bbox, mapviewer=self.mapviewer)
                self.cloud.myprop.width = 3
                self.cloud.myprop.color = getIfromRGB([0, 0, 255])
            else:
                logging.error(_('Point file not found : {}').format(pointfile))


    def plot(self, sx=None, sy=None, xmin=None, ymin=None, xmax=None, ymax=None, size=None):
        """ Plot data in OpenGL context

        :param sx: x scaling factor
        :param sy: y scaling factor
        :param xmin: minimum x value
        :param ymin: minimum y value
        :param xmax: maximum x value
        :param ymax: maximum y value
        :param size: size of the points
        """

        if self.zones is not None:
            self.zones.plot(sx=sx, sy=sy, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, size=size)
        if self.cloud is not None:
            self.cloud.plot(sx=sx, sy=sy, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, size=size)

    def check_plot(self):
        """ Generic function responding to check operation from mapviewer """

        super().check_plot()

        from .PyDraw import WolfMapViewer
        self.mapviewer:WolfMapViewer

        if self.mapviewer is not None:

            xmin, xmax, ymin, ymax = self.mapviewer.xmin, self.mapviewer.xmax, self.mapviewer.ymin, self.mapviewer.ymax

            bbox = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])
            self.read_data(bbox = bbox)

            self.mapviewer.Refresh()

    def uncheck_plot(self, unload: bool = True):
        """ Generic function responding to uncheck operation from mapviewer """

        super().uncheck_plot(unload = unload)

        if unload:
            self.zones = None
            self.cloud = None

    def show_properties(self):
        """ Showing properties of the object """

        if self.zones is not None:
            self.zones.show_properties()
        else:
            logging.warning(_('No zones properties to show !'))

        if self.cloud is not None:
            self.cloud.show_properties()
        else:
            logging.warning(_('No cloud properties to show !'))

    def Active_vector(self, vector_to_activate:vector):
        """ Activate a vector """

        self.active_vector = vector_to_activate
        self.active_zone = vector_to_activate.parentzone

        if self.mapviewer is not None:
            self.mapviewer.Active_vector(vector_to_activate)

        else:
            logging.warning(_('No mapviewer to activate vector !'))

    def Active_zone(self, zone_to_activate:zone):
        """ Activate a zone """

        self.active_zone = zone_to_activate

        if len(zone_to_activate.myvectors) > 0:
            self.active_vector = zone_to_activate.myvectors[0]

        if self.mapviewer is not None:
            self.mapviewer.Active_vector(self.active_vector)

        else:
            logging.warning(_('No mapviewer to activate zone !'))

class Cadaster_data(Picc_data):
    """ Read and show cadaster data """

    def __init__(self,
                 idx:str = '',
                 plotted:bool = True,
                 mapviewer = None,
                 need_for_wx:bool = False,
                 data_dir:Path = Path(r'./data/Cadastre'),
                 bbox:Union[Polygon, list[float]] = None) -> None:

        super().__init__(idx = idx, plotted = plotted, mapviewer = mapviewer, need_for_wx= need_for_wx, data_dir = data_dir, bbox = bbox)

        self._filename_vector = 'Cadastre.shp'
        self._filename_points = ''

    def read_data(self, data_dir: Path = None, bbox:Union[Polygon, List[float]] = None, colorize: bool = True) -> None:

        super().read_data(data_dir, bbox, colorize=False)
        if self.zones is not None:
            self.zones.set_width(3)
