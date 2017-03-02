# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is where a rectangular plt.plot is created 
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

import db_utils
from matplotlib.figure import Figure as figure
import numpy as np
import matplotlib.pyplot as plt
import datetime 
import sqlite3 as sqlite
import itertools
import midvatten_utils as utils

class PiperPlot():
    def __init__(self,msettings,activelayer):
        self.ms = msettings
        self.activelayer = activelayer
        self.create_parameter_selection()
        self.get_selected_observations()
        if self.ms.settingsdict['piper_markers']=='type':
            self.get_selected_obstypes()#gets unique plt.plottypes and a plt.plot type dictionary
            self.create_markers()
        elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
            self.create_markers()
        elif self.ms.settingsdict['piper_markers']=='date_time':
            self.get_selected_datetimes()
            self.create_markers()
        self.get_piper_data()
        #here is a simple printout (to python console) to let the user see the piper plt.plot data
        print """obsid, date_time, type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na+K_meqPl, Ca_meqPl, Mg_meqPl"""
        for row in self.obsrecarray:
            #print ','.join([unicode(col).encode('utf-8') for col in row])
            try:
                print ','.join([utils.returnunicode(col) for col in row])
            except:
                print "failed printing piper data..."            
        self.make_the_plot()

    def big_sql(self):
        # Data must be stored as mg/l in the database since it is converted to meq/l in code here...
        sql = r"""select a.obsid as obsid, date_time, obs_points.type as type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl + K_meqPl as NaK_meqPl, Ca_meqPl, Mg_meqPl
        from (select obsid, date_time, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl, K_meqPl, Ca_meqPl, Mg_meqPl
            from (
                  select obsid, date_time, 
                      (max (case when %s then reading_num end))/35.453 as Cl_meqPl,
                      (max (case when %s then reading_num end))/61.0168 as HCO3_meqPl,
                      2*(max (case when %s then reading_num end))/96.063 as SO4_meqPl,
                      (max (case when %s then reading_num end))/22.9898 as Na_meqPl,
                      (max (case when %s then reading_num end))/39.0983 as K_meqPl,
                      2*(max (case when %s then reading_num end))/40.078 as Ca_meqPl,
                      2*(max (case when %s then reading_num end))/24.305 as Mg_meqPl
                  from w_qual_lab where obsid in %s 
                  group by obsid, date_time
                )
            where Ca_meqPl is not null and Mg_meqPl is not null and Na_meqPl is not null and K_meqPl is not null and HCO3_meqPl is not null and Cl_meqPl is not null and SO4_meqPl is not null
            ) as a, obs_points WHERE a.obsid = obs_points.obsid""" %(self.ParameterList[0],self.ParameterList[1],self.ParameterList[2],self.ParameterList[3],self.ParameterList[4],self.ParameterList[5],self.ParameterList[6],(str(self.observations)).encode('utf-8').replace('[','(').replace(']',')'))
        return sql

    def create_markers(self):
        marker = itertools.cycle(('r+', 'b.', 'c*','go', 'mv', 'r^', 'b<', 'c>', 'g8', 'ms', 'rp', 'b*', 'ch', 'gH', 'mD', 'rd','b+', 'c.', 'g*','mo', 'rv', 'b^', 'c<', 'g>', 'm8', 'rs', 'bp', 'c*', 'gh', 'mH', 'rD', 'bd', 'c+', 'g.', 'm*','ro', 'bv', 'c^', 'g<', 'm>', 'r8', 'bs', 'cp', 'g*', 'mh', 'rH', 'bD', 'cd','g+', 'm.', 'r*','bo', 'cv', 'g^', 'm<', 'r>', 'b8', 'cs', 'gp', 'm*', 'rh', 'bH', 'cD', 'gd','m+', 'r.', 'b*','co', 'gv', 'm^', 'r<', 'b>', 'c8', 'gs', 'mp', 'r*', 'bh', 'cH', 'gD', 'md')) 
        self.markerset = {}
        if self.ms.settingsdict['piper_markers']=='type':
            for tp in self.distincttypes:
                self.markerset[tp[0]] =marker.next()
        elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
            for obs in self.observations:
                self.markerset[obs] =marker.next()
        elif self.ms.settingsdict['piper_markers']=='date_time':
            for date_time in self.date_times:
                self.markerset[date_time[0]] =marker.next()

    def create_parameter_selection(self):
        self.ParameterList=[]# ParameterList = ['Klorid, Cl','Alkalinitet, HCO3','Sulfat, SO4','Natrium, Na','Kalium, K','Kalcium, Ca','Magnesium, Mg']
        if self.ms.settingsdict['piper_cl']!='':
            self.ParameterList.append(r"""parameter = '""" + self.ms.settingsdict['piper_cl'] + "'")
        else:
            self.ParameterList.append(r"""(lower(parameter) like '%klorid%' or lower(parameter) like '%chloride%')""")
        if self.ms.settingsdict['piper_hco3']!='':
            self.ParameterList.append(r"""parameter = '""" + self.ms.settingsdict['piper_hco3'] + "'")
        else:
            self.ParameterList.append(r"""(lower(parameter) like '%alkalinitet%' or lower(parameter) like '%alcalinity%')""")
        if self.ms.settingsdict['piper_so4']!='':
            self.ParameterList.append(r"""parameter = '""" + self.ms.settingsdict['piper_so4'] + "'")
        else:
            self.ParameterList.append(r"""(lower(parameter) like '%sulfat%' or lower(parameter) like '%sulphat%')""")
        if self.ms.settingsdict['piper_na']!='':
            self.ParameterList.append(r"""parameter = '""" + self.ms.settingsdict['piper_na'] + "'")
        else:
            self.ParameterList.append(r"""(lower(parameter) like '%natrium%')""")
        if self.ms.settingsdict['piper_k']!='':
            self.ParameterList.append(r"""parameter = '""" + self.ms.settingsdict['piper_k'] + "'")
        else:
            self.ParameterList.append(r"""(lower(parameter) like '%kalium%' or lower(parameter) like '%potassium%')""")
        if self.ms.settingsdict['piper_ca']!='':
            self.ParameterList.append(r"""parameter = '""" + self.ms.settingsdict['piper_ca'] + "'")
        else:
            self.ParameterList.append(r"""(lower(parameter) like '%kalcium%' or lower(parameter) like '%calcium%')""")
        if self.ms.settingsdict['piper_mg']!='':
            self.ParameterList.append(r"""parameter = '""" + self.ms.settingsdict['piper_mg'] + "'")
        else:
            self.ParameterList.append(r"""(lower(parameter) like '%magnesium%')""")

    def get_selected_datetimes(self):
        sql1 = self.big_sql()
        sql2 = r""" select distinct date_time from (""" + sql1 + r""") order by date_time"""
        ConnOK, self.date_times = db_utils.sql_load_fr_db(sql2)
        
    def get_selected_observations(self):
        obsar = utils.getselectedobjectnames(self.activelayer)
        observations = obsar
        i=0
        for obs in obsar:
                observations[i] = obs.encode('utf-8') #turn into a list of python byte strings
                i += 1 
        self.observations=observations#A list with selected obsid

    def get_selected_obstypes(self):
        sql = "select obsid, type from obs_points where obsid in " +  str(self.observations).encode('utf-8').replace('[','(').replace(']',')')
        ConnOK, types = db_utils.sql_load_fr_db(sql)
        self.typedict = dict(types)#make it a dictionary
        sql = "select distinct type from obs_points where obsid in " +  str(self.observations).encode('utf-8').replace('[','(').replace(']',')')
        ConnOK, self.distincttypes = db_utils.sql_load_fr_db(sql)
        
    def get_piper_data(self):
        #These observations are supposed to be in mg/l and must be stored in a Midvatten database, table w_qual_lab
        sql = self.big_sql()
        print(sql)#debug
        # get data into a list: obsid, date_time, type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na+K_meqPl, Ca_meqPl, Mg_meqPl
        obsimport = db_utils.sql_load_fr_db(sql)[1]
        #convert to numpy ndarray W/O format specified
        self.obsnp_nospecformat = np.array(obsimport)
        #define format
        """ some problems with string fields
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
        
    def make_the_plot(self):
        nosamples = len(self.obsrecarray.obsid) # Determine number of samples in file
        # Change default settings for figures
        # -------------------------------------------------------------------------------- #
        plt.rc('savefig', dpi = 300)
        plt.rc('xtick', labelsize = 10)
        plt.rc('ytick', labelsize = 10)
        plt.rc('font', size = 12)
        plt.rc('legend', fontsize = 12)
        plt.rc('figure', figsize = (14,4.5)) # defines size of Figure window

        markersize = 8
        linewidth = 2
        xtickpositions = np.linspace(0,100,6) # desired xtickpositions for graphs

        # Make Figure
        # -------------------------------------------------------------------------------- #

        fig=plt.figure()

        # CATIONS
        # 2 lines below needed to create 2nd y-axis (ax1b) for first plt.subplot
        ax1 = fig.add_subplot(131)
        ax1b = ax1.twinx()

        ax1.fill([100,0,100,100],[0,100,100,0],color = (0.8,0.8,0.8))
        ax1.plot([100, 0],[0, 100],'k')
        ax1.plot([50, 0, 50, 50],[0, 50, 50, 0],'k--')
        ax1.text(25,15, 'Na type')
        ax1.text(75,15, 'Ca type')
        ax1.text(25,65, 'Mg type')

        # loop to use different symbol marker for each water type ("loop through samples and add one plt.plot per sample")
        if self.ms.settingsdict['piper_markers']=='type':
            for i in range(0, nosamples):
                ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), self.markerset[self.typedict[self.obsrecarray.obsid[i]]], ms = markersize)
        elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
            for i in range(0, nosamples):
                ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), self.markerset[self.obsrecarray.obsid[i]], ms = markersize)
        elif self.ms.settingsdict['piper_markers']=='date_time':
            for i in range(0, nosamples):
                ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), self.markerset[self.obsrecarray.date_time[i]], ms = markersize)
        else:#filled black circle is default if no unique markers are selected
            for i in range(0, nosamples):
                ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 'o', color="black", ms = markersize)
        
        ax1.set_xlim(0,100)
        ax1.set_ylim(0,100)
        ax1b.set_ylim(0,100)
        ax1.set_xlabel('<= Ca (% meq)')
        ax1b.set_ylabel('Mg (% meq) =>')
        plt.setp(ax1, yticklabels=[])

        # next two lines needed to reverse x axis:
        ax1.set_xlim(ax1.get_xlim()[::-1])

        # ANIONS
        plt.subplot(1,3,3)
        plt.fill([100,100,0,100],[0,100,100,0],color = (0.8,0.8,0.8))
        plt.plot([0, 100],[100, 0],'k')
        plt.plot([50, 50, 0, 50],[0, 50, 50, 0],'k--')
        plt.text(55,15, 'Cl type')
        plt.text(5,15, 'HCO3 type')
        plt.text(5,65, 'SO4 type')

        # loop to use different symbol marker for each water type
        if self.ms.settingsdict['piper_markers']=='type':
            for i in range(0, nosamples):
                plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), self.markerset[self.typedict[self.obsrecarray.obsid[i]]], ms = markersize)
        elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
            for i in range(0, nosamples):
                plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), self.markerset[self.obsrecarray.obsid[i]], ms = markersize)
        elif self.ms.settingsdict['piper_markers']=='date_time':
            for i in range(0, nosamples):
                plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), self.markerset[self.obsrecarray.date_time[i]], ms = markersize)
        else:#filled black circle is default if no unique markers are selected
            for i in range(0, nosamples):
                plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 'o',color="black", ms = markersize)
                
        plt.xlim(0,100)
        plt.ylim(0,100)
        plt.xlabel('Cl (% meq) =>')
        plt.ylabel('SO4 (% meq) =>')

        # CATIONS AND ANIONS COMBINED IN DIAMOND SHAPE PLOT = BOX IN RECTANGULAR COORDINATES
        # 2 lines below needed to create 2nd y-axis (ax1b) for first plt.subplot
        ax2 = fig.add_subplot(132)
        ax2b = ax2.twinx()

        ax2.plot([0, 100],[10, 10],'k--')
        ax2.plot([0, 100],[50, 50],'k--')
        ax2.plot([0, 100],[90, 90],'k--')
        ax2.plot([10, 10],[0, 100],'k--')
        ax2.plot([50, 50],[0, 100],'k--')
        ax2.plot([90, 90],[0, 100],'k--')
        plt.text(40,96, 'CO3+HCO3')
        plt.text(25,86, 'CO3+HCO3, SO4+Cl')
        plt.text(25,18, 'SO4+Cl, CO3+HCO3')
        plt.text(40,8, 'SO4+Cl')
        plt.text(3,40,'Ca+Mg',rotation=90)
        plt.text(16,30,'Ca+Mg, Na+K',rotation=90)
        plt.text(83,30,'Na+K, Ca+Mg',rotation=90)
        plt.text(93,40,'Na+K',rotation=90)

        # loop to use different symbol marker for each water type
        h=[]
        for i in range(0, nosamples):
            catsum = (self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i])
            ansum = (self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i])            
            if self.ms.settingsdict['piper_markers']=='type':
                h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, self.markerset[self.typedict[self.obsrecarray.obsid[i]]], ms = markersize,label=self.typedict[self.obsrecarray.obsid[i]]))
            elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
                h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, self.markerset[self.obsrecarray.obsid[i]], ms = markersize,label=self.obsrecarray.obsid[i]))
            elif self.ms.settingsdict['piper_markers']=='date_time':
                h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, self.markerset[self.obsrecarray.date_time[i]], ms = markersize,label=self.obsrecarray.date_time[i]))
            else:#filled black circle is default if no unique markers are selected
                h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'o',color="black", ms = markersize))
        ax2.set_xlim(0,100)
        ax2.set_ylim(0,100)
        ax2.set_xlabel('Na+K (% meq) =>')
        ax2.set_ylabel('SO4+Cl (% meq) =>')
        ax2.set_title('<= Ca+Mg (% meq)', fontsize = 12)
        ax2b.set_ylabel('<= CO3+HCO3 (% meq)')
        ax2b.set_ylim(0,100)
        # next two lines needed to reverse 2nd y axis:
        ax2b.set_ylim(ax2b.get_ylim()[::-1])

        # Legend for Figures, use dummy plt.plots for proxy artist legend
        if self.ms.settingsdict['piper_markers']=='type':
            dummyplot=[]
            for tp in self.distincttypes:
                dummyplot.append(ax1.plot(1000,1000,self.markerset[tp[0]],ms = markersize, ls='',label=tp[0]))
                ph,l = ax1.get_legend_handles_labels()
            leg = plt.figlegend(ph,l, ncol=6, shadow=False, fancybox=True, loc='lower center', handlelength = 1,numpoints = 1)
            leg.draggable(state=True)
            frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
            frame.set_facecolor('0.80')    # set the frame face color to light gray
            frame.set_fill(False)    # set the frame face color transparent              
        elif self.ms.settingsdict['piper_markers']=='obsid':
            dummyplot=[]
            for obs in self.observations:
                dummyplot.append(ax1.plot(1000,1000,self.markerset[obs],ms = markersize, ls='',label=obs))
                ph,l = ax1.get_legend_handles_labels()
            leg = plt.figlegend(ph,l, ncol=6, shadow=False, fancybox=True, loc='lower center', handlelength = 1,numpoints = 1)
            leg.draggable(state=True)
            frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
            frame.set_facecolor('0.80')    # set the frame face color to light gray
            frame.set_fill(False)    # set the frame face color transparent  
        elif self.ms.settingsdict['piper_markers']=='date_time':
            dummyplot=[]
            for date_time in self.date_times:
                dummyplot.append(ax1.plot(1000,1000,self.markerset[date_time[0]],ms = markersize, ls='',label=date_time[0]))
                ph,l = ax1.get_legend_handles_labels()
            leg = plt.figlegend(ph,l, ncol=6, shadow=False, fancybox=True, loc='lower center', handlelength = 1,numpoints = 1)
            leg.draggable(state=True)
            frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
            frame.set_facecolor('0.80')    # set the frame face color to light gray
            frame.set_fill(False)    # set the frame face color transparent
        else:    #no legend if no unique markers
            pass

        # adjust position plt.subplots
        plt.subplots_adjust(left=0.05, bottom=0.2, right=0.95, top=0.90, wspace=0.4, hspace=0.0)
        plt.show()
