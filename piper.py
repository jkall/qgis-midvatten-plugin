# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is where a rectangular plot is created 
 NOTE - if using this file, it has to be imported by midvatten.py
                             -------------------
        begin                : 2013-11-27
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com

This part of Midvatten plugin is partly based upon code from
__author__ = "B.M. van Breukelen <b.m.vanbreukelen@vu.nl>"
__version__ = "1.0"
__date__ = "Nov 2012"
__modified_by__ = u'Josef Källgården'
__modified_date__ = "Nov 2013"

   Adopted from: Ray and Mukherjee (2008) Groundwater 46(6): 893-896
    Development date: 8/5/2011
***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from pylab import * # ONLY DURING DEVELOPMENT the pylab module combines Pyplot (MATLAB type of plotting) with Numpy into a single namespace
import numpy as np # prefer this instead of pylab 
import sqlite3 as sqlite
import midvatten_utils as utils

class PiperPlot():
    def __init__(self,msettings,activelayer):
        self.ms = msettings
        self.activelayer = activelayer
        self.ParameterList=[]# ParameterList = ['Klorid, Cl','Alkalinitet, HCO3','Sulfat, SO4','Natrium, Na','Kalium, K','Kalcium, Ca','Magnesium, Mg']
        self.ParameterList.append(self.ms.settingsdict['piper_cl'])
        self.ParameterList.append(self.ms.settingsdict['piper_hco3'])
        self.ParameterList.append(self.ms.settingsdict['piper_so4'])
        self.ParameterList.append(self.ms.settingsdict['piper_na'])
        self.ParameterList.append(self.ms.settingsdict['piper_k'])
        self.ParameterList.append(self.ms.settingsdict['piper_ca'])
        self.ParameterList.append(self.ms.settingsdict['piper_mg'])

        self.GetSelectedObservations()
        self.GetPiperData()
        #self.GetSamplePiperData()#during development
        #self.MakeThePlot()
        #self.FinishPlotWindow()

    def big_sql(self):
        # Data must be stored as mg/l in the database since it is converted to meq/l in code here...
        sql = r"""select a.obsid as obsid, date_time, obs_points.type as type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl, K_meqPl, Ca_meqPl, Mg_meqPl
        from (select obsid, date_time, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl, K_meqPl, Ca_meqPl, Mg_meqPl
            from (
                  select obsid, date_time, 
                      (max (case when parameter = '%s' then reading_num end))/35.453 as Cl_meqPl,
                      (max (case when parameter = '%s' then reading_num end))/61.0168 as HCO3_meqPl,
                      2*(max (case when parameter = '%s' then reading_num end))/96.063 as SO4_meqPl,
                      (max (case when parameter = '%s' then reading_num end))/22.9898 as Na_meqPl,
                      (max (case when parameter = '%s' then reading_num end))/39.0983 as K_meqPl,
                      2*(max (case when parameter = '%s' then reading_num end))/40.078 as Ca_meqPl,
                      2*(max (case when parameter = '%s' then reading_num end))/24.305 as Mg_meqPl
                  from w_qual_lab where obsid in %s 
                  group by obsid, date_time
                )
            where Ca_meqPl is not null and Mg_meqPl is not null and Na_meqPl is not null and K_meqPl is not null and HCO3_meqPl is not null and Cl_meqPl is not null and SO4_meqPl is not null
            ) as a, obs_points WHERE a.obsid = obs_points.obsid""" %(self.ParameterList[0],self.ParameterList[1],self.ParameterList[2],self.ParameterList[3],self.ParameterList[4],self.ParameterList[5],self.ParameterList[6],(str(self.observations)).encode('utf-8').replace('[','(').replace(']',')'))
        return sql

    def GetSelectedObservations(self):
        obsar = utils.getselectedobjectnames(self.activelayer)
        observations = obsar
        i=0
        for obs in obsar:
                observations[i] = obs.encode('utf-8') #turn into a list of python byte strings
                i += 1 
        self.observations=observations#A list with selected obsid
        
    def GetSamplePiperData(self):
        self.observations=('Rb0917', 'Rb0918', 'Br1002', 'Rb0919', 'Br1101', 'snow', 'Br139', 'Br140', 'Br141', 'Br142', 'Rb1038', 'Br143', 'Rb1002', 'Rb1039', 'Rb1004', 'Rb1005', 'Rb1045', 'pegel Christenssen', 'Rb1015', 'Rb1016', 'Rb0905', 'Rb1055', 'Rb1021')
        #These sample data are given in meq/l and the loaded columns are: #Type, Cl, HCO3, SO4, NaK, Ca, Mg, EC, NO3, Sicc
        #observations are expected have meq/l units with parameters in the order: Cl, HCO3, SO4, Na, K, Ca, Mg
        self.obs=loadtxt(r"""/home/josef/pythoncode/scripts/plot/ternary_plots/piper_rectangular_watersamples.txt""", delimiter='\t', comments='#') # first row with headers is skipped, matrix with data is assigned to obs (obs is a numpy array)
        self.obs[self.obs == -9999] = NaN # if observations are missing, label them as -9999 (for example) in excel and make them Not a Number (NaN)
        print self.obs

    def GetPiperData(self):
        #These observations are supposed to be in mg/l and must be stored in a Midvatten database, table w_qual_lab
        sql = self.big_sql()
        self.obsimport = utils.sql_load_fr_db(sql)[1]# a list is returned 
        self.obsimport = np.asarray(self.obsimport)#convert to np array
        
        nosamples = len(self.obsimport[:,0]) # Determine number of samples in file
        print self.obsimport
        # Next step must be to create a column Na+K since that is the one to be plotted
        # Column Index for parameters
        Type = 3
        Cl = 4
        HCO3 = Cl+1
        SO4 = Cl+2
        Na = Cl + 3
        K = Cl+4
        Ca = Cl+5
        Mg = Cl+6
        # Then categorize the Type to decide plot symbol dependent on typ
        # Then check date interval to set plot symbol color as a scale dependent on date
        
    def MakeThePlot(self):
        # Change default settings for figures
        # -------------------------------------------------------------------------------- #
        rc('savefig', dpi = 300)
        rc('xtick', labelsize = 10)
        rc('ytick', labelsize = 10)
        rc('font', size = 12)
        rc('legend', fontsize = 12)
        rc('figure', figsize = (14,4.5)) # defines size of Figure window

        markersize = 8
        linewidth = 2
        xtickpositions = linspace(0,100,6) # desired xtickpositions for graphs

        # Make Figure
        # -------------------------------------------------------------------------------- #

        fig=figure()

        # CATIONS
        # 2 lines below needed to create 2nd y-axis (ax1b) for first subplot
        ax1 = fig.add_subplot(131)
        ax1b = ax1.twinx()

        ax1.fill([100,0,100,100],[0,100,100,0],color = (0.8,0.8,0.8))
        ax1.plot([100, 0],[0, 100],'k')
        ax1.plot([50, 0, 50, 50],[0, 50, 50, 0],'k--')
        ax1.text(25,15, 'Na type')
        ax1.text(75,15, 'Ca type')
        ax1.text(25,65, 'Mg type')

        # loop to use different symbol marker for each water type
        for i in range(0, nosamples):
            if self.obs[i, 0] == 1:
                plotsym= 'rs'
            elif self.obs[i, 0] == 2:
                plotsym= 'b>'
            elif self.obs[i, 0] == 3:
                plotsym= 'c<'
            elif self.obs[i, 0] == 4:
                plotsym= 'go'
            elif self.obs[i, 0] == 5:
                plotsym= 'm^'
            else:
                plotsym= 'bs'
            ax1.plot(100*self.obs[i,Ca]/(self.obs[i,NaK]+self.obs[i,Ca]+self.obs[i,Mg]), 100*self.obs[i,Mg]/(self.obs[i,NaK]+self.obs[i,Ca]+self.obs[i,Mg]), plotsym, ms = markersize)

        ax1.set_xlim(0,100)
        ax1.set_ylim(0,100)
        ax1b.set_ylim(0,100)
        ax1.set_xlabel('<= Ca (% meq)')
        ax1b.set_ylabel('Mg (% meq) =>')
        setp(ax1, yticklabels=[])

        # next two lines needed to reverse x axis:
        ax1.set_xlim(ax1.get_xlim()[::-1])


        # ANIONS
        subplot(1,3,3)
        fill([100,100,0,100],[0,100,100,0],color = (0.8,0.8,0.8))
        plot([0, 100],[100, 0],'k')
        plot([50, 50, 0, 50],[0, 50, 50, 0],'k--')
        text(55,15, 'Cl type')
        text(5,15, 'HCO3 type')
        text(5,65, 'SO4 type')

        # loop to use different symbol marker for each water type
        for i in range(0, nosamples):
            if self.obs[i, 0] == 1:
                plotsym= 'rs'
            elif self.obs[i, 0] == 2:
                plotsym= 'b>'
            elif self.obs[i, 0] == 3:
                plotsym= 'c<'
            elif self.obs[i, 0] == 4:
                plotsym= 'go'
            elif self.obs[i, 0] == 5:
                plotsym= 'm^'
            else:
                plotsym= 'bs'
            plot(100*self.obs[i,Cl]/(self.obs[i,Cl]+self.obs[i,HCO3]+self.obs[i,SO4]), 100*self.obs[i,SO4]/(self.obs[i,Cl]+self.obs[i,HCO3]+self.obs[i,SO4]), plotsym, ms = markersize)

        xlim(0,100)
        ylim(0,100)
        xlabel('Cl (% meq) =>')
        ylabel('SO4 (% meq) =>')


        # CATIONS AND ANIONS COMBINED IN DIAMOND SHAPE PLOT = BOX IN RECTANGULAR COORDINATES
        # 2 lines below needed to create 2nd y-axis (ax1b) for first subplot
        ax2 = fig.add_subplot(132)
        ax2b = ax2.twinx()

        ax2.plot([0, 100],[10, 10],'k--')
        ax2.plot([0, 100],[50, 50],'k--')
        ax2.plot([0, 100],[90, 90],'k--')
        ax2.plot([10, 10],[0, 100],'k--')
        ax2.plot([50, 50],[0, 100],'k--')
        ax2.plot([90, 90],[0, 100],'k--')
        text(40,96, 'CO3+HCO3')
        text(25,86, 'CO3+HCO3, SO4+Cl')
        text(25,18, 'SO4+Cl, CO3+HCO3')
        text(40,8, 'SO4+Cl')
        text(3,40,'Ca+Mg',rotation=90)
        text(16,30,'Ca+Mg, Na+K',rotation=90)
        text(83,30,'Na+K, Ca+Mg',rotation=90)
        text(93,40,'Na+K',rotation=90)

        # loop to use different symbol marker for each water type
        for i in range(0, nosamples):
            catsum = (self.obs[i,NaK]+self.obs[i,Ca]+self.obs[i,Mg])
            ansum = (self.obs[i,Cl]+self.obs[i,HCO3]+self.obs[i,SO4])
            if self.obs[i, 0] == 1:
                h1,=ax2.plot(100*self.obs[i,NaK]/catsum, 100*(self.obs[i,SO4]+self.obs[i,Cl])/ansum, 'rs', ms = markersize)
            elif self.obs[i, 0] == 2:
                h2,=ax2.plot(100*self.obs[i,NaK]/catsum, 100*(self.obs[i,SO4]+self.obs[i,Cl])/ansum, 'b>', ms = markersize)
            elif self.obs[i, 0] == 3:
                h3,=ax2.plot(100*self.obs[i,NaK]/catsum, 100*(self.obs[i,SO4]+self.obs[i,Cl])/ansum, 'c<', ms = markersize)
            elif self.obs[i, 0] == 4:
                h4,=ax2.plot(100*self.obs[i,NaK]/catsum, 100*(self.obs[i,SO4]+self.obs[i,Cl])/ansum, 'go', ms = markersize)
            else:
                h5,=ax2.plot(100*self.obs[i,NaK]/catsum, 100*(self.obs[i,SO4]+self.obs[i,Cl])/ansum, 'm^', ms = markersize)

        ax2.set_xlim(0,100)
        ax2.set_ylim(0,100)
        ax2.set_xlabel('Na+K (% meq) =>')
        ax2.set_ylabel('SO4+Cl (% meq) =>')
        ax2.set_title('<= Ca+Mg (% meq)', fontsize = 12)
        ax2b.set_ylabel('<= CO3+HCO3 (% meq)')
        ax2b.set_ylim(0,100)
        # next two lines needed to reverse 2nd y axis:
        ax2b.set_ylim(ax2b.get_ylim()[::-1])

    def FinishPlotWindow(self):
        # Legend for Figure
        figlegend((h1,h2,h3,h4,h5),('Dinkel','Tributaries NL','Tributaries G','Lakes','Groundwater'), ncol=5, shadow=False, fancybox=True, loc='lower center', handlelength = 3)
        #figlegend((h1,h2,h3,h4),(u'Grundvattenrör',u'Pumpbrunn',u'Ljusnan',u'Privat bergbrunn'), ncol=5, shadow=False, fancybox=True, loc='lower center', handlelength = 3)

        # adjust position subplots
        subplots_adjust(left=0.05, bottom=0.2, right=0.95, top=0.90, wspace=0.4, hspace=0.0)
        show()
