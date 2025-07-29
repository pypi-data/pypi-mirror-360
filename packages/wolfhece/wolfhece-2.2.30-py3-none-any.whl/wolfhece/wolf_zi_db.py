"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

import geopandas as gpd
import pandas as pd
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import logging
from enum import Enum
from pathlib import Path
from typing import Literal, Union
import wx

from shapely.geometry import Polygon

from .PyVertexvectors import Zones, zone, vector, wolfvertex
from .wolf_texture import genericImagetexture
from .PyTranslate import _

class ColNames_PlansTerriers(Enum):
    """ Enum for the column names in the database """

    KEY   = 'Clé primaire'
    ORIGX = 'Origine x'
    ORIGY = 'Origine y'
    ENDX  = 'Xsup'
    ENDY  = 'Ysup'
    WIDTH = 'Largeur'
    HEIGHT= 'Hauteur'
    FULLRES = 'Acces'
    LOWRES  = 'Acces2'
    RIVER   = 'River'

class ZI_Databse_Elt():
    """ Class to store the database elements """

    def __init__(self,
                 origx:float,
                 origy:float,
                 endx:float,
                 endy:float,
                 width:float,
                 height:float,
                 fullpath:Path,
                 lowpath:Path) -> None:

        """ Constructor for the class

        :param origx: The x coordinate of the origin (Lower-left corner)
        :type origx: float
        :param origy: The y coordinate of the origin (Lower-left corner)
        :type origy: float
        :param endx: The x coordinate of the end (Upper-right corner)
        :type endx: float
        :param endy: The y coordinate of the end (Upper-right corner)
        :type endy: float
        :param width: The width of the image [m]
        :type width: float
        :param height: The height of the image [m]
        :type height: float
        :param fullpath: The full path to the full resolution image
        :type fullpath: Path
        :param lowpath: The full path to the low resolution image
        :type lowpath: Path
        """

        self.origx = origx
        self.origy = origy
        self.endx = endx
        self.endy = endy
        self.width = width
        self.height = height
        self.fullpath = fullpath
        self.lowpath = lowpath

class PlansTerrier(Zones):
    """
    Class to handle the "Plans Terriers" -- Black and white scanned tif files from SPW.

    Override the Zones class to handle the 'plans terriers' contours. In the "myzones" list, the object will store the contours for each river.

    Elements will be stored in the self.maps dictionary, with the key being the name of the river and the name of the file.

    The textures (images) will be stored in the self.textures dictionary, with the key being the ZI_Databse_Elt object.

    In the mapviewer, the user can choose the rivers to display, and the images will be loaded/unloaded on the fly when the user clicks on the map.

    During import of the images, the system will apply transparency based on a color and a tolerance, and,
    if necessary, will replace the other colors with another one (self.color). If self.color is None, no replacement will be done.

    :param parent: The wx parent of the object
    :type parent: wx.Window
    :param idx: The index of the object
    :type idx: str
    :param plotted: If the object is plotted
    :type plotted: bool
    :param mapviewer: The mapviewer object
    :type mapviewer: MapViewer
    :param rivers: The list of rivers to display
    :type rivers: list[str]

    """

    def __init__(self,
                 parent=None,
                 idx: str = '',
                 plotted: bool = True,
                 mapviewer=None,
                 rivers:list[str] = ['Vesdre', 'Hoegne']) -> None:

        super().__init__('', 0., 0., 0., 0., parent, True, idx, plotted, mapviewer, True, None, False)

        self.maps:dict[str, ZI_Databse_Elt] = {}
        self.textures:dict[ZI_Databse_Elt, genericImagetexture] = {}

        self.color = np.asarray([0,0,0,255])
        self.tolerance = 0
        self.transparent_color = [255, 255, 255]

        self.rivers = rivers

        self.initialized = False

        self.wx_exists = wx.GetApp() is not None

    def set_tolerance(self, tol:int):
        """
        Set the tolerance for the transparency

        Color will be considered transparent if the difference between the color and the transparent color is less than the tolerance.

        """

        self.tolerance = tol

    def set_transparent_color(self, color:list[int, int, int]):
        """
        Set the transparent color.

        Color is a list of 3 integers, representing the RGB color (0 -> 255).

        """

        self.transparent_color = color

    def set_color(self, color:tuple[int, int, int]):
        """
        Set the color of the image.

        As the provided images are black and white, the color will be used to replace the black color.

        If the images are not black and white, the color will be used to replace all non-transparent colors.

        """

        self.color = np.asarray(color)

    def check_plot(self):
        """ Activate the plot if the object is initialized """

        if not self.initialized:
            self.read_db(self.filename)

        if self.initialized:
            super().check_plot()

    def _create_zones(self):

        """
        Create the zones for the selected rivers.

        Each river will be a zone, and the vectors will be the contours of the images.

        """

        for curriver in self.rivers:
            curzone = zone(name=curriver, parent=self)
            self.add_zone(curzone)

    def read_db(self, filename:Union[str,Path], sel_rivers: list[str] = None):
        """ Read the database (Excel file) and create the zones and the vectors.

        The user will be prompted to select the rivers to display.

        """

        self.filename = Path(filename)

        if not self.filename.exists() or filename == '':

            if self.wx_exists:

                dlg= wx.FileDialog(None, _("Choose a file"), defaultDir= "", wildcard="Excel (*.xlsx)|*.xlsx", style = wx.FD_OPEN)
                ret = dlg.ShowModal()
                if ret == wx.ID_OK:
                    self.filename = Path(dlg.GetPath())
                    dlg.Destroy()
                else:
                    logging.error('No file selected')
                    dlg.Destroy()
                    return

            else:
                logging.error('No file selected or the file does not exist.')
                return

        self.db = pd.read_excel(self.filename, sheet_name='Plans_Terriers')

        rivers = list(self.db[ColNames_PlansTerriers.RIVER.value].unique())
        rivers.sort()

        self.rivers = []

        if sel_rivers is None and self.wx_exists:

            with wx.MessageDialog(None, _("Choose the rivers to display"), _("Rivers"), wx.YES_NO | wx.ICON_QUESTION) as dlg:

                if dlg.ShowModal() == wx.ID_YES:

                    with wx.MultiChoiceDialog(None, _("Choose the rivers to display"), _("Rivers"), rivers) as dlg_river:
                        ret = dlg_river.ShowModal()

                        if ret == wx.ID_OK:
                            for curidx in dlg_river.GetSelections():
                                self.rivers.append(rivers[curidx])
                else:
                    self.rivers = rivers

        elif sel_rivers is not None:

            for curruver in sel_rivers:
                if curruver in rivers:
                    self.rivers.append(curruver)
                else:
                    logging.error(f'River {curruver} not found in the database -- Ignoring !')

        self._create_zones()
        self._filter_db()

        self.initialized = True

    def _filter_db(self):

        for curline in self.db.iterrows():

            fullpath:str
            lowpath:str
            fullpath = curline[1][ColNames_PlansTerriers.FULLRES.value]
            lowpath = curline[1][ColNames_PlansTerriers.LOWRES.value]

            for curriver in self.rivers:
                curzone = self.get_zone(curriver)

                if curriver in fullpath:

                    fullpath = fullpath.replace(r'\\192.168.2.185\Intranet\Data\Données Topographiques\Plans Terriers\Full resu',
                                                str(self.filename.parent) +r'\Plans_Terriers\Fullresu')
                    lowpath = lowpath.replace(r'\\192.168.2.185\Intranet\Data\Données Topographiques\Plans Terriers\Low resu',
                                                str(self.filename.parent) + r'\Plans_Terriers\Lowresu')
                    fullpath = Path(fullpath)
                    lowpath = Path(lowpath)

                    if fullpath.exists() and lowpath.exists():

                        curelt = ZI_Databse_Elt(curline[1][ColNames_PlansTerriers.ORIGX.value],
                                                curline[1][ColNames_PlansTerriers.ORIGY.value],
                                                curline[1][ColNames_PlansTerriers.ENDX.value],
                                                curline[1][ColNames_PlansTerriers.ENDY.value],
                                                curline[1][ColNames_PlansTerriers.WIDTH.value],
                                                curline[1][ColNames_PlansTerriers.HEIGHT.value],
                                                fullpath,
                                                lowpath)

                        self.maps[curriver + fullpath.name] = curelt

                        curvector = vector(parentzone=curzone, name=fullpath.name)
                        curzone.add_vector(curvector)

                        curvector.add_vertex(wolfvertex(x=curelt.origx, y=curelt.origy))
                        curvector.add_vertex(wolfvertex(x=curelt.endx, y=curelt.origy))
                        curvector.add_vertex(wolfvertex(x=curelt.endx, y=curelt.endy))
                        curvector.add_vertex(wolfvertex(x=curelt.origx, y=curelt.endy))
                        curvector.close_force()
                    else:
                        logging.error(f'File {fullpath} does not exist')

                    break

        self.find_minmax(True)


    def _find_map(self, x:float, y:float):

        for curzone in self.myzones:
            for curvector in curzone.myvectors:
                if curvector.isinside(x, y):
                    return self.maps[curzone.myname+curvector.myname]

        return None

    def load_texture(self, x:float, y:float, which:Literal['full', 'low'] = 'low'):

        curmap = self._find_map(x, y)

        if curmap is not None:
            if curmap not in self.textures:

                if which == 'full':
                    curpath= curmap.fullpath
                else:
                    curpath = curmap.lowpath

                self.textures[curmap] = genericImagetexture(which = which,
                                                            label=curmap.fullpath,
                                                            mapviewer=self.mapviewer,
                                                            xmin=curmap.origx,
                                                            ymin=curmap.origy,
                                                            xmax=curmap.endx,
                                                            ymax=curmap.endy,
                                                            imageFile=curpath,
                                                            transparent_color=self.transparent_color,
                                                            tolerance=self.tolerance,
                                                            replace_color=self.color
                                                            )

            else:
                self.unload_textture(x, y)

            # return self.textures[curmap]
        else:
            return None

    def unload_textture(self, x:float, y:float):
        curmap = self._find_map(x, y)
        if curmap is not None:
            if curmap in self.textures:
                self.textures[curmap].unload()
                del self.textures[curmap]

    def plot(self, sx=None, sy=None, xmin=None, ymin=None, xmax=None, ymax=None, size=None):
        super().plot(sx, sy, xmin, ymin, xmax, ymax, size)

        for curtexture in self.textures.values():
            curtexture.plot(sx, sy, xmin, ymin, xmax, ymax, size)