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
#from pylab import * # the pylab module combines Pyplot (MATLAB type of plotting) with Numpy into a single namespace
import numpy as np # prefer this instead of pylab 
import sqlite3 as sqlite
import midvatten_utils as utils#when ready, remove self.sql_load_fr_db and replace with utils.sql_load_fr_db

class piperplot():
    def __init__(self,dbpath,OBSID,ParameterList):
        # Specify locations of files and open the files
        # -------------------------------------------------------------------------------- #
        # Import observations
        # Observations are expected have meq/l units with parameters in the order: Cl, HCO3, SO4, Na, K, Ca, Mg
        sql = self.big_sql(OBSID,ParameterList)
        obs = self.sql_load_fr_db(dbpath,sql[1]# a list is returned # LATER, change to utils.sql_load_fr_db and skip dbpath as arg
        obs = np.asarray(obs)#convert to np array
        #obs=loadtxt(r"""U:\My Documents\pythoncode\scripts\ternary_plots\piper_rectangular_watersamples.txt""", delimiter='\t', comments='#') # first row with headers is skipped, matrix with data is assigned to obs (obs is a numpy array)
        #obs[obs == -9999] = NaN # if observations are missing, label them as -9999 (for example) in excel and make them Not a Number (NaN)

        nosamples = len(obs[:,0]) # Determine number of samples in file
        print obs
        """
        # Column Index for parameters
        Type = 3
        Cl = 4
        HCO3 = Cl+1
        SO4 = Cl+2
        Na = Cl + 3
        K = Cl+4
        Ca = Cl+5
        Mg = Cl+6

        # ---------------------------------->>>>>>DET HÄR ANGREPPSSÄTTET GÅR INTE-------------
        # MAN MÅSTE TA IN mg/l och
        " 1.  Loopa igenom arrayen och "find and replace" alla '<' som indikerar att vi är uder detektionsgränsen
        # 1b. Eventuellt ersätta med halva mätgränsvärdet
        # 2. Beräkna meq/l i koden...
        #
        # Sen åter på banan, nästa steg är då...
        # Fixa också en ny kolumn med Na+K eftersom det är den som ska plottas



        

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
            if obs[i, 0] == 1:
                plotsym= 'rs'
            elif obs[i, 0] == 2:
                plotsym= 'b>'
            elif obs[i, 0] == 3:
                plotsym= 'c<'
            elif obs[i, 0] == 4:
                plotsym= 'go'
            elif obs[i, 0] == 5:
                plotsym= 'm^'
            else:
                plotsym= 'bs'
            ax1.plot(100*obs[i,Ca]/(obs[i,NaK]+obs[i,Ca]+obs[i,Mg]), 100*obs[i,Mg]/(obs[i,NaK]+obs[i,Ca]+obs[i,Mg]), plotsym, ms = markersize)

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
            if obs[i, 0] == 1:
                plotsym= 'rs'
            elif obs[i, 0] == 2:
                plotsym= 'b>'
            elif obs[i, 0] == 3:
                plotsym= 'c<'
            elif obs[i, 0] == 4:
                plotsym= 'go'
            elif obs[i, 0] == 5:
                plotsym= 'm^'
            else:
                plotsym= 'bs'
            plot(100*obs[i,Cl]/(obs[i,Cl]+obs[i,HCO3]+obs[i,SO4]), 100*obs[i,SO4]/(obs[i,Cl]+obs[i,HCO3]+obs[i,SO4]), plotsym, ms = markersize)

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
            catsum = (obs[i,NaK]+obs[i,Ca]+obs[i,Mg])
            ansum = (obs[i,Cl]+obs[i,HCO3]+obs[i,SO4])
            if obs[i, 0] == 1:
                h1,=ax2.plot(100*obs[i,NaK]/catsum, 100*(obs[i,SO4]+obs[i,Cl])/ansum, 'rs', ms = markersize)
            elif obs[i, 0] == 2:
                h2,=ax2.plot(100*obs[i,NaK]/catsum, 100*(obs[i,SO4]+obs[i,Cl])/ansum, 'b>', ms = markersize)
            elif obs[i, 0] == 3:
                h3,=ax2.plot(100*obs[i,NaK]/catsum, 100*(obs[i,SO4]+obs[i,Cl])/ansum, 'c<', ms = markersize)
            elif obs[i, 0] == 4:
                h4,=ax2.plot(100*obs[i,NaK]/catsum, 100*(obs[i,SO4]+obs[i,Cl])/ansum, 'go', ms = markersize)
            else:
                h5,=ax2.plot(100*obs[i,NaK]/catsum, 100*(obs[i,SO4]+obs[i,Cl])/ansum, 'm^', ms = markersize)

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
        figlegend((h1,h2,h3,h4,h5),('Dinkel','Tributaries NL','Tributaries G','Lakes','Groundwater'), ncol=5, shadow=False, fancybox=True, loc='lower center', handlelength = 3)
        #figlegend((h1,h2,h3,h4),(u'Grundvattenrör',u'Pumpbrunn',u'Ljusnan',u'Privat bergbrunn'), ncol=5, shadow=False, fancybox=True, loc='lower center', handlelength = 3)

        # adjust position subplots
        subplots_adjust(left=0.05, bottom=0.2, right=0.95, top=0.90, wspace=0.4, hspace=0.0)
        show()
        """
        
    def big_sql(self,OBSID, ParameterList):
    # ---------------------------- THE SOLUTION-----------------------------
        sql = r"""select a.obsid as obsid, date_time, obs_points.type as type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl, K_meqPl, Ca_meqPl, Mg_meqPl
        from (select obsid, date_time, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl, K_meqPl, Ca_meqPl, Mg_meqPl
            from (
                  select obsid, date_time, 
                      (max (case when parameter = '%s' then reading_txt end))/35.453 as Cl_meqPl,
                      (max (case when parameter = '%s' then reading_txt end))/61.0168 as HCO3_meqPl,
                      2*(max (case when parameter = '%s' then reading_txt end))/96.063 as SO4_meqPl,
                      (max (case when parameter = '%s' then reading_txt end))/22.9898 as Na_meqPl,
                      (max (case when parameter = '%s' then reading_txt end))/39.0983 as K_meqPl,
                      2*(max (case when parameter = '%s' then reading_txt end))/40.078 as Ca_meqPl,
                      2*(max (case when parameter = '%s' then reading_txt end))/24.305 as Mg_meqPl
                  from w_qual_lab where obsid in %s 
                  group by obsid, date_time
                )
            where Ca_meqPl is not null and Mg_meqPl is not null and Na_meqPl is not null and K_meqPl is not null and HCO3_meqPl is not null and Cl_meqPl is not null and SO4_meqPl is not null
            ) as a, obs_points WHERE a.obsid = obs_points.obsid""" %(ParameterList[0],ParameterList[1],ParameterList[2],ParameterList[3],ParameterList[4],ParameterList[5],ParameterList[6],OBSID)
        return sql

def sql_load_fr_db(sql=''):#sql sent as unicode, result from db returned as list of unicode strings
    #qgis.utils.iface.messageBar().pushMessage("Debug",sql, 0,duration=30)#debug
    dbpath = QgsProject.instance().readEntry("Midvatten","database")
    try:
        conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)#dbpath[0] is unicode already #MacOSC fix1 
        curs = conn.cursor()
        resultfromsql = curs.execute(sql) #Send SQL-syntax to cursor #MacOSX fix1
        result = resultfromsql.fetchall()
        resultfromsql.close()
        conn.close()
        ConnectionOK = True
    except:
        pop_up_info("Could not connect to the database, please check Midvatten settings!\n Perhaps you need to reset settings first?")
        ConnectionOK = False
        result = ''
    return ConnectionOK, result
# ---------------------------- /THE SOLUTION-----------------------------

def main(dbpath, OBSID,ParameterList): #when this script is run directly or from python interpreter outside qgis
    print 'alright, main function called'
    """
    app=QtGui.QApplication.instance() # checks if QApplication already exists 
    if not app: # create QApplication if it doesnt exist 
        app = QtGui.QApplication(sys.argv)
        print 'there was no app so I did a new'
    """
    mypiper = piperplot(dbpath,OBSID,ParameterList)
    #sys.exit(app.exec_())#comment out when using Ipython

if __name__ == '__main__':#if this script is run directly
    """
    --------------<USER VARIABLES ARE FOUND HERE>--------------------------
    --------------WHEN RUNNING THIS SCRIPT, THEN THESE ARE SENT AS ARGS TO MAIN,
    -------------OTHERWISE IMPORT MODULE AND SEND OTHER ARGUMENTS
    """
    print 'I did start'
    #dbpath=u"/mnt/data/synkade_mappar/2666_veman_gvu/ARBETSDATA/DATABAS/2666_Midv_obsdb.sqlite"
    dbpath=u"/mnt/data/synkade_mappar/2513_funas/ARBETSDATA/DATABAS/2513_obs.sqlite"
    OBSID=('Rb0917', 'Rb0918', 'Br1002', 'Rb0919', 'Br1101', 'snow', 'Br139', 'Br140', 'Br141', 'Br142', 'Rb1038', 'Br143', 'Rb1002', 'Rb1039', 'Rb1004', 'Rb1005', 'Rb1045', 'pegel Christenssen', 'Rb1015', 'Rb1016', 'Rb0905', 'Rb1055', 'Rb1021')#2513
    ParameterList = ['Klorid, Cl','Alkalinitet, HCO3','Sulfat, SO4','Natrium, Na','Kalium, K','Kalcium, Ca','Magnesium, Mg']
    mypiper = main(dbpath, OBSID,ParameterList)
