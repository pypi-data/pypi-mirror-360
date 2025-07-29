"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

import wx

from .PyTranslate import _
from .PyDraw import WolfMapViewer
from .RatingCurve import *
from.PyVertexvectors import vector, Zones, zone, getIfromRGB, getRGBfromI

import logging


class selectpoint(wx.Frame):

    def __init__(self, parent=None, title="Default Title", w=500, h=200, SPWstations: SPWMIGaugingStations = None,
                 DCENNstations: SPWDCENNGaugingStations = None):
        wx.Frame.__init__(self, parent, title=title, size=(w, h), style=wx.DEFAULT_FRAME_STYLE)

        self.SPWMI = SPWstations
        self.SPWDCENN = DCENNstations

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerv = wx.BoxSizer(wx.VERTICAL)

        self.buttonOK = wx.Button(self, label="OK")
        self.buttonOK.Bind(wx.EVT_BUTTON, self.Apply)

        lblList = [_('Coordinates'), _('Code station'), _('River/Name')]
        self.rbox = wx.RadioBox(self, label='Which', choices=lblList, majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)

        self.tcoordx = wx.StaticText(self, label="X: ")
        self.coordx = wx.TextCtrl(self, value=_("X coordinate"), size=(140, -1))
        self.tcoordy = wx.StaticText(self, label="Y: ")
        self.coordy = wx.TextCtrl(self, value=_("Y coordinate"), size=(140, -1))
        self.coords = [self.tcoordx, self.coordx, self.tcoordy, self.coordy]

        mycodes = [str(x) for x in SPWstations.mystations.keys()] + [str(x) for x in DCENNstations.mystations.keys()]

        myrivers = [*list(SPWstations.myrivers.keys()), *list(DCENNstations.myrivers.keys())]

        self.tcodestation = wx.StaticText(self, label=_("Code station: "))
        self.codestation = wx.ComboBox(self, size=(95, -1), choices=mycodes, style=wx.CB_DROPDOWN)
        self.codes = [self.tcodestation, self.codestation]

        self.triverstation = wx.StaticText(self, label=_("River: "))
        self.riverstation = wx.ComboBox(self, size=(95, -1), choices=myrivers, style=wx.CB_DROPDOWN)
        self.tnamestation = wx.StaticText(self, label=_("Station name: "))
        self.namestation = wx.ComboBox(self, size=(95, -1), choices=[], style=wx.CB_DROPDOWN)
        self.riverstation.Bind(wx.EVT_COMBOBOX, self.onComboRiver)

        self.riversname = [self.triverstation, self.riverstation, self.tnamestation, self.namestation]

        self.sizerv.Add(self.rbox, 0, wx.EXPAND)

        for curitem in self.coords:
            self.sizerv.Add(curitem, 1, wx.EXPAND)
        for curitem in self.codes:
            self.sizerv.Add(curitem, 1, wx.EXPAND)
            curitem.Hide()
        for curitem in self.riversname:
            self.sizerv.Add(curitem, 1, wx.EXPAND)
            curitem.Hide()

        self.sizer.Add(self.sizerv, 1, wx.EXPAND)
        self.sizer.Add(self.buttonOK, 0, wx.EXPAND)

        # ajout du sizer à la page
        self.SetSizer(self.sizer)
        # self.SetSize(w,h)
        self.SetAutoLayout(1)

        # affichage de la page
        self.Show(True)

    def Apply(self):
        pass

    def onComboRiver(self, evt):
        str = self.riverstation.GetStringSelection()

        namestation = []
        if str in self.SPWMI.myrivers.keys():
            namestation += list(self.SPWMI.myrivers[str].keys())
        if str in self.SPWDCENN.myrivers.keys():
            namestation += list(self.SPWDCENN.myrivers[str].keys())

        self.namestation.SetItems(namestation)

        pass

    def onRadioBox(self, evt):
        str = self.rbox.GetStringSelection()
        if str == _('Coordinates'):
            for curitem in self.coords:
                curitem.Show()
            for curitem in self.codes:
                curitem.Hide()
            for curitem in self.riversname:
                curitem.Hide()
        elif str == _('Code station'):
            for curitem in self.coords:
                curitem.Hide()
            for curitem in self.codes:
                curitem.Show()
            for curitem in self.riversname:
                curitem.Hide()
        elif str == _('River/Name'):
            for curitem in self.coords:
                curitem.Hide()
            for curitem in self.codes:
                curitem.Hide()
            for curitem in self.riversname:
                curitem.Show()

        self.sizerv.Layout()


class GuiHydrology(WolfMapViewer):
    """ Mapviewer of the hydrology model -- see HydrologyModel in PyGui.py """

    def __init__(self, parent=None, title='WOLF Hydrological model - viewer', w=500, h=500, treewidth=200, wolfparent=None, wxlogging=None):
        """ Constructor

        :param parent: parent window - wx.Frame
        :param title: title of the window - str
        :param w: width of the window - int
        :param h: height of the window - int
        :param treewidth: width of the tree - int
        :param wolfparent: wolf parent instance -- PyGui.HydrologyModel
        :type wolfparent: HydrologyModel
        :param wxlogging: logging instance -- PyGui.WolfLog
        """

        super(GuiHydrology, self).__init__(parent, title=title, w=w, h=h,
                                           treewidth=treewidth,
                                           wolfparent=wolfparent,
                                           wxlogging=wxlogging)

        from .PyGui import HydrologyModel

        self.wolfparent:HydrologyModel

        # self.filemenu.Insert(0, wx.ID_ANY, _('New from scratch'), _('Create a new simulation from scratch...'))

        self.modelmenu = wx.Menu()
        paramgen = self.modelmenu.Append(wx.ID_ANY, _('Choose outlet'), _('Wizard !'))
        paramgen = self.modelmenu.Append(wx.ID_ANY, _('Interior points'), _('Interior points'))
        paramgen = self.modelmenu.Append(wx.ID_ANY, _('Topology'), _('Topology manager'))
        paramgen = self.modelmenu.Append(wx.ID_ANY, _('Main model'), _('General parameters'))
        paramgen = self.modelmenu.Append(wx.ID_ANY, _('Basin'), _('Basin parameters'))
        paramgen = self.modelmenu.Append(wx.ID_ANY, _('Subbasins'), _('Sub-Basin parameters'))
        self.menubar.Append(self.modelmenu, _('&Hydrological model'))

        self.toolsmenu = wx.Menu()
        self.toolsmenu.Append(wx.ID_ANY, _('Forced exchanges'), _('Manage the forced exchanges...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Crop MNT/MNS'), _('Cropping data...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Crop land use (COSW)'), _('Cropping data...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Analyze slope'), _('Slope analyzer...'))
        self.toolsmenu.Append(wx.ID_ANY, _('IRM - QDF'), _('Manage data...'))

        self.toolsmenu.AppendSeparator()

        self.toolsmenu.Append(wx.ID_ANY, _('Find upstream watershed'), _('Find upstream watershed based on click...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Find upstream watershed - limit to sub'), _('Find upstream watershed based on click but limit to subbasin...'))

        self.toolsmenu.AppendSeparator()

        self.toolsmenu.Append(wx.ID_ANY, _('Select upstream watershed'), _('Select upstream watershed based on click...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Select upstream watershed - limit to sub'), _('Select upstream watershed based on click but limit to subbasin...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Select upstream rivers'), _('Select upstream rivers based on click...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Select upstream rivers - limit to sub'), _('Select upstream rivers based on click but limit to subbasin...'))
        self.toolsmenu.Append(wx.ID_ANY, _('Select downstream rivers'), _('Select downstream rivers based on click...'))

        self.menubar.Append(self.toolsmenu, _('&Tools Hydrology'))

        # self.computemenu = wx.Menu()
        # paramgen = self.computemenu.Append(1300,_('Calibration/Optimisation'),_('Parameters calibration of the model'))
        # paramgen = self.computemenu.Append(1301,_('Run'),_('Run simulation !'))
        # self.menubar.Append(self.computemenu,_('&Computation'))

        # self.resultsmenu = wx.Menu()
        # paramgen = self.resultsmenu.Append(1400,_('Assemble'),_('Run postprocessing !'))
        # paramgen = self.resultsmenu.Append(1401,_('Plot'),_('Plot'))
        # self.menubar.Append(self.resultsmenu,_('&Results'))

    @property
    def watershed(self):

        if self.wolfparent is None:
            return None

        if self.wolfparent.mycatchment is None:
            return None

        return self.wolfparent.mycatchment.charact_watrshd

    def OnMenubar(self, event):
        """ Event handler for the menubar """

        # Call the parent event handler
        super().OnMenubar(event)

        # If not handled by the parent, handle it here

        id = event.GetId()
        item = self.menubar.FindItemById(id)
        if item is None:
            return

        itemlabel = item.ItemLabel

        if itemlabel == _('Choose outlet'):
            myselect = selectpoint(title=_('Outlet'),
                                   SPWstations=self.wolfparent.SPWstations,
                                   DCENNstations=self.wolfparent.DCENNstations)
            myselect.Show()

        elif itemlabel == _('Interior points'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('Topology'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('Main model'):
            self.wolfparent.mainparams.Show()

        elif itemlabel == _('Basin'):
            self.wolfparent.basinparams.Show()

        elif itemlabel == _('Subbasins'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('Forced exchanges'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('Crop MNT/MNS'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('Crop land use (COSW)'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('Analyze slope'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('IRM - QDF'):
            logging.warning(_('Not yet implemented !'))

        elif itemlabel == _('Find upstream watershed'):
            self.action = 'Find upstream watershed'

        elif itemlabel == _('Find upstream watershed - limit to sub'):
            self.action = 'Find upstream watershed - limit to sub'

        elif itemlabel == _('Select upstream watershed'):
            self.action = 'Select upstream watershed'

        elif itemlabel == _('Select upstream watershed - limit to sub'):
            self.action = 'Select upstream watershed - limit to sub'

        elif itemlabel == _('Select upstream rivers'):
            self.action = 'Select upstream rivers'

        elif itemlabel == _('Select upstream rivers - limit to sub'):
            self.action = 'Select upstream rivers - limit to sub'

        elif itemlabel == _('Select downstream rivers'):
            self.action = 'Select downstream rivers'


    def On_Mouse_Right_Down(self, e: wx.MouseEvent):

        # Call the parent event handler
        super().On_Mouse_Right_Down(e)

        if self.action is None:
            logging.info(_('No action selected !'))
            return

        if self.action == '':
            logging.info(_('No action selected !'))
            return

        pos = e.GetPosition()
        x, y = self.getXY(pos)

        alt = e.AltDown()
        ctrl = e.ControlDown()
        shiftdown = e.ShiftDown()

        if self.active_array is None:
            logging.warning(_('No active array !'))
            return

        if not (self.active_array.dx == self.watershed.header.dx and self.active_array.dy == self.watershed.header.dy):
            logging.warning(_('Active array and watershed do not have the same resolution !'))
            return

        if 'Find upstream watershed' in self.action:

            starting_node = self.watershed.get_node_from_xy(x,y)
            up_vect = self.watershed.get_vector_from_upstream_node(starting_node, limit_to_sub='limit to sub' in self.action)

            if up_vect is None:
                logging.warning(_('No upstream watershed found !'))
                return

            def props_vec(vec:vector):
                vec.myprop.color = getIfromRGB((255,0,0))
                vec.myprop.width = 3
                vec.myprop.transparent = False
                vec.myprop.alpha = 122
                vec.myprop.filled = False

            if self.active_array.Operations is not None:
                newzone = zone(name = str(starting_node.sub))

                self.active_array.Operations.show_structure_OpsVectors()
                self.active_array.Operations.myzones.add_zone(newzone, forceparent=True)
                newzone.add_vector(up_vect, forceparent=True)

                props_vec(up_vect)

                self.active_array.Operations.myzones.prep_listogl()
                self.active_array.Operations.myzones.fill_structure()

                self.Refresh()
            else:
                logging.warning(_('No operations frame in the active array!'))

        elif 'Select upstream watershed' in self.action:

            xy = self.watershed.get_xy_upstream_node(self.watershed.get_node_from_xy(x,y), limit_to_sub='limit to sub' in self.action)
            self.active_array.SelectionData.set_selection_from_list_xy(xy)
            self.Refresh()

        elif 'Select upstream rivers' in self.action:

            xy = self.watershed.get_xy_upstream_node(self.watershed.get_node_from_xy(x,y),
                                                     limit_to_sub='limit to sub' in self.action,
                                                     limit_to_river=True)

            self.active_array.SelectionData.set_selection_from_list_xy(xy)
            self.Refresh()

        elif 'Select downstream rivers' in self.action:

            xy = self.watershed.get_xy_downstream_node(self.watershed.get_node_from_xy(x,y))
            self.active_array.SelectionData.set_selection_from_list_xy(xy)
            self.Refresh()


