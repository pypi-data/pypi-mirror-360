"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

from osgeo import ogr, gdal
import geopandas as gpd
from os.path import exists, join, dirname, basename
from os import getcwd, chdir
from typing import Union, Literal
import numpy as np
from pathlib import Path
import logging

import wx
import wx.grid

from .PyTranslate import _
from .PyPalette import wolfpalette

WALOUS_MAJ_NIV1 = {'Production primaire': 1.,
                   'Production secondaire': 2.,
                   'Production tertiaire': 3.,
                   'Réseaux de transport, Logistique et réseaux d\'utilité publique': 4.,
                   'Usage résidentiel': 5.,
                   'Autres usages': 6.,
                   'Zones naturelles': 7.}

WALOUS_MAJ_NIV2 = {'Agriculture': 11.,
                   'Sylviculture': 12.,
                   'Industries Extractives': 13.,
                   'Aquaculture et pêche':14,
                   'Production secondaire non définie': 20.,
                   'Industrie de matières premières': 21.,
                   'Industrie lourde': 22.,
                   'Industrie légère': 23.,
                   'Production d\'énergie': 24.,
                   'Service commerciaux': 31.,
                   'Services financiers, spécialisés et d\'information': 32.,
                   'Services publics': 33.,
                   'Services culturels, Services de loisirs et Services récréatifs': 34.,
                   'Réseaux de transport': 41.,
                   'Services Logistiques et d\'entreposage': 42.,
                   'Réseau d\'utilité publique': 43.,
                   'Usage résidentiel permanent': 51.,
                   'Usage résidentiel avec d\'autres usages compatibles': 52.,
                   'Autres usages résidentiels': 53.,
                   'Zones abandonnées': 62.,
                   'Usage inconnu': 66.,
                   'Zones naturelles': 70.}

WALOUS_COLORMAP_MAJ_NIV1 = {1.: (181,230,90,255),
                            2.: (99,99,99,255),
                            3.: (159,187,215,255),
                            4.: (181,121,241,255),
                            5.: (241,121,99,255),
                            6.: (221,221,221,255),
                            7.: (255,255,190,255)}

WALOUS_COLORMAP_MAJ_NIV2 = {11.: (153,230,0,255),
                            12.: (55,168,0,255),
                            13.: (142,181,180,255),
                            14.: (172,250,192,255),
                            20.: (179,179,179,255),
                            21.: (0,0,0,255),
                            22.: (157,157,157,255),
                            23.: (225,225,225,255),
                            24.: (79,79,79,255),
                            31.: (0,133,168,255),
                            32.: (186,236,245,255),
                            33.: (71,214,242,255),
                            34.: (102,154,171,255),
                            41.: (169,0,230,255),
                            42.: (213,196,245,255),
                            43.: (180,135,247,255),
                            51.: (255,0,0,255),
                            52.: (168,0,0,255),
                            53.: (255,127,127,255),
                            62.: (136,69,69,255),
                            66.: (206,136,102,255),
                            70.: (255,255,190,255)}

def get_palette_walous(which:Literal['MAJ_NIV1', 'MAJ_NIV2']) -> wolfpalette:
    """
    Get the palette for WALOUS

    :return : palette
    """

    locpal = wolfpalette()
    locpal.interval_cst = True
    locpal.automatic = False

    if which == 'MAJ_NIV1':
        locpal.set_values_colors(values = list(WALOUS_MAJ_NIV1.values()),
                                 colors = list(WALOUS_COLORMAP_MAJ_NIV1.values()))
    elif which == 'MAJ_NIV2':
        locpal.set_values_colors(values = list(WALOUS_MAJ_NIV2.values()),
                                 colors = list(WALOUS_COLORMAP_MAJ_NIV2.values()))
    else:
        logging.error('Unknown WALOUS level')

    return locpal

def update_palette_walous(which:Literal['MAJ_NIV1', 'MAJ_NIV2'], pal:wolfpalette):
    """
    Update the palette for WALOUS MAJ_NIV1

    :param pal : palette to update
    :return : updated palette
    """

    if which == 'MAJ_NIV1':
        for k, v in WALOUS_COLORMAP_MAJ_NIV1.items():
            pal.set_values_colors(values = list(WALOUS_MAJ_NIV1.values()),
                                 colors = list(WALOUS_COLORMAP_MAJ_NIV1.values()))
    elif which == 'MAJ_NIV2':
        for k, v in WALOUS_COLORMAP_MAJ_NIV2.items():
            pal.set_values_colors(values = list(WALOUS_MAJ_NIV2.values()),
                                 colors = list(WALOUS_COLORMAP_MAJ_NIV2.values()))

    pal.interval_cst = True
    pal.automatic = False

    return 0


WALOUS2MANNING_MAJ_NIV1 = {1.: 0.04, # Production primaire
                           2.: 0.02, # Production secondaire
                           3.: 0.02, # Production tertiaire
                           4.: 0.03, # Réseaux de transport, Logistique et réseaux d'utilité publique
                           5.: 0.025,# Usage résidentiel
                           6.: 0.04, # Autres usages
                           7.: 0.05} # Zones naturelles

WALOUS2MANNING_MAJ_NIV2 = {11.: 0.04, # Agriculture
                           12.: 0.04, # Sylviculture
                           13.: 0.04, # Industries Extractives
                           14.: 0.04, # Aquaculture et pêche
                           20.: 0.03, # Production secondaire non définie
                           21.: 0.03, # Industrie de matières premières
                           22.: 0.03, # Industrie lourde
                           23.: 0.03, # Industrie légère
                           24.: 0.03, # Production d'énergie
                           31.: 0.02, # Service commerciaux
                           32.: 0.02, # Services financiers, spécialisés et d'information
                           33.: 0.02, # Services publics
                           34.: 0.02, # Services culturels, Services de loisirs et Services récréatifs
                           41.: 0.025, # Réseaux de transport
                           42.: 0.02, # Services Logistiques et d'entreposage
                           43.: 0.025, # Réseau d'utilité publique
                           51.: 0.025, # Usage résidentiel permanent
                           52.: 0.025, # Usage résidentiel avec d'autres usages compatibles
                           53.: 0.025, # Autres usages résidentiels
                           62.: 0.04, # Zones abandonnées
                           66.: 0.04, # Usage inconnu
                           70.: 0.05} # Zones naturelles

class Walous_data():
    """
    La donnée Walous est liée à l'utilisation des sols en Wallonie

    source : https://geoportail.wallonie.be/walous

    Cette classe permet la manipulation de la donnée dans le cadre du projet MODREC
    et plus spécifiquement la distribution d'un coefficient de frottement sur base
    de la donnée Walous.

    """

    def __init__(self,
                 dir_data:str = '',
                 fn:str = 'WAL_UTS__2018_L72',
                 bounds:Union[list[float, float, float, float],list[list[float, float], list[float, float]]] = None) -> None:
        """
        Constructor

        :param dir_data : directory of the data
        :param fn : filename without extension (shp)
        :param bounds : Two ways to set spatial bounds -- [xmin, ymin, xmax, ymax] or [[xmin, xmax], [ymin, ymax]]

        """

        self._dir = dir_data    # directory of the data
        self._fn  = fn          # filename without extension
        self._gdf = None        # geopandas dataframe

        if bounds is not None:
            # Bounds are set -> read file
            self.read(True, bounds=bounds)

    def read(self,
             force:bool = False,
             bounds:Union[list[float, float, float, float],list[list[float, float], list[float, float]]] = None):
        """
        Read data from file

        :param force : force to read even read was done before
        :param bounds : [xmin, ymin, xmax, ymax] or [[xmin, xmax], [ymin, ymax]]
        """

        if self._gdf is None or force:
            assert self._dir!="" and self._fn != ''

            filepath = (Path(self._dir)/ self._fn).with_suffix('.shp')

            if filepath.exists():
                if bounds is not None:
                    if len(bounds)==2:
                        # [[xmin, xmax], [ymin, ymax]]
                        xmin = bounds[0][0]
                        xmax = bounds[0][1]
                        ymin = bounds[1][0]
                        ymax = bounds[1][1]
                    else:
                        # [xmin, ymin, xmax, ymax]
                        xmin = bounds[0]
                        xmax = bounds[2]
                        ymin = bounds[1]
                        ymax = bounds[3]

                    # read part of the file
                    self._gdf = gpd.read_file(str(filepath), bbox=(xmin,ymin,xmax,ymax))
                else:
                    # read all
                    self._gdf = gpd.read_file(str(filepath))

                # self._gdf['MAJ_NIV2'] = np.asarray(self._gdf['MAJ_NIV2'], dtype=int)
                # self._gdf['MAJ_NIV3'] = np.asarray(self._gdf['MAJ_NIV3'], dtype=int) # ne fonctionne pas car le niveau 3 contient des lettres --> à généraliser
            else:
                self._gdf = None

    def write(self, fnout:str='out_clip.shp'):
        """
        Write _gdf to file

        :param fnout : output filename
        """

        try:
            curdir = getcwd()
            detsdir = dirname(fnout)

            chdir(detsdir)

            self._gdf.to_file(basename(fnout))

            chdir(curdir)
            return 0

        except:
            logging.error('Error in writing data - Walous module')
            return -1


    def to_file(self, fn:str='out_clip.shp'):
        """
        Alias to write

        :param fn : output filename
        """

        self.write(fn)

    def rasterize(self,
                  bounds:Union[list[float, float, float, float],list[list[float, float], list[float, float]]],
                  layer:Literal['MAJ_NIV1','MAJ_NIV2'] ='MAJ_NIV1',
                  fn_out:str = 'out.tif',
                  pixel_size:float = 0.5,
                  NoData_value:float = -99999.,
                  num_type = gdal.GDT_Float32
                  ):

        """
        Rasterization of polygon data to tif

        :param bounds : [xmin, ymin, xmax, ymax] or [[xmin, xmax], [ymin, ymax]]
        :param layer : layer to rasterize
        :param fn_out : output filename
        :param pixel_size : pixel size
        :param NoData_value : NoData value
        :param num_type : type of the number
        """

        if bounds is None:
            logging.error('Bounds must be set')
            return None
        else:
            if len(bounds)==4:
                # [[xmin, xmax], [ymin, ymax]]
                bounds = [[bounds[0], bounds[2]], [bounds[1], bounds[3]]]

        if self._gdf is None:
            logging.info('Reading data')
            self.read(bounds=bounds)
            logging.info('End of reading data')

        if self._gdf is None:
            logging.error('No data to rasterize')
            return None

        if layer not in self._gdf.keys():
            logging.error('Layer not found in the data')
            return None

        ret = self.write(str(fn_out) + '.shp')

        if ret !=0:
            logging.error('An error occured in writing the data to file')
            return -1

        try:

            # Add a new column for mapping based on the desired layer
            self._gdf['Mapping'] = np.float32(self._gdf[layer])

            if layer == 'MAJ_NIV2':
                self._gdf['Mapping'] = np.float32(self._gdf['Mapping'].replace('_', ''))

            source_ds:ogr.DataSource
            source_layer:ogr.Layer

            source_ds = ogr.Open(self._gdf.to_json())

            # source_srs:ogr.
            source_layer = source_ds.GetLayer()
            source_srs = source_layer.GetSpatialRef()

            # Create the destination data source
            x_res = int((bounds[0][1] - bounds[0][0]) / pixel_size)
            y_res = int((bounds[1][1] - bounds[1][0]) / pixel_size)

            driver:gdal.Driver
            driver = gdal.GetDriverByName('GTiff')
            target_ds = driver.Create(str(fn_out), x_res, y_res, 1, num_type)

            target_ds:gdal.Dataset
            band:gdal.Band
            target_ds.SetGeoTransform((bounds[0][0], pixel_size, 0, bounds[1][1], 0, -pixel_size))
            band = target_ds.GetRasterBand(1)
            band.SetNoDataValue(NoData_value)

            target_ds.SetProjection(source_srs.ExportToWkt())

            # Rasterize
            gdal.RasterizeLayer(target_ds,
                                [1], source_layer,
                                options = ["ALL_TOUCHED=TRUE", "ATTRIBUTE=Mapping"])

            target_ds = None

            return fn_out

        except:
            logging.error('Error in rasterization')
            return -2


class  DlgMapWalous(wx.Dialog):
    """ Modal dialog for mapping WALOUS value to another ones """

    def __init__(self, parent, title:str = _("Mapping WALOUS value to ..."), which:str = 'MAJ_NIV1'):

        super(DlgMapWalous, self).__init__(parent, title=title, size=(450, 400))

        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._table = wx.grid.Grid(panel)

        if which == 'MAJ_NIV1':
            self._table.CreateGrid(len(WALOUS_MAJ_NIV1), 3)
            self._table.SetColLabelValue(0, _("Name"))
            self._table.SetColLabelValue(1, _("Value"))
            self._table.SetColLabelValue(2, _("Manning 'n'"))
            self._table.HideRowLabels()

            for i, (k, v) in enumerate(WALOUS_MAJ_NIV1.items()):
                self._table.SetCellValue(i, 0, str(k))
                self._table.SetCellValue(i, 1, str(v))
                self._table.SetCellValue(i, 2, str(WALOUS2MANNING_MAJ_NIV1[v]))
                self._table.SetCellAlignment(i, 1, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                self._table.SetCellAlignment(i, 2, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        elif which == 'MAJ_NIV2':
            self._table.CreateGrid(len(WALOUS_MAJ_NIV2), 3)
            self._table.SetColLabelValue(0, _("Name"))
            self._table.SetColLabelValue(1, _("Value"))
            self._table.SetColLabelValue(2, _("Manning 'n'"))
            self._table.HideRowLabels()

            for i, (k, v) in enumerate(WALOUS_MAJ_NIV2.items()):
                self._table.SetCellValue(i, 0, str(k))
                self._table.SetCellValue(i, 1, str(v))
                self._table.SetCellValue(i, 2, str(WALOUS2MANNING_MAJ_NIV2[v]))
                self._table.SetCellAlignment(i, 1, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                self._table.SetCellAlignment(i, 2, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        self._table.SetColFormatFloat(1, 2, 0)
        self._table.SetColFormatFloat(2, 6, 4)
        self._table.SetColSize(0, 250)
        self._table.SetColSize(1, 50)
        self._table.SetColSize(2, 100)


        sizer.Add(self._table, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        sizer_btns = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, wx.ID_OK, _("OK"))
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, _("Cancel"))
        sizer_btns.Add(btn_ok, 0, wx.ALL, 5)
        sizer_btns.Add(btn_cancel, 0, wx.ALL, 5)

        sizer.Add(sizer_btns, 0, wx.ALIGN_CENTER)

        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)

        self.Center()

    def on_ok(self, event):
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def get_mapping(self) -> dict:

        retdict = {}

        try:
            for i in range(self._table.GetNumberRows()):
                retdict[float(self._table.GetCellValue(i, 1))] = float(self._table.GetCellValue(i, 2))
        except:
            retdict = -1
            logging.error('Error in getting mapping')

        return retdict


class WalousLegend(wx.Dialog):
    """ Show the legend of WALOUS """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw, size = (400, 650))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self._text_v1 = wx.StaticText(panel, label=_("WALOUS MAJ_NIV1"))
        self._text_v2 = wx.StaticText(panel, label=_("WALOUS MAJ_NIV2"))

        self._legend_v1 = wx.grid.Grid(panel)
        self._legend_v1.CreateGrid(len(WALOUS_MAJ_NIV1), 3)
        self._legend_v1.SetColSize(0, 200)
        self._legend_v1.SetColLabelValue(0, _("Name"))
        self._legend_v1.SetColLabelValue(1, _("Value"))
        self._legend_v1.SetColLabelValue(2, _("Color"))
        self._legend_v1.HideRowLabels()

        for i, (k, v) in enumerate(WALOUS_MAJ_NIV1.items()):
            self._legend_v1.SetCellValue(i, 0, str(k))
            self._legend_v1.SetCellValue(i, 1, str(v))
            self._legend_v1.SetCellBackgroundColour(i, 2, WALOUS_COLORMAP_MAJ_NIV1[v])

        self._legend_v2 = wx.grid.Grid(panel)
        self._legend_v2.CreateGrid(len(WALOUS_MAJ_NIV2), 3)
        self._legend_v2.SetColLabelValue(0, _("Name"))
        self._legend_v2.SetColSize(0, 200)
        self._legend_v2.SetColLabelValue(1, _("Value"))
        self._legend_v2.SetColLabelValue(2, _("Color"))
        self._legend_v2.HideRowLabels()

        for i, (k, v) in enumerate(WALOUS_MAJ_NIV2.items()):
            self._legend_v2.SetCellValue(i, 0, str(k))
            self._legend_v2.SetCellValue(i, 1, str(v))
            self._legend_v2.SetCellBackgroundColour(i, 2, WALOUS_COLORMAP_MAJ_NIV2[v])

        sizer.Add(self._text_v1, 0, wx.EXPAND, border=5)
        sizer.Add(self._legend_v1, 1, wx.EXPAND, border=5)
        sizer.Add(self._text_v2, 0, wx.EXPAND, border=5)
        sizer.Add(self._legend_v2, 1, wx.EXPAND, border=5)

        panel.SetSizer(sizer)
        self.Center()

        self.Show()

    def __del__(self):
        self.Destroy()

    def close(self):
        self.Destroy()
