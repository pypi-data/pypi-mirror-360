"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

#Code INS des communes belges
import re
from os import path, mkdir
from pathlib import Path
from time import sleep
from typing import Literal, Union
import logging

from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize,curve_fit
from scipy.stats import gumbel_r,genextreme
import numpy as np

# We have tried pymupdf but its license is AGPL so it's more or less a no-go.
import pdfplumber

from .ins import Localities
from .PyTranslate import _

Montana_a1 = 'a1'
Montana_a2 = 'a2'
Montana_a3 = 'a3'
Montana_b1 = 'b1'
Montana_b2 = 'b2'
Montana_b3 = 'b3'

RT2 = '2'
RT5 = '5'
RT10 = '10'
RT15 = '15'
RT20 ='20'
RT25 ='25'
RT30 = '30'
RT40 ='40'
RT50 ='50'
RT75 = '75'
RT100 ='100'
RT200  = '200'

RT = [RT2,RT5,RT10,RT15,RT20,RT25,RT30,RT40,RT50,RT75,RT100,RT200]
freqdep=np.array([1./float(x) for x in RT])
freqndep=1.-freqdep

dur10min = '10 min'
dur20min = '20 min'
dur30min = '30 min'
dur1h = '1 h'
dur2h = '2 h'
dur3h = '3 h'
dur6h = '6 h'
dur12h = '12 h'
dur1d = '1 d'
dur2d = '2 d'
dur3d = '3 d'
dur4d = '4 d'
dur5d = '5 d'
dur7d = '7 d'
dur10d = '10 d'
dur15d = '15 d'
dur20d = '20 d'
dur25d = '25 d'
dur30d = '30 d'

durationstext=[dur10min,dur20min,dur30min,dur1h,dur2h,dur3h,dur6h,dur12h,dur1d,
                dur2d,dur3d,dur4d,dur5d,dur7d,dur10d,dur15d,dur20d,dur25d,dur30d]
durations=np.array([10,20,30,60,120,180,360,720],np.float64)
durationsd=np.array([1,2,3,4,5,7,10,15,20,25,30],np.float64)*24.*60.
durations = np.concatenate([durations,durationsd])

class MontanaIRM():
    """ Classe pour la gestion des relations de Montana pour les précipitations """

    def __init__(self,coeff:pd.DataFrame,time_bounds=None) -> None:

        if time_bounds is None:
            self.time_bounds = [25,6000]
        else:
            self.time_bounds = time_bounds

        self.coeff=coeff

    def get_ab(self, dur, T):
        """ Get the Montana coefficients for a given duration and return period

        :param dur: the duration
        :param T: the return period
        """

        curcoeff = self.coeff.loc[float(T)]
        if dur<self.time_bounds[0]:
            a=curcoeff[Montana_a1]
            b=curcoeff[Montana_b1]
        elif dur<=self.time_bounds[1]:
            a=curcoeff[Montana_a2]
            b=curcoeff[Montana_b2]
        else:
            a=curcoeff[Montana_a3]
            b=curcoeff[Montana_b3]

        return a,b

    def get_meanrain(self, dur, T, ab= None):
        """ Get the mean rain for a given duration and return period

        :param dur: the duration
        :param T: the return period
        :param ab: the Montana coefficients
        """

        if ab is None:
            ab = self.get_ab(dur,T)
        return ab[0]*dur**(-ab[1])

    def get_instantrain(self, dur, T, ab= None):
        """ Get the instantaneous rain for a given duration and return period

        :param dur: the duration
        :param T: the return period
        :param ab: the Montana coefficients
        """
        if ab is None:
            ab = self.get_ab(dur,T)
        meani=self.get_meanrain(dur,T,ab)
        return (1.-ab[1])*meani

    def get_Q(self, dur, T):
        """ Get the quantity of rain for a given duration and return period

        :param dur: the duration
        :param T: the return period
        """

        rain = self.get_meanrain(dur,T)
        return rain*dur/60. #to obtains [mm.h^-1] as dur is in [min]

    def get_hyeto(self, durmax, T, r= 0.5):
        """ Get the hyetogram for a given return period

        :param durmax: the maximum duration of the hyetogram
        :param T: the return period
        :param r: Decentration coefficient
        """

        x = np.arange(10,durmax,1,dtype=np.float64)
        # y = [self.get_instantrain(curx,T) for curx in x]

        startpeak=durmax*r-5
        endpeak=durmax*r+5

        if r==1.:
            xbeforepeak = np.zeros(1)
        else:
            xbeforepeak = np.arange(-float(durmax-10)*(1.-r),0,(1.-r))
        if r==0.:
            xafterpeak = endpeak
        else:
            xafterpeak  = np.arange(0,float(durmax-10)*r,r)

        xbeforepeak+= startpeak
        xafterpeak += endpeak

        x_hyeto = np.concatenate([xbeforepeak, [startpeak,endpeak], xafterpeak])
        y_hyeto = np.zeros(len(x_hyeto))
        for k in range(len(x_hyeto)):
            if x_hyeto[k] <= startpeak:
                y_hyeto[k] = self.get_instantrain((startpeak-x_hyeto[k])/(1.-r)+10,T)
            else:
                y_hyeto[k] = self.get_instantrain((x_hyeto[k]-endpeak)/r+10,T)

        if r==0.:
            y_hyeto[-1]=0.
        elif r==1.:
            y_hyeto[0]=0.

        return x_hyeto,y_hyeto

    def plot_hyeto(self, durmax, T, r= 0.5):
        """ Plot the hyetogram for a given return period

        :param durmax: the maximum duration of the hyetogram
        :param T: the return period
        :param r: Decentration coefficient
        """
        x,y = self.get_hyeto(durmax,T,r)

        fig,ax = plt.subplots(1,1,figsize=[15,10])
        ax.plot(x,y,label=_("Hyetogram"))

        ax.set_xlabel(_('Time [min]'))
        ax.set_ylabel(_('Intensity [mm/h]'))
        ax.legend().set_draggable(True)

        return fig,ax

    def plot_hyetos(self, durmax, r= 0.5):
        """ Plot the hyetograms for all return periods

        :param durmax: the maximum duration of the hyetograms
        :param r: Decentration coefficient
        """

        fig,ax = plt.subplots(1,1,figsize=[15,10])

        for curT in RT:
            x,y = self.get_hyeto(durmax,curT,r)

            ax.plot(x,y,label=curT)

        ax.set_xlabel(_('Time [min]'))
        ax.set_ylabel(_('Intensity [mm/h]'))
        ax.legend().set_draggable(True)

        return fig,ax

class Qdf_IRM():
    """
    Gestion des relations QDF calculées par l'IRM

    Exemple d'utilisation :

    Pour importer les fichiers depuis le site web de l'IRM meteo.be
    from wolfhece.irm_qdf import Qdf_IRM
    qdf = Qdf_IRM(force_import=True)
    qdf =

    Il est possible de spécifier le répertoire de stockage des fichiers Excel
    Par défaut, il s'agit d'un sous-répertoire 'irm' du répertoire courant qui sera créé s'il n'exsiste pas

    Une fois importé/téléchargé, il est possible de charger une commune sur base de l'INS ou de son nom

    myqdf = Qdf_IRM(name='Jalhay')

    Les données sont ensuite disponibles dans les propriétés, qui sont des "dataframes" pandas (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) :

        - qdf           : les relation Quantité/durée/fréquence
        - standarddev   : l'écart-type de l'erreur
        - confintlow    : la valeur inférieure de l'intervalle de confiance (-2*stddev)
        - confintup     : la valeur supérieure de l'intervalle de confiance (+2*stddev)
        - montanacoeff  : les coeffciients de Montana

    Il est par exemple possible d'accéder aux coefficients de Montana via l'une de ces lignes ou une combinaison :

    display(myqdf.montanacoeff)
    rt = myqdf.montanacoeff.index
    display(myqdf.montanacoeff.loc[rt[0]])
    display(myqdf.montanacoeff.iloc[0])
    display(myqdf.get_Montanacoeff(qdf.RT2))

    """

    def __init__(self, store_path= 'irm',
                 code:int= 0, name= '',
                 force_import= False,
                 ins:Literal['2018', '2019', '2025', 2018, 2019, 2025] = 2018,
                 localities:Localities = None) -> None:

        if localities is None:

            assert int(ins) in [2018, 2019, 2025], _('Bad INS - Retry !')

            self.myloc = Localities(ins)
        else:
            self.myloc = localities

        self.store = store_path


        # This one will hold Qdf data of one locality. If it is None it means no
        # data has been loaded.
        self.qdf = None

        if force_import:
            # Import all QDF's from IRM
            Qdf_IRM.importfromwebsite(store_path, ins=ins)
        self._code = None
        self._name = None

        if code !=0:
            if self.ins_read_excel(code=str(code)):
                self.fit_all()
                self._code = code
                self._name = self.myloc.get_namefromINS(code)
            else:
                logging.debug(f"INS code {code} not found in the store")
        elif name!='':
            if self.ins_read_excel(name=name):
                self.fit_all()
                self._name = name
                self._code = self.myloc.get_INSfromname(name)
            else:
                logging.debug(f"Name {name} not found in the store")

    def has_data_for_locality(self) -> bool:
        """ Has this instance been initialized with data from a locality ?
        """
        return self.qdf is not None

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @property
    def code_name(self):
        return str(self._code) + '-' + self._name

    @property
    def name_code(self):
        return self._name + '-' + str(self._code)

    def export_allmontana2xls(self):
        """ Export all Montana coefficients to an Excel file """

        newdf = []

        for curcode in self.myloc.get_allcodes():

            self.ins_read_excel(code=curcode)
            if self.montanacoeff is not None:
                self.montanacoeff['INS'] = [curcode]*12
                self.montanacoeff['Name'] = [self.myloc.get_namefromINS(int(curcode))]*12

                newdf.append(self.montanacoeff.copy())
                self.montanacoeff=None

        newdf = pd.concat(newdf)

        newdf.to_excel("allmontana.xlsx")


    @classmethod
    def importfromwebsite(cls, store_path= 'irm', verbose:bool= False, waitingtime:float= .01, ins:Literal['2018', '2019', '2025', 2018, 2019, 2025] = 2018, ins_code: int = None):
        """ Import Excel files for one or all municipalities from the IRM website

        :param store_path: Where to store the downloaded data. Directory will be created if it doesn't exists.
        :param verbose: If `True`, will print some progress information.
                        If `False`, will do nothing.
                        If a callable, then will call it with a float in [0, 1].
                        0 means nothing downloaded, 1 means everything downloaded.

        :param waitingtime: How long to wait (in seconds) betwenn the download
                            of each station (will make sure we don't overwhelm IRM's website).

        :param ins: The year of the INS codes to use.
        :param code: Restricts the data download to a specific NIS code. `None` means full download.
        """
        import requests

        myloc = Localities(ins)

        if ins_code is not None:
            codes_to_load = [ins_code]
        else:
            if not path.exists(store_path):
                mkdir(store_path)
            codes_to_load = myloc.inscode2name

        for key,myins in enumerate(codes_to_load):
            #chaîne URL du fichier Excel
            url="https://www.meteo.be//resources//climatology//climateCity//xls//IDF_table_INS"+str(myins)+".xlsx"
            #Obtention du fichiers depuis le site web de l'IRM
            response=requests.get(url)

            if str(response.content).find("Page not found")==-1 :

                # Make sure we create the store path only if we have
                # something to put inside.
                if ins_code is not None and not path.exists(store_path):
                    mkdir(store_path)

                file=open(path.join(store_path,str(myins)+".xlsx"), 'wb')
                file.write(response.content)
                file.close()
                if verbose:
                    if callable(verbose):
                        verbose(key/len(codes_to_load))
                    else:
                        print(myins)
            else:
                #logging.error(response.content)
                logging.error(f"Failed to load IRM data: {url} --> {response}")

            sleep(waitingtime)

    def ins_read_excel(self,code='',name=''):
        """Lecture des caractéristiques d'une commune depuis le fichier Excel associé au code INS"""
        import warnings

        if code !='':
            loccode=str(code)
            name = self.myloc.get_namefromINS(int(loccode))
        elif name!='':
            if not name.lower() in self.myloc.insname2code.keys():
                return _('Bad name ! - Retry')
            loccode=str(self.myloc.insname2code[name.lower()])

        self._code = loccode
        self._name = name

        store = Path(self.store)

        pathname_xls = store / (loccode+".xlsx")
        pathname_csv = store / 'csv' / loccode

        if pathname_csv.exists():
            self.qdf = pd.read_csv(pathname_csv / 'qdf.csv', index_col=0)
            self.standarddev = pd.read_csv(pathname_csv / 'standarddev.csv', index_col=0)
            self.confintlow = pd.read_csv(pathname_csv / 'confintlow.csv', index_col=0)
            self.confintup = pd.read_csv(pathname_csv / 'confintup.csv', index_col=0)
            self.montanacoeff = pd.read_csv(pathname_csv / 'montanacoeff.csv', index_col=0)
            self.montana = MontanaIRM(self.montanacoeff)
            return True
        else:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                if path.exists(pathname_xls):
                    self.qdf=pd.read_excel(pathname_xls,"Return level",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                    self.standarddev=pd.read_excel(pathname_xls,"Standard deviation",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                    self.confintlow=pd.read_excel(pathname_xls,"Conf. interval, lower bound",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                    self.confintup=pd.read_excel(pathname_xls,"Conf. interval, upper bound",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                    self.montanacoeff=pd.read_excel(pathname_xls,"Montana coefficients",index_col=0,skiprows=range(11),nrows=12,usecols="A:G",engine='openpyxl', engine_kwargs={'read_only': True})
                    self.montana = MontanaIRM(self.montanacoeff)
                    return True
                else:
                    self.qdf=None
                    self.standarddev=None
                    self.confintlow=None
                    self.confintup=None
                    self.montanacoeff=None
                    self.montana=None
                    return False

    @classmethod
    def convert_xls2csv(cls, store_path= 'irm', ins:Literal['2018', '2019', '2025', 2018, 2019, 2025] = 2018):
        """ Convert all Excel files to JSON files

        :param store_path: Where to store the downloaded data. Directory will be created if it doesn't exists.
        :param ins: The year of the INS codes to use.
        """

        myloc = Localities(ins)

        store_path = Path(store_path)

        for key,myins in enumerate(myloc.get_allcodes()):
            pathname = store_path / (str(myins)+".xlsx")
            if pathname.exists():

                qdf=pd.read_excel(pathname,"Return level",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                standarddev=pd.read_excel(pathname,"Standard deviation",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                confintlow=pd.read_excel(pathname,"Conf. interval, lower bound",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                confintup=pd.read_excel(pathname,"Conf. interval, upper bound",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl', engine_kwargs={'read_only': True})
                montanacoeff=pd.read_excel(pathname,"Montana coefficients",index_col=0,skiprows=range(11),nrows=12,usecols="A:G",engine='openpyxl', engine_kwargs={'read_only': True})

                store_csv = store_path / 'csv' / str(myins)
                store_csv.mkdir(exist_ok=True)

                qdf.to_csv(store_csv / 'qdf.csv')
                standarddev.to_csv(store_csv / 'standarddev.csv')
                confintlow.to_csv(store_csv / 'confintlow.csv')
                confintup.to_csv(store_csv / 'confintup.csv')
                montanacoeff.to_csv(store_csv / 'montanacoeff.csv')


    def plot_idf(self,T=None,which='All',color=[27./255.,136./255.,245./255.]):
        """
        Plot IDF relations on a new figure

        :param T       : the return period (based on RT constants)
        :param which   : information to plot
            - 'Montana'
            - 'QDFTable'
            - 'All'
        """
        fig,ax = plt.subplots(1,1,figsize=(15,10))
        ax.set_xscale('log')
        ax.set_yscale('log')

        if T is None:
            for k in range(len(RT)):
                pond = .3+.7*float(k/len(RT))
                mycolor = color+[pond]
                if which=='All' or which=='QDFTable':
                    ax.scatter(durations,self.qdf[RT[k]]/durations*60.,label=RT[k] + _(' QDF Table'),color=mycolor)

                if which=='All' or which=='Montana':
                    iMontana = [self.montana.get_meanrain(curdur,RT[k]) for curdur in durations]
                    ax.plot(durations,iMontana,label=RT[k] + ' Montana',color=mycolor)
        else:
            if which=='All' or which=='QDFTable':
                ax.scatter(durations,self.qdf[T],label=T+ _(' QDF Table'),color=color)

            if which=='All' or which=='Montana':
                iMontana = [self.montana.get_instantrain(curdur,T) for curdur in durations]
                ax.plot(durations,iMontana,label=T + ' Montana',color=color)

        ax.legend().set_draggable(True)
        ax.set_xlabel(_('Duration [min]'))
        ax.set_ylabel(_('Intensity [mm/h]'))
        ax.set_xticks(durations)
        ax.set_xticklabels(durationstext,rotation=45)
        ax.set_title(self._name + ' - code : ' + str(self._code))

        return fig,ax

    def plot_qdf(self,T=None,which='All',color=[27./255.,136./255.,245./255.]):
        """
        Plot QDF relations on a new figure
        :param T       : the return period (based on RT constants)
        :param which   : information to plot
            - 'Montana'
            - 'QDFTable'
            - 'All'
        """
        fig,ax = plt.subplots(1,1,figsize=(15,10))
        ax.set_xscale('log')

        if T is None:
            for k in range(len(RT)):
                pond = .3+.7*float(k/len(RT))
                mycolor = color+[pond]
                if which=='All' or which=='QDFTable':
                    ax.scatter(durations,self.qdf[RT[k]],label=RT[k] + _(' QDF Table'),color=mycolor)

                if which=='All' or which=='Montana':
                    QMontana = [self.montana.get_Q(curdur,RT[k]) for curdur in durations]
                    ax.plot(durations,QMontana,label=RT[k] + ' Montana',color=mycolor)
        else:
            if which=='All' or which=='QDFTable':
                ax.scatter(durations,self.qdf[T],label=T+ _(' QDF Table'),color=color)

            if which=='All' or which=='Montana':
                QMontana = [self.montana.get_Q(curdur,T) for curdur in durations]
                ax.plot(durations,QMontana,label=T + ' Montana',color=color)

        ax.legend().set_draggable(True)
        ax.set_xlabel(_('Duration [min]'))
        ax.set_ylabel(_('Quantity [mm]'))
        ax.set_xticks(durations)
        ax.set_xticklabels(durationstext,rotation=45)
        ax.set_title(self._name + ' - code : ' + str(self._code))

        return fig,ax

    def plot_cdf(self,dur=None):
        """ Plot the cdf of the QDF data for a given duration """

        fig,ax = plt.subplots(1,1,figsize=(10,10))
        if dur is None:
            for k in range(len(durations)):
                pond = .3+.7*float(k/len(durations))
                mycolor = (27./255.,136./255.,245./255.,pond)
                ax.scatter(self.qdf.loc[durationstext[k]],freqndep,marker='o',label=durationstext[k],color=mycolor)
        else:
            ax.scatter(self.qdf.loc[dur],freqndep,marker='o',label=dur,color=(0,0,1))

        ax.legend().set_draggable(True)
        ax.set_ylabel(_('Cumulative distribution function (cdf)'))
        ax.set_xlabel(_('Quantity [mm]'))
        ax.set_title(self._name + ' - code : ' + str(self._code))

        return fig,ax

    def fit_all(self):
        """ Fit all durations with a Generalized Extreme Value distribution """

        self.load_fits_json()

        if self.popt_all == {}:
            for curdur in durationstext:
                fig,ax,popt,pcov = self.fit_cdf(curdur)
                self.popt_all[curdur]=popt
                # self.pcov_all[curdur]=pcov

            self.save_fits_json()

    def save_fits_json(self):
        """ Save the fits in a csv file """

        with open(path.join(self.store, str(self._code) + '_fits.json'), 'w') as f:
            df = pd.DataFrame(self.popt_all)
            df.to_json(f)

        # with open(path.join(self.store, str(self.code) + '_fits_cov.json'), 'w') as f:
        #     df = pd.DataFrame(self.pcov_all)
        #     df.to_json(f)

    def load_fits_json(self):
        """ Load the fits from a json file """

        import json

        filename = path.join(self.store, str(self._code) + '_fits.json')

        if path.exists(filename):
            with open(filename, 'r') as f:
                self.popt_all = json.load(f)

            for key in self.popt_all.keys():
                self.popt_all[key] = np.array([val for val in self.popt_all[key].values()])
        else:
            self.popt_all = {}

        # filename = path.join(self.store, str(self.code) + '_fits_cov.json')

        # if path.exists(filename):
        #     with open(filename, 'r') as f:
        #         self.pcov_all = json.load(f)
        # else:
        #     self.pcov_all = {}

    def fit_cdf(self, dur=None, plot=False):
        """ Fit the cdf of the QDF data with a Generalized Extreme Value distribution

        :param dur: the duration to fit
        :param plot: if True, will plot the cdf with the fit
        """

        if dur is None:
            return _('Bad duration - Retry !')
        if dur not in durationstext:
            return _('Bad duration - Retry !')

        x=np.asarray(self.qdf.loc[dur], dtype=np.float64)

        def locextreme(x,a,b,c):
            return genextreme.cdf(x, a, loc=b, scale=c)

        def locextreme2(a):
            LL = -np.sum(genextreme.logpdf(x,a[0],loc=a[1],scale=a[2]))
            return LL

        popt = genextreme.fit(x)
        popt, pcov = curve_fit(locextreme, x, freqndep, p0=popt)

        #ptest = minimize(locextreme2,popt,bounds=[[-10.,0.],[0.,100.],[0.,100.]])

        # perr = np.sqrt(np.diag(pcov))

        fig=ax=None
        if plot:
            fig,ax=self.plot_cdf(dur)
            ax.plot(x,genextreme.cdf(x,popt[0],loc=popt[1],scale=popt[2]),label='fit')
            # ax.plot(x,genextreme.cdf(x,ptest.x[0],loc=ptest.x[1],scale=ptest.x[2]),label='fit_MLE')
            ax.legend().set_draggable(True)

        self.stat = genextreme

        return fig,ax,popt,pcov

    def get_Tfromrain(self, Q, dur=dur1h):
        """ Get the return period for a given quantity of rain

        :param Q: the quantity of rain
        :param dur: the duration
        """

        return 1./self.stat.sf(Q, self.popt_all[dur][0], loc=self.popt_all[dur][1], scale=self.popt_all[dur][2])

    def get_rainfromT(self, T, dur= dur1h):
        """ Get the quantity of rain for a given return period and duration

        :param T: the return period
        :param dur: the duration
        """

        return self.stat.isf(1./T,self.popt_all[dur][0],loc=self.popt_all[dur][1],scale=self.popt_all[dur][2])

    def get_MontanacoeffforT(self, return_period):
        """ Get the Montana coefficients for a given return period

        :param return_period: the return period
        """

        if return_period in RT:
            return self.montanacoeff.loc[float(return_period)]
        else:
            return _('Bad RT - Retry !')

    def plot_hyeto(self, durmax, T, r=.5):
        """ Plot the hyetogram for a given return period

        :param durmax: the maximum duration of the hyetogram
        :param T: the return period
        :param r: the decentration coefficient
        """

        fig,ax = self.montana.plot_hyeto(durmax,T,r)
        ax.set_title(self._name + ' - code : ' + str(self._code))

        return fig

    def plot_hyetos(self, durmax, r=.5):
        """ Plot the hyetograms for all return periods

        :param durmax: the maximum duration of the hyetograms
        :param r: the decentration coefficient
        """

        fig,ax = self.montana.plot_hyetos(durmax,r)
        ax.set_title(self._name + ' - code : ' + str(self._code))

    def __str__(self) -> str:
        """ Return the QDF data as a string """
        return self.qdf.__str__()

class QDF_Belgium():

    def __init__(self, store_path= 'irm', ins:Literal['2018', '2019', '2025', 2018, 2019, 2025] = 2018) -> None:

        self.localities = Localities(ins)
        self.store_path = Path(store_path)

        self.all = {}
        for loc_ins in tqdm(self.localities.get_allcodes()):
            loc = Qdf_IRM(store_path=str(self.store_path), code=loc_ins, localities=self.localities)
            if loc.qdf is not None:
                self.all[loc_ins] = loc

    def __getitem__(self, key) -> Qdf_IRM:

        if isinstance(key, int):
            if key in self.all:
                return self.all[key]
            else:
                logging.error(f"INS code {key} not found in the data")
                return None

        elif isinstance(key, str):
            key = self.localities.get_INSfromname(key)
            if key is not None:
                if key in self.all:
                    return self.all[key]
                else:
                    logging.error(f"INS code {key} not found in the data")
                    return None
            else:
                logging.error(f"Name {key} not found in the data")
                return None


TRANSLATION_HEADER = {'année': 'year', 'janv.': 'January', 'févr.': 'February', 'mars': 'March',
            'avr.': 'April', 'mai': 'May', 'juin': 'June',
            'juil.': 'July', 'août': 'August', 'sept.': 'September',
            'oct.': 'October', 'nov.': 'November', 'déc.': 'December'}
RE_REFERENCE = re.compile(r"\([0-9]+\)")

class Climate_IRM():

    def __init__(self, store_path= 'irm', ins:Literal['2018', '2019', '2025', 2018, 2019, 2025] = 2018) -> None:
        self.store_path = Path(store_path)
        self.localities = Localities(ins)

        self._climate_data = {}

    def __getitem__(self, key):
        return self._climate_data[key]

    @classmethod
    def importfromwebsite(cls, store_path= 'irm', verbose:bool= False, waitingtime:float= .01, ins:Literal['2018', '2019', '2025', 2018, 2019, 2025] = 2018, ins_code: int = None, convert=False):
        """ Import Excel files for one or all municipalities from the IRM website

        :param store_path: Where to store the downloaded data. Directory will be created if it doesn't exists.
        :param verbose: If `True`, will print some progress information.
                        If `False`, will do nothing.
                        If a callable, then will call it with a float in [0, 1].
                        0 means nothing downloaded, 1 means everything downloaded.

        :param waitingtime: How long to wait (in seconds) betwenn the download
                            of each station (will make sure we don't overwhelm IRM's website).

        :param ins: The year of the INS codes to use.
        :param code: Restricts the data download to a specific NIS code. `None` means full download.
        :param convert: Converts the downloaded PDF to Excel files.
        """
        import requests

        myloc = Localities(ins)

        if ins_code is not None:
            codes_to_load = [ins_code]
        else:
            if not path.exists(store_path):
                mkdir(store_path)
            codes_to_load = myloc.inscode2name

        for key,myins in enumerate(codes_to_load):
            #chaîne URL du fichier Excel
            url="https://www.meteo.be//resources//climatology//climateCity//pdf//climate_INS"+str(myins)+"_9120_fr.pdf"
            #Obtention du fichiers depuis le site web de l'IRM
            response=requests.get(url)

            if str(response.content).find("Page not found")==-1 :

                # Make sure we create the store path only if we have
                # something to put inside.
                if ins_code is not None and not path.exists(store_path):
                    mkdir(store_path)

                pdf_file = path.join(store_path,str(myins)+".pdf")
                file=open(pdf_file, 'wb')
                file.write(response.content)
                file.close()

                if convert:
                    cls._convert_irm_file(pdf_file)

                if verbose:
                    if callable(verbose):
                        verbose(key/len(codes_to_load))
                    else:
                        print(myins)
            else:
                #logging.error(response.content)
                logging.error(f"Failed to load IRM data: {url} --> {response}")

            if len(codes_to_load) >= 2:
                sleep(waitingtime)

    @classmethod
    def _scrap_table(cls, t):
        """
        Helper method to transform a table represented as a list of list to a
        pandas DataFrame.
        """

        def fix_cid(strings: list[str]):
            # The CID thing is a known issue:
            # https://github.com/euske/pdfminer/issues/122
            return [s.replace('(cid:176)C ', '°C').replace('¢', "'") for s in strings]

        nt = []
        row_headers = []
        for rndx in range(1, len(t)):
            # In the row header, we remove the "references" like "(1)".
            row_headers.append( RE_REFERENCE.sub("", t[rndx][0]) )

            # The PDFs use different "minus" glyph instead of an ASCII one,
            # let's fix it.
            nt.append( list(map(lambda s:float(s.replace("−","-")), t[rndx][1:])))

        columns_headers = map(TRANSLATION_HEADER.get, t[0][1:])
        df = pd.DataFrame(nt, columns=fix_cid(columns_headers), index=fix_cid(row_headers))
        return df

    @classmethod
    def _convert_irm_file(cls, pdf_file: Union[str, Path]):
        """
        Scrap a PDF from IRM into two tables in a single Excel file with two
        sheets.
        """
        pdf_file = Path(pdf_file)
        with pdfplumber.open(pdf_file) as pdf:

            # Rain data
            df = cls._scrap_table(pdf.pages[1].extract_table())

            # Sun data
            df_sun = cls._scrap_table(pdf.pages[4].extract_table())

            dest_file = pdf_file.with_suffix('.xlsx')
            with pd.ExcelWriter(dest_file) as writer:  # doctest: +SKIP
                df.to_excel(writer, sheet_name='Rain')
                df_sun.to_excel(writer, sheet_name='Sun')
