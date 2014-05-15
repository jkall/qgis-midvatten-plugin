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
import matplotlib.pyplot as plt
import datetime 
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
        self.MakeThePlot()
        #self.FinishPlotWindow()

    def big_sql(self):
        # Data must be stored as mg/l in the database since it is converted to meq/l in code here...
        sql = r"""select a.obsid as obsid, date_time, obs_points.type as type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl + K_meqPl as NaK_meqPl, Ca_meqPl, Mg_meqPl
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
        #print dtype(self.obs)#debug
        #print self.obs#debug

    def GetPiperData(self):
        #These observations are supposed to be in mg/l and must be stored in a Midvatten database, table w_qual_lab
        sql = self.big_sql()
        # get data into a list: obsid, date_time, type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl, K_meqPl, Ca_meqPl, Mg_meqPl
        obsimport = utils.sql_load_fr_db(sql)[1]
        
        """Transform data to a numpy.recarray
        ### PROBLEMS WITH STRINGS! PERHAPS SKIP THEM IN NUMPY ARRAY????
        #convert to numpy array - could also have used 'asarray' but it does not matter in this situation
        """
        #convert to numpy ndarray W/O format specified
        self.obsnp_nospecformat = np.array(obsimport) 
                
        #define format
        """ some problems with string fiels
        np.str_
        My_format = [('obsid', str), 
        My_format = [('obsid', unicode), 
        My_format = [('obsid', np.dtype('a35')), 
        My_format = [('obsid', np.dtype(np.str_)),
        My_format = [('obsid', np.str_),
        My_format = [('obsid', object),
        none is working besides from 'a35' which limits string length to 35 characters 
        least bad is the "object" type, then everything is loaded, but all strings as unicode strings which _should_ be ok
        """
        My_format = [('obsid', object), ('date_time', datetime.datetime),('obstype', object),('Cl_meqPl', float),('HCO3_meqPl', float),('SO4_meqPl', float),('NaK_meqPl', float),('Ca_meqPl', float),('Mg_meqPl', float)]
        
        #convert to numpy ndarray W format specified - i.e. a structured array
        self.obsnp_specified_format = np.array(obsimport, dtype=My_format)
        
        #convert to np recarray - takes the structured array and makes the columns into callable objects, i.e. write table2.Cl_meqPl
        self.obsrecarray=self.obsnp_specified_format.view(np.recarray)
        
        """
        #some debugging printouts
        print "obsimport should be a list ", obsimport
        print obsimport[0][0]
        print "obsnp_nospecformat ", self.obsnp_nospecformat
        print self.obsnp_nospecformat[:,0]
        print "obsnp_specified_format ", self.obsnp_specified_format
        print self.obsnp_specified_format[:]['obsid']
        print "obsrecarray ", self.obsrecarray#debug
        print self.obsrecarray.obsid#debug
        print self.obsrecarray.NaK_meqPl#debug
        #ok works, use self.obsrecarray for floats and date_time. might need to access obsid and type one-by-one
        # Next step must be to create a column Na+K since that is the one to be plotted
        
        #size obsimport
        print len(obsimport)
        print self.obsnp_nospecformat.shape
        print self.obsnp_specified_format.shape
        """
        # Then categorize the Type to decide plot symbol dependent on typ
        # Then check date interval to set plot symbol color as a scale dependent on date
        
    def MakeThePlot(self):
        nosamples = len(self.obsrecarray.obsid) # Determine number of samples in file
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

        # loop to use different symbol marker for each water type ("loop through samples and add one plot per sample")
        for i in range(0, nosamples):
            if self.obsrecarray.obstype[i] == 1:
                plotsym= 'rs'
            elif self.obsrecarray.obstype[i] == 2:
                plotsym= 'b>'
            elif self.obsrecarray.obstype[i] == 3:
                plotsym= 'c<'
            elif self.obsrecarray.obstype[i] == 4:
                plotsym= 'go'
            elif self.obsrecarray.obstype[i] == 5:
                plotsym= 'm^'
            else:
                plotsym= 'bs'
            ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), plotsym, ms = markersize)

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
            if self.obsrecarray.obstype[i] == 1:
                plotsym= 'rs'
            elif self.obsrecarray.obstype[i] == 2:
                plotsym= 'b>'
            elif self.obsrecarray.obstype[i] == 3:
                plotsym= 'c<'
            elif self.obsrecarray.obstype[i] == 4:
                plotsym= 'go'
            elif self.obsrecarray.obstype[i] == 5:
                plotsym= 'm^'
            else:
                plotsym= 'bs'
            plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), plotsym, ms = markersize)
            
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
            catsum = (self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i])
            ansum = (self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i])
            if self.obsrecarray.obstype[i] == 1:
                h1,=ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'rs', ms = markersize)
            elif self.obsrecarray.obstype[i] == 2:
                h2,=ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'b>', ms = markersize)
            elif self.obsrecarray.obstype[i] == 3:
                h3,=ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'c<', ms = markersize)
            elif self.obsrecarray.obstype[i] == 4:
                h4,=ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'go', ms = markersize)
            elif self.obsrecarray.obstype[i] == 5:
                h5,=ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'm^', ms = markersize)
            else:
                h6,=ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'bs', ms = markersize)
                
        ax2.set_xlim(0,100)
        ax2.set_ylim(0,100)
        ax2.set_xlabel('Na+K (% meq) =>')
        ax2.set_ylabel('SO4+Cl (% meq) =>')
        ax2.set_title('<= Ca+Mg (% meq)', fontsize = 12)
        ax2b.set_ylabel('<= CO3+HCO3 (% meq)')
        ax2b.set_ylim(0,100)
        # next two lines needed to reverse 2nd y axis:
        ax2b.set_ylim(ax2b.get_ylim()[::-1])

        # Legend for Figure
        #figlegend((h1,h2,h3,h4,h5,h6),('Dinkel','Tributaries NL','Tributaries G','Lakes','Groundwater','Other'), ncol=6, shadow=False, fancybox=True, loc='lower center', handlelength = 3)
        #figlegend((h1,h2,h3,h4),(u'Grundvattenrör',u'Pumpbrunn',u'Ljusnan',u'Privat bergbrunn'), ncol=5, shadow=False, fancybox=True, loc='lower center', handlelength = 3)

        # adjust position subplots
        subplots_adjust(left=0.05, bottom=0.2, right=0.95, top=0.90, wspace=0.4, hspace=0.0)
        show()
