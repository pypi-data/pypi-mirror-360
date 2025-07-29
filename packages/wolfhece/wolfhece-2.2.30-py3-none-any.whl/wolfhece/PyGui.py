"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""
try:
    from osgeo import gdal
except ImportError as e:
    print(f"Import Error: {e} - GDAL")
    print("Please install GDAL for your Python version.")

try:
    from os import scandir, getcwd, makedirs
    from os.path import exists, join, isdir, isfile, dirname, normpath, splitext
    from pathlib import Path
    import numpy.ma as ma
    import wx
    import logging
    from pathlib import Path
except ImportError as e:
    print(f"Import Error: {e} - extern modules")
    print("Please install the required modules using 'pip install -r requirements.txt'")

try:
    from .apps.splashscreen import WolfLauncher
except ImportError as e:
    print(f"Import Error: {e} - Splashscreen")
    print("Please install the required modules using 'pip install -r requirements.txt'")

try:
    from .wolf_array import WOLF_ARRAY_FULL_LOGICAL, WOLF_ARRAY_MB_SINGLE, WolfArray, getkeyblock, WOLF_ARRAY_FULL_INTEGER16, WOLF_ARRAY_MB_INTEGER
except ImportError as e:
    print(f"Import Error: {e} - WolfArray")
    print("Please install the required modules using 'pip install -r requirements.txt'")
try:
    from .PyTranslate import _
except ImportError as e:
    print(f"Import Error: {e} - PyTranslate")
    print("Please install the required modules using 'pip install -r requirements.txt'")
try:
    from .PyDraw import WolfMapViewer,imagetexture, draw_type
except ImportError as e:
    print(f"Import Error: {e} - PyDraw")
    print("Please install the required modules using 'pip install -r requirements.txt'")

try:
    from .hydrometry.kiwis_wolfgui import hydrometry_wolfgui
except ImportError as e:
    print(f"Import Error: {e} - hydrometry_wolfgui")
    print("Please install the required modules using 'pip install -r requirements.txt'")

try:
    from .PyConfig import WolfConfiguration, ConfigurationKeys
    from .pylogging import create_wxlogwindow
except ImportError as e:
    print(f"Import Error: {e} - PyConfig, pylogging")
    print("Please install the required modules using 'pip install -r requirements.txt'")

try:
    from .RatingCurve import SPWMIGaugingStations,SPWDCENNGaugingStations
    from .mesh2d.wolf2dprev import *
    # from .Results2DGPU import wolfres2DGPU
    from .PyGuiHydrology import GuiHydrology
    from .RatingCurve import SPWMIGaugingStations,SPWDCENNGaugingStations
    from .hydrology.Catchment import Catchment
    from .hydrology.forcedexchanges import forced_exchanges
    from .PyParams import Wolf_Param
    from .picc import Picc_data, Cadaster_data
    from .wolf_zi_db import ZI_Databse_Elt, PlansTerrier
    from .CpGrid import CpGrid
    from .mesh2d.gpu_2d import Sim_2D_GPU
    from .mesh2d.wolf2dprev import prev_sim2D
    from .mesh2d.cst_2D_boundary_conditions import BCType_2D, BCType_2D_OO, BCType_2D_GPU, Direction

except ImportError as e:
    print(f"Import Error: {e} - RatingCurve, mesh2d, Results2DGPU, PyGuiHydrology, RatingCurve, hydrology, PyParams, picc, wolf_zi_db, CpGrid")
    print("Please install the required modules using 'pip install -r requirements.txt'")


GEOM_GROUP_NAME = _('Block geometry')
MAGN_GROUP_NAME = _('Magnetic grid')

class GenMapManager(wx.Frame):
    """
    Default class for a Wolf Map Manager.

    Will be overriden by the specific classes MapManager, GPU2DModel, HydrologyModel, Wolf2DModel.

    It is not suitable for direct use.

    """

    def __init__(self, *args, **kw):
        # `args` and `kwargs` represent parameters
        # that have to be passed to `wx.Frame.__init__`

        self.mapviewer:WolfMapViewer = None
        self.wx_exists:bool = wx.App.Get() is not None # test if wx App is running
        self.mylogs=None

        if self.wx_exists:

            super().__init__(parent = None)

            if len(args) == 0:
                # FIXME This is hackish. the parent parameter should be passed explicitely.
                # I do it this way to not have to recheck the whole project

                # We're missing the parent parameter of wx.Frame.__init__
                # So we put a default.
                # (it appears that wx.Frame.__init__ will accept a call
                # without parent silently, leadings to issue in child
                # frames).
                # See https://gitlab.uliege.be/HECE/HECEPythaaon/-/issues/36
                args = (None,)

            self._configuration = WolfConfiguration()
            SPLASH_PARAM="splash"
            if kw.get(SPLASH_PARAM,True):
                # Make it a instance's variable so that
                # the garbage collector don't remove it
                # before us (WolfLauncher has no parent
                # so it dangles).
                self._MySplash = WolfLauncher(play_sound=self._configuration[ConfigurationKeys.PLAY_WELCOME_SOUND])
                # Don't pollute the call to wf.Frame.__init__
                kw.pop(SPLASH_PARAM, None)

            # super().__init__(*args)
            self.mylogs = create_wxlogwindow(_('Informations'))

    def setup_mapviewer(self, title:str, wolfparent):
        """ Setup of a WolfMapViewer """

        self.mapviewer = WolfMapViewer(None,
                                       title=title,
                                       wolfparent= wolfparent,
                                       wxlogging=self.mylogs)
        self.mapviewer.add_grid()
        self.mapviewer.add_WMS()

    def get_mapviewer(self) -> WolfMapViewer:
        """ Retourne une instance WolfMapViewer """

        return self.mapviewer

    def get_configuration(self) -> WolfConfiguration:
        """ Retourne la configuration de Wolf """

        return self._configuration

class MapManager(GenMapManager):

    def __init__(self,*args, **kw):

        logging.info("MapManager")
        super().__init__(*args, **kw)

        icon = wx.Icon()

        icon_path = Path(__file__).parent / "apps/wolf_logo2.bmp"

        icon.CopyFromBitmap(wx.Bitmap(str(icon_path), wx.BITMAP_TYPE_ANY))

        self.setup_mapviewer(title = 'Wolf - main data manager', wolfparent=self)

        try:
            self.mapviewer.mytooltip.SetIcon(icon)
        except:
            logging.error("No icon for the tooltip window")

        try:
            self.mapviewer.SetIcon(icon)
        except:
            logging.error("No icon for the mapviewer window")

        if self.wx_exists:
            try:
                self.mylogs.GetFrame().SetIcon(icon)
            except:
                logging.error("No icon for the log window")

        logging.info("MapManager - MapViewer created")
        # Set directory for hydrometry data, relative to the current file
        dir_data = Path(__file__).parent / "data"
        dir_hydro = dir_data / "hydrometry"
        if not dir_hydro.exists():
            dir_hydro.mkdir(parents=True, exist_ok=True)

        dir_cadaster = dir_data / "Cadaster"
        if not dir_cadaster.exists():
            dir_cadaster.mkdir(parents=True, exist_ok=True)

        dir_picc = dir_data / "PICC"
        if not dir_picc.exists():
            dir_picc.mkdir(parents=True, exist_ok=True)

        logging.info("MapManager - Data directories created")
        try:
            self.SPWhydrometry = hydrometry_wolfgui(dir=dir_hydro, idx = 'SPW hydrometry', mapviewer=self.mapviewer, parent = self, plotted=False)
            logging.info("MapManager - hydrometry_wolfgui created")
            self.picc          = Picc_data(data_dir=dir_picc, mapviewer=self.mapviewer)
            logging.info("MapManager - Picc_data created")
            self.cadaster      = Cadaster_data(data_dir=dir_cadaster, mapviewer=self.mapviewer)
            logging.info("MapManager - Cadaster_data created")
            self.landmaps      = PlansTerrier(mapviewer=self.mapviewer, parent = self, idx='LandMaps', plotted=True)
            logging.info("MapManager - PlansTerrier created")

            self.mapviewer.add_object(which='other',
                                    newobj=self.SPWhydrometry,
                                    ToCheck=False,
                                    id='SPW hydrometry')

            self.mapviewer.add_object(which='other',
                                    newobj=self.picc,
                                    ToCheck=False,
                                    id='PICC data')

            self.mapviewer.add_object(which='other',
                                    newobj=self.cadaster,
                                    ToCheck=False,
                                    id='Cadaster data')

            self.mapviewer.add_object(which='other',
                                    newobj=self.landmaps,
                                    ToCheck=False,
                                    id='Land maps')
        except:
            logging.warning("Can't load some data (hydrometry, picc, cadaster, landmaps) -- Please check the data directories and/or report the issue")

        self.mapviewer.menu_walous()
        logging.info("MapManager - Menu Walous created")

# class GPU2DModel(GenMapManager):

#     mydir:str
#     files_results_array:dict
#     mybed:WolfArray

#     def __init__(self,dir:str='', *args, **kw):
#         super(GPU2DModel, self).__init__(*args, **kw)

#         self.setup_mapviewer(title='Wolf GPU 2D')

#         if dir=='':
#             idir=wx.DirDialog(None,"Choose Directory")
#             if idir.ShowModal() == wx.ID_CANCEL:
#                 return
#             self.mydir =idir.GetPath()
#         else:
#             self.mydir=normpath(dir)

#         ext=['.top','.frott','.cls_pos','.cls_Z','.hbin','.zbin','.srcq']
#         for myext in ext:
#             if exists(self.mydir+'//simul'+myext):

#                 self.mapviewer.add_object(which='array',
#                                           filename=self.mydir+'//simul'+myext,
#                                           id=myext,
#                                           ToCheck=False)

#         self.mybed=WolfArray(self.mydir +'//simul.top')
#         self.result = wolfres2DGPU(self.mydir,self.mybed,parent=self)

#         self.mapviewer.add_object(which='array',
#                                   newobj=self.result,
#                                   id='res1',
#                                   ToCheck=False)

#         self.mapviewer.findminmax(True)
#         self.mapviewer.Autoscale(False)

class HydrologyModel(GenMapManager):

    mydir:str
    mydircharact:str
    mydirwhole:str
    files_hydrology_array:dict
    files_hydrology_vectors:dict
    mainparams:Wolf_Param
    basinparams:Wolf_Param
    SPWstations:SPWMIGaugingStations
    DCENNstations:SPWDCENNGaugingStations
    mycatchment:Catchment
    myexchanges:forced_exchanges

    def __init__(self,dir:str='', splash=True, *args, **kw):

        self.wx_exists = wx.App.Get() is not None # test if wx App is running

        self.SPWstations=SPWMIGaugingStations()
        self.DCENNstations=SPWDCENNGaugingStations()

        if dir=='':
            idir=wx.DirDialog(None,"Choose Directory")
            if idir.ShowModal() == wx.ID_CANCEL:
                return
            self.mydir =idir.GetPath()
        else:
            self.mydir=normpath(dir)

        if self.wx_exists:
            super(HydrologyModel, self).__init__(splash=splash, *args, **kw)
        else:
            if "splash" in kw and kw["splash"]:
                raise Exception("You can't have the splash screen outside a GUI")

        self.mydircharact=join(self.mydir,'Characteristic_maps\\Drainage_basin')
        self.mydirwhole=join(self.mydir,'Whole_basin\\')

        self.mycatchment = Catchment('Mysim',self.mydir,False,True)
        self.myexchanges = forced_exchanges(self.mydir)

        if self.wx_exists:
            self.mapviewer=GuiHydrology(title='Model : '+self.mydir, wolfparent=self, wxlogging=self.mylogs)
            # self.setup_mapviewer(title='Wolf - Hydrology model', wolfparent=self)


            self.files_hydrology_array={'Characteristic_maps':[
                ('.b','Raw elevation [m]'),
                ('corr.b','Corrected elevation [m]'),
                #('diff.b','Corrections (corr-raw) [m]'),
                ('.nap','Mask [-]'),
                ('.sub','SubBasin index [-]'),
                ('.cnv','Accumulation [km²]'),
                ('.time','Total time [s]'),
                ('.coeff','RunOff coeff [-]'),
                ('.slope','Slope [-]'),
                ('.reachs','Reach index [-]'),
                ('.strahler','Strahler index [-]'),
                ('.reachlevel','Reach accumulation [-]'),
                ('.landuse1','Woodlands [m²]'),
                ('.landuse2','Pastures [m²]'),
                ('.landuse3','Cultivated [m²]'),
                ('.landuse4','Pavements [m²]'),
                ('.landuse5','Water [m²]'),
                ('.landuse6','River [m²]'),
                ('.landuse_limited_area','LandUse Verif'),
                ('.principal_landuse_cropped','Principal landuse [-]'),
                ('_encode.sub','Coded index SubB [-]')]}


            self.files_hydrology_vectors={'Characteristic_vectors':[('.delimit.vec','Watershed')],
                                        'Whole_basin':[('Rain_basin_geom.vec','Rain geom'),
                                                        ('Evap_basin_geom.vec','Evapotranspiration geom')]}

            for curfile in self.files_hydrology_array['Characteristic_maps']:
                curext=curfile[0]
                curidx=curfile[1]
                self.mapviewer.add_object(which='array',filename=self.mydircharact+curext,id=curidx,ToCheck=False)


            for curfile in self.files_hydrology_vectors['Characteristic_vectors']:
                curext=curfile[0]
                curidx=curfile[1]

                delimit = Zones(filename=self.mydircharact+curext, mapviewer=self.mapviewer, parent = self.mapviewer)

                for idx, cur_zone in enumerate(delimit.myzones):
                    cur_sub = self.mycatchment.get_subBasin(idx+1)
                    cur_zone.myname = cur_sub.name
                    cur_vect = cur_zone.myvectors[0]
                    cur_vect.set_legend_to_centroid(cur_sub.name + ' - ' + str(cur_sub.iDSorted), visible=True)
                    cur_vect.myprop.legendfontsize = 12

                delimit.reset_listogl()

                self.mapviewer.add_object(which='vector',newobj = delimit, id=curidx, ToCheck=True)

            for curfile in self.files_hydrology_vectors['Whole_basin']:
                curext=curfile[0]
                curidx=curfile[1]
                if exists(self.mydirwhole+curext):
                    self.mapviewer.add_object(which='vector',filename=self.mydirwhole+curext,id=curidx,ToCheck=False)

            self.mapviewer.add_object(which='vector',newobj=self.myexchanges.mysegs,id='Forced exchanges',ToCheck=False)

            zones_RT = self.mycatchment.get_retentionbasin_zones()
            zones_RT.parent = self
            self.mapviewer.add_object(which='vector',newobj=zones_RT,id='Anthropic links',ToCheck=False)

            self.mapviewer.add_object(which='cloud',newobj=self.mycatchment.subBasinCloud,id='Local outlets',ToCheck=False)
            self.mapviewer.add_object(which='cloud',newobj=self.mycatchment.retentionBasinCloud,id='Anthropic inlets/outlets',ToCheck=False)

            self.mycatchment.subBasinCloud.set_mapviewer(self.mapviewer)
            self.mycatchment.retentionBasinCloud.set_mapviewer(self.mapviewer)

            self.mapviewer.add_object(which='cloud',newobj=self.myexchanges.mycloudup,id='Up nodes',ToCheck=False)
            self.mapviewer.add_object(which='cloud',newobj=self.myexchanges.myclouddown,id='Down nodes',ToCheck=False)

            self.mapviewer.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
            self.mapviewer.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

            self.mapviewer.add_grid()
            self.mapviewer.add_WMS()

            self.mapviewer.findminmax(True)
            self.mapviewer.Autoscale(False)

            #Fichiers de paramètres
            self.mainparams=Wolf_Param(self.mapviewer,filename=self.mydir+'\\Main_model.param',title="Model parameters",DestroyAtClosing=False)
            self.basinparams=Wolf_Param(self.mapviewer,filename=self.mydircharact+'.param',title="Basin parameters",DestroyAtClosing=False)
            self.mainparams.Hide()
            self.basinparams.Hide()


class Wolf2DPartArrays():

    def __init__(self, sim:prev_sim2D, mapviewer:WolfMapViewer) -> None:

        self.wx_exists = wx.App.Get() is not None # test if wx App is running
        self.sim = sim
        self._gui = None
        self.mapviewer = mapviewer

        self._cur_list = None

        if self.wx_exists:
            self.setup_gui()

    def setup_gui(self):
        """
        Create the GUI

        A listbox in the upper part of the window will list the different part arrays.

        When a part array is selected, the listbox on the left will list the files
        associated with the selected part array. The listbox on the right will list
        the blocks associated with the selected file.

        """

        self._gui = wx.Frame(None, title="Part Arrays", size=(400, 600))

        self._panel = wx.Panel(self._gui)

        sizer_vert = wx.BoxSizer(wx.VERTICAL)
        sizer_hor = wx.BoxSizer(wx.HORIZONTAL)
        sizer_vert_left = wx.BoxSizer(wx.VERTICAL)
        sizer_vert_right = wx.BoxSizer(wx.VERTICAL)
        sizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        sizer_hor.Add(sizer_vert_left, 1, wx.EXPAND)
        sizer_hor.Add(sizer_vert_right, 1, wx.EXPAND)

        self._lists = wx.ListBox(self._panel,
                                 choices = [_("Topography"),
                                            _("Friction"),
                                            _("Water depth"),
                                            _("Discharge X"),
                                            _("Discharge Y"),
                                            _("Buildings"),
                                            _("Bridges"),
                                            _("Infiltration")],
                                 style= wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB)

        self._lists.Bind(wx.EVT_LISTBOX, self.on_list)

        sizer_vert.Add(self._lists, 0, wx.EXPAND)
        sizer_vert.Add(sizer_hor, 1, wx.EXPAND)

        self._list_files = wx.ListBox(self._panel,
                                        style=wx.LB_SINGLE,
                                        choices = [])

        self._list_files.Bind(wx.EVT_LISTBOX, self.on_list_files)

        self._list_blocks = wx.ListBox(self._panel,
                                        style=wx.LB_MULTIPLE,
                                        choices = [str(i+1) for i in range(self.sim.nb_blocks)])

        self._list_blocks.Bind(wx.EVT_LISTBOX, self.on_list_blocks)


        self_btn_addfile = wx.Button(self._panel, label=_("Add file"))
        self_btn_addfile.Bind(wx.EVT_BUTTON, self.on_addfile)
        self_btn_addfile.SetToolTip(_("Add a file to the selected part array"))

        self_btn_delfile = wx.Button(self._panel, label=_("Delete file"))
        self_btn_delfile.Bind(wx.EVT_BUTTON, self.on_delfile)
        self_btn_delfile.SetToolTip(_("Delete the selected file from the selected part array"))

        self._btn_apply = wx.Button(self._panel, label=_("Apply"))
        self._btn_apply.Bind(wx.EVT_BUTTON, self.on_apply)
        self._btn_apply.SetToolTip(_("Apply the values in the grid to the in-memory simulation (without writing to disk)"))

        self._btn_toviewer = wx.Button(self._panel, label=_("To viewer"))
        self._btn_toviewer.Bind(wx.EVT_BUTTON, self.on_toviewer)

        sizer_btns.Add(self_btn_addfile, 1, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self_btn_delfile, 1, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_apply, 2, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_toviewer, 2, wx.EXPAND | wx.ALL, 2)

        sizer_vert.Add(sizer_btns, 0, wx.EXPAND)

        sizer_vert_left.Add(self._list_files, 1, wx.EXPAND)
        sizer_vert_right.Add(self._list_blocks, 1, wx.EXPAND)


        self._panel.SetSizer(sizer_vert)
        self._panel.SetAutoLayout(1)


    def on_toviewer(self, event):
        """ Add the selected array to the mapviewer """

        if self.mapviewer is None:
            logging.error("No mapviewer created")
            return

        selected = self._list_files.GetSelection()

        if selected != wx.NOT_FOUND:

            fpath = Path(self.sim.filenamegen).parent / self._cur_list[selected][0]
            locarray = WolfArray(fpath)

            try:

                self.mapviewer.add_object(which='array',
                                          newobj=locarray,
                                          id=fpath.name,
                                          ToCheck=True)

                self.mapviewer.Refresh()

            except:
                logging.error(_(f"Can't add {fpath} to the mapviewer"))


    def on_list(self, event):
        """ When a part array is selected """

        selected = self._lists.GetSelection()

        if selected == 0:
            self._cur_list = self.sim.part_arrays._topography

        elif selected == 1:
            self._cur_list = self.sim.part_arrays._friction

        elif selected == 2:
            self._cur_list = self.sim.part_arrays._watedepth

        elif selected == 3:
            self._cur_list = self.sim.part_arrays._dischargeX

        elif selected == 4:
            self._cur_list = self.sim.part_arrays._dischargeY

        elif selected == 5:
            self._cur_list = self.sim.part_arrays._buildings

        elif selected == 6:
            self._cur_list = self.sim.part_arrays._bridges

        elif selected == 7:
            self._cur_list = self.sim.part_arrays._infiltration

        self._list_files.Set([cur[0] for cur in self._cur_list])

    def on_list_files(self, event):
        """ When a file is selected """

        selected = self._list_files.GetSelection()

        self._list_blocks.Set([str(i+1) for i in range(self.sim.nb_blocks)])

        for i in self._cur_list[selected][2]:
            self._list_blocks.SetSelection(i-1)

    def on_list_blocks(self, event):
        pass

    def on_addfile(self, event):
        """ Add a file to the selected part array """

        dlg = wx.FileDialog(self._gui, _("Choose a file"), "", "", "All files (*.bin)|*.bin", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:

            file = Path(dlg.GetPath())

            head = file / '.txt'

            if head.exists():
                locarray = WolfArray(file)

                relative = file.relative_to(self.sim.filenamegen)

                self._cur_list.append([relative, locarray.get_header(), [1]])
                self._list_files.Set([cur[0] for cur in self._cur_list])

    def on_delfile(self, event):
        """ Delete the selected file """

        selected = self._list_files.GetSelection()

        if selected != wx.NOT_FOUND:

            dlg = wx.MessageDialog(self._gui, _("Are you sure you want to delete this file ?"), _("Delete file"), wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                self._cur_list.pop(selected)
                self._list_files.Set([cur[0] for cur in self._cur_list])

            dlg.Destroy()

    def on_apply(self, event):

        selected = self._list_files.GetSelection()

        if selected != wx.NOT_FOUND:

            self._cur_list[selected][2] = [int(i) for i in self._list_blocks.GetSelections()]

    def Show(self):

        if self._gui is not None:
            self._gui.Show()
        else:
            logging.error("No GUI created")

class Wolf2DInfiltration():

    def __init__(self, sim:prev_sim2D = None):

        self.wx_exists = wx.App.Get() is not None # test if wx App is running
        self.sim = sim
        self._gui = None

        if self.wx_exists:
            self.setup_gui()

    @property
    def number_of_infiltration(self):

        return self.sim.infiltration.nb_zones

    def setup_gui(self):

        if not self.wx_exists:
            logging.error("You can't create a GUI outside a wx.App")

        self._gui = wx.Frame(None, title="Infiltration", size=(600, 400))

        self._panel = wx.Panel(self._gui)

        sizer_hor = wx.BoxSizer(wx.HORIZONTAL)
        sizer_vert = wx.BoxSizer(wx.VERTICAL)
        sizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        self._grid = CpGrid(self._panel,wx.ID_ANY, wx.WANTS_CHARS)
        self._grid.CreateGrid(self.sim.infiltration.nb_steps, self.sim.infiltration.nb_zones)

        self._btn_apply = wx.Button(self._panel, label=_("Apply"))
        self._btn_apply.Bind(wx.EVT_BUTTON, self.on_apply)
        self._btn_apply.SetToolTip(_("Apply the values in the grid to the in-memory simulation (without writing to disk)"))

        self._btn_check = wx.Button(self._panel, label=_("Check"))
        self._btn_check.Bind(wx.EVT_BUTTON, self.on_check)
        self._btn_check.SetToolTip(_("Check the consistency of the in-memory simulation (.fil and .inf files)"))

        self._btn_reload = wx.Button(self._panel, label=_("Reload"))
        self._btn_reload.Bind(wx.EVT_BUTTON, self.on_reload)
        self._btn_reload.SetToolTip(_("Reload the values from the in-memory simulation"))

        self._btn_plot = wx.Button(self._panel, label=_("Plot"))
        self._btn_plot.Bind(wx.EVT_BUTTON, self.on_plot)
        self._btn_plot.SetToolTip(_("Plot the discharges"))

        self._btn_plus = wx.Button(self._panel, label="+")
        self._btn_plus.Bind(wx.EVT_BUTTON, self.on_plus)
        self._btn_plus.SetToolTip(_("Add zone(s) or step(s)"))

        self._btn_minus = wx.Button(self._panel, label="-")
        self._btn_minus.Bind(wx.EVT_BUTTON, self.on_minus)
        self._btn_minus.SetToolTip(_("Remove zone(s) or step(s)"))

        self._btn_adjust = wx.Button(self._panel, label=_("Adjust"))
        self._btn_adjust.Bind(wx.EVT_BUTTON, self.on_adjust)
        self._btn_adjust.SetToolTip(_("Adjust the number of rows and columns of the grid"))

        sizer_btns.Add(self._btn_apply, 2, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_check, 2, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_reload, 2, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_plot, 2, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_plus, 1, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_minus, 1, wx.EXPAND | wx.ALL, 2)
        sizer_btns.Add(self._btn_adjust, 2, wx.EXPAND | wx.ALL, 2)

        self._txt_info = wx.TextCtrl(self._panel, style=wx.TE_MULTILINE|wx.TE_READONLY)

        sizer_vert.Add(self._grid, 1, wx.EXPAND)
        sizer_vert.Add(sizer_btns, 0, wx.EXPAND)
        sizer_vert.Add(self._txt_info, 1, wx.EXPAND)

        sizer_hor.Add(sizer_vert, 1, wx.EXPAND)

        self._panel.SetSizer(sizer_hor)
        self._panel.SetAutoLayout(1)

    def on_apply(self, event):

        i_max = 0
        while self._grid.GetCellValue(i_max, 0) != "" and i_max < self._grid.GetNumberRows()-1:
            i_max += 1

        j_max = 1
        while self._grid.GetCellValue(0, j_max) != "" and j_max < self._grid.GetNumberCols()-1:
            j_max += 1

        chronos = np.zeros((i_max, j_max+1), dtype=np.float64)

        try:
            for i in range(i_max):
                for j in range(j_max+1):
                    chronos[i,j] = self._grid.GetCellValue(i, j)
        except:
            logging.error("Error converting the grid to Float")
            return

        self.sim.infiltration.infiltrations_chronology = chronos
        self.on_check(1)

    def _fillgrid(self):
        """ Fill the CpGrid """

        if self.sim is None:
            logging.error("No simulation loaded")
            return

        grid = self._grid

        nb_steps = self.sim.infiltration.nb_steps
        nb_zones = self.sim.infiltration.nb_zones

        chronos = self.sim.infiltration.infiltrations_chronology

        if nb_steps > grid.GetNumberRows():
            grid.AppendRows(nb_steps - grid.GetNumberRows())

        if nb_zones > grid.GetNumberCols()-1:
            grid.AppendCols(nb_zones+1 - grid.GetNumberCols())

        grid.ClearGrid()

        grid.SetColLabelValue(0, _("Time"))
        for i in range(1,max(nb_zones, grid.GetNumberCols())+1):
            grid.SetColLabelValue(i, f"Zone {i}")

        for i in range(nb_steps):
            for j in range(nb_zones+1):
                grid.SetCellValue(i, j, str(chronos[i][j]))

    def on_adjust(self, event):
        """ Adjust the number of rows and columns of the CpGrid """

        nb_steps = self.sim.infiltration.nb_steps
        nb_zones = self.sim.infiltration.nb_zones

        if self._grid.GetNumberCols() < nb_zones+1:
            self._grid.AppendCols(nb_zones+1-self._grid.GetNumberCols())
        elif self._grid.GetNumberCols() > nb_zones+1:
            self._grid.DeleteCols(nb_zones, self._grid.GetNumberCols()-nb_zones-1)

        if self._grid.GetNumberRows() < nb_steps:
            self._grid.AppendRows(nb_steps-self._grid.GetNumberRows())
        elif self._grid.GetNumberRows() > nb_steps:
            self._grid.DeleteRows(nb_steps, self._grid.GetNumberRows()-nb_steps)

        self._btn_check.SetBackgroundColour(wx.NullColour)

    def on_plus(self, event):
        """ Add a zone or steps"""

        nb_zones = 0
        nb_steps = 0

        dlg = wx.NumberEntryDialog(self._gui, _('Number of zones to add'), _('Add zones'), _('Add'), value = 1, min=0, max=1000)
        if dlg.ShowModal() == wx.ID_OK:
            nb_zones = int(dlg.GetValue())

        dlg.Destroy()

        dlg = wx.NumberEntryDialog(self._gui, _('Number of steps to add'), _('Add steps'), _('Add'), value = 1, min=0, max=1000)
        if dlg.ShowModal() == wx.ID_OK:
            nb_steps = int(dlg.GetValue())

        dlg.Destroy()

        self._fillgrid()

        self._grid.AppendCols(nb_zones)
        self._grid.AppendRows(nb_steps)

        self._btn_check.SetBackgroundColour(wx.NullColour)

    def on_minus(self, event):
        """ Remove a zone or steps"""

        nb_zones = 0
        nb_steps = 0

        dlg = wx.NumberEntryDialog(self._gui, _('Number of zones to remove'), _('Remove zones'), _('Remove'), value = 0, min=0, max=self._grid.GetNumberCols())
        if dlg.ShowModal() == wx.ID_OK:
            nb_zones = int(dlg.GetValue())

        dlg.Destroy()

        dlg = wx.NumberEntryDialog(self._gui, _('Number of steps to remove'), _('Remove steps'), _('Remove'), value=0, min=0, max=self._grid.GetNumberRows())
        if dlg.ShowModal() == wx.ID_OK:
            nb_steps = int(dlg.GetValue())

        dlg.Destroy()

        self._grid.DeleteCols(nb_zones)
        self._grid.DeleteRows(nb_steps)

        self._fillgrid()

        self._btn_check.SetBackgroundColour(wx.NullColour)

    def on_check(self, event):

        if self.sim is None:
            self._txt_info.SetValue("No simulation loaded")
            return

        ret = self.sim.check_infiltration()
        self._txt_info.SetValue(ret)

        if "Warning" in ret:
            self._btn_check.SetBackgroundColour(wx.RED)
        else:
            self._btn_check.SetBackgroundColour(wx.GREEN)

    def on_reload(self, event):

        self._fillgrid()

    def on_plot(self, event):

        if self.sim is None:
            self._txt_info.SetValue("No simulation loaded")
            return

        self.sim.infiltration.plot_plt()

        self._btn_check.SetBackgroundColour(wx.NullColour)

    def Show(self):

        if self._gui is not None:
            self._fillgrid()
            self._gui.Show()
        else:
            logging.error("No GUI created")

class Wolf2DModel(GenMapManager):

    mydir:str
    sim:prev_sim2D

    # A path to the beacon file (not just the filename)
    filenamegen:str

    # When updating these, pay attention to the fact they are heavliy intertwined.
    # - Boundary conditions coordinates must coincide with cell borders

    SPWstations:SPWMIGaugingStations
    DCENNstations:SPWDCENNGaugingStations

    @property
    def mymnap(self):
        return self.sim.mymnap

    @property
    def xyzones(self):
        return self.sim.xyfile.myzones

    @property
    def mysuxsuy(self):
        return self.sim.sux_suy

    @property
    def blocfile(self):
        return self.sim.bloc_description

    def __init__(self, *args, dir:str='',  **kw):
        """
        :param dir: directory containing the simulation, the base file name (e.g. "simul") will be autodetected.
                  If you create a model from scracth, then you must provide
                  the base file name as well (e.g. "d:/mywolfsim/sim")

            self.wx_exists : If True, then this model will connect itself to the GUI.
                      If False, the model will stand alone (so you can use it outside
                      of the GUI).
        """

        super(Wolf2DModel, self).__init__(*args, **kw)

        self._ref_block = None
        self._prop_frame = None

        # Gauging stations - SPW
        self.SPWstations    = SPWMIGaugingStations()
        self.DCENNstations  = SPWDCENNGaugingStations()

        if dir != '':
            # Either a directory or a file "/_/_/_/dir/simul" for example.

            assert exists(dir) or dirname(dir), f"'{dir}' does not exists"

        if dir=='':
            if self.wx_exists:
                # Propose a dialog window to choose the directory

                idir=wx.DirDialog(None,"Choose Directory")
                if idir.ShowModal() == wx.ID_CANCEL:
                    self.setup_mapviewer(title='Blank 2D model',wolfparent=self)
                    self.mapviewer.findminmax(True)
                    self.mapviewer.Autoscale(False)
                    self.mapviewer.menu_sim2D()
                    return
            else:
                return

            self.mydir =idir.GetPath()
        else:
            self.mydir=normpath(dir)

        if self.wx_exists:

            self.setup_mapviewer(title='2D model : '+self.mydir, wolfparent=self)

        try:
            if exists(self.mydir) and isfile(self.mydir): # Either a file or doesn't exist
                assert not Path(self.mydir).suffix, \
                    "A generic file path should have no extension," \
                    f" we have {self.mydir}"
                self.filenamegen=self.mydir
                self.mydir = str(Path(self.mydir).parent)
            else:
                # FIXME This is a big problem: we can't decide
                # if self.mydir is intended to be a directory
                # or a path to the generic file. Morevoer the
                # MNAP code confuses the generic name and the
                # .MNAP name when checking if it can load an array.
                if not exists(self.mydir):
                    self.mydir = dirname(self.mydir)

                self.filenamegen=""
                second_choice = None

                #recherche du nom générique --> sans extension
                scandir_obj = scandir(self.mydir)
                for curfile in scandir_obj:
                    if curfile.is_file():
                        ext=splitext(curfile)
                        if len(ext[1])==0:
                            self.filenamegen = join(self.mydir,curfile.name)
                            break
                        elif ext[1] == ".sux":
                            # Some extension present, we choose .sux because
                            # it works, see comment below.
                            second_choice = ext[0]
                scandir_obj.close()

                if self.filenamegen=='':
                    if second_choice:
                        # If the beacon file has not been found, we take
                        # a suitable default.
                        # This is needed when one reads a simulation that
                        # has just been created with the VB application.
                        # In that case, there's no beacon file.
                        self.filenamegen = second_choice
                    else:
                        logging.info(_(f"The provided directory doesn't seem to be a Wolf simulation"))
                        self.filenamegen = str(Path(self.mydir) /'newsim')


            logging.info(_(f'Generic file is : {self.filenamegen}'))
            logging.info(_('Creating GUI'))

            # Initilisation d'une simulation 2D sur base des fichiers
            self.sim:prev_sim2D
            self.sim = prev_sim2D(self.filenamegen)

            # Liste des objets à ajouter au GUI
            self.fines_array=[]

            logging.info(_('Treating arrays'))

            self._add_arrays_to_mapviewer()
            self._add_vectors_to_mapviewer()

            logging.info(_('Zooming'))
            self.mapviewer.findminmax(True)
            self.mapviewer.Autoscale(False)

            self.show_properties()

            if self.wx_exists:
                self.mapviewer.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
                self.mapviewer.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

                logging.info(_('Adapting menu'))
                self.mapviewer.menu_sim2D()

            logging.info(_('Verifying files'))
            self.sim.verify_files()

            logging.info(_('Model loaded !!'))

        except Exception as ex:
            logging.error(str(ex), exc_info=True)

    @property
    def writing_mode(self):
        return self.sim.parameters._writing_mode

    @property
    def writing_frequency(self):
        return self.sim.parameters._writing_frequency

    @property
    def dx_fine(self):
        return self.sim.parameters._fine_mesh_dx

    @property
    def dy_fine(self):
        return self.sim.parameters._fine_mesh_dy

    def _dx_block(self, idx):
        return self.sim.bloc_description.my_blocks[idx].dx

    def _dy_block(self, idx):
        return self.sim.bloc_description.my_blocks[idx].dy

    @property
    def scheme_rk(self):
        return self.sim.parameters._scheme_rk


    def _add_arrays_to_mapviewer(self, force_reload=False):
        """ Add arrays to the mapviewer """

        # Mono-blocks
        # ------------

        fines = self.sim.files_fine_array['Characteristics']

        existing_id = self.mapviewer.get_list_keys(drawing_type=draw_type.ARRAYS, checked_state=None)

        for ext, name, wolftype in fines:

            locarray = self.sim.get_wolf_array(ext)

            if locarray is not None:

                if name.lower() not in existing_id:

                    # locarray.nullvalue = 99999.

                    self.mapviewer.add_object(which='array',
                                            ToCheck=False,
                                            newobj=locarray,
                                            id=name.lower())
                elif force_reload:
                    self.sim.force_reload(locarray)

                    if locarray.plotted:
                        locarray.reset_plot()

        locarray = self.sim.zbin
        name = _('Water level [m]')
        if locarray is not None:

            if name.lower() not in existing_id:

                # locarray.nullvalue = 99999.

                self.mapviewer.add_object(which='array',
                                        ToCheck=False,
                                        newobj=locarray,
                                        id=name.lower())

            elif force_reload:

                self.sim.force_reload(locarray)

                if locarray.checked:
                    locarray.reset_plot()

        # Multi-blocks
        # ------------

        # MNAP
        multiblocks = self.sim.files_MB_array['Characteristics']

        for ext, name, wolftype in multiblocks:

            locarray = self.sim.get_wolf_array(ext)

            if locarray is not None:

                if name.lower() not in existing_id:

                    # locarray.nullvalue = 99999.

                    self.mapviewer.add_object(which='array',
                                              ToCheck=False,
                                              newobj=locarray,
                                              id=name.lower())
                elif force_reload:
                    self.sim.force_reload(locarray)

                    if locarray.checked:
                        locarray.reset_plot()


        multiblocks = self.sim.files_MB_array['Initial Conditions']

        for ext, name, wolftype in multiblocks:

            locarray = self.sim.get_wolf_array(ext)

            if locarray is not None:

                if name.lower() not in existing_id:

                    # locarray.nullvalue = 99999.

                    self.mapviewer.add_object(which='array',
                                              ToCheck=False,
                                              newobj=locarray,
                                              id=name.lower())
                elif force_reload:
                    self.sim.force_reload(locarray)

                    if locarray.checked:
                        locarray.reset_plot()

        locarray = self.sim.zbinb
        name = _('MB - Water level [m]')
        if locarray is not None:

            if name.lower() not in existing_id:

                # locarray.nullvalue = 99999.

                self.mapviewer.add_object(which='array',
                                          ToCheck=False,
                                          newobj=locarray,
                                          id=name.lower())
            elif force_reload:

                self.sim.force_reload(locarray)

                if locarray.checked:
                    locarray.reset_plot()


    def _add_vectors_to_mapviewer(self):
        """ Add vectors to the mapviewer """

        existing_id = self.mapviewer.get_list_keys(drawing_type=draw_type.ARRAYS, checked_state=False)

        # for key, values in self.sim.files_vectors.items():
        values = self.sim.files_vectors['Block file']

        for cur in values:

            ext, name = cur

            if Path(self.filenamegen+ext).exists():

                if name not in existing_id:

                    locZones = self.sim.get_Zones_from_extension(ext)

                    if locZones is not None:

                        assert isinstance(locZones, Zones), 'locZones is not a Zones object'

                        self.mapviewer.add_object(which='vector',
                                                ToCheck=False if ext != '.bloc' else True,
                                                newobj=locZones,
                                                id=name)

        # We must set the parent of the "Zones" object to permit access to the mapviewer
        # prep_listogl() is called to prepare the display of the zones and "mapviewer" is needed
        if self.sim.bloc_description is not None:
            self.sim.bloc_description.my_vec_blocks.parent = self
            self.sim.bloc_description.my_vec_blocks.set_mapviewer()
            self.sim.bloc_description.my_vec_blocks.prep_listogl()

        # self.sim.sux_suy.myborders.parent = self
        # self.sim.sux_suy.myborders.set_mapviewer()
        # self.sim.sux_suy.myborders.prep_listogl()


    def mimic_mask(self, source:WolfArray):
        """ Copy the mask of the source array to all arrays in the model. """

        self.sim.mimic_mask(source)

    def show_properties(self):
        """
        Show the properties of the model
        """

        if self.wx_exists:

            if self._prop_frame is not None:
                self._prop_frame.CenterOnScreen()
                self._prop_frame.Iconize(False)
                self._prop_frame.Show()
                return

            # Création d'un wx Frame pour les paramètres
            self._prop_frame = wx.Frame(self,
                                        title=_('Parameters') + self.filenamegen,
                                        size=(650, 800),
                                        style = wx.DEFAULT_FRAME_STYLE)

            # add a panel
            self._panel = wx.Panel(self._prop_frame)

            # Set sizers
            #
            # The panel is decomposed in three parts:
            # - List of toogle buttons + properties
            # - Buttons to add/remove blocks/update structure
            # - Information zone (multiline text)

            self._sizer_gen = wx.BoxSizer(wx.HORIZONTAL)

            self._sizer_run_results = wx.BoxSizer(wx.VERTICAL)

            self._sizer_principal = wx.BoxSizer(wx.VERTICAL)

            self._sizer_properties = wx.BoxSizer(wx.HORIZONTAL)

            self._sizer_btnsblocks = wx.BoxSizer(wx.VERTICAL)

            self._sizer_btnsactions = wx.BoxSizer(wx.HORIZONTAL)
            self._sizer_btnsactions_left = wx.BoxSizer(wx.VERTICAL)
            self._sizer_btnsactions_right = wx.BoxSizer(wx.VERTICAL)

            self._sizer_btnsactions.Add(self._sizer_btnsactions_left, 1, wx.EXPAND)
            self._sizer_btnsactions.Add(self._sizer_btnsactions_right, 1, wx.EXPAND)

            self._sizer_btns_creation = wx.BoxSizer(wx.HORIZONTAL)

            # Buttons
            # ********

            # Boundary conditions
            # ---------------------

            self._btn_bc = wx.Button(self._panel, label=_('BCs'))
            self._btn_bc.SetToolTip(_('Set the boundary conditions'))
            self._btn_bc.Bind(wx.EVT_BUTTON, self._set_bc)

            self._sizer_run_results.Add(self._btn_bc, 1, wx.EXPAND)

            # Infiltration
            # --------------

            self._btn_infiltration = wx.Button(self._panel, label=_('Infiltration'))
            self._btn_infiltration.SetToolTip(_('Set the infiltration'))
            self._btn_infiltration.Bind(wx.EVT_BUTTON, self._set_infiltration)

            self._sizer_run_results.Add(self._btn_infiltration, 1, wx.EXPAND)

            # Part arrays
            # ------------

            self._btn_part_arrays = wx.Button(self._panel, label=_('Part arrays'))
            self._btn_part_arrays.SetToolTip(_('Set the part arrays'))
            self._btn_part_arrays.Bind(wx.EVT_BUTTON, self._set_part_arrays)

            self._sizer_run_results.Add(self._btn_part_arrays, 1, wx.EXPAND)

            # Check
            # -----

            self._btn_checkerrors = wx.Button(self._panel, label=_('Check errors'))
            self._btn_checkerrors.SetToolTip(_('Check the errors in the model'))
            self._btn_checkerrors.Bind(wx.EVT_BUTTON, self._check_errors)

            self._sizer_run_results.Add(self._btn_checkerrors, 1, wx.EXPAND)

            # Write files
            # ------------

            self._btn_write = wx.Button(self._panel, label=_('Write files'))
            self._btn_write.SetToolTip(_('Write the files to disk'))
            self._btn_write.Bind(wx.EVT_BUTTON, self._write_files)

            self._sizer_run_results.Add(self._btn_write, 1, wx.EXPAND)

            # Run simulation
            # ---------------

            self._btn_run = wx.Button(self._panel, label=_('Run'))
            self._btn_run.SetToolTip(_('Run the simulation - wolfcli.exe code'))
            self._btn_run.Bind(wx.EVT_BUTTON, self._run)

            self._sizer_run_results.Add(self._btn_run, 1, wx.EXPAND)

            # Results
            # --------

            self._btn_results = wx.Button(self._panel, label=_('Results'))
            self._btn_results.SetToolTip(_('Display the results of the simulation'))
            self._btn_results.Bind(wx.EVT_BUTTON, self._results)

            self._sizer_run_results.Add(self._btn_results, 1, wx.EXPAND)

            # Result as IC
            # ------------

            self._btn_rs2ic = wx.Button(self._panel, label=_('Results as IC'))
            self._btn_rs2ic.SetToolTip(_('Set one result as initial conditions'))
            self._btn_rs2ic.Bind(wx.EVT_BUTTON, self._results2ic)

            self._sizer_run_results.Add(self._btn_rs2ic, 1, wx.EXPAND)

            # Copy 2 GPU
            # -----------

            self._btn_copy2gpu = wx.Button(self._panel, label=_('Copy 2 GPU'))
            self._btn_copy2gpu.SetToolTip(_('Copy/Convert the simulation to the GPU framework'))
            self._btn_copy2gpu.Bind(wx.EVT_BUTTON, self._copy2gpu)

            self._sizer_run_results.Add(self._btn_copy2gpu, 1, wx.EXPAND)

            # Wizard
            # ------

            self._btn_wizard = wx.Button(self._panel, label=_('Wizard'))
            self._btn_wizard.SetToolTip(_('Launch the wizard to create a new model'))
            self._btn_wizard.Bind(wx.EVT_BUTTON, self._wizard)

            self._sizer_principal.Add(self._btn_wizard, 1, wx.EXPAND)

            # Creation
            # ---------

            self._btn_fromvector = wx.Button(self._panel, label=_('Create From vector'))
            self._btn_fromarray  = wx.Button(self._panel, label=_('Create From array'))
            self._btn_fromfootprint = wx.Button(self._panel, label=_('Create From footprint'))

            self._btn_fromvector.SetToolTip(_('Create a simulation from an existing polygon'))
            self._btn_fromarray.SetToolTip(_('Create a simulation from the active array'))
            self._btn_fromfootprint.SetToolTip(_('Create a simulation from the footprint (ox, oy, nbx, nby, dy, dy)'))

            self.Bind(wx.EVT_BUTTON, self._create_from_vector, self._btn_fromvector)
            self.Bind(wx.EVT_BUTTON, self._create_from_array, self._btn_fromarray)
            self.Bind(wx.EVT_BUTTON, self._create_from_footprint, self._btn_fromfootprint)

            self._sizer_btns_creation.Add(self._btn_fromvector, 1, wx.EXPAND)
            self._sizer_btns_creation.Add(self._btn_fromarray, 1, wx.EXPAND)
            self._sizer_btns_creation.Add(self._btn_fromfootprint, 1, wx.EXPAND)

            self._sizer_principal.Add(self._sizer_btns_creation, 1, wx.EXPAND)


            self._sizer_magn_res = wx.BoxSizer(wx.HORIZONTAL)

            # Magnetic grid
            # -------------

            self._btn_magnetic_grid = wx.Button(self._panel, label=_('Magnetic grid'))
            self._btn_magnetic_grid.SetToolTip(_('Set a magnetic grid for the model'))
            self._btn_magnetic_grid.Bind(wx.EVT_BUTTON, self._set_magnetic_grid)

            self._sizer_magn_res.Add(self._btn_magnetic_grid, 1, wx.EXPAND)

            # Resolution
            # -----------

            self._btn_set_fine_res = wx.Button(self._panel, label=_('Set fine resolution'))
            self._btn_set_fine_res.SetToolTip(_('Set the fine resolution of the model'))
            self._btn_set_fine_res.Bind(wx.EVT_BUTTON, self._choose_fine_resolution)

            self._sizer_magn_res.Add(self._btn_set_fine_res, 1, wx.EXPAND)


            # Chesk Translation
            # -----------------

            self._chk_translation = wx.CheckBox(self._panel, label=_('Shift to (0., 0.)'), style=wx.ALIGN_CENTER)
            self._chk_translation.SetToolTip(_('Shift the global coordinates to (0., 0.) and define shifting parameters'))
            self._chk_translation.SetValue(True)

            self._sizer_magn_res.Add(self._chk_translation, 1, wx.EXPAND)

            self._sizer_principal.Add(self._sizer_magn_res, 1, wx.EXPAND)


            self._sizer_add_mesh_create = wx.BoxSizer(wx.HORIZONTAL)

            # Add blocks
            # -----------

            self._btn_add_blocks = wx.Button(self._panel, label=_('Add blocks'))
            self._btn_add_blocks.SetToolTip(_('Add blocks to the model'))
            self._btn_add_blocks.Bind(wx.EVT_BUTTON, self._add_blocks)

            self._sizer_add_mesh_create.Add(self._btn_add_blocks, 1, wx.EXPAND)

            # Mesher
            # -------

            self._btn_mesher = wx.Button(self._panel, label=_('Mesher'))
            self._btn_mesher.SetToolTip(_('Mesh the model -- call to the Fortran code wolfcli.exe'))
            self._btn_mesher.Bind(wx.EVT_BUTTON, self._mesher)

            self._sizer_add_mesh_create.Add(self._btn_mesher, 1, wx.EXPAND)

            # Create arrays
            # -------------

            self._btn_create_arrays = wx.Button(self._panel, label=_('Create arrays'))
            self._btn_create_arrays.SetToolTip(_('Create the fine arrays for the model'))
            self._btn_create_arrays.Bind(wx.EVT_BUTTON, self._create_arrays)

            self._sizer_add_mesh_create.Add(self._btn_create_arrays, 1, wx.EXPAND)

            self._sizer_principal.Add(self._sizer_add_mesh_create, 1, wx.EXPAND)

            # Apply changes
            # -------------
            self._btn_apply = wx.Button(self._panel, label=_('Apply changes'))
            self._btn_apply.SetToolTip(_('Apply the changes to the memory (not saved on disk)'))
            self._btn_apply.Bind(wx.EVT_BUTTON, self._apply_changes)

            # Update structure
            # ----------------
            self._btn_update_struct = wx.Button(self._panel, label=_('Update structure'))
            self._btn_update_struct.SetToolTip(_('Update the structure of the model (add/remove blocks)'))
            self._btn_update_struct.Bind(wx.EVT_BUTTON, self._update_structure)

            # Add/remove blocks
            # -----------------
            self._btn_plus = wx.Button(self._panel, label='+')
            self._btn_plus.SetToolTip(_('Add a block to the model'))
            self._btn_plus.Bind(wx.EVT_BUTTON, self._add_block)

            self._btn_minus = wx.Button(self._panel, label='-')
            self._btn_minus.SetToolTip(_('Remove a block from the model'))
            self._btn_minus.Bind(wx.EVT_BUTTON, self._remove_block)

            # Checkboxes
            # **********

            # Show all parameters
            # -------------------
            self._check_show_all = wx.CheckBox(self._panel, label=_('All parameters'))
            self._check_show_all.SetToolTip(_('Show all parameters even if they have the default value (default: show only modified parameters)'))
            self._check_show_all.Bind(wx.EVT_CHECKBOX, self._all_parameters)

            # Force update if multiple blocks are toggled
            # -------------------------------------------
            self._check_force = wx.CheckBox(self._panel, label=_('Force update'))
            self._check_force.SetToolTip(_('Force the update of some parameters in all selected blocks (default: update only the first one - considered as the reference block)'))
            self._check_force.Bind(wx.EVT_CHECKBOX, self._force_update)


            # add widgets to sizers
            # *********************

            self._sizer_btnsactions_left.Add(self._btn_apply, 1, wx.EXPAND)
            self._sizer_btnsactions_left.Add(self._btn_update_struct, 1, wx.EXPAND)

            self._sizer_btnsactions_right.Add(self._btn_plus, 1, wx.EXPAND)
            self._sizer_btnsactions_right.Add(self._btn_minus, 1, wx.EXPAND)
            self._sizer_btnsactions_right.Add(self._check_show_all, 1, wx.EXPAND)
            self._sizer_btnsactions_right.Add(self._check_force, 1, wx.EXPAND)

            self._panel.SetSizer(self._sizer_gen)

            self._sizer_principal.Add(self._sizer_properties, 4, wx.EXPAND)
            self._sizer_principal.Add(self._sizer_btnsactions, 1, wx.EXPAND)

            self._txt_info = wx.TextCtrl(self._panel, style=wx.TE_MULTILINE|wx.TE_READONLY)

            self._sizer_principal.Add(self._txt_info, 2, wx.EXPAND)

            self._sizer_gen.Add(self._sizer_principal, 5, wx.EXPAND)
            self._sizer_gen.Add(self._sizer_run_results, 1, wx.EXPAND)


            # Create the local list of parameters
            # - for global parameters
            # - for blocks
            self._prop_gen = prev_parameters_simul()
            self._prop_block = prev_parameters_blocks()

            # Create the widget PropertyGridManager for the parameters
            self._prop_gen._params.ensure_prop(wxparent = self._panel, show_in_active_if_default= False)
            self._prop_block._params.ensure_prop(wxparent = self._panel, show_in_active_if_default= False)

            # Create the buttons for the blocks and the global parameters
            self._fill_buttons_genblocks()

            self._sizer_properties.Add(self._sizer_btnsblocks, 1, wx.EXPAND)

            # add the properties to the sizer
            self._sizer_properties.Add(self._prop_gen._params.prop, 5, wx.EXPAND)
            self._sizer_properties.Add(self._prop_block._params.prop, 5, wx.EXPAND)


            # Hide the block properties
            self._prop_gen._params.prop.Show()
            self._prop_block._params.prop.Hide()


            # The default view is the global parameters
            self._show_glob_properties()

            # Show the frame
            self._prop_frame.Show()

        else:
            logging.info(_('No GUI available'))

    def _set_bc(self, e:wx.EVT_BUTTON):
        """ Set the boundary conditions """

        from .mesh2d.bc_manager import BcManager, choose_bc_type

        if self.mapviewer.active_bc is None:

            newbc = BcManager(self,
                            linked_array=self.sim.napbin,
                            version = 1,
                            DestroyAtClosing=True,
                            Callback=self.mapviewer.pop_boundary_manager,
                            mapviewer=self.mapviewer,
                            wolfparent = self)


            self.mapviewer.mybc.append(newbc)

            self.mapviewer.active_bc = newbc

            self.mapviewer.Refresh()

        else:
            self.mapviewer.active_bc.Show()

    def _set_infiltration(self, e:wx.EVT_BUTTON):

        inf_frame = Wolf2DInfiltration(self.sim)
        inf_frame.Show()

    def _set_part_arrays(self, e:wx.EVT_BUTTON):

        part_frame = Wolf2DPartArrays(self.sim, self.mapviewer)
        part_frame.Show()

    def add_boundary_condition(self, i: int, j: int, bc_type:BCType_2D,  bc_value: float, border:Direction):
        """ alias """

        self.sim.add_boundary_condition(i, j, bc_type, bc_value, border)

    def reset_boundary_conditions(self):
        """ Reset the boundary conditions """

        self.sim.parameters.reset_all_boundary_conditions()


    def _check_errors(self, e:wx.EVT_BUTTON):
        """ Check the errors in the model """

        self._txt_info.Clear()

        valid, ret = self.sim.parameters.check_all(1)

        if valid:
            self._btn_checkerrors.SetBackgroundColour(wx.GREEN)
        else:
            self._btn_checkerrors.SetBackgroundColour(wx.RED)

        self._txt_info.AppendText(ret)


    def _write_files(self, e:wx.EVT_BUTTON):
        """ Write the files to disk """

        if self.sim.parameters._mesher_only:

            dlg = wx.MessageDialog(None, _('You have selected "Mesh only" - Do you want to uncheck it ?'), _('Warning'), wx.YES_NO)
            ret = dlg.ShowModal()
            dlg.Destroy()

            if ret == wx.ID_YES:
                self.sim.unset_mesh_only()

        self.sim.save()


    def _run(self, e:wx.EVT_BUTTON):
        """ Run the simulation """

        valid, ret = self.sim.parameters.check_all()

        if not valid:
            self._txt_info.AppendText(_('\n\nWe can not run the simulation\n\n'))
            logging.error(_('We can not run the simulation -- Check the errors !'))

            self._btn_checkerrors.SetBackgroundColour(wx.RED)

            return

        self._btn_checkerrors.SetBackgroundColour(wx.GREEN)

        self.sim.run_wolfcli()

    def _results(self, e:wx.EVT_BUTTON):
        """ Display the results """

        self.mapviewer.add_object(which='res2d',
                                  filename=self.filenamegen,
                                  id='Results')
        self.mapviewer.menu_wolf2d()
        self.mapviewer.Refresh()

    def _results2ic(self, e:wx.EVT_BUTTON):
        """ Choose one result as initial conditions """

        from .wolfresults_2D import Wolfresults_2D
        from datetime import timedelta

        myres = Wolfresults_2D(self.filenamegen, plotted=False)

        times, steps = myres.get_times_steps()

        times_hms = [timedelta(seconds=int(curtime), milliseconds=int(curtime-int(curtime))*1000) for curtime in times]

        choices = [_('Last one')] + ['{:3f} [s] - {} [h:m:s] - {} [step index]'.format(curtime, curtimehms, curstep) for curtime, curtimehms, curstep in zip(times, times_hms, steps)]

        dlg = wx.SingleChoiceDialog(None, _('Choose the time step to set as initial conditions'), _('Results as IC'), choices)

        ret = dlg.ShowModal()

        if ret == wx.ID_CANCEL:
            logging.info(_('Aborting - No time step selected'))
            return

        idx = dlg.GetSelection() - 1 # -1 because of the first choice is the last one and it is the convention used in the code

        dlg.Destroy()

        as_multiblocks = False # Default value

        if self.sim.is_multiblock:

            dlg = wx.SingleChoiceDialog(None, _('Choose the type of storage'), _('Results as IC'), [_('Multi-blocks'), _('Mono-block')])

            ret = dlg.ShowModal()

            if ret == wx.ID_CANCEL:
                logging.info(_('Aborting - No storage type selected'))
                return

            storage = dlg.GetSelection()

            as_multiblocks = storage == 0

        myres.set_hqxqy_as_initial_conditions(idx, as_multiblocks)

        if self.sim.parameters.has_turbulence:
            myres.set_keps_as_initial_conditions(idx, as_multiblocks)

        # update the arrays
        self._add_arrays_to_mapviewer(force_reload=True)

    def _copy2gpu(self, e:wx.EVT_BUTTON):
        """ Click on the button to copy to the GPU """

        if self.sim.nb_blocks > 1:
            logging.error(_('Multiple blocks defined - Copy to GPU not possible'))
            self._txt_info.AppendText(_('Multiple blocks defined - Copy to GPU not possible !\n'))
            self._txt_info.AppendText(_('Please define only one block or convert you simulation manually.\n'))
            return

        if self.sim.parameters.has_turbulence:
            logging.error(_('Turbulence is defined - Copy to GPU not yet possible'))
            self._txt_info.AppendText(_('Turbulence is defined - Copy to GPU not yet possible !\n'))
            self._txt_info.AppendText(_('Please remove the turbulence or help to implement the turbulence model in the GPU framework.\n'))
            return

        if self.sim.parameters.blocks[0]._friction_law != 0:
            logging.error(_('Friction law is not Manning-Strickler or a more sophisticated surface evaluation - Copy to GPU not yet possible'))
            self._txt_info.AppendText(_('Friction law is not Manning-Strickler or a more sophisticated surface evaluation - Copy to GPU not yet possible !\n'))
            self._txt_info.AppendText(_('Please change the friction law or help to implement the friction law in the GPU framework.\n'))
            return

        if self.sim.inf.array.min() < 0:
            logging.error(_('Negative infiltration zoning values - Copy to GPU not yet possible'))
            self._txt_info.AppendText(_('Negative infiltration zoning values - Copy to GPU not yet possible !\n'))
            self._txt_info.AppendText(_('Please change the infiltration mode or help to implement ther variable infiltration in the GPU framework.\n'))
            return

        dirout = wx.DirDialog(None, _('Choose the output directory for the GPU simulation'))

        if dirout.ShowModal() == wx.ID_CANCEL:
            return

        gpudir = dirout.GetPath()

        ret = self.sim.copy2gpu(gpudir)

        self._txt_info.AppendText(ret)

        if _('All files copied successfully') in ret:
            logging.info(_('All files copied successfully'))


    def _wizard(self, e:wx.EVT_BUTTON):
        """ Launch the wizard """

        from wx.adv import Wizard, WizardPageSimple

        wizard_text = self.sim.get_wizard_text()

        self.wizard = Wizard(None, -1, _('Wizard GPU simulation'))

        self.wizard.SetPageSize((400, 300))

        self.wiz_pages:list[WizardPageSimple] = []

        for curpage in wizard_text:
            self.wiz_pages.append(WizardPageSimple(self.wizard))
            self.wiz_pages[-1].SetBackgroundColour(wx.Colour(255, 255, 255))
            self.wiz_pages[-1].SetSizer(wx.BoxSizer(wx.VERTICAL))

        for idx, curpage in enumerate(wizard_text):
            for curstep in curpage:
                self.wiz_pages[idx].GetSizer().Add(wx.StaticText(self.wiz_pages[idx], -1, curstep), 0, wx.ALIGN_LEFT)

        for i in range(len(self.wiz_pages)-1):
            self.wiz_pages[i].Chain(self.wiz_pages[i+1])


        ret = self.wizard.RunWizard(self.wiz_pages[0])

        if ret:
            logging.info(_('Wizard finished'))
        else:
            logging.warning(_('Wizard cancelled - Are you sure ?'))

    def _mesher(self, e:wx.EVT_BUTTON):
        """ Call the mesher """

        if self.nb_blocks == 0:
            logging.error(_('No block defined -- Please add a block to the model (see "+ button")'))
            return

        nb_vert = [len(self.sim.bloc_description.my_blocks[i].contour.myvertices) for i in range(self.nb_blocks)]
        nb_vert.sort()

        if nb_vert[0] ==0:
            logging.error(_(' At least one block is not defined -- Please draw the polygons for each block'))
            return

        self.sim.translate_origin2zero = self._chk_translation.GetValue()
        self.sim.mesh()

        self._add_arrays_to_mapviewer()
        self._add_vectors_to_mapviewer()

    def _create_arrays(self, e:wx.EVT_BUTTON):
        """ Create the fine arrays """

        if self.nb_blocks == 0:
            logging.error(_('No block defined -- Please add a block to the model and mesh'))
            return

        self.sim.create_fine_arrays(with_tubulence= self.sim.parameters.has_turbulence)
        self.sim.create_sux_suy()

        self._add_arrays_to_mapviewer()


    def _add_blocks(self, e:wx.EVT_BUTTON):
        """ Add blocks to the model """

        dlg = wx.TextEntryDialog(None, _('How many blocks do you want to add ?'), _('Add blocks'), '1', wx.OK | wx.CANCEL | wx.CENTRE)

        dlg.ShowModal()

        if dlg.GetReturnCode() == wx.ID_CANCEL:
            dlg.Destroy()
            return

        nb = int(dlg.GetValue())

        dlg.Destroy()


        for i in range(nb):

            name = f'Block {self.nb_blocks+1}'
            # Set the external border as the first block
            newvec = self.sim.bloc_description.external_border
            self.sim.add_block(newvec, self.dx_fine, self.dy_fine, name)


        self._update_structure(0)

        dlg = wx.MessageDialog(None, _('Block(s) added\n\nYou must define the polygons'), _('Information'), wx.OK)

        pass

    def _create_from_vector(self, e:wx.EVT_BUTTON):
        """ Create a simulation from a vector """

        if self.mapviewer.active_vector is None:
            logging.error(_('No active vector defined - Please select or create a vector/polygon as external border'))
            return

        self.sim.set_external_border_vector(self.mapviewer.active_vector)

    def _create_from_array(self, e:wx.EVT_BUTTON):
        """ Create a simulation from an array """

        if self.mapviewer.active_array is None:
            logging.error(_('No active array defined - Please select or create an array as external border'))
            return

        self.sim.set_external_border_wolfarray(self.mapviewer.active_array)
        self.sim.set_mesh_fine_size(self.mapviewer.active_array.dx, self.mapviewer.active_array.dy)

        self._show_glob_properties()

    def _create_from_footprint(self, e:wx.EVT_BUTTON):
        """ Create a simulation from a footprint """

        dlg = wx.TextEntryDialog(None, _('Footprint'), _('Footprint'), 'ox, oy, nbx, nby, dx, dy')

        if dlg.ShowModal() == wx.ID_OK:
            try:
                ox, oy, nbx, nby, dx, dy = dlg.GetValue().split(',')

                newhead = header_wolf()
                newhead.nbx = int(nbx)
                newhead.nby = int(nby)
                newhead.dx = float(dx)
                newhead.dy = float(dy)
                newhead.origx = float(ox)
                newhead.origy = float(oy)

                self.sim.set_external_border_header(newhead)

                self.sim.set_mesh_fine_size(float(dx), float(dy))
                self._show_glob_properties()
            except:
                logging.error(_('Invalid footprint'))

        dlg.Destroy()

    def _set_magnetic_grid(self, e:wx.EVT_BUTTON):
        """ Set the magnetic grid """

        dlg = wx.TextEntryDialog(None, _('Magnetic grid'), _('Magnetic grid'), 'ox, oy, dx, dy')

        if dlg.ShowModal() == wx.ID_OK:
            try:
                ox, oy, dx, dy = dlg.GetValue().split(',')
                self.sim.set_magnetic_grid(float(dx), float(dy), float(ox), float(oy))
                self._show_glob_properties()
            except:
                logging.error(_('Invalid magnetic grid'))

        dlg.Destroy()

    def _choose_fine_resolution(self, e:wx.EVT_BUTTON):
        """ Choose the fine resolution """

        dlg = wx.TextEntryDialog(None, _('Choose the fine resolution'), _('Fine resolution'), 'dx, dy')

        if dlg.ShowModal() == wx.ID_OK:
            try:
                dx, dy = dlg.GetValue().split(',')

                try:
                    floatdx = float(dx)
                    floatdy = float(dy)
                except:
                    logging.error(_('Invalid fine resolution'))
                    return

                self.sim.set_mesh_fine_size(floatdx, floatdy)
                self._show_glob_properties()
            except:
                logging.error(_('Invalid fine resolution'))

        dlg.Destroy()

        self._show_glob_properties()


    def _add_block(self, e:wx.EVT_BUTTON):
        """ Add a block to the model """

        newvec = vector()
        self.sim.add_block(newvec, self.dx_fine, self.dy_fine)

        dlg = wx.MessageDialog(None, _('Block added\nDo not forget to :\n - draw the contour\n - set the spatial resolution if not the same that the fine one'), _('Information'), wx.OK)

        dlg.ShowModal()
        dlg.Destroy()

        self._update_structure(0)

        pass

    def _remove_block(self, e:wx.EVT_BUTTON):
        """ Remove a block from the model """

        dlg = wx.MessageDialog(None, _('Are you sure you want to remove the block ?'), _('Warning'), wx.YES_NO)

        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()

            select = wx.MultiChoiceDialog(None, _('Select the block to remove'), _('Remove block'), [f'Block {idx+1}' for idx in range(self.nb_blocks)])

            if select.ShowModal() == wx.ID_OK:
                selected = select.GetSelections()

                for idx in selected:
                    self.sim.remove_block(idx)

                dlg = wx.MessageDialog(None, _('Block(s) removed'), _('Information'), wx.OK)

                dlg.ShowModal()
                dlg.Destroy()

                self._update_structure(0)

            select.Destroy()

        else:
            dlg.Destroy()


    def _update_structure(self, e:wx.EVT_BUTTON):
        """ Update the structure of the model """

        self._fill_buttons_genblocks()
        self._show_glob_properties()


    def _all_parameters(self, e:wx.EVT_CHECKBOX):
        """ Show all parameters """

        show_all = self._check_show_all.GetValue()

        if self._prop_block._params.show_in_active_if_default != show_all:
            self._prop_block._params.show_in_active_if_default = show_all
            self._prop_block._params.Populate(sorted_groups=True)

        if self._prop_gen._params.show_in_active_if_default != show_all:
            self._prop_gen._params.show_in_active_if_default = show_all
            self._prop_gen._params.Populate(sorted_groups=True)

    def _force_update(self, e:wx.EVT_CHECKBOX):
        """ Force the update """
        pass

    def _update_layout(self):
        """ Update the layout of the frame """

        self._panel.Layout()
        self._prop_frame.Layout()

    def _fill_buttons_genblocks(self):
        """
        Fill the buttons for the blocks
        """

        self._sizer_btnsblocks.Clear(True)

        self._btn_gen = wx.ToggleButton(self._panel, label=_('Global'))

        self._btn_blocks = [wx.ToggleButton(self._panel, label=_('Blocks ')+str(idx)) for idx in range(1, self.nb_blocks+1)]

        self._sizer_btnsblocks.Add(self._btn_gen, 1, wx.EXPAND)
        for btn in self._btn_blocks:
            self._sizer_btnsblocks.Add(btn, 1, wx.EXPAND)

        self._btn_gen.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleGen)
        for btn in self._btn_blocks:
            btn.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleBlock)

        # self._sizer_properties.Clear(True)

        # self._sizer_properties.Add(self._sizer_btnsblocks, 1, wx.EXPAND)

        # # add the properties to the sizer
        # self._sizer_properties.Add(self._prop_gen._params.prop, 5, wx.EXPAND)
        # self._sizer_properties.Add(self._prop_block._params.prop, 5, wx.EXPAND)

        self._update_layout()

    def _get_togglestates(self):
        """ Get the toggle states of the buttons """

        return self._btn_gen.GetValue(), [btn.GetValue() for btn in self._btn_blocks] # True if toggled, False otherwise


    def _show_glob_properties(self):
        """ Show the general properties """

        self._btn_gen.SetValue(True)

        self._prop_gen.copy(self.sim.parameters)

        if self._prop_block._params.prop.IsShown():
            self._prop_gen._params.prop.Show()
            self._prop_block._params.prop.Hide()

        self._append_magnetic_grid_to_prop()

        self._txt_info.Clear()
        self._txt_info.AppendText(_('Global parameters are shown'))

        self._update_layout()

    def _set_default_background(self):
        """ Set the default background """

        self._btn_gen.SetBackgroundColour(wx.NullColour)

        for btn in self._btn_blocks:
            btn.SetBackgroundColour(wx.NullColour)

    def _set_color_background(self):
        """ Set the color background """

        self._set_default_background()

        toggle_gen, toggle_blocks = self._get_togglestates()

        if self._ref_block is None:
            return

        for btn, idx, toggled in zip(self._btn_blocks, range(self.nb_blocks), toggle_blocks):

            if toggled and idx != self._ref_block:

                color = wx.Colour(255, 0, 0) if self.sim.parameters.blocks[idx] != self.sim.parameters.blocks[self._ref_block] else wx.Colour(0, 255, 0)
                btn.SetBackgroundColour(color)

    def OnToggleGen(self, e:wx.EVT_TOGGLEBUTTON):
        """
        Toggle the global properties
        """

        toggle_gen, toggle_blocks = self._get_togglestates()

        if toggle_gen:
            # General is toggled --> untoggle all blocks
            logging.info(_('General is toggled --> untoggling blocks'))
            for btn in self._btn_blocks:
                btn.SetValue(False)

            self._show_glob_properties()

        elif any(toggle_blocks):
            # At least one block is toggled --> untoggle the general
            pass
        else:
            # No block is toggled --> toggle the general
            self._show_glob_properties()

        self._set_color_background()

    def OnToggleBlock(self, e:wx.EVT_TOGGLEBUTTON):
        """
        Toggle the properties of a block
        """

        toggle_gen, toggle_blocks = self._get_togglestates()

        if toggle_gen:
            logging.info(_('General is toggled --> untoggling it'))
            self._btn_gen.SetValue(False)

        if any(toggle_blocks):
            # At least one block is toggled --> untoggle the general

            nb = toggle_blocks.count(True)

            if nb == 1:
                # One block is toggled --> show its properties
                idx = toggle_blocks.index(True)
                logging.info(_(f'Block {idx} is toggled'))

                self._prop_block.copy(self.sim.parameters.blocks[idx])

                if self._prop_gen._params.prop.IsShown():
                    self._prop_block._params.prop.Show()
                    self._prop_gen._params.prop.Hide()

                self._txt_info.Clear()
                self._txt_info.AppendText(_(f'Block {idx+1} parameters are shown'))

                self._ref_block = idx

                self._append_geometry_block_to_prop(idx)

            else:
                # test is ref block is toggled
                if not toggle_blocks[self._ref_block]:
                    self._ref_block = toggle_blocks.index(True)
                    logging.info(_('Changing reference block to ') + str(self._ref_block+1))
                    self._prop_block.copy(self.sim.parameters.blocks[self._ref_block])


                # multiple blocks are toggled
                # --> Find the difference
                # The first one is the "reference"
                self._txt_info.Clear()
                chain = _('Multiple blocks are toggled')
                self._txt_info.AppendText(chain + '\n')
                self._txt_info.AppendText('-'*len(chain) + '\n\n')

                self._txt_info.AppendText(_('Differences between the blocks') + '\n')
                self._txt_info.AppendText(_('  - Reference block : ')  + str(self._ref_block+1) + '\n')

                idx_comp = [idx+1 for idx in range(self.nb_blocks) if idx != self._ref_block and toggle_blocks[idx]]
                self._txt_info.AppendText(_('  - Other blocks : ') + str(idx_comp) + '\n\n')

                others = [self.sim.parameters.blocks[idx] for idx in range(self.nb_blocks) if idx != self._ref_block and toggle_blocks[idx]]

                self._txt_info.AppendText(self._prop_block.diff_print(others))

                dx_dy = [(idx, self._dx_block(idx),self._dy_block(idx)) for idx in range(self.nb_blocks) if idx != self._ref_block and toggle_blocks[idx]]

                dx_ref = self._dx_block(self._ref_block)
                dy_ref = self._dy_block(self._ref_block)

                self._txt_info.AppendText('\n')

                for idx, dx, dy in dx_dy:
                    if dx != dx_ref or dy != dy_ref:
                        self._txt_info.AppendText(_(f'Block {idx+1} has different resolution)') + '\n')
                        self._txt_info.AppendText(_(f'  - dx : {dx} (ref : {dx_ref})') + '\n')
                        self._txt_info.AppendText(_(f'  - dy : {dy} (ref : {dy_ref})') + '\n\n')

        else:
            self._show_glob_properties()

        self._set_color_background()

        self._update_layout()

    def _append_magnetic_grid_to_prop(self):
        """ Append the magnetic grid to the properties """

        self._prop_gen._params.add_param(MAGN_GROUP_NAME,
                                         'Dx',
                                            0.,
                                            Type_Param.Float,
                                            _('Spatial resolution of the magnetic grid along X-axis'),
                                            whichdict='All'
                                            )
        self._prop_gen._params.add_param(MAGN_GROUP_NAME,
                                            'Dy',
                                            0.,
                                            Type_Param.Float,
                                            _('Spatial resolution of the magnetic grid along Y-axis'),
                                            whichdict='All'
                                            )

        self._prop_gen._params.add_param(MAGN_GROUP_NAME,
                                            'Ox',
                                            -99999.,
                                            Type_Param.Float,
                                            _('Origin of the magnetic grid along X-axis'),
                                            whichdict='All'
                                            )

        self._prop_gen._params.add_param(MAGN_GROUP_NAME,
                                            'Oy',
                                            -99999.,
                                            Type_Param.Float,
                                            _('Origin of the magnetic grid along Y-axis'),
                                            whichdict='All'
                                            )

        if self.sim.magnetic_grid is None:
            self.sim.set_magnetic_grid(1., 1., 0., 0.)

        self._prop_gen._params[(MAGN_GROUP_NAME, 'Dx')] = self.sim.magnetic_grid.dx
        self._prop_gen._params[(MAGN_GROUP_NAME, 'Dy')] = self.sim.magnetic_grid.dy

        self._prop_gen._params[(MAGN_GROUP_NAME, 'Ox')] = self.sim.magnetic_grid.origx
        self._prop_gen._params[(MAGN_GROUP_NAME, 'Oy')] = self.sim.magnetic_grid.origy

        self._prop_gen._params.Populate(sorted_groups=True)

    def _append_geometry_block_to_prop(self, idx:int):
        """ Append the geometry of the block to the properties """

        self._prop_block._params.add_param(GEOM_GROUP_NAME,
                                            _('Dx'),
                                            0.,
                                            Type_Param.Float,
                                            _('Spatial resolution of the block along X-axis'),
                                            whichdict='All'
                                            )
        self._prop_block._params.add_param(GEOM_GROUP_NAME,
                                            _('Dy'),
                                            0.,
                                            Type_Param.Float,
                                            _('Spatial resolution of the block along Y-axis'),
                                            whichdict='All'
                                            )

        self._prop_block._params.add_param(GEOM_GROUP_NAME,
                                            _('X min (info)'),
                                            -99999.,
                                            Type_Param.Float,
                                            _('Origin of the block along X-axis'),
                                            whichdict='All'
                                            )

        self._prop_block._params.add_param(GEOM_GROUP_NAME,
                                            _('Y min (info)'),
                                            -99999.,
                                            Type_Param.Float,
                                            _('Origin of the block along X-axis'),
                                            whichdict='All'
                                            )

        self._prop_block._params.add_param(GEOM_GROUP_NAME,
                                            _('X max (info)'),
                                            99999.,
                                            Type_Param.Float,
                                            _('End of the block along X-axis'),
                                            whichdict='All'
                                            )

        self._prop_block._params.add_param(GEOM_GROUP_NAME,
                                            _('Y max (info)'),
                                            99999.,
                                            Type_Param.Float,
                                            _('End of the block along X-axis'),
                                            whichdict='All'
                                            )


        self._prop_block._params.add_param(GEOM_GROUP_NAME,
                                            _('Associated polygon (info)'),
                                            '',
                                            Type_Param.String,
                                            _('Name of the polygon associated to the block'),
                                            whichdict='All'
                                            )

        self._prop_block._params[(GEOM_GROUP_NAME, _('Dx'))] = self._dx_block(idx)
        self._prop_block._params[(GEOM_GROUP_NAME, _('Dy'))] = self._dy_block(idx)
        self._prop_block._params[(GEOM_GROUP_NAME, _('X min (info)'))]= self.sim.bloc_description[idx+1].xmin
        self._prop_block._params[(GEOM_GROUP_NAME, _('Y min (info)'))]= self.sim.bloc_description[idx+1].ymin
        self._prop_block._params[(GEOM_GROUP_NAME, _('X max (info)'))]= self.sim.bloc_description[idx+1].xmax
        self._prop_block._params[(GEOM_GROUP_NAME, _('Y max (info)'))]= self.sim.bloc_description[idx+1].ymax
        self._prop_block._params[(GEOM_GROUP_NAME, _('Associated polygon (info)'))]= self.sim.bloc_description[idx+1].contour.myname

        self._prop_block._params.Populate(sorted_groups=True)

    def _apply_changes(self, e:wx.EVT_BUTTON):
        """
        Apply the changes to the parameters
        """

        toggle_gen, toggle_blocks = self._get_togglestates()

        if toggle_gen:
            self._prop_gen.apply_changes_to_memory()

            self.sim.parameters._set_debug_params(self._prop_gen._get_debug_params())
            self.sim.parameters._set_general_params(self._prop_gen._get_general_params())

            mag_dx = self._prop_gen._params[(MAGN_GROUP_NAME, 'Dx')]
            mag_dy = self._prop_gen._params[(MAGN_GROUP_NAME, 'Dy')]
            mag_ox = self._prop_gen._params[(MAGN_GROUP_NAME, 'Ox')]
            mag_oy = self._prop_gen._params[(MAGN_GROUP_NAME, 'Oy')]

            if mag_dx != self.sim.magnetic_grid.dx or mag_dy != self.sim.magnetic_grid.dy or mag_ox != self.sim.magnetic_grid.origx or mag_oy != self.sim.magnetic_grid.origy:

                dlg = wx.MessageDialog(None, _('Do you want to update the magnetic grid?'), _('Update magnetic grid'), wx.YES_NO)

                if dlg.ShowModal() == wx.ID_YES:

                    self.sim.set_magnetic_grid(mag_dx, mag_dy, mag_ox, mag_oy)

                dlg.Destroy()


        elif any(toggle_blocks):

            nb = toggle_blocks.count(True)

            if nb == 1:

                idx = self._ref_block

                dx = self._prop_gen._params[(GEOM_GROUP_NAME, _('Dx'))]
                dy = self._prop_gen._params[(GEOM_GROUP_NAME, _('Dy'))]

                self.sim.bloc_description[idx+1].set_dx_dy(dx, dy)

                self._prop_block.apply_changes_to_memory()

                self.sim.parameters.blocks[idx]._set_debug_params(self._prop_block._get_debug_params())
                self.sim.parameters.blocks[idx]._set_general_params(self._prop_block._get_general_params())

            else:

                dx = self._prop_gen._params[(GEOM_GROUP_NAME, _('Dx'))]
                dy = self._prop_gen._params[(GEOM_GROUP_NAME, _('Dy'))]

                self._prop_block.apply_changes_to_memory()

                force = self._check_force.GetValue()

                if not force:
                    logging.info(_('No force update - Apply to the reference block only'))

                    idx = self._ref_block
                    self.sim.parameters.blocks[idx]._set_debug_params(self._prop_block._get_debug_params())
                    self.sim.parameters.blocks[idx]._set_general_params(self._prop_block._get_general_params())

                    self.sim.bloc_description[idx+1].set_dx_dy(dx, dy)

                else:
                    groups = self._prop_block.gen_groups + self._prop_block.debug_groups
                    names = self._prop_block.gen_names + self._prop_block.debug_names

                    choices = ['{} - {}'.format(GEOM_GROUP_NAME, _('Dx')), '{} - {}'.format(GEOM_GROUP_NAME, _('Dy'))] + [f'{group} - {name}' for group, name in zip(groups, names) if NOT_USED not in group]

                    dlg = wx.MultiChoiceDialog(self,
                                               _('Which parameters should be updated in all blocks?'),
                                               _('Parameters'),
                                                choices = choices,
                                                style = wx.CHOICEDLG_STYLE | wx.OK | wx.CANCEL)

                    if dlg.ShowModal() == wx.ID_OK:
                        selections = dlg.GetSelections()
                        for sel in selections:
                            group, name = choices[sel].split(' - ')

                            if group == GEOM_GROUP_NAME:
                                if name == _('Dx'):
                                    for idx in range(self.nb_blocks):
                                        if toggle_blocks[idx]:
                                            self.sim.bloc_description.my_blocks[idx+1].dx = dx
                                elif name == _('Dy'):
                                    for idx in range(self.nb_blocks):
                                        if toggle_blocks[idx]:
                                            self.sim.bloc_description.my_blocks[idx+1].dy = dy
                            else:

                                for idx in range(self.nb_blocks):
                                    if toggle_blocks[idx]:
                                        # idx+1 because the blocks are 1-indexed in the __getitem__ method
                                        self.sim[idx+1].set_parameter(group, name, self._prop_block._params[(group, name)])
                    dlg.Destroy()

            self._prop_block._params.Populate(sorted_groups=True)


        self._txt_info.Clear()
        self._txt_info.AppendText(_('Changes applied'))


    def extend_bed_elevation(self):
        """
        Extension du modèle topographique
        """
        if not self.wx_exists:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        dlg = wx.MessageDialog(self,_('Do you want to autocomplete elevation from external file?'),style=wx.YES_NO|wx.YES_DEFAULT)
        ret=dlg.ShowModal()
        dlg.Destroy()

        if ret == wx.ID_NO:
            logging.info(_('Nothing to do !'))
            return

        if not self.top.loaded:
            self.top.check_plot()
            self.top.copy_mask_log(self.curmask)
            self.top.loaded=True

        filterArray = "bin (*.bin)|*.bin|all (*.*)|*.*"
        fdlg = wx.FileDialog(self, "Choose file", wildcard=filterArray, style=wx.FD_OPEN)
        if fdlg.ShowModal() != wx.ID_OK:
            fdlg.Destroy()
            return

        filename = fdlg.GetPath()
        fdlg.Destroy()

        logging.info(_('Importing data from file'))
        newtop = WolfArray(fname=filename,mapviewer=self.mapviewer)

        logging.info(_('Finding nodes -- plotting disabled for speed'))
        self.top.mngselection.hideselection = True
        self.top.mngselection.condition_select(2,0., usemask=True)

        if len(self.top.mngselection.myselection)>0:
            newtop.mngselection.myselection = self.top.mngselection.myselection
            newtop.mngselection.hideselection = True
            newtop.mngselection.update_nb_nodes_selection()

            logging.info(_('Copying values'))
            z = newtop.mngselection.get_values_sel()
            logging.info(_('Pasting values'))
            self.top.set_values_sel(self.top.mngselection.myselection, z, False)

        self.top.mngselection.hideselection = False
        self.top.mngselection.myselection=[]
        self.top.copy_mask_log(self.curmask)
        self.top.reset_plot()

        logging.info('')
        logging.info(_('Do not forget to save your changes to files !'))
        logging.info('')

    def extend_freesurface_elevation(self,selection:list):
        """
        Extension des Conditions Initiales
        """

        logging.info(_('Loading necessary values'))
        listarrays=[self.top,self.hbin,self.zbin]
        for curarray in listarrays:
            if not curarray.loaded:
                logging.info('  ' + curarray.idx)
                curarray.check_plot()
                curarray.copy_mask_log(self.curmask)
                curarray.loaded=True
                curarray.mngselection.hideselection = True

        logging.info(_('Hiding positive values'))
        self.hbin.mngselection.myselection = selection.copy()
        self.hbin.mngselection.condition_select(4,0., usemask=True)
        nullvalues = self.hbin.mngselection.myselection.copy()

        nb = len(nullvalues)
        if nb==0:
            logging.info(_('Nothing to do -- exit !'))
            return

        logging.info('  ' + str(len(nullvalues)) + _(' to interpolate'))

        logging.info(_('Hiding null values'))
        self.hbin.mngselection.myselection = selection.copy()
        self.hbin.mngselection.condition_select(2,0., usemask=True)
        nb = len(self.hbin.mngselection.myselection)

        logging.info('  ' + str(nb) + _(' source nodes'))
        if nb<2:
            logging.info(_('Not enough source nodes -- exit !'))
            return

        logging.info(_('Copying selection to zbin'))
        self.zbin.mngselection.myselection = self.hbin.mngselection.myselection.copy()
        z = self.zbin.mngselection.get_values_sel()
        xy = np.asarray(self.zbin.mngselection.myselection)

        logging.info(_('Interpolating free surface'))
        self.zbin.mngselection.myselection = nullvalues.copy()
        self.zbin.interpolate_on_cloud(xy,z,'nearest')

        logging.info(_('Filtering negative values'))
        self.hbin.array = self.zbin.array - self.top.array
        self.hbin.array[np.where(self.hbin.array<0.)]=0.

        self.zbin.array = self.hbin.array+self.top.array

        logging.info(_('Refreshing mask and plot'))
        for curarray in listarrays:
            curarray.copy_mask_log(self.curmask)
            curarray.mngselection.myselection=[]
            curarray.mngselection.hideselection=False
            curarray.reset_plot()

        logging.info('')
        logging.info(_('Do not forget to save your changes to files !'))
        logging.info('')

    def extend_roughness(self,selection:list):
        """
        Extension du frottement
        """
        if not self.wx_exists:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        # La sélection contient tous les points utiles
        sel=selection.copy()

        dlg = wx.TextEntryDialog(None,_('Which value should be replace by nearest one?'),_('Value'),value='0.04')
        ret = dlg.ShowModal()

        if ret == wx.ID_CANCEL:
            dlg.Destroy()
            return

        oldval = float(dlg.GetValue())
        eps = oldval/1000.
        dlg.Destroy()

        logging.info(_('Loading necessary values'))
        listarrays=[self.frot]
        for curarray in listarrays:
            if not curarray.loaded:
                logging.info('  ' + curarray.idx)
                curarray.check_plot()
                curarray.copy_mask_log(self.curmask)
                curarray.loaded=True
                curarray.mngselection.hideselection = True

        logging.info(_('Selecting old values'))
        self.frot.mngselection.hideselection = True
        self.frot.mngselection.myselection = sel.copy()

        # On cherche les points à interpoler --> on resélectionne les mailles en dehors de l'intervalle
        # La double sélection supprime la maille de la zone déjà sélectionnée
        self.frot.mngselection.condition_select('<>',oldval-eps,oldval+eps, usemask=True)
        nullvalues = self.frot.mngselection.myselection.copy()

        nb = len(nullvalues)
        if nb==0:
            logging.info(_('Nothing to do -- exit !'))
            return

        logging.info('  ' + str(len(nullvalues)) + _(' to interpolate'))

        logging.info(_('Hiding old values'))
        self.frot.mngselection.myselection = sel.copy()

        # On cherche les points depuis où interpoler --> on resélectionne les mailles dans l'intervalle
        # La double sélection supprime la maille de la zone déjà sélectionnée
        self.frot.mngselection.condition_select('>=<=',oldval-eps,oldval+eps, usemask=True)
        nb = len(self.frot.mngselection.myselection)

        logging.info('  ' + str(nb) + _(' source nodes'))
        if nb<2:
            logging.info(_('Not enough source nodes -- exit !'))
            return

        logging.info(_('Interpolating NN'))
        # Récupération des z et xy des mailles actuellement sélectionnées
        z = self.frot.mngselection.get_values_sel()
        xy = np.asarray(self.frot.mngselection.myselection)
        # Recopiage des mailles à interpoler depuis le stockage temporaire
        self.frot.mngselection.myselection = nullvalues
        # Interpolation par voisin le plus proche
        self.frot.interpolate_on_cloud(xy,z,'nearest')

        logging.info(_('Refreshing mask and plot'))
        for curarray in listarrays:
            curarray.copy_mask_log(self.curmask)
            curarray.mngselection.myselection=[]
            curarray.mngselection.hideselection = False
            curarray.mngselection.update_nb_nodes_selection()
            curarray.reset_plot()

        logging.info('')
        logging.info(_('Do not forget to save your changes to files !'))
        logging.info('')




    def set_type_ic(self, which:Literal[1,2,3]=2, dialog:bool=True):
        """ Définition du type de conditions initiales """

        if (not self.wx_exists) and dialog:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        if dialog and self.wx_exists:
            dlg = wx.SingleChoiceDialog(None,_('How do you want to read initial conditions ?'),_('Reading mode'),choices=[_('Text'),_('Binary mono-block'),_('Binary multi-blocks')])
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                dlg.Destroy()
                return

            which = dlg.GetSelection()+1
            dlg.Destroy()

        if which<1 or which>3:
            return

        self.sim.parameters._initial_cond_reading_mode = which
        self.sim.parameters.write_file()


    def replace_external_contour(self, newvec:vector, interior:bool):
        """ Remplacement du contour externe """

        logging.info(_('Copying extrenal contour'))

        logging.info(_('   ... in .bloc'))
        ext_zone:zone
        ext_zone = self.sim.bloc_description.my_vec_blocks.myzones[0]
        ext_zone.myvectors[0] = newvec

        logging.info(_('   ... in xy --> Fortran will update this file after internal meshing process'))
        self.xyzones.myzones[0].myvectors[0] = newvec

        self.sim.bloc_description.my_vec_blocks.reset_listogl()
        self.sim.bloc_description.my_vec_blocks.prep_listogl()

        logging.info(_('Updating .bloc file'))
        self.sim.bloc_description.interior=interior
        self.sim.bloc_description.my_vec_blocks.find_minmax(True)
        self.sim.bloc_description.write_file()


    def transfer_ic(self,vector):
        """
        Transfert de conditions initiales
        """

        if not self.wx_exists:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        dlg = wx.DirDialog(None,_('Choose directory containing destination model'),style=wx.DD_DIR_MUST_EXIST)
        ret = dlg.ShowModal()

        if ret==wx.ID_CANCEL:
            dlg.Destroy()
            return

        dstdir = dlg.GetPath()
        dlg.Destroy()

        logging.info(_('Reading destination model'))
        dstmodel = Wolf2DModel(dir=dstdir,splash=False)

        logging.info(_('Reading data sources'))
        srcarrays=[self.top,self.hbin,self.qxbin,self.qybin]
        for loc in srcarrays:
            if not loc.loaded:
                loc.read_data()
                loc.copy_mask_log(self.curmask)

        logging.info(_('Reading data destination'))
        destarrays=[dstmodel.top,dstmodel.hbin,dstmodel.qxbin,dstmodel.qybin]
        for loc in destarrays:
            if not loc.loaded:
                loc.read_data()
                loc.copy_mask_log(dstmodel.curmask)

        logging.info(_('Copying data'))
        for src,dst in zip(srcarrays,destarrays):
            logging.info('  '+src.idx)

            vals,xy = src.get_values_insidepoly(vector,getxy=True)
            dst.set_values_sel(xy,vals)

        logging.info(_('Writing data on disk'))
        for loc in destarrays:
            loc.write_all()

        logging.info(_('Finished !'))

        pass



    # **********
    # DEPRECATED
    # **********

    @property
    def is_multiblock(self):
        """ Deprecated, use the property from the infiltration object """

        return self.sim.is_multiblock

    @property
    def nb_blocks(self):
        """ Deprecated, use the property from the infiltration object """

        return self.sim.nb_blocks

    def help_files(self):
        """
        Aide sur les fichiers

        Deprecated, use the method from the infiltration object
        """

        return self.sim.help_files()


    def check_infiltration(self):
        """ Vérification des zones d'infiltration

        Deprecated, use the method from the infiltration object
        """

        return self.sim.check_infiltration()


    def copy2gpu(self, dirout:str=''):
        """
        Copie des matrices pour le code GPU

        Deprecated, use the method from the simulation object
        """

        return self.sim.copy2gpu(dirout)

    def write_bloc_file(self):
        """ Mise à jour du fichier de blocs """

        logging.info(_('Updating .bloc file'))
        self.sim.bloc_description.modify_extent()
        self.sim.bloc_description.write_file()


    def get_header_MB(self, abs=False):
        """Renvoi d'un header avec les infos multi-blocs

        :param abs: If True, the header will be absolute, if False, it will be relative
        :type abs: bool

        :return: header_wolf
        """

        return self.sim.get_header_MB(abs)

    def get_header(self, abs=False):
        """
        Renvoi d'un header de matrice "fine" non MB

        :param abs: If True, the header will be absolute, if False, it will be relative
        :type abs: bool

        :return: header_wolf
        """

        self.sim.get_header(abs)

    def read_fine_array(self, which:str=''):
        """
        Lecture d'une matrice fine

        :param which: suffixe du fichier
        :type which: str
        """

        return self.sim.read_fine_array(which)

    def read_MB_array(self, which:str=''):
        """
        Lecture d'une matrice MB

        :param which: suffixe du fichier
        :type which: str
        """

        return self.sim.read_MB_array(which)

    def read_fine_nap(self) -> np.ndarray:
        """Lecture de la matrice nap sur le maillage fin"""

        return self.sim.read_fine_array('.napbin')

class Wolf2DGPUModel(GenMapManager):

    def __init__(self, *args, dir:str='',  **kw):
        """
        :param dir: directory containing the simulation

        self.wx_exists : If True, then this model will connect itself to the GUI.
                    If False, the model will stand alone (so you can use it outside
                    of the GUI).
        """

        super(Wolf2DGPUModel, self).__init__(*args, **kw)

        self._wp = None
        self.dir = ''
        self._prop_frame = None
        self._sim:Sim_2D_GPU = None

        # Liste des objets à ajouter au GUI
        self.arrays={}

        # Gauging stations - SPW
        self.SPWstations    = SPWMIGaugingStations()
        self.DCENNstations  = SPWDCENNGaugingStations()

        if dir != '':
            # Either a directory or a file "/_/_/_/dir/simul" for example.

            assert exists(dir) or dirname(dir), f"'{dir}' does not exists"

        if dir=='':
            if self.wx_exists:
                # Propose a dialog window to choose the directory

                idir=wx.DirDialog(None,"Choose Directory -- Abort for a new model from scratch", style=wx.DD_DEFAULT_STYLE)
                ret = idir.ShowModal()

                dir =Path(idir.GetPath())
                if 'simul_gpu_results' in dir.name:
                    dir = dir.parent

                if ret == wx.ID_CANCEL or not (dir / 'parameters.json').exists():
                    self.setup_mapviewer(title='Blank 2D model',wolfparent=self)
                    self.mapviewer.findminmax(True)
                    self.mapviewer.Autoscale(False)
                    self.mapviewer.menu_sim2DGPU()
                    if ret == wx.ID_CANCEL:
                        self._sim = Sim_2D_GPU()
                    else:
                        self._sim = Sim_2D_GPU(idir.GetPath())
                    self.show_properties()
                    if self.wx_exists:
                        self.mapviewer.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
                        self.mapviewer.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')
                    idir.Destroy()
                    return
            else:
                return

            self.dir = dir
            idir.Destroy()
        else:
            self.dir=Path(normpath(dir))

            if 'simul_gpu_results' in self.dir:
                self.dir = self.dir.parent

        try:
            logging.info(_(f'Simulation directory is : {self.dir}'))
            logging.info(_('Creating GUI'))

            self._sim = Sim_2D_GPU(self.dir)

            if self.wx_exists:

                self.setup_mapviewer(title='2D GPU model : '+ str(self.dir), wolfparent=self)
                self.show_properties()

                if self.sim._sim is not None:
                    self._btn_fromarray.Enable(False)
                    self._btn_fromfootprint.Enable(False)
                    self._btn_fromvector.Enable(False)
                    self._btn_magnetic_grid.Enable(False)

                    self._btn_add_arrays2viewer.SetLabel(_('Reload arrays'))

            logging.info(_('Treating arrays'))

            self._add_arrays_to_mapviewer()
            self._add_vectors_to_mapviewer()

            logging.info(_('Zooming'))
            self.mapviewer.findminmax(True)
            self.mapviewer.Autoscale(False)

            self.show_properties()

            if self.wx_exists:
                self.mapviewer.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
                self.mapviewer.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

                logging.info(_('Adapting menu'))
                self.mapviewer.menu_sim2DGPU()

            logging.info(_('Verifying files'))
            self._sim.verify_files()

            logging.info(_('Model loaded !!'))

        except Exception as ex:
            logging.error(str(ex), exc_info=True)

    @property
    def sim(self):
        """ Alias """

        return self._sim

    def _add_arrays_to_mapviewer(self, force_reload:bool=False):
        """
        Add the arrays to the mapviewer
        """

        logging.info(_('Adding arrays to mapviewer'))

        arrays_in_viewer = self.mapviewer.get_list_objects(draw_type.ARRAYS, checked_state=None)

        if force_reload:
            self._sim.reload_all()
            for cur in self.arrays.values():

                if cur.idx == 'water surface elevation [m]':
                    ## Force to recompute the water surface elevation
                    cur.array.data[:,:] = self.arrays['bathymetry'].array.data[:,:] + self.arrays['h'].array.data[:,:]
                    cur.array.mask[:,:] = self.arrays['bathymetry'].array.mask[:,:]

                cur.reset_plot()
            # self.mapviewer.Refresh()
        else:

            self.arrays = self._sim.get_arraysasdict()

            for array in self.arrays.values():
                if array.loaded:
                    if array.idx not in [cur.idx for cur in arrays_in_viewer]:
                        self.mapviewer.add_object(which='array', newobj=array, ToCheck=False, id= array.idx)


    def _add_vectors_to_mapviewer(self):
        """
        Add the vectors to the mapviewer
        """

        logging.info(_('Adding vectors to mapviewer'))
        pass

    def show_properties_sim(self):
        """
        Show the properties of the model
        """

        logging.info(_('Opening parameters for simulation {}'.format(self.dir)))

        self._wp:Wolf_Param
        self._wp = self._sim.sim.to_wolfparam()
        self._wp.show_in_active_if_default = True
        self._wp.set_callbacks(self._callbackwp, self._callbackwp_destroy)
        self._wp._set_gui(title='Parameters for simulation {}'.format(self.dir), toShow=False)
        self._wp.hide_selected_buttons()
        self._wp.Show()

    def _callbackwp(self):
        """ Callback for wolfparam """

        if self._wp is not None:
            try:
                self._sim.sim.from_wolfparam(self._wp)
                self._sim.sim._save_json()
            except Exception as e:
                self._wp = None
                logging.debug(_('Error while saving parameters for simulation {}'.format(self._sim.sim.path.name)))
                logging.debug(str(e))

    def _callbackwp_destroy(self):
        """ Callback for wolfparam """

        if self._wp is not None:
            try:
                if self._wp.Shown:
                    self._sim.sim.from_wolfparam(self._wp)
                    self._sim.sim._save_json()
            except Exception as e:
                self._wp = None
                logging.debug(_('Error while saving parameters for simulation {}'.format(self._sim.sim.path.name)))
                logging.debug(str(e))

    def _set_bc(self, e:wx.EVT_BUTTON):
        """ Set the boundary conditions """

        from .mesh2d.bc_manager import BcManager, choose_bc_type

        if self._sim is None:
            logging.error(_('No simulation found'))
            return

        if 'nap' not in self.arrays:
            logging.error(_('No nap array found'))
            return

        if self.mapviewer.active_bc is None:

            newbc = BcManager(self,
                            linked_array=self.arrays['nap'],
                            version = 'gpu',
                            DestroyAtClosing=True,
                            Callback=self.mapviewer.pop_boundary_manager,
                            mapviewer=self.mapviewer,
                            wolfparent = self)


            self.mapviewer.mybc.append(newbc)

            self.mapviewer.active_bc = newbc

            self.mapviewer.Refresh()

        else:
            self.mapviewer.active_bc.Show()
            # self.mapviewer.active_bc.

    def _set_infiltration(self, e:wx.EVT_BUTTON):

        inf_frame = Wolf2DInfiltration(self._sim)
        inf_frame.Show()

    def add_boundary_condition(self, i: int, j: int, bc_type:BCType_2D_GPU,  bc_value: float, border:Direction):
        """ alias """
        try:
            from wolfgpu.simple_simulation import BoundaryConditionsTypes, Direction as ss_direction
        except ImportError:
            logging.error(_('Cannot import BoundaryConditionsTypes and Direction from wolfgpu.simple_simulation'))

        def convert_dirhece2gpu(direction:Direction) -> ss_direction:
            """ Convert the boundary conditions from HECE to GPU """
            if direction == Direction.LEFT:
                return ss_direction.LEFT
            if direction == Direction.BOTTOM:
                return ss_direction.BOTTOM

        def convert_bchece2gpu(bctype:BCType_2D_GPU) -> BoundaryConditionsTypes:
            """ Convert the boundary conditions from HECE to GPU """
            if bctype == BCType_2D_GPU.FROUDE_NORMAL:
                return BoundaryConditionsTypes.FROUDE_NORMAL
            if bctype == BCType_2D_GPU.HMOD:
                return BoundaryConditionsTypes.HMOD
            if bctype == BCType_2D_GPU.NONE:
                return BoundaryConditionsTypes.NONE
            if bctype == BCType_2D_GPU.QX:
                return BoundaryConditionsTypes.QX
            if bctype == BCType_2D_GPU.QY:
                return BoundaryConditionsTypes.QY

        self._sim.sim.add_boundary_condition(i, j, convert_bchece2gpu(bc_type), bc_value, convert_dirhece2gpu(border))


    def reset_boundary_conditions(self):
        """ Reset the boundary conditions """

        self._sim.sim.clear_boundary_conditions()


    def _check_errors(self, e:wx.EVT_BUTTON):
        """ Check the errors in the model """

        ret_warnings = self._sim.sim.check_warnings()
        ret_errors = self._sim.sim.check_errors()
        ret_wolfgpu = self._sim.check_environment()

        ret_infil=[]
        nmax = ma.max(self.arrays['infiltration_zones'].array)

        if nmax == 99999:
            logging.warning(_('Maximum index in infiltration zones is 99999. It seems to be a bad null value - Check the array !'))
            logging.warning(_('Replacing 99999 by 0'))
            self.arrays['infiltration_zones'].array[self.arrays['infiltration_zones'].array == 99999] = 0
            nmax = ma.max(self.arrays['infiltration_zones'].array)
            logging.info(_('New maximum index in infiltration zones is {}'.format(nmax)))

        nmin = ma.min(self.arrays['infiltration_zones'].array[self.arrays['infiltration_zones'].array > 0])
        l = ma.unique(self.arrays['infiltration_zones'].array[self.arrays['infiltration_zones'].array > 0]).tolist()
        chronos = self.sim.sim.infiltrations_chronology

        if nmin !=1:
            ret_infil.append(_('Infiltration zones index must be strictly positive. the first one is 1.'))
        if nmax != len(l):
            ret_infil.append(_('Infiltration zones must be between 1 and N'))
            ret_infil.append(_('N is the number of infiltration zones'))
            ret_infil.append(_('You have {} zones in the arrays and the maximum index in the array is {}'.format(len(l), nmax)))
        if len(chronos[0][1]) != len(l):
            ret_infil.append(_('Infiltration zones must be between 1 and N'))
            ret_infil.append(_('N is the number of infiltration zones'))
            ret_infil.append(_('You have {} zones in the chronology and the maximum index in the array is {}'.format(len(chronos[0][1]), nmax)))
            ret_infil.append(_('You have {} different zones in the array and the maximum index in the array is {}'.format(len(l), nmax)))
            ret_infil.append(_('Check the chronology file and the array !'))


        if ret_warnings is None:
            ret_warnings = []
        if ret_errors is None:
            ret_errors = []

        self._txt_info.Clear()

        if len(ret_wolfgpu) > 0:
            self.append_infos(_('Environment :\n'))
            self.append_infos('\n'.join(ret_wolfgpu))
            self.append_infos('\n')

        if len(ret_warnings) + len(ret_errors) + len(ret_infil) == 0:
            self.append_infos(_('No errors found'))
            self._enable_disable_buttons(False)
            self._btn_checkerrors.SetBackgroundColour(wx.Colour(0, 255, 0))
            return

        if len(ret_warnings) > 0:
            self.append_infos(_('\n**WARNINGS** found :\n\n'))
            self.append_infos('\n'.join(ret_warnings))
            self._btn_checkerrors.SetBackgroundColour(wx.Colour(255, 255, 0))
            self._enable_disable_buttons(False)

        if len(ret_errors) > 0:
            self.append_infos(_('\n**ERRORS** found :\n\n'))
            self.append_infos('\n'.join(ret_errors))
            self._btn_checkerrors.SetBackgroundColour(wx.Colour(255, 0, 0))
            self._enable_disable_buttons(True)

        if len(ret_infil) > 0:
            self.append_infos(_('\n**ERRORS** in Infiltration zones :\n\n'))
            self.append_infos('\n'.join(ret_infil))
            self._btn_checkerrors.SetBackgroundColour(wx.Colour(255, 0, 0))
            self._enable_disable_buttons(True)

    def _enable_disable_buttons(self, errors:bool = False):
        """ Enable or isable buttons"""

        self._btn_write.Enable(not errors)
        self._btn_run.Enable(not errors)

        self._btn_results.Enable((Path(self.dir) / 'simul_gpu_results').exists())
        self._btn_rs2ic.Enable((Path(self.dir) / 'simul_gpu_results').exists())
        self._btn_copy2newdir.Enable((Path(self.dir) / 'simul_gpu_results').exists())


    def _write_files(self, e:wx.EVT_BUTTON):
        """ Write the files to disk """

        if self.dir == '':
            dlg = wx.DirDialog(None, _('Choose directory to save the simulation'), style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_CANCEL:
                dlg.Destroy()
                return

            self.dir = dlg.GetPath()
            dlg.Destroy()

        curdir = Path(self.dir)
        if not curdir.exists():
            logging.error(_('Directory does not exist'))
            return

        if self.mapviewer.active_bc is not None:
            # Transfer boundary conditions
            self.mapviewer.active_bc.send_to_wolfparent()

        self._sim.sim.save(Path(self.dir))


    def _run(self, e:wx.EVT_BUTTON):
        """ Run the simulation """

        dlg = wx.MessageDialog(None, _('Do you want to run the simulation in a separate process ?'), _('Run simulation'), wx.YES_NO)
        if dlg.ShowModal() == wx.ID_NO:
            dlg.Destroy()
            return

        dlg.Destroy()


        dlg = wx.MessageDialog(None, _("Do you want to limit dryup loops?"), _("Dryup loops"), wx.YES_NO)
        ret = dlg.ShowModal()
        if ret == wx.ID_YES:
            nbloops = wx.GetNumberFromUser(_("Number of dryup loops"), _("Dryup loops"), _("Dryup loops"), 2, 0, 1000)
        else:
            nbloops = -1

        dlg.Destroy()

        # Run wolfgpu in a separate command line
        self._sim.run(limit_dryuploops=nbloops)


    def _results(self, e:wx.EVT_BUTTON):
        """ Display the results """

        self.mapviewer.add_object(which='res2d_gpu',
                                  filename=str(self.dir),
                                  id=Path(self.dir).name)
        self.mapviewer.menu_wolf2d()
        self.mapviewer.Refresh()

    def _results2ic(self, e:wx.EVT_BUTTON):
        """ Choose one result as initial conditions """

        from .wolfresults_2D import Wolfresults_2D
        from .Results2DGPU import wolfres2DGPU
        from datetime import timedelta

        myres = wolfres2DGPU(self.dir, plotted=False)

        times, steps = myres.get_times_steps()

        times_hms = [timedelta(seconds=int(curtime), milliseconds=int(curtime-int(curtime))*1000) for curtime in times]

        choices = [_('Last one')] + ['{:3f} [s] - {} [h:m:s] - {} [step index]'.format(curtime, curtimehms, curstep) for curtime, curtimehms, curstep in zip(times, times_hms, steps)]

        dlg = wx.SingleChoiceDialog(None, _('Choose the time step to set as initial conditions'), _('Results as IC'), choices)

        ret = dlg.ShowModal()

        if ret == wx.ID_CANCEL:
            logging.info(_('Aborting - No time step selected'))
            return

        idx = dlg.GetSelection() - 1 # -1 because of the first choice is the last one and it is the convention used in the code

        dlg.Destroy()

        myres.set_hqxqy_as_initial_conditions(idx)

        # update the arrays
        self._add_arrays_to_mapviewer(force_reload=True)

    def _wizard(self, e:wx.EVT_BUTTON):
        """ Launch the wizard """

        from wx.adv import Wizard, WizardPageSimple

        wizard_text = self._sim.get_wizard_text()

        self.wizard = Wizard(None, -1, _('Wizard Multiblocks simulation'))

        self.wizard.SetPageSize((400, 300))

        self.wiz_pages:list[WizardPageSimple] = []

        for curpage in wizard_text:
            self.wiz_pages.append(WizardPageSimple(self.wizard))
            self.wiz_pages[-1].SetBackgroundColour(wx.Colour(255, 255, 255))
            self.wiz_pages[-1].SetSizer(wx.BoxSizer(wx.VERTICAL))

        for idx, curpage in enumerate(wizard_text):
            for curstep in curpage:
                self.wiz_pages[idx].GetSizer().Add(wx.StaticText(self.wiz_pages[idx], -1, curstep), 0, wx.ALIGN_LEFT)

        for i in range(len(self.wiz_pages)-1):
            self.wiz_pages[i].Chain(self.wiz_pages[i+1])


        ret = self.wizard.RunWizard(self.wiz_pages[0])

        if ret:
            logging.info(_('Wizard finished'))
        else:
            logging.warning(_('Wizard cancelled - Are you sure ?'))

    def _add_arrays2viewer(self, e:wx.EVT_BUTTON):
        """ Create the fine arrays """

        self._add_arrays_to_mapviewer(force_reload= self._btn_add_arrays2viewer.GetLabel() == _('Reload arrays'))

    def _apply_mask(self, e:wx.EVT_BUTTON):
        """ Apply the mask """

        if self.mapviewer.active_array is None:
            logging.error(_('No active array defined - Please select an array'))
            return

        if self.mapviewer.active_array not in self.arrays.values():
            logging.error(_("Active array not found in the list of model's arrays"))
            return

        keys = self.sim._get_description_arrays()
        self._sim.mimic_mask(self.mapviewer.active_array, [cur for key,cur in zip(keys,self.arrays.values()) if key != self.mapviewer.active_array.idx])
        for cur in self.arrays.values():
            cur.reset_plot()

        self.mapviewer.Refresh()

    def _create_from_vector(self, e:wx.EVT_BUTTON):
        """ Create a simulation from a vector """

        if self._sim.sim is not None:
            dlg = wx.MessageDialog(None, _('Do you want to erase the current simulation ?'), _('Erase simulation'), wx.YES_NO)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return

            dlg.Destroy()
            self._sim.sim = None

        if self.mapviewer.active_vector is None:
            logging.error(_('No active vector defined - Please select or create a vector/polygon as external border'))
            return

        dlg = wx.TextEntryDialog(None, _('Size/Spatial resolution'), _('Spatial resolution'), 'dx, dy')
        if dlg.ShowModal() == wx.ID_OK:

            try:
                dx, dy = dlg.GetValue().split(',')
                self._sim.create_from_vector(self.mapviewer.active_vector, float(dx), float(dy))
                self.update_wp()
                self.clear_infos()
                self.append_infos(str(self._sim.sim))
            except Exception as e:
                logging.error(_('Invalid mesh sizes or error {e}'))

        dlg.Destroy()

        self._btn_fromvector.Enable(False)
        self._btn_fromfootprint.Enable(False)
        self._btn_fromarray.Enable(False)

    def _create_from_array(self, e:wx.EVT_BUTTON):
        """ Create a simulation from an array """

        if self._sim.sim is not None:
            dlg = wx.MessageDialog(None, _('Do you want to erase the current simulation ?'), _('Erase simulation'), wx.YES_NO)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return

            dlg.Destroy()
            self._sim.sim = None

        if self.mapviewer.active_array is None:
            logging.error(_('No active array defined - Please select or create an array as external border'))
            return

        self._sim.create_from_array(self.mapviewer.active_array)

        dlg = wx.MessageDialog(None, _('Do you want to use the data from the array as bathymetry?'), _('Use bathymetry'), wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self._sim.sim._bathymetry[:,:] = self.mapviewer.active_array.array[:,:] # copy the array

        dlg.Destroy()

        self.update_wp()
        self.clear_infos()
        self.append_infos(str(self._sim.sim))

        self._btn_fromvector.Enable(False)
        self._btn_fromfootprint.Enable(False)
        self._btn_fromarray.Enable(False)

    def _create_from_footprint(self, e:wx.EVT_BUTTON):
        """ Create a simulation from a footprint """

        if self._sim.sim is not None:
            dlg = wx.MessageDialog(None, _('Do you want to erase the current simulation ?'), _('Erase simulation'), wx.YES_NO)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return

            dlg.Destroy()
            self._sim.sim = None

        dlg = wx.TextEntryDialog(None, _('Footprint'), _('Footprint'), 'ox, oy, nbx, nby, dx, dy')

        if dlg.ShowModal() == wx.ID_OK:
            try:
                ox, oy, nbx, nby, dx, dy = dlg.GetValue().split(',')

                newhead = header_wolf()
                newhead.nbx = int(nbx)
                newhead.nby = int(nby)
                newhead.dx = float(dx)
                newhead.dy = float(dy)
                newhead.origx = float(ox)
                newhead.origy = float(oy)

                self._sim.create_from_header(newhead)
                self.update_wp()
                self.clear_infos()
                self.append_infos(str(self._sim.sim))

            except:
                logging.error(_('Invalid footprint'))

        dlg.Destroy()

        self._btn_fromvector.Enable(False)
        self._btn_fromfootprint.Enable(False)
        self._btn_fromarray.Enable(False)


    def _set_magnetic_grid(self, e:wx.EVT_BUTTON):
        """ Set the magnetic grid """

        dlg = wx.TextEntryDialog(None, _('Magnetic grid'), _('Magnetic grid'), 'ox, oy, dx, dy')

        if dlg.ShowModal() == wx.ID_OK:
            try:
                ox, oy, dx, dy = dlg.GetValue().split(',')
                self._sim.set_magnetic_grid(float(dx), float(dy), float(ox), float(oy))
                self.update_wp()
            except:
                logging.error(_('Invalid magnetic grid'))

        dlg.Destroy()

    def _choose_resolution(self, e:wx.EVT_BUTTON):
        """ Choose the fine resolution """

        dlg = wx.TextEntryDialog(None, _('Choose the fine resolution'), _('Fine resolution'), 'dx, dy')

        if dlg.ShowModal() == wx.ID_OK:
            try:
                dx, dy = dlg.GetValue().split(',')

                try:
                    floatdx = float(dx)
                    floatdy = float(dy)
                except:
                    logging.error(_('Invalid fine resolution'))
                    return

                self._sim.set_mesh_size(floatdx, floatdy)
            except:
                logging.error(_('Invalid fine resolution'))

        dlg.Destroy()

    def _copy2dir(self, e:wx.EVT_BUTTON):
        """ Copy the simulation to another directory """

        dlg = wx.DirDialog(None, _('Choose the destination directory'))

        if dlg.ShowModal() == wx.ID_OK:
            newdir = dlg.GetPath()
            self._sim.copy2dir(newdir)

        dlg.Destroy()

    def _apply_changes(self, e:wx.EVT_BUTTON):
        """ Apply the changes """

        if self._wp is not None:
            self._wp.apply_changes_to_memory()
            self._callbackwp()

    def show_properties(self):
        """
        Show the properties of the model
        """

        if self.wx_exists:

            if self._prop_frame is not None:
                self._prop_frame.CenterOnScreen()
                self._prop_frame.Iconize(False)
                self._prop_frame.Show()
                return

            # Création d'un wx Frame pour les paramètres
            self._prop_frame = wx.Frame(self,
                                        title=_('Parameters') + str(self.dir),
                                        size=(650, 800),
                                        style = wx.DEFAULT_FRAME_STYLE)

            # add a panel
            self._panel = wx.Panel(self._prop_frame)

            # Set sizers
            #
            # The panel is decomposed in three parts:
            # - List of toogle buttons + properties
            # - Buttons to add/remove blocks/update structure
            # - Information zone (multiline text)

            self._sizer_gen = wx.BoxSizer(wx.HORIZONTAL)

            self._sizer_run_results = wx.BoxSizer(wx.VERTICAL)

            self._sizer_principal = wx.BoxSizer(wx.VERTICAL)

            self._sizer_properties = wx.BoxSizer(wx.HORIZONTAL)

            # self._sizer_btnsblocks = wx.BoxSizer(wx.VERTICAL)

            self._sizer_btnsactions = wx.BoxSizer(wx.HORIZONTAL)
            self._sizer_btnsactions_left = wx.BoxSizer(wx.VERTICAL)
            self._sizer_btnsactions_right = wx.BoxSizer(wx.VERTICAL)

            self._sizer_btnsactions.Add(self._sizer_btnsactions_left, 1, wx.EXPAND)
            self._sizer_btnsactions.Add(self._sizer_btnsactions_right, 1, wx.EXPAND)

            self._sizer_btns_creation = wx.BoxSizer(wx.HORIZONTAL)

            # Buttons
            # ********

            # Boundary conditions
            # ---------------------

            self._btn_bc = wx.Button(self._panel, label=_('BCs'))
            self._btn_bc.SetToolTip(_('Set the boundary conditions'))
            self._btn_bc.Bind(wx.EVT_BUTTON, self._set_bc)

            self._sizer_run_results.Add(self._btn_bc, 1, wx.EXPAND)

            # Infiltration
            # --------------

            self._btn_infiltration = wx.Button(self._panel, label=_('Infiltration'))
            self._btn_infiltration.SetToolTip(_('Set the infiltration'))
            self._btn_infiltration.Bind(wx.EVT_BUTTON, self._set_infiltration)

            self._sizer_run_results.Add(self._btn_infiltration, 1, wx.EXPAND)

            # Check
            # -----

            self._btn_checkerrors = wx.Button(self._panel, label=_('Check errors'))
            self._btn_checkerrors.SetToolTip(_('Check the errors in the model'))
            self._btn_checkerrors.Bind(wx.EVT_BUTTON, self._check_errors)

            self._sizer_run_results.Add(self._btn_checkerrors, 1, wx.EXPAND)

            # Write files
            # ------------

            self._btn_write = wx.Button(self._panel, label=_('Write files'))
            self._btn_write.SetToolTip(_('Write the files to disk'))
            self._btn_write.Bind(wx.EVT_BUTTON, self._write_files)
            self._btn_write.Enable(False)


            self._sizer_run_results.Add(self._btn_write, 1, wx.EXPAND)

            # Run simulation
            # ---------------

            self._btn_run = wx.Button(self._panel, label=_('Run'))
            self._btn_run.SetToolTip(_('Run the simulation - wolfgpu.exe code'))
            self._btn_run.Bind(wx.EVT_BUTTON, self._run)
            self._btn_run.Enable(False)

            self._sizer_run_results.Add(self._btn_run, 1, wx.EXPAND)

            # Results
            # --------

            self._btn_results = wx.Button(self._panel, label=_('Results'))
            self._btn_results.SetToolTip(_('Display the results of the simulation'))
            self._btn_results.Bind(wx.EVT_BUTTON, self._results)
            self._btn_results.Enable(False)

            self._sizer_run_results.Add(self._btn_results, 1, wx.EXPAND)

            # Result as IC
            # ------------

            self._btn_rs2ic = wx.Button(self._panel, label=_('Results as IC'))
            self._btn_rs2ic.SetToolTip(_('Set one result as initial conditions'))
            self._btn_rs2ic.Bind(wx.EVT_BUTTON, self._results2ic)
            self._btn_rs2ic.Enable(False)

            self._sizer_run_results.Add(self._btn_rs2ic, 1, wx.EXPAND)

            # Copy Simulation
            # ---------------

            self._btn_copy2newdir = wx.Button(self._panel, label=_('Copy to...'))
            self._btn_copy2newdir.SetToolTip(_('Copy the simulation to another directory'))
            self._btn_copy2newdir.Bind(wx.EVT_BUTTON, self._copy2dir)
            self._btn_copy2newdir.Enable(False)

            self._sizer_run_results.Add(self._btn_copy2newdir, 1, wx.EXPAND)

            # Wizard
            # ------

            self._btn_wizard = wx.Button(self._panel, label=_('Wizard'))
            self._btn_wizard.SetToolTip(_('Launch the wizard to create a new model'))
            self._btn_wizard.Bind(wx.EVT_BUTTON, self._wizard)

            self._sizer_principal.Add(self._btn_wizard, 1, wx.EXPAND)

            self._sizer_magn_res = wx.BoxSizer(wx.HORIZONTAL)

            # Magnetic grid
            # -------------

            self._btn_magnetic_grid = wx.Button(self._panel, label=_('Magnetic grid'))
            self._btn_magnetic_grid.SetToolTip(_('Set a magnetic grid for the model'))
            self._btn_magnetic_grid.Bind(wx.EVT_BUTTON, self._set_magnetic_grid)

            self._sizer_magn_res.Add(self._btn_magnetic_grid, 1, wx.EXPAND)

            # # Resolution
            # # -----------

            # self._btn_set_fine_res = wx.Button(self._panel, label=_('Set fine resolution'))
            # self._btn_set_fine_res.SetToolTip(_('Set the fine resolution of the model'))
            # self._btn_set_fine_res.Bind(wx.EVT_BUTTON, self._choose_resolution)

            # self._sizer_magn_res.Add(self._btn_set_fine_res, 1, wx.EXPAND)


            # Chesk Translation
            # # -----------------

            # self._chk_translation = wx.CheckBox(self._panel, label=_('Shift to (0., 0.)'), style=wx.ALIGN_CENTER)
            # self._chk_translation.SetToolTip(_('Shift the global coordinates to (0., 0.) and define shifting parameters'))
            # self._chk_translation.SetValue(True)

            # self._sizer_magn_res.Add(self._chk_translation, 1, wx.EXPAND)

            self._sizer_principal.Add(self._sizer_magn_res, 1, wx.EXPAND)

            self._sizer_add_mesh_create = wx.BoxSizer(wx.HORIZONTAL)

            # Creation
            # ---------

            self._btn_fromvector = wx.Button(self._panel, label=_('Create From vector'))

            self._btn_fromarray  = wx.Button(self._panel, label=_('Create From array'))
            self._btn_fromfootprint = wx.Button(self._panel, label=_('Create From footprint'))

            self._btn_fromvector.SetToolTip(_('Create a simulation from an existing polygon'))
            self._btn_fromarray.SetToolTip(_('Create a simulation from the active array'))
            self._btn_fromfootprint.SetToolTip(_('Create a simulation from the footprint (ox, oy, nbx, nby, dy, dy)'))

            self.Bind(wx.EVT_BUTTON, self._create_from_vector, self._btn_fromvector)
            self.Bind(wx.EVT_BUTTON, self._create_from_array, self._btn_fromarray)
            self.Bind(wx.EVT_BUTTON, self._create_from_footprint, self._btn_fromfootprint)

            self._sizer_magn_res.Add(self._btn_fromvector, 1, wx.EXPAND)

            self._sizer_btns_creation.Add(self._btn_fromarray, 1, wx.EXPAND)
            self._sizer_btns_creation.Add(self._btn_fromfootprint, 1, wx.EXPAND)

            self._sizer_principal.Add(self._sizer_btns_creation, 1, wx.EXPAND)


            # Create arrays
            # -------------

            self._btn_add_arrays2viewer = wx.Button(self._panel, label=_('Add arrays to viewer'))
            self._btn_add_arrays2viewer.SetToolTip(_('Add all model arrays to the viewer'))
            self._btn_add_arrays2viewer.Bind(wx.EVT_BUTTON, self._add_arrays2viewer)

            self._btn_apply_mask = wx.Button(self._panel, label=_('Apply mask from active array to all'))
            self._btn_apply_mask.SetToolTip(_('Apply the mask from the active array to all arrays'))
            self._btn_apply_mask.Bind(wx.EVT_BUTTON, self._apply_mask)

            self._sizer_add_mesh_create.Add(self._btn_add_arrays2viewer, 1, wx.EXPAND)
            self._sizer_add_mesh_create.Add(self._btn_apply_mask, 1, wx.EXPAND)

            self._sizer_principal.Add(self._sizer_add_mesh_create, 1, wx.EXPAND)

            # Apply changes
            # -------------
            self._btn_apply = wx.Button(self._panel, label=_('Apply changes'))
            self._btn_apply.SetToolTip(_('Apply the changes to the memory (and save on disk)'))
            self._btn_apply.Bind(wx.EVT_BUTTON, self._apply_changes)

            self._sizer_principal.Add(self._btn_apply, 1, wx.EXPAND)

            self._panel.SetSizer(self._sizer_gen)

            self._sizer_principal.Add(self._sizer_properties, 4, wx.EXPAND)
            self._sizer_principal.Add(self._sizer_btnsactions, 1, wx.EXPAND)

            self._txt_info = wx.TextCtrl(self._panel, style=wx.TE_MULTILINE|wx.TE_READONLY)

            self._sizer_principal.Add(self._txt_info, 3, wx.EXPAND)

            self._sizer_gen.Add(self._sizer_principal, 5, wx.EXPAND)
            self._sizer_gen.Add(self._sizer_run_results, 1, wx.EXPAND)


            # Create the local list of parameters
            # - for global parameters
            # - for blocks

            # Create the widget PropertyGridManager for the parameters
            self._wp = Wolf_Param(self._panel, to_read=False, force_even_if_same_default=True, withbuttons=False, init_GUI=False)
            self._wp.ensure_prop(wxparent = self._panel, show_in_active_if_default= True)
            self._append_magnetic_grid_to_prop()

            if self._sim.sim is not None:
                # FIXME : Not the right place -> check in SimpleSimulation
                self._wp.add_param(_('Scheme'), _('Time step strategy'), 2, Type_Param.Integer, jsonstr={"Values":{"Fixed time step":1,"Optimized time step":2}})
                self._wp.add_param(_('Infiltration'), _('Interpolation mode'), 0, Type_Param.Integer, jsonstr={"Values":{"None":0, "Linear":1}})
                self._sim.sim.add_to_wolfparam(self._wp)
                self._wp.Populate(sorted_groups=True)

            # add the properties to the sizer
            self._sizer_properties.Add(self._wp.prop, 5, wx.EXPAND)

            # self._sizer_properties.Add(self._sizer_btnsblocks, 1, wx.EXPAND)

            self._prop_frame.Bind(wx.EVT_CLOSE, self.onclose)

            # Show the frame
            self._prop_frame.Show()

        else:
            logging.info(_('No GUI available'))

    def onclose(self, e:wx.EVT_CLOSE):
        """ Close the properties frame """

        if self._prop_frame is not None:
            self._prop_frame.Hide()

    def _append_magnetic_grid_to_prop(self):
        """ Append the magnetic grid to the properties """

        self._wp.add_param(MAGN_GROUP_NAME,
                                         'Dx',
                                            0.,
                                            Type_Param.Float,
                                            _('Spatial resolution of the magnetic grid along X-axis'),
                                            whichdict='All'
                                            )
        self._wp.add_param(MAGN_GROUP_NAME,
                                            'Dy',
                                            0.,
                                            Type_Param.Float,
                                            _('Spatial resolution of the magnetic grid along Y-axis'),
                                            whichdict='All'
                                            )

        self._wp.add_param(MAGN_GROUP_NAME,
                                            'Ox',
                                            -99999.,
                                            Type_Param.Float,
                                            _('Origin of the magnetic grid along X-axis'),
                                            whichdict='All'
                                            )

        self._wp.add_param(MAGN_GROUP_NAME,
                                            'Oy',
                                            -99999.,
                                            Type_Param.Float,
                                            _('Origin of the magnetic grid along Y-axis'),
                                            whichdict='All'
                                            )

        if self._sim.magnetic_grid is None:
            self._sim.set_magnetic_grid(1., 1., 0., 0.)

        self._wp[(MAGN_GROUP_NAME, 'Dx')] = self._sim.magnetic_grid.dx
        self._wp[(MAGN_GROUP_NAME, 'Dy')] = self._sim.magnetic_grid.dy

        self._wp[(MAGN_GROUP_NAME, 'Ox')] = self._sim.magnetic_grid.origx
        self._wp[(MAGN_GROUP_NAME, 'Oy')] = self._sim.magnetic_grid.origy

        self._wp.Populate(sorted_groups=True)

    def update_wp(self):
        """ Update the properties """

        if self._wp is not None:
            self._wp[(MAGN_GROUP_NAME, 'Dx')] = self._sim.magnetic_grid.dx
            self._wp[(MAGN_GROUP_NAME, 'Dy')] = self._sim.magnetic_grid.dy

            self._wp[(MAGN_GROUP_NAME, 'Ox')] = self._sim.magnetic_grid.origx
            self._wp[(MAGN_GROUP_NAME, 'Oy')] = self._sim.magnetic_grid.origy

            if self._sim.sim is not None:
                self._sim.sim.add_to_wolfparam(self._wp)

            self._wp.Populate(sorted_groups=True)

    def clear_infos(self):
        """ Clear the information zone """

        if self.wx_exists:
            self._txt_info.Clear()

    def append_infos(self, text):
        """ Append text to the information zone """

        if self.wx_exists:
            self._txt_info.AppendText(text)