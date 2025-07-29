"""
Author: HECE - University of Liege, Pierre Archambeau, Utashi Ciraane Docile
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

from numpy import asarray,ndarray,arange,zeros,linspace,concatenate,unique,amin,amax
import math
import matplotlib.pyplot as plt
from shapely.geometry import LineString,MultiLineString,Point,Polygon,CAP_STYLE,Point
from shapely.prepared import prep
from shapely.ops import nearest_points,substring
from OpenGL.GL  import *
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from os import path
import pygltflib
import typing
import copy
from enum import Enum
import logging
import wx
from typing import Union, Literal
from pathlib import Path

from .PyTranslate import _
from .drawing_obj import Element_To_Draw
from .PyVertexvectors import vector,zone,Zones
from .PyVertex import wolfvertex,cloud_vertices, getIfromRGB
from .lazviewer.laz_viewer import xyz_laz_grids, myviewer

example_largesect="""-138 100
-114 90
-70 80
-45 70
-32 62
0 61.5
32 62
60 70
80 80
98 84
120 87"""

example_smallsect="""0 68
10 67
12 65
15 63
20 62
24 61.5
30 62
35 64
40 66
42 66.5
50 68"""

example_diffsect1="""0 10
10 5
12 5
15 6
16 6
17 5
20 3
25 3
30 5
42 7
50 10"""

def INTERSEC(x1,y1,x2,y2,el):
    """Procédure de calcul de l'abscisse d'intersection d'une altitude donnée el
    dans un segment défini par ses coordonnées (x1,y1) et (x2,y2)"""
    xx=1.0e10

    if x2-x1==0.:
        if y2>y1:
            if y1<=el<=y2:
                return x2
        elif y2<y1:
            if y2<=el<=y1:
                return x2
    elif 0.0<abs(y2-y1):
        a=(y2-y1)/(x2-x1)
        b=(x2*y1-x1*y2)/(x2-x1)
        xx=(el-b)/a
    return xx

def partranslation(base, x, y ):

    copie = base.copy()
    copie[:,0] += x
    copie[:,1] += y
    return(copie)

def  find_xy(section,x3,y3):
    x1 = section[0,0]
    y1 = section[0,1]
    x2 = section[-1,0]
    y2 = section[-1,1]

    if x2==x1:
        y4 = y3
        x4 = x1
    else:
        a = (y2-y1)/(x2-x1)
        b = y1-(a*x1)

        vecteur = ([1,a])
        normale = ([-a,1])
        normale_opposée = ([a,-1])

        c = -1/a
        d = y3-(c*x3)

        x4 = (d-b)/(a-c)
        y4 = a*x4 + b

    x = (x3-x4)
    y = (y3-y4)

    return x,y

class postype(Enum):
    """
    Mode de stockage des points de référence (berges, fond lit)
    """
    BY_VERTEX   = 0 # sur base de coordonnées (wolfvertex)
    BY_S3D      = 1 # sur base d'une position curviligne 3D (le long de la trace de la section)
    BY_INDEX    = 2 # sur base d'un index de vertex
class profile(vector):
    """
    Surcharge d'un vecteur en vue de définir un profil de rivière

    Les coordonnées attendues sont en 3D (x,y,z)
    """

    def __init__(self, name, data_sect='',parent=None) -> None:
        super().__init__(name=name)

        if data_sect!='':
            for curline in data_sect.splitlines():
                values=curline.split(' ')
                curvert=wolfvertex(float(values[0]),0.,float(values[1]))
                self.add_vertex(curvert)

        # Les positions de référence sont intanciées à None
        # Elles sont accessibles comme "property" de l'objet --> valeur "brute"
        # mais il est également possible d'obtenir l'info à travers :
        #  - bankleft_vertex, bankright_vertex, bed_vertex qui retournent un vertex quel que soit le format de stockage
        #  - bankleft_s3D, bankright_s3D, bed_s3D qui retournent la position curvi 3D quel que soit le format de stockage
        #  - bankleft_sz, bankright_sz, bed_sz qui retournent un couple (s,z) quel que soit le format de stockage
        self._bankleft=None
        self._bankright=None
        self._bed=None

        self.banksbed_postype = postype.BY_VERTEX

        self.refpoints={}

        self.s = 0.0
        self.up:profile = None
        self.down:profile = None

        self.laz=False

        if parent is not None:
            assert isinstance(parent,crosssections), _('Bad type of parent object')
        self.parent=parent

        self.zdatum = 0.
        self.add_zdatum=False

        self.sdatum = 0.
        self.add_sdatum=False

        self.orient = None

        self.sz = None
        self.sz_bankbed = None
        self.s3d_bankbed = None
        self.prepared=False # if True, one can call self.sz instead of self.get_sz

    @property
    def linked_arrays(self):
        if self.parent is not None:
            return self.parent.get_linked_arrays()
        else:
            return {}

    @property
    def bankleft(self):
        return self._bankleft

    @bankleft.setter
    def bankleft(self,value):
        self._bankleft=value

    @property
    def bankright(self):
        return self._bankright

    @bankright.setter
    def bankright(self,value):
        self._bankright=value

    @property
    def bed(self):
        return self._bed

    @bed.setter
    def bed(self,value):
        self._bed=value

    @property
    def bankleft_vertex(self):
        if self.banksbed_postype == postype.BY_VERTEX:
            return self._bankleft
        elif self.banksbed_postype == postype.BY_INDEX:
            return self.myvertices[self._bankleft]
        else:
            return self.interpolate(self._bankleft, adim=False)

    @property
    def bankright_vertex(self):
        if self.banksbed_postype == postype.BY_VERTEX:
            return self._bankright
        elif self.banksbed_postype == postype.BY_INDEX:
            return self.myvertices[self._bankright]
        else:
            return self.interpolate(self._bankright, adim=False)

    @property
    def bed_vertex(self):
        if self.banksbed_postype == postype.BY_VERTEX:
            return self._bed
        elif self.banksbed_postype == postype.BY_INDEX:
            return self.myvertices[self._bed]
        else:
            return self.interpolate(self._bed, adim=False)

    @property
    def bankleft_s3D(self):
        if self.banksbed_postype == postype.BY_S3D:
            return self._bankleft
        else:
            # on dispose d'un vertex 3D et on doit retnvoyer une position s3D
            # --> projection x,y sur la trace --> récupération de 's'
            # --> calcul de la distance s3D via shapely LineString sz en projetant '(s,z)'
            if self.bankleft_vertex is not None:
                ls2d = self.asshapely_ls()
                lssz = self.asshapely_sz()
                curvert = self.bankleft_vertex
                s = ls2d.project(Point(curvert.x, curvert.y))
                s3d = lssz.project(Point(s,curvert.z))
            else:
                s3d = 0.
            return s3d

    @property
    def bankright_s3D(self):
        if self.banksbed_postype == postype.BY_S3D:
            return self._bankright
        else:
            # on dispose d'un vertex 3D et on doit retnvoyer une position s3D
            # --> projection x,y sur la trace --> récupération de 's'
            # --> calcul de la distance s3D via shapely LineString sz en projetant '(s,z)'
            if self.bankright_vertex is not None:
                ls2d = self.asshapely_ls()
                lssz = self.asshapely_sz()
                curvert = self.bankright_vertex
                s = ls2d.project(Point(curvert.x, curvert.y))
                s3d = lssz.project(Point(s,curvert.z))
            else:
                s3d = self.length3D
            return s3d

    @property
    def bed_s3D(self):
        if self.banksbed_postype == postype.BY_S3D:
            return self._bed
        else:
            # on dispose d'un vertex 3D et on doit retnvoyer une position s3D
            # --> projection x,y sur la trace --> récupération de 's'
            # --> calcul de la distance s3D via shapely LineString sz en projetant '(s,z)'
            if self.bed_vertex is not None:
                ls2d = self.asshapely_ls()
                lssz = self.asshapely_sz()
                curvert = self.bed_vertex
                s = ls2d.project(Point(curvert.x, curvert.y))
                s3d = lssz.project(Point(s,curvert.z))
            else:
                s3d = self.length3D/2.
            return s3d

    @property
    def bankleft_sz(self):
        ls2d = self.asshapely_ls()
        curvert = self.bankleft_vertex
        s = ls2d.project(Point(curvert.x, curvert.y))
        return s, curvert.z

    @property
    def bankright_sz(self):
        ls2d = self.asshapely_ls()
        curvert = self.bankright_vertex
        s = ls2d.project(Point(curvert.x, curvert.y))
        return s, curvert.z

    @property
    def bed_sz(self):
        ls2d = self.asshapely_ls()
        curvert = self.bed_vertex
        s = ls2d.project(Point(curvert.x, curvert.y))
        return s, curvert.z

    def verif(self):

        self.update_lengths()

        # for curl in self._lengthparts3D

    def triangulation_gltf(self, zmin):
        """
        Génération d'un info de triangulation pour sortie au format GLTF --> Blender
        :zmin : position d'altitude minimale de la triangulation
        """
        section = self.asnparray3d()
        base = section.copy()
        base[:,2] = zmin
        points = np.concatenate((section,base),axis=0)
        triangles=[]
        nb=self.nbvertices
        for j in range (nb-1):
            a = 0+j
            b = nb+1+j
            c = nb+j
            for i in range(2):
                triangles.append([a,b,c])
                c = b
                b = a+1

        return points,triangles

    def triangulation_ponts(self,x,y, zmax):
        """
        Triangulation d'une section de pont
        """
        section = self.asnparray3d()
        x1,y1=find_xy(section,x,y)
        parallele = partranslation(section,x1,y1)

        base1 = section.copy()
        base1[:,2]= zmax
        base2 = parallele.copy()
        base2[:,2]= zmax
        points = np.concatenate((section,base1,parallele,base2),axis=0)
        triangles=[]
        for j in range (len(section)-1):
            a = 0+j
            b = len(section)+1+j
            c = len(section)+j
            for i in range(2):
                triangles.append([a,b,c])
                c = b
                b = a+1
        for j in range (len(section)-1):
            a = len(section)+j
            b = len(section)*3+j+1
            c = len(section)*3+j
            for i in range(2):
                triangles.append([a,b,c])
                c = b
                b = a+1
        for j in range (len(section)-1):
            a = len(section)*2+j
            b = len(section)*3+j+1
            c = len(section)*3+j
            for i in range(2):
                triangles.append([a,b,c])
                c = b
                b = a+1
        for j in range (len(section)-1):
            a = 0+j
            b = len(section)*2+j+1
            c = len(section)*2+j
            for i in range(2):
                triangles.append([a,b,c])
                c = b
                b = a+1
        triangles.append([0,len(section)*3,len(section)*2])
        triangles.append([0,len(section),len(section)*3])
        triangles.append([len(section)-1,len(section)*4-1,len(section)*3-1])
        triangles.append([len(section)-1,len(section)*2-1,len(section)*4-1])
        return(np.asarray([[curpt[0],curpt[2],-curpt[1]] for curpt in points],dtype=np.float32),np.asarray(triangles,dtype=np.uint32))

    def set_orient(self):
        """
        Calcul du vecteur directeur de la section sur base des points extrêmes
        """
        self.orient = asarray([self.myvertices[-1].x-self.myvertices[0].x,
                              self.myvertices[-1].y-self.myvertices[0].y])
        self.orient = self.orient /np.linalg.norm(self.orient)

    def get_xy_from_s(self,s) -> tuple[float, float]:
        """
        Récupération d'un tuple (x,y) sur base d'une distance 2D 's' orientée dans l'axe de la section
        """
        if self.orient is None:
            self.set_orient()

        return self.myvertices[0].x+self.orient[0]*s,self.myvertices[0].y+self.orient[1]*s

    def set_vertices_sz_orient(self, sz:np.ndarray, xy1:np.ndarray, xy2:np.ndarray):
        """
        Ajout de vertices depuis :
          - une matrice numpy (s,z) -- shape = (nb_vert,2)
          - d'un point source [x,y]_1
          - d'un point visé [x,y]_2
        """

        if isinstance(sz,list):
            sz = np.asarray(sz)
        if isinstance(sz,tuple):
            sz = np.asarray(sz)
        if isinstance(xy1,list):
            xy1 = np.asarray(xy1)
        if isinstance(xy2,list):
            xy2 = np.asarray(xy2)
        if isinstance(xy1,tuple):
            xy1 = np.asarray(xy1)
        if isinstance(xy2,tuple):
            xy2 = np.asarray(xy2)

        if sz.shape[1]==2 and xy1.shape==(2,) and xy2.shape==(2,):
            if not np.array_equal(xy1,xy2):
                self.myvertices=[]

                dx, dy = xy2[0]-xy1[0], xy2[1]-xy1[1]
                norm = np.linalg.norm([dx,dy])
                dx, dy = dx/norm, dy/norm

                for cur in sz:
                    x, y = xy1[0] + dx*cur[0], xy1[1] + dy*cur[0]
                    self.add_vertex(wolfvertex(x, y, float(cur[1])))

    def get_laz_around(self,length_buffer=10.):
        """
        Récupération de points LAZ autour de la section
        """
        myls = self.asshapely_ls()
        mypoly = myls.buffer(length_buffer,cap_style=CAP_STYLE.square)
        mybounds = ((mypoly.bounds[0],mypoly.bounds[2]),(mypoly.bounds[1],mypoly.bounds[3]))

        myxyz = self.parent.gridlaz.scan(mybounds)

        prep_poly = prep(mypoly)
        mytests = [prep_poly.contains(Point(cur[:3])) for cur in myxyz]

        self.usedlaz = np.asarray(myxyz[mytests])

        orig = [self.myvertices[0].x,self.myvertices[0].y]
        a=[self.myvertices[-1].x-self.myvertices[0].x,self.myvertices[-1].y-self.myvertices[0].y]
        a= a/np.linalg.norm(a)

        self.s_laz = np.asarray([np.dot(a,cur[:2]-orig) for cur in self.usedlaz])

        self.colors_laz=np.ones((self.usedlaz.shape[0],4),dtype=np.float32)

        self.colors_laz[self.usedlaz[:,3]==1]=[.5,.5,.5,1.]
        self.colors_laz[self.usedlaz[:,3]==2]=[.5,.25,.25,1.]
        self.colors_laz[self.usedlaz[:,3]==4]=[0.,0.5,0.,1.]
        self.colors_laz[self.usedlaz[:,3]==9]=[0.,0.5,1.,1.]
        self.colors_laz[self.usedlaz[:,3]==10]=[1,0.2,0.2,1.]

        s = np.asarray([float(np.cross(a,cur[:2]-orig))  for cur in self.usedlaz])
        smax=np.max(np.abs(s))
        self.colors_laz[:,3] = 1.-np.abs(s)/smax

        up=np.where(s[:]<0.)[0]
        down=np.where(s[:]>=0.)[0]
        self.uplaz = self.s_laz[up]
        self.downlaz = self.s_laz[down]

        self.uplaz_colors = self.colors_laz[up]
        self.downlaz_colors = self.colors_laz[down]

        self.upz = self.usedlaz[up]
        self.downz = self.usedlaz[down]

        self.laz=True

    def plot_laz(self,length_buffer=5.,fig:Figure=None,ax:Axes=None,show=False):
        """
        Dessin des points LAZ sur le graphique Matplotlib
        """
        if not self.laz:
            self.get_laz_around(length_buffer)

        if ax is None:
            fig = plt.figure()
            ax=fig.add_subplot(111)

        # ax.scatter(self.s_laz,self.usedlaz[:,2],c=self.colors_laz,marker='.')
        ax.scatter(self.uplaz,self.upz[:,2],c=self.uplaz_colors,marker='.')
        ax.scatter(self.downlaz,self.downz[:,2],c=self.downlaz_colors,marker='+')

        if show:
            fig.show()

        return np.min(self.usedlaz[:,2]),np.max(self.usedlaz[:,2])

    def slide_vertex(self,s):
        """
        Glissement des vertices d'une constante 's'
        """

        if self.orient is None:
            self.set_orient()

        dx = self.orient[0] *s
        dy = self.orient[1] *s

        for curv in self.myvertices:
            curv.x +=dx
            curv.y +=dy

    def movebankbed_index(self,which,orientation):
        """
        Déplacement des points de référence sur base d'un index
        Le cas échéant, adaptation du mode de stockage
        """
        if self.banksbed_postype == postype.BY_VERTEX:
            if which=='left':
                k = self.myvertices.index(self._bankleft)
            elif which=='right':
                k = self.myvertices.index(self._bankright)
            elif which=='bed':
                k = self.myvertices.index(self._bed)

            if orientation=='left':
                k=max(0,k-1)
            elif orientation=='right':
                k=min(self.nbvertices-1,k+1)

            if which=='left':
                self._bankleft=k
            elif which=='right':
                self._bankright=k
            elif which=='bed':
                self._bed=k
        elif self.banksbed_postype == postype.BY_S3D:
            if which=='left':
                k = 0
                self._bankleft=k
            elif which=='right':
                k = self.nbvertices-1
                self._bankright=k
            elif which=='bed':
                k = int(self.nbvertices/2)
                self._bed=k
        if self.banksbed_postype == postype.BY_INDEX:
            if which=='left':
                k = self._bankleft
            elif which=='right':
                k = self._bankright
            elif which=='bed':
                k = self._bed

            if orientation=='left':
                k=max(0,k-1)
            elif orientation=='right':
                k=min(self.nbvertices-1,k+1)

            if which=='left':
                self._bankleft=k
            elif which=='right':
                self._bankright=k
            elif which=='bed':
                self._bed=k

        self.banksbed_postype = postype.BY_INDEX

        if self.prepared:
            self.sz_bankbed = self.get_sz_banksbed(force=True)
            self.s3d_bankbed = self.get_s3d_banksbed(force=True)

    def update_sdatum(self, new_sdatum):
        """
        MAJ de la position de la section selon sa trace
        """

        sdatum_prev = self.sdatum

        self.sdatum = new_sdatum
        self.add_sdatum = True

        if self.prepared:
            delta = new_sdatum-sdatum_prev
            self.sz[:,0] += delta
            self.smin += delta
            self.smax += delta

    def update_zdatum(self, new_zdatum):
        """
        MAJ de l'altitude de référence de la section
        """

        zdatum_prev = self.zdatum

        self.zdatum = new_zdatum
        self.add_zdatum = True

        if self.prepared:
            delta = new_zdatum-zdatum_prev
            self.sz[:,1] +=new_zdatum-zdatum_prev
            self.zmin += delta
            self.zmax += delta

    def update_banksbed_from_s3d(self, which, s:float):
        """
        MAJ des points de référence depuis une coordonnée curvi 3D
        """

        if self.banksbed_postype != postype.BY_S3D:
            s1, s2, s3 = self.get_s3d_banksbed()
            self.bankleft = s1
            self.bed = s2
            self.bankright = s3

        self.banksbed_postype = postype.BY_S3D

        if which=='left':
            self.bankleft = s

            if self.prepared:
                self.s3d_bankbed[0]=s

        elif which =='right':
            self.bankright = s

            if self.prepared:
                self.s3d_bankbed[2]=s

        elif which=='bed':
            self.bed = s

            if self.prepared:
                self.s3d_bankbed[1]=s

        if self.prepared:
            self.sz_bankbed = self.get_sz_banksbed(force=True)

    def save(self,f):
        """
        Surcharge de l'opération d'écriture
        """

        if self.parent.forcesuper:
            super().save(f)
        else:
            for curvert in self.myvertices:
                which=''
                if curvert is self.bed:
                    which = "BED"
                elif curvert is self.bankleft:
                    which = "LEFT"
                elif curvert is self.bankright:
                    which = "RIGHT"

                f.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(self.myname,curvert.x,curvert.y,which,curvert.z))

    def get_s_from_xy(self, xy:wolfvertex) -> float:
        """
        Retourne la coordonnér curvi sur base d'un vertex
        """

        x1 = self.myvertices[0].x
        y1 = self.myvertices[0].y
        length = math.sqrt((xy.x-x1)**2.+(xy.y-y1)**2.)

        return length

    def get_sz(self, cumul=True) -> tuple[np.ndarray, np.ndarray]:
        """
        Retourne 2 vecteurs avec la position curvi 2D et l'altitude des points
        """

        if self.prepared:
            return self.sz[:,0], self.sz[:,1]

        z = asarray([self.myvertices[i].z for i in range(self.nbvertices)])

        if self.add_zdatum:
            z+=self.zdatum

        nb = len(z)
        s = zeros(nb)

        if cumul:
            x1 = self.myvertices[0].x
            y1 = self.myvertices[0].y
            for i in range(nb-1):
                x2 = self.myvertices[i+1].x
                y2 = self.myvertices[i+1].y

                length = np.sqrt((x2-x1)**2.+(y2-y1)**2.)
                s[i+1] = s[i]+length

                x1=x2
                y1=y2
        else:
            for i in range(nb):
                s[i] = self.myvertices[0].dist2D(self.myvertices[i])

        if self.add_sdatum:
            s+=self.sdatum

        return s,z

    def set_sz(self, sz, trace):
        """
        Calcule les positions des vertices sur base d'une matrice sz et d'une trace
            s : colonne 0
            z : colonne 1
            trace : liste de 2 couples xy -> [[x1,y1], [x2,y2]]
        """

        orig = trace[0]
        end = trace[1]

        vec = np.asarray(end)-np.asarray(orig)
        vec = vec/np.linalg.norm(vec)

        xy = np.asarray([s*vec+np.asarray(orig) for s in sz[:,0]])

        for i in range(len(xy)):
            curvert = wolfvertex(xy[i,0],xy[i,1],sz[i,1])
            self.add_vertex(curvert)

    def get_sz_banksbed(self, cumul=True, force:bool=False) -> tuple[float, float, float, float, float, float]:
        """
        Retourne les positions des points de référence  mais avec la coordonnée curvi 2D
         - (sleft, sbed, sright, zleft, zbed, zright)
        """

        if self.prepared and not force:
            return self.sz_bankbed

        x1 = self.myvertices[0].x
        y1 = self.myvertices[0].y

        if self.bankleft is not None:
            if cumul:
                sleft, zleft = self.bankleft_sz
            else:
                curvert = self.bankleft_vertex
                x2 = curvert.x
                y2 = curvert.y
                sleft = math.sqrt((x2-x1)**2.+(y2-y1)**2.)
                zleft=curvert.z
        else:
            sleft=-99999.
            zleft=-99999.

        if self.bankright is not None:
            if cumul:
                sright, zright = self.bankright_sz
            else:
                curvert = self.bankright_vertex
                x2 = curvert.x
                y2 = curvert.y
                sright = math.sqrt((x2-x1)**2.+(y2-y1)**2.)
                zright=curvert.z
        else:
            sright=-99999.
            zright=-99999.

        if self.bed is not None:
            if cumul:
                sbed, zbed = self.bed_sz
            else:
                curvert = self.bed_vertex
                x2 = curvert.x
                y2 = curvert.y
                sbed = math.sqrt((x2-x1)**2.+(y2-y1)**2.)
                zbed=curvert.z
        else:
            sbed=-99999.
            zbed=-99999.

        if self.add_sdatum:
            sleft+=self.sdatum
            sbed+=self.sdatum
            sright+=self.sdatum
        if self.add_zdatum:
            zleft+=self.zdatum
            zbed+=self.zdatum
            zright+=self.zdatum

        return sleft,sbed,sright,zleft,zbed,zright

    def get_s3d_banksbed(self, force:bool=False)-> tuple[float, float, float]:
        """
        Retourne les coordonnée curvi 3D des points de référence
         - (sleft, sbed, sright)
        """

        if self.prepared and not force:
            return self.s3d_bankbed

        return self.bankleft_s3D, self.bed_s3D, self.bankright_s3D

    def asshapely_sz(self) -> LineString:
        """
        Retroune la section comme objet shapely - polyligne selon la trace avec altitudes
        """

        s,z = self.get_sz()
        return LineString(np.asarray([[curs, curz] for curs, curz in zip(s,z)]))

    def asshapely_s3dz(self) -> LineString:
        """
        Retroune la section comme objet shapely - polyligne selon la trace 3D avec altitudes
        """

        s = self.get_s3d()
        z = [cur.z for cur in self.myvertices]
        return LineString(np.asarray([[curs, curz] for curs, curz in zip(s,z)]))

    def prepare(self,cumul=True):
        """
        Pre-Compute sz and sz_banked to avoid multiple computation
        """

        self.reset_prepare()
        self.update_lengths()
        x,y = self.get_sz()
        self.sz = np.column_stack([x,y])
        self.smin = min(x)
        self.smax = max(x)
        self.zmin = min(y)
        self.zmax = max(y)

        self.prepare_shapely()
        self.sz_bankbed = list(self.get_sz_banksbed(cumul))
        self.s3d_bankbed = list(self.get_s3d_banksbed())

        self.prepared=True

    def reset_prepare(self):
        """
        Réinitialisation de la préparation de la section
        """

        self.sz = None
        self.smin = -99999
        self.smax = -99999
        self.zmin = -99999
        self.zmax = -99999
        self.sz_bankbed = None
        self.s3d_bankbed = None
        self.linestring = None

        self.prepared=False

    def get_min(self):
        return sorted(self.myvertices,key=lambda x:x.z)[0]

    def get_max(self):
        return sorted(self.myvertices,key=lambda x:x.z)[-1]

    def get_minz(self):
        return amin(list(x.z for x in self.myvertices))

    def get_maxz(self):
        return amax(list(x.z for x in self.myvertices))

    def plot_linked(self, fig, ax, linked_arrays:dict):

        colors=['red','blue','green']

        k=0
        for curlabel, curarray in linked_arrays.items():
            if curarray.plotted:
                myls = self.asshapely_ls()

                length = myls.length
                ds = min(curarray.dx,curarray.dy)
                nb = int(np.ceil(length/ds*2))

                alls = np.linspace(0,int(length),nb)

                pts = [myls.interpolate(curs) for curs in alls]

                allz = [curarray.get_value(curpt.x,curpt.y) for curpt in pts]

                if np.max(allz)>-99999:
                    ax.plot(alls,allz,
                            color=colors[np.mod(k,3)],
                            lw=2.0,
                            label=curlabel)
                k+=1

    def _plot_only_cs(self,fig:Figure=None,ax:Axes=None,label='',alpha=0.8,lw=1.,style: str ='dashed',centerx=0.,centery=0.,grid=True, col_ax: str = 'black'):
        # plot
        x,y=self.get_sz()

        sl,sb,sr,yl,yb,yr = self.get_sz_banksbed()

        if centerx >0. and sb!=-99999.:
            decal = centerx-sb
            x+=decal
            sl+=decal
            sb+=decal
            sr+=decal

        if centery >0. and yb!=-99999.:
            decal = centery-yb
            y+=decal
            yl+=decal
            yb+=decal
            yr+=decal

        ax.plot(x,y,color=col_ax,
                lw=lw,
                linestyle=style,
                alpha=alpha,
                label=label)

        curtick=ax.get_xticks()
        ax.set_xticks(np.arange(min(curtick[0],(x[0]//2)*2),max(curtick[-1],(x[-1]//2)*2),2))

        if sl != -99999.:
            ax.plot(sl,yl,'or',alpha=alpha)
        if sb != -99999.:
            ax.plot(sb,yb,'ob',alpha=alpha)
        if sr != -99999.:
            ax.plot(sr,yr,'og',alpha=alpha)

    def plot_cs(self, fwl=None, show=False, forceaspect=True, fig:Figure=None, ax:Axes=None, plotlaz=True, clear=True, linked_arrays:dict={}):
        # plot
        x,y=self.get_sz()

        sl,sb,sr,yl,yb,yr = self.get_sz_banksbed()

        xmin=x[0]
        xmax=x[-1]
        ymin=self.get_minz()
        ymax=self.get_maxz()

        dy=ymax-ymin
        ymin-=dy/4.
        ymax+=dy/4.

        if ax is None:
            redraw=False
            fig = plt.figure()
            ax=fig.add_subplot(111)
        else:
            redraw=True
            if clear:
                ax.cla()

        if np.min(y) != -99999. and np.max(y) != -99999.:
            ax.plot(x,y,color='black',
                    lw=2.0,
                    label='Profil')

        if self.parent is not None:
            if plotlaz and self.parent.gridlaz is not None:
                minlaz=ymin
                maxlaz=ymax
                minlaz,maxlaz=self.plot_laz(fig=fig,ax=ax)
                if np.min(y) != -99999. and np.max(y) != -99999.:
                    ymin = min(ymin,minlaz)
                    ymax = max(ymax,maxlaz)
                else:
                    ymin = minlaz
                    ymax = maxlaz

        self.plot_linked(fig,ax,linked_arrays)

        if fwl is not None:
            ax.fill_between(x,y,fwl,where=y<=fwl,facecolor='cyan',alpha=0.3,interpolate=True)

        if sl != -99999.:
            ax.plot(sl,yl,'or')
        if sb != -99999.:
            ax.plot(sb,yb,'ob')
        if sr != -99999.:
            ax.plot(sr,yr,'og')

        ax.set_title(self.myname)
        ax.set_xlabel(_('Distance [m]'))
        ax.set_ylabel('Elevation [EL.m]')
        ax.legend()

        tol=(xmax-xmin)/10.
        ax.set_xlim(xmin-tol,xmax+tol)
        ax.set_ylim(ymin,ymax)

        nbticks = 20
        dzticks = max((((ymax-ymin)/nbticks) // .25) *.25,.25)

        ax.set_yticks(np.arange((ymin//.25)*.25,(ymax//.25)*.25,dzticks))
        ax.grid()

        if forceaspect:
            aspect=1.0*(ymax-ymin)/(xmax-xmin)*(ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0])
            ax.set_aspect(aspect)

        if show:
            fig.show()

        if redraw:
            fig.canvas.draw()

        return sl,sb,sr,yl,yb,yr

    def relation_oneh(self,cury,x=None,y=None):

        if x is None and y is None:
            x,y=self.get_sz()

        s=a=w=0.0
        for i in range(0,len(x)-1):
            #recherche des intersections sur les segments
            x1=x[i]
            y1=y[i]
            x2=x[i+1]
            y2=y[i+1]

            #calcul des incréments de section et de périmètre
            dS=0.0
            dA=0.0
            dL=0.0
            # if y1<=cury and y2<=cury: # The inferiority was not strict under this condition especially for the computation of the wetted perimeter
            if y1<cury and y2<cury:
                #le segment est totalement situé en dessous de la hauteur utile
                dS=math.sqrt((x2-x1)**2.+(y2-y1)**2.)
                dA=0.5*(2.0*cury-y1-y2)*(x2-x1)
                dL=(x2-x1)
            else:
                xx=INTERSEC(x1,y1,x2,y2,cury)
                if x1<=xx and xx<=x2:
                    #le segment intersecte la hauteur utile
                    if y2<=cury and cury<=y1:
                        dS=math.sqrt((x2-xx)**2.+(y2-cury)**2.)
                        dA=0.5*(x2-xx)*(cury-y2)
                        dL=(x2-xx)
                    if y1<=cury and cury<=y2:
                        dS=math.sqrt((xx-x1)**2.+(cury-y1)**2.)
                        dA=0.5*(xx-x1)*(cury-y1)
                        dL=(xx-x1)

            #ajout des incréments
            s+=dS
            a+=dA
            w+=dL

        if 0.0<s:
            r=a/s
        else:
            r=0.

        return a,s,w,r

    def relations(self, discretize: int = 100, plot = True):
        """
        This method returns 6 numpy arrays each containing the evolution
        of a specific hydraulic characteristic with respect to the water depth in the profile
        (wetted area, wetted perimeter, top width, water detph, hydraulic radius, critical discharge).
        """
        x,y=self.get_sz()

        ymin=min(y)
        ymax=max(y)

        yy = concatenate([linspace(ymin,ymax,discretize),y])   #  To avoid hard coding the discretization
        yy=unique(yy)
        yy.sort()

        nb=len(yy)

        a=zeros(nb)      # Area
        s=zeros(nb)      # Wet perimeter
        w=zeros(nb)      # Top width
        r=zeros(nb)      # Hydraulic radius
        h=zeros(nb)      # Water depth
        qcr = zeros(nb)  # Critical discharge

        for k in range(nb):
            a[k],s[k],w[k],r[k] = self.relation_oneh(yy[k],x,y)
            h[k]=yy[k]-ymin
            # Test to avoid division by zero in case the top width equals 0 (often first value)
            if w[k] != 0:
                qcr[k] = math.sqrt((9.81*((a[k])**3))/(w[k]))
            else:
                qcr[k] = 0.

        #Initialisation for plots
        if plot:                                        # In order to allow other usages apart from Graphprofile.
            self.wetarea = a
            self.wetperimeter = s
            self.hyrdaulicradius = r
            self.waterdepth=h
            self.localwidth=w
            self.criticaldischarge = qcr

        return a,s,r,h,w,qcr

    def slopes(self):

        slopedown = (self.get_minz() - self.down.get_minz()) / abs(self.down.s - self.s+1.e-10)
        slopeup   = (self.up.get_minz() - self.get_minz()) / abs(self.s - self.up.s+1.e-10)
        slopecentered = (self.up.get_minz() - self.down.get_minz()) / abs(self.down.s - self.up.s+1.e-10)

        return slopeup,slopecentered,slopedown

    def ManningStrickler_Q(self,slope=1.e-3,nManning=0.,KStrickler=0.):
        """Procédure générique pour obtenir une relation uniforme Q-H sur base
            - nManning : un coefficient de frottement
            - slope : une pente
        """

        if nManning==0. and KStrickler==0.:
            return
        elif nManning>0.:
            coeff=1./nManning
        elif KStrickler>0.:
            coeff = KStrickler

        nn=len(self.waterdepth)
        sqrtslope=math.sqrt(slope)

        self.q=asarray([coeff * self.hyrdaulicradius[k]**(2./3.)*sqrtslope * self.wetarea[k] for k in range(nn)])

    def ManningStrickler_oneQ(self,slope=1.e-3,nManning=0.,KStrickler=0.,cury=0.):
        """Procédure générique pour obtenir une relation uniforme Q-H sur base
            - nManning : un coefficient de frottement
            - slope : une pente
        """

        if nManning==0. and KStrickler==0.:
            return
        elif nManning>0.:
            coeff=1./nManning
        elif KStrickler>0.:
            coeff = KStrickler

        a,s,w,r = self.relation_oneh(cury)

        sqrtslope=math.sqrt(slope)

        q=coeff * r**(2./3.) * sqrtslope * a

        return q

    # Methods added
    def deepcopy_profile(self, name: str = None):
        """
        This method returns a deepcopy of the active profile.
        The profile features are individually transferred, therefore,
        only the necessary features are copied.
        """
        # if a new name is not given, we add _copy to the current profile's name.
        if name is None:
            name = self.myname + "_copy"

        # We create the new  profile (copy).
        copied_profile = profile(name)

        # Deep copies
        # 1. Vertices
        copied_profile.myvertices = copy.deepcopy(self.myvertices)
        # 3. The river banks
        copied_profile.bankleft = copy.deepcopy(self.bankleft)
        copied_profile.bankright = copy.deepcopy(self.bankright)
        copied_profile.bed = copy.deepcopy(self.bed)
        copied_profile.banksbed_postype = copy.deepcopy(self.banksbed_postype)

        return copied_profile

    def color_active_profile(self, width: float = 3., color: list = [255, 0, 0], plot_opengl = True):
        """
        This method colors and thickens the active profile
        (default width : 3, default color: red).
        """
        self.myprop.width = width
        self.myprop.color = getIfromRGB(color)
        if plot_opengl:
            self.parentzone.plot(True) # FIXME (Parent zone)

    def highlightning(self, width: float = 3., color: list = [255, 0, 0] , plot_opengl = True):
        """Alias for color_active_profile"""
        self.color_active_profile(width, color)

    def uncolor_active_profile(self, plot_opengl = True):
        """
        This method resets the width and the color of the active profile to 1 and black.
        """
        self.myprop.width = 1
        self.myprop.color = getIfromRGB([0, 0, 0])

        if plot_opengl:
            self.parentzone.plot(True)

    def withdrawing(self , plot_opengl = True):
        """Alias for uncolor_active_profile"""
        self.uncolor_active_profile(plot_opengl)

    def ManningStrickler_profile(self, slope: float =1.e-3, nManning: float =0., KStrickler: float=0.):
        """
        Procédure générique pour obtenir une relation uniforme Q-H d'un profile sur base:
            - nManning ou KStrickler: un coefficient de frottement,
            - slope : une pente fournie (default: 0.001),

        ainsi que les relations correspondant aux pentes aval(slope down), amont(slopeup), et amont-aval (centered).
        """
        if self.down is not None and self.up is not None:
            slopeup,slopecentered,slopedown = self.slopes()
        else:
            slopecentered = 0
            slopedown = 0
            slopeup = 0

        if nManning==0. and KStrickler==0.:
            return
        elif nManning>0.:
            coeff=1./nManning
        elif KStrickler>0.:
            coeff = KStrickler

        nn=len(self.waterdepth)


        sqrtslope = math.sqrt(slope)
        if slopedown > 0:
            sqrtslopedown= math.sqrt(slopedown)
        else:
            sqrtslopedown = 0.

        if slopecentered > 0:
            sqrtslopecentered= math.sqrt(slopecentered)
        else:
            sqrtslopecentered = 0.
        if slopeup > 0:
            sqrtslopeup= math.sqrt(slopeup)
        else:
            sqrtslopeup = 0.

        self.q_slope = asarray([coeff*(self.hyrdaulicradius[k]**(2/3))*sqrtslope*self.wetarea[k] for k in range (nn)])
        self.q_down=asarray([coeff * self.hyrdaulicradius[k]**(2./3.)*sqrtslopedown * self.wetarea[k] for k in range(nn)])
        self.q_up=asarray([coeff * self.hyrdaulicradius[k]**(2./3.)*sqrtslopeup * self.wetarea[k] for k in range(nn)])
        self.q_centered=asarray([coeff * self.hyrdaulicradius[k]**(2./3.)*sqrtslopecentered * self.wetarea[k] for k in range(nn)])
        return max(max(self.q_slope), max(self.q_down), max(self.q_up), max(self.q_centered), max(self.criticaldischarge))

    def plotcs_profile(self,
                       fig: Figure = None,
                       ax: Axes = None,
                       compare = None,
                       vecs : list = [],
                       col_structure: str ='none',
                       fwl: float = None,
                       fwd: float = None,
                       simuls:list=None,
                       show = False,
                       forceaspect= True,
                       plotlaz= True,
                       clear = True,
                       redraw=True ):
        """
        This method plots the physical geometry of the current cross section (profile).

           - If a reference profile (compare) is given, the method hatchs the differences with resepect to cuts and fills.
           - If forceaspect is activated, the x and y axes are plotted using the same scale, otherwise, the figure is anamorphosed.
           - fwl (for water level) and fwd (for water depth) allow the visualisation of a specific water level on the graph.
           - idsimul: list of available numerical simulations containing this profile,
           - zsimul: list of water level in the simulations.
           - col_structure colors the structure displayed.
        """

        idsimul=None
        zsimul=None
        if simuls is not None:
            if len(simuls)>0:
                idsimul = [cursimul[0] for cursimul in simuls]
                zsimul  = [cursimul[3] for cursimul in simuls]

        sl,sb,sr,zl,zb,zr = self.get_sz_banksbed()
        x,y = self.get_sz()

        if fwl is None:
            if fwd is None or fwd <= 0:
                fwd =0
                fwl= self.zmin+ fwd
            elif fwd > 0 :
                fwl = self.zmin + fwd

        elif fwl is not None:
            fwl = fwl
            fwd = fwl-self.zmin

        # Creation of a new ax for cleaning purposes in the wolfhece.Graphprofile.
        myax1 = ax
        if redraw:
            if clear:
                myax1.clear()

        # Additional drawings on the profile (plots)
        vec: vector
        max_z = [self.zmax] #Fo ylim
        for vec in  vecs:
            n = vec.nbvertices
            verts = vec.asnparray() # 2D array containing x,y corresponding x , z
            max_z.append(np.max( verts[:,1]))

            myax1.fill(verts[:,0], verts[:,1], color= col_structure, lw = 2, hatch = _('///'), edgecolor = 'black')


        #Plots
        myax1.plot(x,y,color=_('black'),lw=2)
        myax1.fill_between(x,y,linewidth= 2,label=_('River bed'), color=_('black'), alpha = 0.2)

        if compare is not None:
            compare_s, compare_z = compare.get_sz()

            # New methods fill & cuts
            # Altitude diferences
            z = y - compare_z
            # Length differences
            s = x[1:] - x[:-1]

            # Method to compute the interection of 2 segments
            def _slope(s1 = 0., z1 = 0., s2 = 0., z2 = 0.):
                m =(z1 - z2)/(s1-s2)
                return m

            def _intersect_s(s1,z1,slp1,  sref1, zref1,slpref1):
                intersection = zref1 - z1 + slp1*s1 -slpref1*sref1
                return intersection

            def _intersect_z(intersect_s, z1, s1, slp1):
                intersection = (intersect_s*slp1) + z1 -slp1*s1
                return intersection

            def _intersect_coords(smod1, zmod1,
                                  smod2, zmod2,
                                  sref1, zref1,
                                  sref2, zref2):

                if smod2 - smod1 == 0 or sref1 - sref2 == 0:
                    raise Exception('Kindly delete duplicated point(s) in your data.')  #FIXME How one could handle this elegantly?

                else:
                    slope_mod = (zmod2 - zmod1)/(smod2 - smod1) # slope modified
                    slope_ref = (zref2 - zref1)/(sref2 - sref1) # slope reference
                    s_int = (zref1 - zmod1 + slope_mod*smod1 - slope_ref*sref1)/(slope_mod - slope_ref)
                    z_int = zmod1 + slope_mod*(s_int -smod1)
                    return s_int, z_int

            # Method to compute the areas (scenarios)

            def _area_triangle(b = None, h = None):
                area = (b*h)/2
                return area

            def _area_trapezoid(b1 = None, b2 = None, h= None):
                area = ((b1+b2)/2)*h
                return area

            # Handling the 4 cases
            positive_trap = []
            negative_trap = []
            positive_tri = []
            negative_tri = []

            for i in range(len(z)-1):
                if z[i] ==0 and z[i+1] ==0:
                    a =0
                    positive_trap.append(a)

                if z[i] > 0. and  z[i+1] > 0.:
                    a = _area_trapezoid(b1=z[i], b2=z[i+1], h = s[i])
                    positive_trap.append(a)

                if z[i] < 0. and z[i+1] < 0.:
                    a = _area_trapezoid(b1=z[i], b2=z[i+1], h = s[i])
                    negative_trap.append(a)

                if z[i] >= 0. and z[i+1] < 0. or z[i] > 0. and z[i+1] <= 0.:
                    #s_inter, z_inter = _intersect_coords(smod=s_x[i], zmod=z_y[i], sref =sref_x[i], zref = zref_y[i])
                    s_inter, z_inter = _intersect_coords(smod1 = x[i], zmod1 = y[i],
                                                         smod2 = x[i+1], zmod2 = y[i+1],
                                                         sref1 = compare_s[i], zref1 = compare_z[i],
                                                         sref2 = compare_s[i+1], zref2 = compare_z[i+1])
                    a_fill = (z[i] *(s_inter - compare_s[i]))/2
                    a_cut = (z[i+1]*(compare_s[i+1] - s_inter))/2
                    positive_tri.append(a_fill)
                    negative_tri.append(a_cut)

                if z[i] <= 0. and  z[i+1]>0 or z[i] < 0. and  z[i+1]>=0:
                    s_inter, z_inter = _intersect_coords(smod1 = x[i], zmod1 = y[i],
                                                         smod2 = x[i+1], zmod2 = y[i+1],
                                                         sref1 = compare_s[i], zref1 = compare_z[i],
                                                         sref2 = compare_s[i+1], zref2 = compare_z[i+1])
                    a_fill = (z[i+1]*(compare_s[i+1] - s_inter))/2
                    a_cut = (z[i] *(s_inter - compare_s[i]))/2
                    positive_tri.append(a_fill)
                    negative_tri.append(a_cut)

            fill = sum(positive_trap) + sum(positive_tri)
            cut = sum(negative_trap) + sum(negative_tri)
            total_area = abs(cut) + abs(fill)
            balance = fill + cut
            myax1.annotate('earthmoving: %.2f $m^3/m$ \n balance: %.2f $m^3/m$'% (total_area, balance), (self.smax/2, self.zmax-1), fontsize = _('x-small'))

            myax1.plot(compare_s,compare_z,color=_('red'), lw=2, ls = _('dashed'), label =_('Reference'))

            myax1.fill_between(x, y, compare_z, where=(y < compare_z), interpolate= True,color =_('none'),\
                                alpha = 0.2, hatch = _('///'), edgecolor= _('red'), label =_('Cuts: %.2f $m^3/m$'%(cut)))

            myax1.fill_between(x,  y, compare_z,where=(y > compare_z), interpolate= True, color =_('red'),\
                                alpha = 0.2, hatch = _('///'), edgecolor= _('white'), label=_('Fill: %.2f $m^3/m$'%(fill)))




        #Banks
        if sl != -99999.:
            myax1.plot(sl,zl,_('om'), label= _('Left bank'))
        if sb != -99999.:
            myax1.plot(sb,zb,_('ob'), label= _('River bed'))
        if sr != -99999.:
            myax1.plot(sr,zr,_('og'), label= _('Right bank'))

        #Available simulations
        if zsimul is not None:
            for i in range(len(zsimul)):
                myax1.axhline(y=zsimul[i], color=_('blue'), alpha=0.7, lw=1, label =_('Simulation'), ls =_('dashed'))
                myax1.annotate(idsimul[i], (self.smax/2, zsimul[i] +0.1 ), alpha=0.7 , fontsize = _('xx-small'), color=_('blue'))

        #Displayed water level
        myax1.fill_between(x,y, fwl, where= y < fwl ,facecolor=_('cyan'),alpha=0.3,interpolate=True)

        #Figure parameter
        if zsimul is not None:
            myax1.set_ylim(self.zmin, max(self.zmax +1, max(zsimul) + 1, max(max_z)+1))   #In case the water level in a simulation is above the maximum altitude of the profile.

        elif max_z != []:
            myax1.set_ylim(self.zmin, max(self.zmax, max(max_z)+1))

        else:
            myax1.set_ylim(self.zmin, self.zmax +1)

        myax1.set_xlim(min(x), max(x))
        myax1.set_xlabel(_('Section Width ($m$)'), size=12)
        myax1.set_ylabel(_('Altitude - Z \n($m$)'), size=12)

        ## equal aspect between axis
        if forceaspect:
            myax1.set_aspect(_('equal'), adjustable=_('box'))

        ## Second Y - axis --> relationship functions
        def alt_to_depth(y):
            return y-self.zmin
        def depth_to_alt(y):
            return y+self.zmin

        secax = myax1.secondary_yaxis(_('right'), functions=(alt_to_depth, depth_to_alt))

        myax1.grid(axis=_('y'), ls= _('--'))

        if show:
            fig.show()

        return sl, sb, sr, zl, zb, zr

    def plotcs_discharges(self,
                          fig: Figure = None,
                          ax: Axes = None,
                          fwl: float = None,
                          fwd: float = None,
                          fwq: float = None,
                          simuls:list=None,
                          show = False,
                          clear = True,
                          labels = True,
                          redraw =True):
        """
        This method plots the discharges relationship computed
        with the methods: relations and ManningStrcikler_profile.

        - fwl: for water level,
        - fwd: for water depth,
        - fwq: for water discharge,
        - idsimul: list of available numerical models.
        - qsimul: list of discharges in the available numerical models,
        - hsimul: list of water depth in the available numerical models.
        """

        hsimul  = None
        qsimul  = None
        idsimul = None
        if simuls is not None:
            if len(simuls)>0:
                hsimul = [cursimul[2] for cursimul in simuls]
                qsimul = [cursimul[1] for cursimul in simuls]
                idsimul= [cursimul[0] for cursimul in simuls]


        sl,sb,sr,zl,zb,zr = self.get_sz_banksbed()
        x,y = self.get_sz()

        if fwl is None:
            if fwd is None or fwd <= 0:
                fwd =0
                fwl= self.zmin+ fwd
            elif fwd > 0 :
                fwl = self.zmin + fwd

        elif fwl is not None:
            fwl = fwl
            fwd = fwl-self.zmin

        # Creation of a new ax for cleaning purposes in the wolfhece.Graphprofile.
        myax2 = ax
        if redraw:
            if clear:
                myax2.clear()

        # Discharges in available numerical models
        if qsimul is not None and hsimul is not None:
            myax2.scatter(qsimul,hsimul + self.zmin, c=_('blue'), alpha= 0.8, label =_('Available models'))
            for i in range(len(qsimul)):
                myax2.annotate(idsimul[i], (qsimul[i], hsimul[i] + self.zmin), alpha= 0.8, fontsize = _('xx-small'),color =_('blue'))

        # plots
        myax2.plot(self.criticaldischarge,self.waterdepth + self.zmin,color=_('red'),lw=2.0,label=_('Critical Discharge ($m^3/s$)'), ls =_('dashed'))
        myax2.plot(self.q_slope,self.waterdepth + self.zmin ,color=_('black'),lw=2.0,label=_('Q - chosen slope'))

        # Other  curves are plotted only if the cross sections are sorted along the river bed.
        if self and self.down and self.up:
            myax2.plot(self.q_down,self.waterdepth + self.zmin,color=_('black'),lw=1.0,label=_('Q - slope (%s - %s)')%(self.myname,self.down.myname), alpha = 0.5, ls = _('dotted'))
            myax2.plot(self.q_up,self.waterdepth + self.zmin,color=_('black'),lw=1.0,label=_('Q slope (%s - %s)')%(self.up.myname,self.myname), alpha= 0.5, ls= _('--'))     #Plot the evolution of the uniform discharge as function of water depth
            myax2.plot(self.q_centered,self.waterdepth + self.zmin ,color=_('black'),lw=1.0,label=_('Q slope (%s -  %s)')%(self.up.myname,self.down.myname), alpha = 0.5, ls = _('-.'))

        # Displayed discharge
        if fwq is not None:
            myax2.axvline(x=fwq, color=_('blue'), alpha=1, lw=2, label =_(' QD - Desired discharge'))

        # River banks
        if zl and zr and zb:
            myax2.axhline(y=zl, color=_('magenta'), alpha=1, lw=1, label =_('Left bank'), ls =_('dotted'))
            myax2.axhline(y=zr, color=_('green'), alpha=1, lw=1, label =_('Right bank'), ls =_('dotted') )
            myax2.axhline(y=zb, color=_('blue'), alpha=1, lw=1, label =_('Bed'), ls =_('dotted'))

        # Desired water depth
        myax2.axhspan(ymin= self.zmin, ymax =fwl,color=_('cyan'), alpha=0.2, lw=2, label =_('Desired water depth'))

        myax2.set_xlabel(_('Discharge - Q ($m^3/s$)'), size=12)
        myax2.set_ylim(self.zmin, self.zmax+1)

        if qsimul is not None:
            myax2.set_xlim(0., max(max(self.q_down),max(self.q_up),max(self.q_centered),max(self.q_slope), max(self.criticaldischarge),max(qsimul)))
        else:
            myax2.set_xlim(0., max(max(self.q_down),max(self.q_up),max(self.q_centered),max(self.q_slope), max(self.criticaldischarge)))

        # Conversion methods for the second matplotlib ax
        def alt_to_depth(y):
            return y-self.zmin
        def depth_to_alt(y):
            return y+self.zmin

        secax = myax2.secondary_yaxis(_('right'), functions=(alt_to_depth,depth_to_alt))
        #secax.set_yticks(y)
        myax2.yaxis.tick_left()
        #myax2.set_yticks(alt_to_depth(self.waterdepth))
        #secax.set_yticks(self.waterdepth +self.ymin)

        #myax2.grid(axis= 'y' , ls= _('--'))

        myax2.grid(axis ='both')



        if labels:
            myax2.set_ylabel(_('Water depth - h\n($m$)'), size=12, rotation=270,labelpad=35)
            myax2.yaxis.set_label_position(_('right'))
            secax.set_ylabel(_('Altitude - Z\n($m$)'), size=12, labelpad=10)
            fig.suptitle('Discharges C.S. - %s'%(self.myname), size=15)


        if show:
            fig.show()

    def plotcs_hspw(self, fig: Figure = None, ax: Axes = None, fwl: float = None, fwd: float = None, fwq: float = None, show = False, clear = True, labels = True,redraw =True):

        """
        This method plots the hydraulic geometries computed by the relations method
        (Hydraulic radius, wetted area, wetted perimeter, Top width).

        - fwl: for water level,
        - fwd: for water depth,
        - fwq: for water discharge.

        """
        sl,sb,sr,zl,zb,zr = self.get_sz_banksbed()
        x,y = self.get_sz()

        if fwl is None:
            if fwd is None or fwd <= 0:
                fwd =0
                fwl= self.zmin+ fwd
            elif fwd > 0 :
                fwl = self.zmin + fwd

        elif fwl is not None:
            fwl = fwl
            fwd = fwl-self.zmin

        # Creation of a new ax for cleaning purposes in the wolfhece.Graphprofile.
        myax3 = ax
        axt3 = ax
        if redraw:
            if clear:
                axt3.clear()
                # myax3.clear()

        # Plots
        # FIXME (Clearing issues) a second x axis for the Hydraulic radius to provide more clarity.
        axt3.plot(self.hyrdaulicradius,self.waterdepth + self.zmin,color=_('green'),lw=2,label=_('H - Hydraulic radius($m$)'), ls= _('--')) #Plot the evaluation of the hydraulic radius as function of water depth
        axt3.set_xlim(0, max(self.hyrdaulicradius))

        myax3.plot(self.wetarea,self.waterdepth + self.zmin,color=_('black'),lw=2.0,label=_('S - Wet area ($m^2$)'))          #Plot the wetted area as function of water depth
        myax3.plot(self.wetperimeter,self.waterdepth + self.zmin,color=_('magenta'),lw=1,label=_('P -  Wet perimeter($m$)'))  #Plot the wetted perimeter as function of water depth
        myax3.plot(self.localwidth,self.waterdepth + self.zmin,color=_('red'),lw=1,label=_('W - Top Width ($m$)'))      #Plot the evalution of the water table as function of water depth

        # Selection of hydraulic geometries based on their index
        if fwq is not None and fwq > 0.:
            # First, We select the closest critical discharge to the user's input.
            mask = np.absolute(self.criticaldischarge - fwq)
            index  = np.argmin(mask)
            # Second, since the matrices have the same shapes and their elements are sorted likewise,
            # we use the index of the selected critical discharge to find the corresponding hydraulic geometries.
            cr_wetarea = self.wetarea[index]
            cr_wetperimeter = self.wetperimeter[index]
            cr_width = self.localwidth[index]
            cr_radius = self.hyrdaulicradius[index]
            cr_h = self.waterdepth[index]
            myax3.plot(cr_wetarea,cr_h + self.zmin,'ok' )
            myax3.annotate(_('$Critical$ $characteristics$ \nH: %s $m$ \nS: %s $m^2$ \nP: %s $m$ \nW: %s $m$  \n \n')% (round(cr_radius,2),round(cr_wetarea,2),round(cr_wetperimeter,2),round(cr_width,2)),\
                 (cr_wetarea, cr_h + self.zmin),  alpha= 1, fontsize = _('x-small'),color =_('black'))

            #Finally, we plot the critical hydraulic geometries as dots.
            myax3.plot(cr_wetperimeter,cr_h + self.zmin,_('om') )
            myax3.plot(cr_width,cr_h + self.zmin,_('or') )
            myax3.plot(cr_radius,cr_h + self.zmin,_('og') )

        #Displayed water depths and banks
        myax3.axhspan(ymin= self.zmin, ymax =fwd + self.zmin,color=_('cyan'), alpha=0.2, lw=2, label =_('Desired water depth'))
        myax3.axhline(y=zl, color=_('magenta'), alpha=1, lw=1, label =_('Left bank'), ls =_('dotted') )
        myax3.axhline(y=zr, color=_('green'), alpha=1, lw=1, label =_('right bank'), ls =_('dotted') )
        myax3.axhline(y=zb, color=_('blue'), alpha=1, lw=1, label =_(' bed '), ls =_('dotted'))

        #Limits and labels
        myax3.set_ylim(self.zmin,self.zmax+1)
        myax3.set_xlim(0., max(max(self.wetarea), max(self.wetperimeter), max(self.localwidth)))
        myax3.set_xlabel(_('S - P - W'), size=12)
        myax3.set_ylabel(_('Water depth - h\n($m$)'), size=12,rotation=270, labelpad=50)

        #Conversion methods for the second y axis
        def alt_to_depth(y):
            return y-self.zmin
        def depth_to_alt(y):
            return y+self.zmin
        secax = myax3.secondary_yaxis(_('right'), functions=(alt_to_depth,depth_to_alt))

        myax3.yaxis.tick_left()
        myax3.yaxis.set_label_position(_('right'))
        if labels:
            secax.set_ylabel(_('Altitude - Z ($m$)'), size=12, rotation=270, labelpad=20)
        myax3.grid()

        if show:
            fig.show()



class crosssections(Element_To_Draw):
    """
    Gestion de sections en travers pour différents formats
        - SPW 2000 --> format ='2000'
        - SPW 2022 --> format ='2022'
        - WOLF vecz --> format ='vecz'
        - WOLF sxy --> format ='sxy'

    L'objet stocke ses informations dans un dictionnaire : self.myprofiles
    Les clés de chaque entrée sont:
        ['index']   : integer
        ['left']    : wolfvertex
        ['bed']     : wolfvertex
        ['right']   : wolfvertex
        ['cs']      : profile (surcharge de vector)

    Pour le moment, il est possible de lire les fichiers et d'effectuer cerrains traitements (tri selon vecteur, export gltf...).

    Une instance de cet objet peut être ajouté à une instance graphique WOLF pour affichage.
    Pour ce faire:
        - une propriété "myzones" de type "Zones" est présente pour stocker les sections sous forme WOLF "ZONES/ZONE/VECTOR/VERTICES". --> "crosssections" n'est donc pas une extension de "Zones" !!
        - deux instances de "cloud_vertices" contiennent les vertices des sections :
            - cloud
            - cloud_all

    :remark !! La classe n'est pas encore prévue pour créer des sections en travers!!

    """

    myprofiles:dict
    mygenprofiles:dict

    def __init__(self,
                 myfile:str = '',
                 format:typing.Literal['2000','2022','vecz','sxy']='2022',
                 dirlaz:typing.Union[str, xyz_laz_grids] =r'D:\OneDrive\OneDrive - Universite de Liege\Crues\2021-07 Vesdre\CSC - Convention - ARNE\Data\LAZ_Vesdre\2023',
                 mapviewer = None,
                 idx='',
                 plotted=True) -> None:


        super().__init__(idx=idx, plotted= plotted, mapviewer=mapviewer, need_for_wx=False)

        self.filename=myfile
        self.myzones=None
        self.myzone=None

        if isinstance(dirlaz,str):
            if path.exists(dirlaz):
                self.dirlaz=dirlaz
                self.gridlaz = xyz_laz_grids(self.dirlaz)
            else:
                self.dirlaz=''
                self.gridlaz =None

        elif isinstance(dirlaz,xyz_laz_grids):
            self.gridlaz = dirlaz
            self.dirlaz = 'instance xyz_laz_grids'

        self.format = None

        self.linked_zones=None

        if format in ['2000','2022','sxy']:
            self.filename=myfile
            if Path(myfile).exists() and myfile!='':
                f=open(myfile,'r')
                lines=f.read().splitlines()
                f.close()
        # For other formats (e.g.  vecz)
        else:
            lines=[]

        self.myprofiles={}
        self.mygenprofiles={}

        self.cloud = None
        self.cloud_all = None

        self.multils = None
        self.sorted = {}
        self.plotted = False

        if len(lines)>0:
            if format=='2000':
                self.format='2000'
                lines.pop(0)
                nameprev=''
                index=0
                for curline in lines:
                    vals=curline.split('\t')
                    name=vals[0]

                    if name!=nameprev:
                        #création d'un nouveau dictionnaire
                        self.myprofiles[name]={}
                        curdict=self.myprofiles[name]
                        curdict['index']=index
                        index+=1
                        curdict['cs']=profile(name=name,parent=self)
                        cursect:profile
                        cursect=curdict['cs']

                    x=float(vals[1])
                    y=float(vals[2])
                    type=vals[3]
                    z=float(vals[4])

                    curvertex=wolfvertex(x,y,z)
                    cursect.add_vertex(curvertex)
                    if type=='LEFT':
                        if cursect.bankleft is None:
                            cursect.bankleft=wolfvertex(x,y,z)
                            curdict['left']=cursect.bankleft
                        else:
                            logging.debug(name)
                    elif type=='BED':
                        if cursect.bed is None:
                            cursect.bed=wolfvertex(x,y,z)
                            curdict['bed']=cursect.bed
                        else:
                            logging.debug(name)
                    elif type=='RIGHT':
                        if cursect.bankright is None:
                            cursect.bankright=wolfvertex(x,y,z)
                            curdict['right']=cursect.bankright
                        else:
                            logging.debug(name)

                    nameprev=name
            elif format=='2022':
                self.format='2022'
                lines.pop(0)
                nameprev=''
                index=0
                for curline in lines:
                    vals=curline.split('\t')

                    if vals[0].find('.')>0:
                        name=vals[0].split('.')[0]
                        xpos=1
                        ypos=xpos+1
                        zpos=ypos+1
                        labelpos=zpos+1
                    else:
                        name=vals[0]
                        xpos=2
                        ypos=xpos+1
                        zpos=ypos+1
                        labelpos=zpos+1

                    if name!=nameprev:
                        #création d'un nouveau dictionnaire
                        self.myprofiles[name]={}
                        curdict=self.myprofiles[name]
                        curdict['index']=index
                        index+=1
                        curdict['cs']=profile(name=name,parent=self)
                        cursect:profile
                        cursect=curdict['cs']

                    x=float(vals[xpos].replace(',','.'))
                    y=float(vals[ypos].replace(',','.'))
                    z=float(vals[zpos].replace(',','.'))

                    curvertex=wolfvertex(x,y,z)
                    cursect.add_vertex(curvertex)

                    type=''
                    type=vals[labelpos]

                    if type=='HBG':
                        if cursect.bankleft is None:
                            cursect.bankleft=wolfvertex(x,y,z)
                            curdict['left']=cursect.bankleft
                        else:
                            logging.debug(name)
                    elif type=='TWG':
                        if cursect.bed is None:
                            cursect.bed=wolfvertex(x,y,z)
                            curdict['bed']=cursect.bed
                        else:
                            logging.debug(name)
                    elif type=='HBD':
                        if cursect.bankright is None:
                            cursect.bankright=wolfvertex(x,y,z)
                            curdict['right']=cursect.bankright
                        else:
                            logging.debug(name)

                    nameprev=name
            elif format=='sxy':
                self.format='sxy'
                nbpotsect = int(lines[0])
                index=1
                for i in range(nbpotsect):
                    vals=lines[index].split(',')
                    nbrel=int(vals[0])
                    index+=1
                    sz = np.asarray([np.float64(cursz) for k in range(index,index+nbrel) for cursz in lines[k].split(',') ]).reshape([nbrel,2],order='C')
                    self.mygenprofiles[i+1]=sz
                    index+=nbrel

                nbsect = int(lines[index])
                # o linked position in a 2D array (i, j) (integer,integer) (optional)
                # o datum (float) – added to the Z_min of the raw cross section (optional)
                # o boolean value indicating whether the relative datum must be added (logical)
                # o boolean value indicating whether it is a real or synthetic section (logical)
                # o ID of the cross section to which this line relates (integer)
                # o pair of coordinates of the left end point (float, float)
                # o pair of coordinates of the right end point (float, float)
                # o pair of coordinates of the minor bed (float, float) (optional)
                # o pair of coordinates of the left bank in local reference (float, float) (optional)
                # o pair of coordinates of the right bank in local reference (float, float) (optional)
                # o boolean value indicating whether an attachment point has been defined (optional)
                # # 2,2,0,#FALSE#,#TRUE#,16,222075.5,110588.5,222331.5,110777.5,99999,99999,99999,99999,99999,99999,#FALSE#
                # 2,2,0,#FALSE#,#TRUE#,17,222131.6,110608.2,222364.4,110667.9,99999,99999,99999,99999,99999,99999,#FALSE#
                index+=1
                #création d'un nouveau dictionnaire
                for i in range(nbsect):
                    name=str(i+1)
                    vals=lines[index].split(',')
                    index+=1

                    posi = int(vals[0])
                    posj = int(vals[1])
                    zdatum = float(vals[2])
                    add_zdatum=vals[3]=='#TRUE#'
                    real_sect=vals[4]=='#TRUE#'
                    id = int(vals[5])
                    startx=float(vals[6])
                    starty=float(vals[7])
                    endx=float(vals[8])
                    endy=float(vals[9])
                    beds=float(vals[10])
                    bedz=float(vals[11])
                    lbs=float(vals[12])
                    lbz=float(vals[13])
                    rbs=float(vals[14])
                    rbz=float(vals[15])
                    attached=vals[16]=='#TRUE#'

                    curdict=self.myprofiles[name]={}
                    curdict['index']=id
                    curdict['cs']=profile(name=name,parent=self)
                    cursect:profile
                    cursect=curdict['cs']

                    cursect.zdatum = zdatum
                    cursect.add_zdatum = add_zdatum

                    cursect.set_sz(self.mygenprofiles[id],[[startx,starty],[endx,endy]])

                    if lbs!=99999:
                        cursect.bankleft=wolfvertex(lbs,lbz)
                        curdict['left']=cursect.bankleft
                    if beds!=99999:
                        cursect.bed=wolfvertex(beds,bedz)
                        curdict['bed']=cursect.bed
                    if rbs!=99999:
                        cursect.bankright=wolfvertex(rbs,rbz)
                        curdict['right']=cursect.bankright

        # To make a distinction between cases for vecz
        elif len(lines)==0:
            if format=='vecz' or format=='zones':

                if isinstance(myfile, Zones):
                    self.filename=myfile.filename
                    tmpzones=myfile
                elif isinstance(myfile, str):
                    self.filename=myfile
                    tmpzones=Zones(myfile, find_minmax=False)

                curzone:zone
                curvec:vector
                curzone=tmpzones.myzones[0]
                index=0
                for curvec in curzone.myvectors:

                    self.myprofiles[curvec.myname]={}
                    curdict=self.myprofiles[curvec.myname]

                    curdict['index']=index
                    curdict['left']=None
                    curdict['bed']=None
                    curdict['right']=None

                    index+=1
                    curdict['cs']=profile(name=curvec.myname,parent=self)
                    cursect:profile
                    cursect=curdict['cs']

                    cursect.myvertices = curvec.myvertices

        self.verif_bed()
        self.find_minmax(True)
        self.init_cloud()

    def init_cloud(self):

        self.cloud = cloud_vertices()
        self.cloud_all = cloud_vertices()
        self.fillin_cloud_all()

        self.cloud.myprop.filled=True
        self.cloud.myprop.width=8
        self.cloud_all.myprop.filled=True
        self.cloud_all.myprop.width=4

    def add(self, newprofile:profile | vector):

        if isinstance(newprofile, profile):
            curvec = newprofile
            curdict = self.myprofiles[newprofile.myname] = {}

            curdict['index']=len(self.myprofiles)
            curdict['cs'] = newprofile
            curdict['left']= newprofile.bankleft_vertex.copy()
            curdict['bed']= newprofile.bed_vertex.copy()
            curdict['right']=newprofile.bankright_vertex.copy()

        elif isinstance(newprofile, vector):
            curvec = newprofile
            curdict = self.myprofiles[curvec.myname] = {}

            curdict['index']=len(self.myprofiles)
            curdict['left']=None
            curdict['bed']=None
            curdict['right']=None

            cursect = curdict['cs'] = profile(name=curvec.myname,parent=self)
            cursect.myvertices = curvec.myvertices

    def get_linked_arrays(self):
        """
        Passerelle pour obntenir les matrices liées
        """
        if self.mapviewer is not None:
            return self.mapviewer.get_linked_arrays()
        else:
            return {}

    def get_profile(self, which_prof, which_dict:str=None):
        """
        Recherche et renvoi d'un profil sur base du nom ou de son index et éventuellement de la liste triée
        """
        if which_dict is not None:
            # on travaille sur les vecteurs triés
            if which_dict in self.sorted.keys():
                curlist = self.sorted[which_dict]['sorted']
                if isinstance(which_prof, str):
                    keys = [curprof.myname for curprof in curlist]
                    if which_prof in keys:
                        return curlist[keys.index(which_prof)]
                elif isinstance(which_prof, int):
                    return curlist[which_prof]

        else:
            if isinstance(which_prof, str):
                keys = self.myprofiles.keys()
                if which_prof in keys:
                    return self.myprofiles[which_prof]['cs']
            elif isinstance(which_prof, int):
                return self.myprofiles[list(self.myprofiles.keys())[which_prof]]['cs']

        return None

    def fillin_cloud_all(self):

        curprof:profile
        for idx,vect in self.myprofiles.items():
            curprof=vect['cs']
            for curvert in curprof.myvertices:
                self.cloud_all.add_vertex(curvert)

        self.cloud_all.find_minmax()

    def update_cloud(self):

        curprof:profile
        for idx,vect in self.myprofiles.items():
            curprof=vect['cs']
            if not curprof.bankleft is None:
                myvert = wolfvertex(curprof.bankleft.x,curprof.bankleft.y)
                self.cloud.add_vertex(myvert)
            if not curprof.bankright is None:
                myvert = wolfvertex(curprof.bankright.x,curprof.bankright.y)
                self.cloud.add_vertex(myvert)
            if not curprof.bed is None:
                myvert = wolfvertex(curprof.bed.x,curprof.bed.y)
                self.cloud.add_vertex(myvert)

            for idx,curvert in curprof.refpoints.items():
                self.cloud.add_vertex(curvert)

        self.cloud.find_minmax(True)

    def create_zone_from_banksbed(self):

        if self.linked_zones is None:
            return

        bed = [curs['cs'].bed for idx,curs in self.myprofiles.items()]
        left = [curs['cs'].bankleft for idx,curs in self.myprofiles.items()]
        right = [curs['cs'].bankright for idx,curs in self.myprofiles.items()]

        newzone=zone(name='banksbed',parent=self.linked_zones,is2D=False)
        self.linked_zones.add_zone(newzone)

        newvec = vector(name='left',is2D=False,parentzone=newzone)
        newvec.myvertices=left
        newzone.add_vector(newvec)

        newvec = vector(name='bed',is2D=False,parentzone=newzone)
        newvec.myvertices=bed
        newzone.add_vector(newvec)

        newvec = vector(name='right',is2D=False,parentzone=newzone)
        newvec.myvertices=right
        newzone.add_vector(newvec)

    def link_external_zones(self,mylink:Zones):
        self.linked_zones = mylink
        self.find_intersect_with_link_zones()

    def find_intersect_with_link_zones(self):

        if self.linked_zones is None:
            return

        which=['THA','HBG','HBD']
        linkprop=['bed','left','right']

        for curzone in self.linked_zones.myzones:
            curzone:zone
            for myvec in curzone.myvectors:
                myvec:vector

                if myvec.myname in which:
                    curlinkprop = linkprop[which.index(myvec.myname)]
                else:
                    curlinkprop = myvec.myname

                myvecls = myvec.asshapely_ls()
                prepls=prep(myvecls)

                for cursname in self.myprofiles.values():
                    curs:profile
                    curs=cursname['cs']
                    cursls = curs.asshapely_ls()
                    if prepls.intersects(cursls):
                        pt = myvecls.intersection(cursls)

                        if pt.geom_type=='MultiPoint':
                            pt=pt.geoms[0]
                        elif pt.geom_type=='GeometryCollection':
                            pt=pt.centroid

                        try:
                            myvert=wolfvertex(pt.x,pt.y,pt.z)
                        except:
                            myvert=wolfvertex(pt.x,pt.y)

                        if curlinkprop=='bed':
                            curs.bed = myvert
                        elif curlinkprop=='left':
                            curs.bankleft = myvert
                        elif curlinkprop=='right':
                            curs.bankright = myvert
                        else:
                            curs.refpoints[curlinkprop]=myvert

                        cursname[curlinkprop]=myvert

        self.update_cloud()

    def export_gltf(self,zmin,fn=''):

        points=[]
        triangles=[]
        incr=0

        curs:profile
        for cursname in self.myprofiles.values():
            curs=cursname['cs']
            m, n = curs.triangulation_gltf(zmin)
            points.append(np.asarray(m,dtype=np.float32))
            triangles.append(np.asarray(n,dtype=np.uint32)+incr)
            incr += len(m)

        points = np.concatenate(points)

        tmpy=points[:,1].copy()
        points[:,1] = points[:,2].copy()
        points[:,2] = -tmpy.copy()
        triangles = np.concatenate(triangles)

        triangles_binary_blob = triangles.flatten().tobytes()
        points_binary_blob = points.tobytes()

        gltf = pygltflib.GLTF2(
            scene=0,
            scenes=[pygltflib.Scene(nodes=[0])],
            nodes=[pygltflib.Node(mesh=0)],
            meshes=[
                pygltflib.Mesh(
                    primitives=[
                        pygltflib.Primitive(
                            attributes=pygltflib.Attributes(POSITION=1), indices=0
                        )
                    ]
                )
            ],
            accessors=[
                pygltflib.Accessor(
                    bufferView=0,
                    componentType=pygltflib.UNSIGNED_INT,
                    count=triangles.size,
                    type=pygltflib.SCALAR,
                    max=[int(triangles.max())],
                    min=[int(triangles.min())],
                ),
                pygltflib.Accessor(
                    bufferView=1,
                    componentType=pygltflib.FLOAT,
                    count=len(points),
                    type=pygltflib.VEC3,
                    max=points.max(axis=0).tolist(),
                    min=points.min(axis=0).tolist(),
                ),
            ],
            bufferViews=[
                pygltflib.BufferView(
                    buffer=0,
                    byteLength=len(triangles_binary_blob),
                    target=pygltflib.ELEMENT_ARRAY_BUFFER,
                ),
                pygltflib.BufferView(
                    buffer=0,
                    byteOffset=len(triangles_binary_blob),
                    byteLength=len(points_binary_blob),
                    target=pygltflib.ARRAY_BUFFER,
                ),
            ],
            buffers=[
                pygltflib.Buffer(
                    byteLength=len(triangles_binary_blob) + len(points_binary_blob)
                )
            ],
        )
        gltf.set_binary_blob(triangles_binary_blob + points_binary_blob)

        if fn=='':
            fn=self.filename.rpartition('.')[0]+'gltf'

        gltf.save(fn)

    def export_gltf_gen(self,points,triangles,fn=''):

        triangles_binary_blob = triangles.flatten().tobytes()
        points_binary_blob = points.tobytes()

        gltf = pygltflib.GLTF2(
            scene=0,
            scenes=[pygltflib.Scene(nodes=[0])],
            nodes=[pygltflib.Node(mesh=0)],
            meshes=[
                pygltflib.Mesh(
                    primitives=[
                        pygltflib.Primitive(
                            attributes=pygltflib.Attributes(POSITION=1), indices=0
                        )
                    ]
                )
            ],
            accessors=[
                pygltflib.Accessor(
                    bufferView=0,
                    componentType=pygltflib.UNSIGNED_INT,
                    count=triangles.size,
                    type=pygltflib.SCALAR,
                    max=[int(triangles.max())],
                    min=[int(triangles.min())],
                ),
                pygltflib.Accessor(
                    bufferView=1,
                    componentType=pygltflib.FLOAT,
                    count=len(points),
                    type=pygltflib.VEC3,
                    max=points.max(axis=0).tolist(),
                    min=points.min(axis=0).tolist(),
                ),
            ],
            bufferViews=[
                pygltflib.BufferView(
                    buffer=0,
                    byteLength=len(triangles_binary_blob),
                    target=pygltflib.ELEMENT_ARRAY_BUFFER,
                ),
                pygltflib.BufferView(
                    buffer=0,
                    byteOffset=len(triangles_binary_blob),
                    byteLength=len(points_binary_blob),
                    target=pygltflib.ARRAY_BUFFER,
                ),
            ],
            buffers=[
                pygltflib.Buffer(
                    byteLength=len(triangles_binary_blob) + len(points_binary_blob)
                )
            ],
        )
        gltf.set_binary_blob(triangles_binary_blob + points_binary_blob)

        if fn=='':
            fn=self.filename.rpartition('.')[0]+'gltf'

        gltf.save(fn)

    def set_zones(self, forceupdate:bool=False):
        if forceupdate:
            self.myzone=None
            self.myzones=None

        if self.myzones is None:
            self.myzones=Zones(is2D=False, mapviewer=self.mapviewer)
            self.myzones.force3D=True
            self.myzone=zone(name='CS',parent=self.myzones)
            self.myzones.add_zone(self.myzone)

            for curprof in self.myprofiles.keys():
                curdict=self.myprofiles[curprof]
                curprof=curdict['cs']
                self.myzone.add_vector(curprof)
                curprof.parentzone=self.myzone

            if self.plotted:
                self._prep_listogl()  #FIXME : Does not work in the context of a 1D model

    def showstructure(self, parent=None, forceupdate=False):
        self.set_zones()
        self.myzones.showstructure(parent, forceupdate)

    def get_upstream(self) -> dict:
        curprof:profile
        curprof=self.myprofiles[list(self.myprofiles.keys())[0]]['cs']

        while curprof.up is not curprof:
            curprof = curprof.up

        return self.myprofiles[curprof.myname]

    def get_downstream(self) -> dict:
        curprof:profile
        curprof=self.myprofiles[list(self.myprofiles.keys())[0]]['cs']

        while curprof.down is not curprof:
            curprof = curprof.down

        return self.myprofiles[curprof.myname]

    def rename(self,fromidx,updown=True):

        idx=fromidx

        if updown:
            curdict=self.get_upstream()
            curvec:profile
            curvec=curdict['cs']
            while curvec.down is not curvec:
                self.myprofiles[idx]=curdict
                self.myprofiles.pop(curvec.myname)
                curvec.myname=str(idx)
                idx+=1

                curdict = self.myprofiles[curvec.down.myname]
                curvec=curvec.down

            self.myprofiles[idx]=curdict
            self.myprofiles.pop(curvec.myname)
            curvec.myname=str(idx)
        else:
            mykeys=list(self.myprofiles.keys())
            for curprof in mykeys:
                curdict=self.myprofiles[idx]=self.myprofiles[curprof]
                self.myprofiles.pop(curprof)
                curdict['cs'].myname=str(idx)
                idx+=1

        self.set_zones(True)

    def saveas(self,filename=None):
        self.forcesuper=False

        if filename is not None:
            self.filename = filename

        if self.filename is None:
            logging.error(_('No Filename -- Retry !'))
            return

        if self.filename.endswith('.vecz'):
            self.forcesuper=True
            self.saveas_wolfvec(self.filename)
        elif self.format=='2000' or self.format=='2022':
            with open(self.filename,'w') as f:
                f.write("Profile\tx\ty\tBerge\tz\n")
                for idx,curvect in self.myprofiles.items():
                    curprof=curvect['cs']
                    curprof.save(f)
        elif self.format=='sxy':
            with open(self.filename,'w') as f:
                f.write(str(len(self.mygenprofiles)))
                for curid in self.mygenprofiles.keys():
                    cursect = self.mygenprofiles[curid]
                    f.write('{n},0'.format(n=len(cursect)))
                    for xy in cursect:
                        f.write('{x},{y}'.format(x=xy[0],y=xy[1]))
                f.write(str(len(self.myprofiles)))
                for curid in self.myprofiles.keys():
                    curdict = self.myprofiles[curid]
                    cursect:profile
                    cursect = curdict['cs']
                    locid=curdict['index']

                    f.write('2,2,{zdatum},{add_datum},#TRUE#,{id},{x1},{y1},{x2},{y2},{beds},{bedz},{lbs},{lbz},{rbs},{rbz},#FALSE#'.format(
                                    zdatum=xy[0],
                                    add_datum=xy[1],
                                    id=locid,
                                    x1=cursect.myvertices[0].x,
                                    y1=cursect.myvertices[0].y,
                                    x2=cursect.myvertices[-1].x,
                                    y2=cursect.myvertices[-1].y,
                                    beds=cursect.get_s_from_xy(cursect.bed),
                                    bedz=cursect.bed.z,
                                    lbs=cursect.get_s_from_xy(cursect.bankleft),
                                    lbz=cursect.bankleft.z,
                                    rbs=cursect.get_s_from_xy(cursect.bankright),
                                    rbz=cursect.bankright.z))

    def verif_bed(self):
        """Verification de l'existence du point lit mineur sinon attribution de l'altitude minimale"""
        for idx,curvect in self.myprofiles.items():
            curprof=curvect['cs']
            if curprof.bed is None:
                curprof.bed = curprof.get_min()

    def get_min(self,whichname='',whichprofile=None):
        curvect:profile
        if whichname!='':
            curvect=self.myprofiles[whichname]['cs']
            curvert=curvect.myvertices
        elif not whichprofile is None:
            curvect=whichprofile['cs']
            curvert=curvect.myvertices
        return sorted(curvert,key=lambda x:x.z)[0]

    def asshapely_ls(self):
        mylines=[]
        curvect:profile
        for idx,curvect in self.myprofiles.items():
            mylines.append(curvect['cs'].asshapely_ls())
        return MultiLineString(mylines)

    def prepare_shapely(self):
        self.multils = self.asshapely_ls()

    def sort_along(self,vecsupport:LineString,name:str,downfirst=True):
        """
        Sélectionne les sections qui intersectent un vecteur support
        et les trie selon l'abscisse curviligne
        """

        curdict = self.sorted[name]={}
        curdict['support'] = vecsupport
        mysorted = curdict['sorted']  = []
        length = vecsupport.length

        prepsup=prep(vecsupport) #Prepare le vecteur support aux opérations récurrentes
        curvect:profile
        for idx,curv in self.myprofiles.items():
            #bouclage sur les sections
            curvect=curv['cs']
            #obtention de la section sous forme d'un objet Shapely
            myline = curvect.asshapely_ls()
            if prepsup.intersects(myline):
                #le vecteur intersecte --> on calcule le point d'intersection
                myintersect = vecsupport.intersection(myline)
                #on projette l'intersection sur le support pour trouver l'abscisse curvi
                mydist = vecsupport.project(myintersect)
                #on ajoute le vecteur à la liste
                mysorted.append(curvect)
                if downfirst:
                    curvect.s = length - mydist
                else:
                    curvect.s = mydist

        #on trie le résultat en place
        mysorted.sort(key=lambda x:x.s)

        mysorted[0].down = mysorted[1]
        mysorted[0].up = mysorted[0]
        mysorted[-1].up = mysorted[-2]
        mysorted[-1].down = mysorted[-1]
        for idx in arange(1,len(mysorted)-1):
            mysorted[idx].down = mysorted[idx+1]
            mysorted[idx].up = mysorted[idx-1]

        return len(mysorted)

    def find_minmax(self, update:bool=False):

        if len(self.myprofiles)==0:
            self.xmin = 0
            self.ymin = 0
            self.xmax = 0
            self.ymax = 0
            return
        
        if update:
            for idx,vect in self.myprofiles.items():
                vect['cs'].find_minmax(only_firstlast = True)

        self.xmin = min(vect['cs'].xmin for idx,vect in self.myprofiles.items())
        self.ymin = min(vect['cs'].ymin for idx,vect in self.myprofiles.items())
        self.xmax = max(vect['cs'].xmax for idx,vect in self.myprofiles.items())
        self.ymax = max(vect['cs'].ymax for idx,vect in self.myprofiles.items())

    def plot(self, sx=None, sy=None, xmin=None, ymin=None, xmax=None, ymax=None, size=None):
        """ Plotting cross-sections """
        self.set_zones()
        self.myzones.plot(sx, sy, xmin, ymin, xmax, ymax, size)

    def _prep_listogl(self):
        """ Prepare list of GL objects """
        self.myzones.prep_listogl()

    def saveas_wolfvec(self,filename:str):

        self.set_zones()
        self.myzones.saveas(filename=filename)

    def select_profile(self,x,y):

        mypt = Point(x,y)
        distmin=1.e300
        profmin=None

        curprof:profile
        for idx,vect in self.myprofiles.items():
            curprof=vect['cs']
            myshap=curprof.asshapely_ls()

            try:
                dist=myshap.distance(mypt)

                if dist<distmin:
                    profmin=curprof
                    distmin=dist
            except:
                pass
        return profmin

class Interpolator():
    """
    Objet d'interpolation sur sections en travers

        - self.interpolants est une liste de listes
        - chaque élément de self.interpolants est également une liste de listes
        - chaque liste de self.interpolants[k] contient les wolfvertex de la section discrétisée

    """

    def __init__(self, vec1:vector, vec2:vector,
                 supports:list[vector], ds=1.) -> None:

        self.interpolants=[]

        sect1={}
        sect2={}

        #Linestrings shapely des sections 1 et 2
        #ATTENTION, SHAPELY est une librairie géométrique 2D --> des outils spécifiques ont été programmés pour faire l'interpolation 3D
        s1=sect1['ls']=vec1.asshapely_ls()
        s2=sect2['ls']=vec2.asshapely_ls()

        nb = 0
        supls={}

        eps=5.e-2

        for curvec in supports:
            #linestring du support courant
            #distances des intersections des sections sur le support
            myls:LineString
            myls=curvec.asshapely_ls()

            #intersections du vecteur support avec les sections
            i1=myls.intersects(s1)
            if not i1:
                pt=Point(s1.xy[0][0],s1.xy[1][0])
                pt1=myls.interpolate(myls.project(pt))
                length = pt1.distance(pt)
                i1 = length<eps

                if i1:
                    vec1.myvertices[0].x=pt1.xy[0][0]
                    vec1.myvertices[0].y=pt1.xy[1][0]
                    s1=vec1.asshapely_ls()

                if not i1:
                    pt=Point(s1.xy[0][-1],s1.xy[1][-1])
                    pt1=myls.interpolate(myls.project(pt))
                    length = pt1.distance(pt)
                    i1 = length<eps
                    if i1:
                        vec1.myvertices[-1].x=pt1.xy[0][-1]
                        vec1.myvertices[-1].y=pt1.xy[1][-1]
                        s1=vec1.asshapely_ls()

            i2=myls.intersects(s2)
            if not i2:
                pt=Point(s2.xy[0][0],s2.xy[1][0])
                pt2=myls.interpolate(myls.project(pt))
                length = pt2.distance(Point(s2.xy[0][0],s2.xy[1][0]))
                i2 = length<eps

                if i2:
                    vec2.myvertices[0].x=pt2.xy[0][0]
                    vec2.myvertices[0].y=pt2.xy[1][0]
                    s2=vec2.asshapely_ls()

                if not i2:
                    pt=Point(s2.xy[0][-1],s2.xy[1][-1])
                    pt2=myls.interpolate(myls.project(pt))
                    length = pt2.distance(pt)
                    i2 = length<eps
                    if i2:
                        vec2.myvertices[-1].x=pt2.xy[0][-1]
                        vec2.myvertices[-1].y=pt2.xy[1][-1]
                        s2=vec2.asshapely_ls()

            if i1 and i2:
                supls[nb]={}
                supls[nb]['ls']=myls
                supls[nb]['vec']=curvec
                nb+=1

        #bouclage sur les vecteurs supports pour trouver les intersections avec les sections
        #  - trouver la portion utile entre intersections des supports
        #  - trouver les distances sur les sections de ces intersections
        for k in range(nb):
            #linestring du support courant
            #distances des intersections des sections sur le support
            myls:LineString
            myls=supls[k]['ls']

            #intersections du vecteur support avec les sections

            #section amont
            i1=myls.intersection(s1)
            if i1.geom_type=='MultiPoint':
                i1=i1.geoms[0]
                logging.debug('MultiPoint -- use first point or debug')

            #section aval
            i2=myls.intersection(s2)
            if i2.geom_type=='MultiPoint':
                i2=i2.geoms[0]
                logging.debug('MultiPoint -- use first point or debug')

            #Les distances, sur les sections, sont calculées en projetant l'intersection du vecteur support et des sections
            sect1[k]=s1.project(i1)
            sect2[k]=s2.project(i2)

            #Les distances, sur le support, sont calculées en projetant l'intersection du vecteur support et des sections
            supls[k][1]=myls.project(i1)
            if supls[k][1]==-1.:
                #problème de précision de calcul
                if myls.distance(Point(s1.xy[0][0],s1.xy[1][0]))<eps:
                    supls[k][1]=myls.project(Point(s1.xy[0][0],s1.xy[1][0]))
                    sect1[k]=s1.project(Point(s1.xy[0][0],s1.xy[1][0]))
                elif myls.distance(Point(s1.xy[0][-1],s1.xy[1][-1]))<eps:
                    supls[k][1]=myls.project(Point(s1.xy[0][-1],s1.xy[1][-1]))
                    sect1[k]=s1.project(Point(s1.xy[0][-1],s1.xy[1][-1]))

            supls[k][2]=myls.project(i2)
            if supls[k][2]==-1.:
                #problème de précision de calcul
                if myls.distance(Point(s2.xy[0][0],s2.xy[1][0]))<eps:
                    supls[k][2]=myls.project(Point(s2.xy[0][0],s2.xy[1][0]))
                    sect2[k]=s2.project(Point(s2.xy[0][0],s2.xy[1][0]))
                elif myls.distance(Point(s2.xy[0][-1],s2.xy[1][-1]))<eps:
                    supls[k][2]=myls.project(Point(s2.xy[0][-1],s2.xy[1][-1]))
                    sect2[k]=s2.project(Point(s2.xy[0][-1],s2.xy[1][-1]))

            #on ne conserve que la fraction utile entre intersections
            supls[k]['vec']=supls[k]['vec'].substring(supls[k][1],supls[k][2],False,False)

        #bouclage sur les intervalles --> nb_supports-1
        for k in range(nb-1):
            interpolant=[]
            self.interpolants.append(interpolant)

            cursupl:vector
            cursupr:vector
            curvec1:vector
            curvec2:vector

            #morceaux de sections entre intersections avec le support
            curvec1=sect1['sub'+str(k)]=vec1.substring(sect1[k],sect1[k+1],is3D=False,adim=False)
            curvec2=sect2['sub'+str(k)]=vec2.substring(sect2[k],sect2[k+1],is3D=False,adim=False)

            #pointeurrs vers les morceaux des supports
            cursupl = supls[k]['vec']
            cursupr = supls[k+1]['vec']

            #MAJ des longueurs 2D et 3D
            cursupl.update_lengths()
            cursupr.update_lengths()
            curvec1.update_lengths()
            curvec2.update_lengths()

            #Trouve la liste des distances à traiter pour le maillage
            nbi = np.ceil(max(curvec1.length3D,curvec2.length3D)/ds)
            locds = 1./float(nbi)
            dist3d = np.concatenate([np.arange(0.,1.,locds),np.cumsum(curvec1._lengthparts3D)/curvec1.length3D,np.cumsum(curvec2._lengthparts3D)/curvec2.length3D])
            dist3d = np.unique(dist3d)

            #nombre de points à traiter sur les supports
            # on divise la longueur 3D des supports par la taille souhaitée et on arrondi à l'entier supérieur
            nbi = int(np.ceil(max(cursupl.length3D,cursupr.length3D)/ds))
            # nouvelle distance de calcul
            locds = 1./float(nbi)

            sloc=0.
            pt1l = curvec1.interpolate(0.,True,True)
            pt2l = curvec2.interpolate(0.,True,True)
            pt1r = curvec1.interpolate(1.,True,True)
            pt2r = curvec2.interpolate(1.,True,True)

            s1dr = vector(name='sectiondroite1')
            s2dr = vector(name='sectiondroite2')
            s1dr.add_vertex([pt1l,pt1r])
            s2dr.add_vertex([pt2l,pt2r])

            s1dr = s1dr.asshapely_ls()
            s2dr = s2dr.asshapely_ls()

            # if np.isnan(pt1l.x):
            #     a=1
            # if np.isnan(pt2l.x):
            #     a=1
            # if np.isnan(pt1r.x):
            #     a=1
            # if np.isnan(pt2r.x):
            #     a=1

            for curalong in range(nbi+1):
                logging.debug(str(curalong))

                #interpolation 3D sur les 2 supports
                l1 = cursupl.interpolate(sloc,True,True)
                l2 = cursupr.interpolate(sloc,True,True)

                curvec=vector(name='loc')
                curvec.add_vertex([l1,l2])
                val = []

                if l1.z!=0.:
                    if pt1l.z==0.:
                        alpha1l=0.
                    else:
                        alpha1l = l1.z/pt1l.z
                    if pt2l.z==0.:
                        alpha2l=0.
                    else:
                        alpha2l = l1.z/pt2l.z
                else:
                    alpha1l = 0.
                    alpha2l = 0.
                if l2.z!=0.:
                    if pt1r.z==0.:
                        alpha1r = 0.
                    else:
                        alpha1r = l2.z/pt1r.z

                    if pt2r.z==0.:
                        alpha2r = 0.
                    else:
                        alpha2r = l2.z/pt2r.z
                else:
                    alpha1r=0.
                    alpha2r=0.

                for curdist in dist3d:

                    #interpolation 3D dans les 2 sections
                    cur1 = curvec1.interpolate(curdist,True,True)
                    cur2 = curvec2.interpolate(curdist,True,True)

                    alpha1 = alpha1l*(1.-curdist)+alpha1r*curdist
                    alpha2 = alpha2l*(1.-curdist)+alpha2r*curdist

                    sr1 = s1dr.project(Point(cur1.x,cur1.y))
                    sr2 = s2dr.project(Point(cur2.x,cur2.y))
                    pr1 = s1dr.interpolate(sr1)
                    pr2 = s2dr.interpolate(sr2)
                    sr1/=s1dr.length
                    sr2/=s2dr.length

                    dx1 = cur1.x-pr1.x
                    dy1 = cur1.y-pr1.y
                    dx2 = cur2.x-pr2.x
                    dy2 = cur2.y-pr2.y
                    dx = dx1*(1.-sloc)+dx2*sloc
                    dy = dy1*(1.-sloc)+dy2*sloc
                    s = sr1*(1.-sloc)+sr2*sloc

                    # dist2d1 = cur1.dist2D(curvec1.myvertices[0])/curvec1.myvertices[0].dist2D(curvec1.myvertices[-1]) #curvec1.length2D
                    # dist2d2 = cur2.dist2D(curvec2.myvertices[0])/curvec2.myvertices[0].dist2D(curvec2.myvertices[-1]) #curvec2.length2D
                    # dist2d  = dist2d1*(1.-sloc) + dist2d2*sloc
                    # pt = curvec.interpolate(dist2d,False,True)
                    pt = curvec.interpolate(s,False,True)

                    # xloc = cur1.x + sloc * (cur2.x-cur1.x)
                    # yloc = cur1.y + sloc * (cur2.y-cur1.y)
                    zloc = cur1.z*alpha1 + sloc * (cur2.z*alpha2-cur1.z*alpha1)

                    val.append(wolfvertex(pt.x+dx,pt.y+dy,zloc))
                    # val.append(wolfvertex(xloc,yloc,zloc))

                interpolant.append(val)

                sloc+=locds
                sloc=min(sloc,1.)

    def get_xyz_for_viewer(self,nbsub=10):

        pts=self.interpolants

        nb=0
        for curpt in pts:
            for curl in curpt:
                nb+=(len(curpt)-1)*(len(curl)-1)*3+(len(curl)-1)+(len(curpt))

        pond=np.arange(0.,1.,1./float(nbsub))
        xyz=np.ones([(nb-1)*nbsub,4],order='F')
        start=0
        for curpt in pts:
            for k in range(len(curpt)-1):
                curl=curpt[k]
                nextl=curpt[k+1]
                for i in range(len(curl)-1):
                    v1=curl[i].getcoords()
                    v2=curl[i+1].getcoords()
                    v3=nextl[i].getcoords()

                    xyz[start:start+nbsub,:3]=[v1+(v2-v1)*curpond for curpond in pond]
                    start+=nbsub
                    xyz[start:start+nbsub,:3]= [v2+(v3-v2)*curpond for curpond in pond]
                    start+=nbsub
                    xyz[start:start+nbsub,:3]= [v3+(v1-v3)*curpond for curpond in pond]
                    start+=nbsub

            curl=curpt[-1]
            for i in range(len(curl)-1):
                v1=curl[i].getcoords()
                v2=curl[i+1].getcoords()
                xyz[start:start+nbsub,:3]=[v1+(v2-v1)*curpond for curpond in pond]
                start+=nbsub
            for k in range(len(curpt)-1):
                curl=curpt[k]
                nextl=curpt[k+1]
                v1=curl[-1].getcoords()
                v3=nextl[-1].getcoords()
                xyz[start:start+nbsub,:3]=[v1+(v3-v1)*curpond for curpond in pond]
                start+=nbsub

        return xyz

    def add_triangles_to_zone(self,myzone:zone):

        nb=0
        npt=1
        for curpt in self.interpolants:
            for k in range(len(curpt)-1):
                curl=curpt[k]
                nextl=curpt[k+1]
                for i in range(len(curl)-1):
                    curvec = vector(name='tr'+'_'+str(npt)+'_'+str(k)+'_'+str(i),parentzone=myzone)
                    curvec.add_vertex([curl[i],curl[i+1],nextl[i]])
                    curvec.close_force()
                    curvec.myprop.used=False
                    myzone.add_vector(curvec)

                    curvec = vector(name='tr'+'_'+str(npt)+'_'+str(k+1)+'_'+str(i),parentzone=myzone)
                    curvec.add_vertex([nextl[i],curl[i+1],nextl[i+1]])
                    curvec.close_force()
                    curvec.myprop.used=False
                    myzone.add_vector(curvec)

            npt+=1
            nb+=(len(curpt)-1)*(len(curl)-1)*3+(len(curl)-1)+(len(curpt))

    def get_triangles(self,forgltf=True):

        points=[]
        triangles=[]
        nbpts=0
        nbtr=0
        for curpt in self.interpolants:

            nb_points_perline = len(curpt[0])
            nbsect=len(curpt)
            if forgltf:
                pointsloc=[[pt.x,pt.z,-pt.y] for curl in curpt for pt in curl]
            else:
                pointsloc=[[pt.x,pt.y,pt.z] for curl in curpt for pt in curl]

            trianglesloc=[[[k+decal*nb_points_perline+nbpts,
                        k+1+decal*nb_points_perline+nbpts,
                        nb_points_perline+k+decal*nb_points_perline+nbpts],

                        [nb_points_perline+k+decal*nb_points_perline+nbpts,
                        k+1+decal*nb_points_perline+nbpts,
                        nb_points_perline+k+decal*nb_points_perline+1+nbpts]]
                            for decal in range(len(curpt)-1) for k in range(nb_points_perline-1)]

            nbpts+=nb_points_perline*nbsect
            nbloc=(nb_points_perline-1)*(nbsect-1)*2
            nbtr+=nbloc

            points.append(pointsloc)
            triangles.append(np.asarray(trianglesloc).reshape([nbloc,3]))


        points=np.asarray(np.concatenate(points),dtype=np.float32)
        triangles=np.asarray(np.concatenate(triangles),dtype=np.uint32)


        if len(np.argwhere(np.isnan(points)==True))>0:
            a=1

        return nbpts,points,triangles

    def get_points(self,forgltf=False):

        points=[]
        nbpts=0
        for curpt in self.interpolants:

            nb_points_perline = len(curpt[0])
            nbsect=len(curpt)
            if forgltf:
                pointsloc=[[pt.x,pt.z,-pt.y] for curl in curpt for pt in curl]
            else:
                pointsloc=[[pt.x,pt.y,pt.z] for curl in curpt for pt in curl]

            nbpts+=nb_points_perline*nbsect
            points.append(pointsloc)

        if forgltf:
            points=np.asarray(np.concatenate(points),dtype=np.float32)
        else:
            points=np.asarray(np.concatenate(points))

        return nbpts,points

    def export_gltf(self,points=None,triangles=None):

        if points is None and triangles is None:
            points,triangles= self.get_triangles()

        triangles_binary_blob = triangles.flatten().tobytes()
        points_binary_blob = points.tobytes()

        gltf = pygltflib.GLTF2(
            scene=0,
            scenes=[pygltflib.Scene(nodes=[0])],
            nodes=[pygltflib.Node(mesh=0)],
            meshes=[
                pygltflib.Mesh(
                    primitives=[
                        pygltflib.Primitive(
                            attributes=pygltflib.Attributes(POSITION=1), indices=0
                        )
                    ]
                )
            ],
            accessors=[
                pygltflib.Accessor(
                    bufferView=0,
                    componentType=pygltflib.UNSIGNED_INT,
                    count=triangles.size,
                    type=pygltflib.SCALAR,
                    max=[int(triangles.max())],
                    min=[int(triangles.min())],
                ),
                pygltflib.Accessor(
                    bufferView=1,
                    componentType=pygltflib.FLOAT,
                    count=len(points),
                    type=pygltflib.VEC3,
                    max=points.max(axis=0).tolist(),
                    min=points.min(axis=0).tolist(),
                ),
            ],
            bufferViews=[
                pygltflib.BufferView(
                    buffer=0,
                    byteLength=len(triangles_binary_blob),
                    target=pygltflib.ELEMENT_ARRAY_BUFFER,
                ),
                pygltflib.BufferView(
                    buffer=0,
                    byteOffset=len(triangles_binary_blob),
                    byteLength=len(points_binary_blob),
                    target=pygltflib.ARRAY_BUFFER,
                ),
            ],
            buffers=[
                pygltflib.Buffer(
                    byteLength=len(triangles_binary_blob) + len(points_binary_blob)
                )
            ],
        )
        gltf.set_binary_blob(triangles_binary_blob + points_binary_blob)

        dlg=wx.FileDialog(None,_('Choose filename'),wildcard='binary gltf2 (*.glb)|*.glb|gltf2 (*.gltf)|*.gltf|All (*.*)|*.*',style=wx.FD_SAVE)
        ret=dlg.ShowModal()
        if ret==wx.ID_CANCEL:
            dlg.Destroy()
            return

        fn=dlg.GetPath()
        dlg.Destroy()

        gltf.save(fn)

    def get_xy_z_for_griddata(self):

        xy = np.asarray([[curvertex.x,curvertex.y] for curpt in self.interpolants for curl in curpt for curvertex in curl])
        z = np.asarray([curvertex.z for curpt in self.interpolants for curl in curpt for curvertex in curl])

        # if len(np.argwhere(np.isnan(z)))>0:
        #     test=1
        # if len(np.argwhere(np.isneginf(z)))>0:
        #     test=1
        # if len(np.argwhere(np.isposinf(z)))>0:
        #     test=1
        return xy,z

class Interpolators():
    """
    Classe de gestion des interpolations sur sections en travers
    """

    def __init__(self, banks:Zones, cs:crosssections, ds=1.) -> None:
        """
        Constructeur de la classe Interpolators

        :param banks: Zones contenant les vecteurs supports
        :param cs: objet 'crosssections' contenant les sections en travers --> voir PyCrosssections
        """

        self.mybanks = [curv for curzone in banks.myzones for curv in curzone.myvectors]

        cs.set_zones()
        self.mycs = cs.myzones

        self.myinterp:list[Interpolator]=[]

        zonecs:zone
        zonecs = self.mycs.myzones[0]

        if zonecs.myvectors[0].up is not None:
            # Les sections ont été triées sur base d'un vecteur support
            # On les traite dans l'ordre du tri
            cs1:profile
            cs1=cs.get_upstream()['cs']

            while cs1.down is not cs1:
                cs2=cs1.down

                logging.info('{} - {}'.format(cs1.myname,cs2.myname))

                myinterp=Interpolator(cs1,cs2,self.mybanks,ds)

                if len(myinterp.interpolants)>0:
                    self.myinterp.append(myinterp)
                else:
                    logging.error('No interpolation found between {} and {}'.format(cs1.myname,cs2.myname))

                cs1=cs2
        else:
            # Les sections n'ont pas été triées --> on les traite dans l'ordre
            for i in range(zonecs.nbvectors-1):
                cs1=zonecs.myvectors[i]
                cs2=zonecs.myvectors[i+1]

                logging.info('{} - {}'.format(cs1.myname,cs2.myname))
                myinterp=Interpolator(cs1,cs2,self.mybanks,ds)
                if len(myinterp.interpolants)>0:
                    self.myinterp.append(myinterp)
                else:
                    logging.error('No interpolation found between {} and {}'.format(cs1.myname,cs2.myname))

        self.add_interpolators(cs.myzones.parent)

    def add_interpolators(self, parent):
        """
        Ajout d'objets 'Interpolators' pour affichage/stockage
        """
        self.myzones = Zones(parent=parent)

        id=0
        points=[]
        triangles=[]
        decal=0

        for curinterp in self.myinterp:
            id+=1

            myzone = zone(name='Interpolator'+str(id), parent=self.myzones, is2D=False)
            myzone.used=False
            self.myzones.add_zone(myzone)
            curinterp.add_triangles_to_zone(myzone)

            nbpts,pts,tr=curinterp.get_triangles()

            points.append(pts)
            triangles.append(tr+decal)
            decal+=nbpts

        curinterp.export_gltf(np.concatenate(points),np.concatenate(triangles))


    def viewer_interpolator(self):

        xyz=[]
        for curinterp in self.myinterp:
            xyz.append(curinterp.get_xyz_for_viewer())

        xyz=np.concatenate(xyz)

        myviewer(xyz,0)

    def interp_on_array(self, myarray, method:Literal["nearest", "linear", "cubic"]):

        xy=[]
        z=[]
        for curinterp in self.myinterp:
            tmpxy,tmpz = curinterp.get_xy_z_for_griddata()
            xy.append(tmpxy)
            z.append(tmpz)

        xy = np.concatenate(xy)
        z = np.concatenate(z)

        myarray.interpolate_on_cloud(xy,z,method)