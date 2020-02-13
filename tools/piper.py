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
__modified_by__ = 'Josef Källgården'
__modified_date__ = "Nov 2013"

   Adopted from: Ray and Mukherjee (2008) Groundwater 46(6): 893-896
    Development date: 8/5/2011
***************************************************************************/
"""
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object

import datetime
import itertools
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import math
from definitions.midvatten_defs import piperplot_style, piperplot2_style

#import plotly.graph_objs as go
#from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru


class PiperPlot(object):
    def __init__(self, msettings, activelayer, version=1):
        self.ms = msettings
        self.activelayer = activelayer
        if version == 1:
            self.plot_function = self.make_the_plot
        else:
            self.plot_function = self.make_the_plot2

        self.labels_positive_rotation = []
        self.labels_negative_rotation = []

    def get_data_and_make_plot(self):

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
        try:
            print("""obsid, date_time, type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na+K_meqPl, Ca_meqPl, Mg_meqPl""")
        except:
            pass
        for row in self.obsrecarray:
            #print ','.join([unicode(col).encode('utf-8') for col in row])
            try:
                # fix_print_with_import
                print(','.join([ru(col) for col in row]))
            except:
                try:
                    # fix_print_with_import
                    print("failed printing piper data...")
                except:
                    pass

        self.plot_function()

    def big_sql(self):
        # Data must be stored as mg/l in the database since it is converted to meq/l in code here...
        sql = """select a.obsid as obsid, date_time, obs_points.type as type, Cl_meqPl, HCO3_meqPl, SO4_meqPl, Na_meqPl + K_meqPl as NaK_meqPl, Ca_meqPl, Mg_meqPl
        from (select u.obsid, u.date_time, u.Cl_meqPl, u.HCO3_meqPl, u.SO4_meqPl, u.Na_meqPl, u.K_meqPl, u.Ca_meqPl, u.Mg_meqPl
            from (
                  select obsid, date_time, 
                      (max (case when %s then reading_num end))/35.453 as Cl_meqPl,
                      (max (case when %s then reading_num end))/61.0168 as HCO3_meqPl,
                      2*(max (case when %s then reading_num end))/96.063 as SO4_meqPl,
                      (max (case when %s then reading_num end))/22.9898 as Na_meqPl,
                      (max (case when %s then reading_num end))/39.0983 as K_meqPl,
                      2*(max (case when %s then reading_num end))/40.078 as Ca_meqPl,
                      2*(max (case when %s then reading_num end))/24.305 as Mg_meqPl
                  from w_qual_lab where obsid in (%s) 
                  group by obsid, date_time
                ) AS u
            where u.Ca_meqPl is not null and u.Mg_meqPl is not null and u.Na_meqPl is not null and u.K_meqPl is not null and u.HCO3_meqPl is not null and u.Cl_meqPl is not null and u.SO4_meqPl is not null
            ) as a, obs_points WHERE a.obsid = obs_points.obsid""" %(ru(self.ParameterList[0]), ru(self.ParameterList[1]), ru(self.ParameterList[2]), ru(self.ParameterList[3]), ru(self.ParameterList[4]), ru(self.ParameterList[5]), ru(self.ParameterList[6]), utils.sql_unicode_list(self.observations))
        return sql

    def create_markers(self):
        marker = itertools.cycle(('r+', 'b.', 'c*','go', 'mv', 'r^', 'b<', 'c>', 'g8', 'ms', 'rp', 'b*', 'ch', 'gH', 'mD', 'rd','b+', 'c.', 'g*','mo', 'rv', 'b^', 'c<', 'g>', 'm8', 'rs', 'bp', 'c*', 'gh', 'mH', 'rD', 'bd', 'c+', 'g.', 'm*','ro', 'bv', 'c^', 'g<', 'm>', 'r8', 'bs', 'cp', 'g*', 'mh', 'rH', 'bD', 'cd','g+', 'm.', 'r*','bo', 'cv', 'g^', 'm<', 'r>', 'b8', 'cs', 'gp', 'm*', 'rh', 'bH', 'cD', 'gd','m+', 'r.', 'b*','co', 'gv', 'm^', 'r<', 'b>', 'c8', 'gs', 'mp', 'r*', 'bh', 'cH', 'gD', 'md')) 
        self.markerset = {}
        if self.ms.settingsdict['piper_markers']=='type':
            for tp in self.distincttypes:
                self.markerset[tp[0]] =next(marker)
        elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
            for obs in self.observations:
                self.markerset[obs] =next(marker)
        elif self.ms.settingsdict['piper_markers']=='date_time':
            for date_time in self.date_times:
                self.markerset[date_time[0]] =next(marker)

    def create_parameter_selection(self):
        self.ParameterList=[]# ParameterList = ['Klorid, Cl','Alkalinitet, HCO3','Sulfat, SO4','Natrium, Na','Kalium, K','Kalcium, Ca','Magnesium, Mg']

        #The dict is not implemented yet
        paramshorts_parameters = {}

        piper_setting_and_backup_names = [(r"""piper_cl""", (r"""klorid""", r"""chloride""")),
                                         (r"""piper_hco3""", (r"""alkalinitet""", r"""alcalinity""")),
                                         (r"""piper_so4""", (r"""sulfat""", r"""sulphat""")),
                                         (r"""piper_na""", (r"""natrium""",)),
                                         (r"""piper_k""", (r"""kalium""", r"""potassium""")),
                                         (r"""piper_ca""", (r"""kalcium""", r"""calcium""")),
                                         (r"""piper_mg""", (r"""magnesium""",))]

        for piper_setting, backup_names in piper_setting_and_backup_names:
            specified_name = self.ms.settingsdict[piper_setting]
            if specified_name != '':
                parameters = paramshorts_parameters.get(specified_name, None)
                if parameters is None:
                    self.ParameterList.append(r"""parameter = '%s'"""%specified_name)
                else:
                    self.ParameterList.append(r"""(""" + r""" or """.join([r"""parameter = '""" + parameter + r"""'""" for parameter in parameters]) + r""")""")
            else:
                self.ParameterList.append(r"""(""" + r""" or """.join([r"""lower(parameter) like '%""" + backup_name + r"""%'""" for backup_name in backup_names]) + r""")""")

    def get_selected_datetimes(self):
        sql1 = self.big_sql()
        sql2 = r""" select distinct date_time from (""" + sql1 + r""") order by date_time"""
        ConnOK, self.date_times = db_utils.sql_load_fr_db(sql2)
        
    def get_selected_observations(self):
        self.observations = utils.getselectedobjectnames(self.activelayer)

    def get_selected_obstypes(self):
        sql = "select obsid, type from obs_points where obsid in ({})".format(utils.sql_unicode_list(self.observations))
        ConnOK, types = db_utils.sql_load_fr_db(sql)
        self.typedict = dict(types)#make it a dictionary
        sql = "select distinct type from obs_points where obsid in ({})".format(utils.sql_unicode_list(self.observations))
        ConnOK, self.distincttypes = db_utils.sql_load_fr_db(sql)
        
    def get_piper_data(self):
        #These observations are supposed to be in mg/l and must be stored in a Midvatten database, table w_qual_lab
        sql = self.big_sql()
        try:
            print(sql)#debug
        except:
            pass
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

        with plt.style.context((piperplot_style())):

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
                    ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), self.markerset[self.typedict[self.obsrecarray.obsid[i]]])
            elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
                for i in range(0, nosamples):
                    ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), self.markerset[self.obsrecarray.obsid[i]])
            elif self.ms.settingsdict['piper_markers']=='date_time':
                for i in range(0, nosamples):
                    ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), self.markerset[self.obsrecarray.date_time[i]])
            else:#filled black circle is default if no unique markers are selected
                for i in range(0, nosamples):
                    ax1.plot(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 'o', color="black")

            ax1.set_xlim(0,100)
            ax1.set_ylim(0,100)
            ax1b.set_ylim(0,100)
            ax1.set_xlabel('<= Ca (% meq)')
            ax1b.set_ylabel('<= Na+K (% meq)')
            self.left_ax = ax1

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
                    plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), self.markerset[self.typedict[self.obsrecarray.obsid[i]]])
            elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
                for i in range(0, nosamples):
                    plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), self.markerset[self.obsrecarray.obsid[i]])
            elif self.ms.settingsdict['piper_markers']=='date_time':
                for i in range(0, nosamples):
                    plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), self.markerset[self.obsrecarray.date_time[i]])
            else:#filled black circle is default if no unique markers are selected
                for i in range(0, nosamples):
                    plt.plot(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 'o',color="black")

            plt.xlim(0,100)
            plt.ylim(0,100)
            plt.xlabel('Cl (% meq) =>')
            plt.ylabel('<= CO3+HCO3 (% meq)')
            self.right_ax = plt.gca()

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
                    h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, self.markerset[self.typedict[self.obsrecarray.obsid[i]]],label=self.typedict[self.obsrecarray.obsid[i]]))
                elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
                    h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, self.markerset[self.obsrecarray.obsid[i]],label=self.obsrecarray.obsid[i]))
                elif self.ms.settingsdict['piper_markers']=='date_time':
                    h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, self.markerset[self.obsrecarray.date_time[i]], label=self.obsrecarray.date_time[i]))
                else:#filled black circle is default if no unique markers are selected
                    h.append(ax2.plot(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum, 'o',color="black"))
            ax2.set_xlim(0,100)
            ax2.set_ylim(0,100)
            ax2.set_xlabel('Na+K (% meq) =>')
            ax2.set_ylabel('SO4+Cl (% meq) =>')
            ax2.set_title('<= Ca+Mg (% meq)')
            ax2b.set_ylabel('<= CO3+HCO3 (% meq)')
            ax2b.set_ylim(0,100)
            # next two lines needed to reverse 2nd y axis:
            ax2b.set_ylim(ax2b.get_ylim()[::-1])

            # Legend for Figures, use dummy plt.plots for proxy artist legend
            if self.ms.settingsdict['piper_markers']=='type':
                dummyplot=[]
                for tp in self.distincttypes:
                    dummyplot.append(ax1.plot(1000,1000,self.markerset[tp[0]], ls='',label=tp[0]))
                    ph,l = ax1.get_legend_handles_labels()
                leg = plt.figlegend(ph,l, ncol=6)
                try:
                    leg.set_draggable(state=True)
                except AttributeError:
                    # For older version of matplotlib
                    leg.draggable(state=True)
                frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_fill(False)    # set the frame face color transparent
            elif self.ms.settingsdict['piper_markers']=='obsid':
                dummyplot=[]
                for obs in self.observations:
                    dummyplot.append(ax1.plot(1000,1000,self.markerset[obs], ls='',label=obs))
                    ph,l = ax1.get_legend_handles_labels()
                leg = plt.figlegend(ph,l, ncol=6)
                try:
                    leg.set_draggable(state=True)
                except AttributeError:
                    # For older version of matplotlib
                    leg.draggable(state=True)
                frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_fill(False)    # set the frame face color transparent
            elif self.ms.settingsdict['piper_markers']=='date_time':
                dummyplot=[]
                for date_time in self.date_times:
                    dummyplot.append(ax1.plot(1000,1000,self.markerset[date_time[0]], ls='',label=date_time[0]))
                    ph,l = ax1.get_legend_handles_labels()
                leg = plt.figlegend(ph,l, ncol=6)
                try:
                    leg.set_draggable(state=True)
                except AttributeError:
                    # For older version of matplotlib
                    leg.draggable(state=True)
                frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_fill(False)    # set the frame face color transparent
            else:    #no legend if no unique markers
                pass

            self.set_rotated_axes_labels()
            self.fig = fig
            self.fig.canvas.mpl_connect('resize_event', self.set_rotated_axes_labels)
            self.fig.canvas.mpl_connect('draw_event', self.set_rotated_axes_labels)
            fig.show()

    def make_the_plot2(self):
        nosamples = len(self.obsrecarray.obsid) # Determine number of samples in file
        # Change default settings for figures

        with plt.style.context((piperplot2_style())):

            # Make Figure
            # -------------------------------------------------------------------------------- #

            fig=plt.figure()

            # CATIONS
            # 2 lines below needed to create 2nd y-axis (ax1b) for first plt.subplot
            plot_size = 1

            ax = fig.add_subplot(111)
            self.ax = ax
            self.fig = fig
            # sidan är figsize / hspace/2.
            hspace = 20
            self.hspace = hspace
            side_length = 100
            self.side_length = side_length
            axes_step = 20
            #side_length, hspace, xmin, ymin, xlim, ylim)
            tri1 = TriangleGraph(side_length=side_length, hspace=hspace, xmin=0, ymin=0, xlim=(100, 0), ylim=(0, 100))
            tri2 = TriangleGraph(side_length=side_length, hspace=hspace, xmin=side_length + hspace, ymin=0,
                                 xlim=(0, 100), ylim=(0, 100))
            rhomb = RhomboidGraph(side_length=side_length, hspace=hspace, xmin=tri1.xmin+side_length/2+hspace/2,
                                  ymin=equilateral_height(hspace), xlim=(0, 100), ylim=(0, 100))

            tri1_t = tri1.get_triangle_nodes(axes_step)
            print(str(tri1_t))

            #ax.triplot(tri1_t[0], tri1_t[1] 'k--')
            #ax.scatter(tri1_t[0], tri1_t[1])
            #print(str(*tri1.transform([0, 100, 0], [0, 0, 100])))


            for axes_edges in [tri1.transform([0, 100, 0, 0], [0, 0, 100, 0]),
                               tri2.transform([0, 100, 0, 0], [0, 0, 100, 0]),
                               rhomb.transform([0, 0, 100, 100, 0], [0, 100, 100, 0, 0])]:
                ax.plot(*axes_edges, color=mpl.rcParams['axes.edgecolor'],
                        linewidth=mpl.rcParams['axes.linewidth'])

            if mpl.rcParams['axes.grid']:
                for l in rhomb.get_grid_lines(axes_step):
                    ax.plot(*l, color=mpl.rcParams['grid.color'],
                            linestyle=mpl.rcParams['grid.linestyle'],
                            linewidth=mpl.rcParams['grid.linewidth'],
                            alpha=mpl.rcParams['grid.alpha'],
                            zorder=0)

            inner_linestyle = 'k--'
            for tri in [tri1, tri2]:
                inner_triangle = [[50, 50, 0, 50], [0, 50, 50, 0]]
                ax.plot(*tri.transform(*inner_triangle), inner_linestyle)

            # Rhomb inner lines
            ax.plot(*rhomb.transform([50, 50], [0, 100]), inner_linestyle)
            ax.plot(*rhomb.transform([0, 100], [50, 50]), inner_linestyle)
            ax.plot(*rhomb.transform([0, 100], [10, 10]), inner_linestyle)
            ax.plot(*rhomb.transform([0, 100], [90, 90]), inner_linestyle)
            ax.plot(*rhomb.transform([10, 10], [0, 100]), inner_linestyle)
            ax.plot(*rhomb.transform([90, 90], [0, 100]), inner_linestyle)

            labels_zorder = 2
            shared_label_params = {'zorder': 2, 'rotation_mode': 'anchor', 'fontsize': mpl.rcParams['ytick.labelsize']}
            # Labels
            ax.text(*tri1.transform(50, 50), '50%', ha='right', va='bottom', **shared_label_params)
            self.labels_positive_rotation.append(ax.text(*tri1.transform(0, 50), '50%', ha='left', va='bottom', rotation=get_rotation(ax, side_length), **shared_label_params))
            self.labels_negative_rotation.append(ax.text(*tri1.transform(50, 0), '50%', ha='left', va='top', rotation=-get_rotation(ax, side_length), **shared_label_params))

            self.labels_negative_rotation.append(ax.text(*tri2.transform(0, 50), '50%', ha='right', va='bottom', rotation=-get_rotation(ax, side_length), **shared_label_params))
            ax.text(*tri2.transform(50, 50), '50%', ha='left', va='bottom', **shared_label_params)
            self.labels_positive_rotation.append(ax.text(*tri2.transform(50, 0), '50%', ha='right', va='bottom', rotation=get_rotation(ax, side_length), **shared_label_params))

            self.labels_positive_rotation.append(ax.text(*tri1.transform(80, 20), 'Mg (% meq) =>', ha='center', va='bottom', **shared_label_params))
            self.labels_negative_rotation.append(ax.text(*tri1.transform(0, 20), '<= Na+K (% meq)', ha='center', va='bottom', rotation=-get_rotation(ax, side_length), **shared_label_params))
            ax.text(*tri1.transform(80, 0), '<= Ca (% meq)', ha='center', va='top', **shared_label_params)

            ax.text(*tri1.transform(15, 15), 'Na type', ha='center', va='center', **shared_label_params)
            ax.text(*tri1.transform(65, 15), 'Ca type', ha='center', va='center', **shared_label_params)
            ax.text(*tri1.transform(15, 65), 'Mg type', ha='center', va='center', **shared_label_params)

            ax.text(*tri2.transform(15, 65), 'SO4 type', ha='center', va='center', **shared_label_params)
            ax.text(*tri2.transform(65, 15), 'Cl type', ha='center', va='center', **shared_label_params)
            ax.text(*tri2.transform(15, 15), 'HCO3 type', ha='center', va='center', **shared_label_params)

            # loop to use different symbol marker for each water type ("loop through samples and add one plt.plot per sample")
            if self.ms.settingsdict['piper_markers']=='type':
                for i in range(0, nosamples):
                    ax.plot(*tri1.transform(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i])), self.markerset[self.typedict[self.obsrecarray.obsid[i]]])
            elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
                for i in range(0, nosamples):
                    ax.plot(*tri1.transform(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i])), self.markerset[self.obsrecarray.obsid[i]])
            elif self.ms.settingsdict['piper_markers']=='date_time':
                for i in range(0, nosamples):
                    ax.plot(*tri1.transform(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i])), self.markerset[self.obsrecarray.date_time[i]])
            else:#filled black circle is default if no unique markers are selected
                for i in range(0, nosamples):
                    ax.plot(*tri1.transform(100*self.obsrecarray.Ca_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i]), 100*self.obsrecarray.Mg_meqPl[i]/(self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i])), 'o', color="black")


            # loop to use different symbol marker for each water type
            if self.ms.settingsdict['piper_markers']=='type':
                for i in range(0, nosamples):
                    plt.plot(*tri2.transform(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i])), self.markerset[self.typedict[self.obsrecarray.obsid[i]]])
            elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
                for i in range(0, nosamples):
                    plt.plot(*tri2.transform(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i])), self.markerset[self.obsrecarray.obsid[i]])
            elif self.ms.settingsdict['piper_markers']=='date_time':
                for i in range(0, nosamples):
                    plt.plot(*tri2.transform(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i])), self.markerset[self.obsrecarray.date_time[i]])
            else:#filled black circle is default if no unique markers are selected
                for i in range(0, nosamples):
                    plt.plot(*tri2.transform(100*self.obsrecarray.Cl_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i]), 100*self.obsrecarray.SO4_meqPl[i]/(self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i])), 'o',color="black")




            # loop to use different symbol marker for each water type
            h=[]
            for i in range(0, nosamples):
                catsum = (self.obsrecarray.NaK_meqPl[i]+self.obsrecarray.Ca_meqPl[i]+self.obsrecarray.Mg_meqPl[i])
                ansum = (self.obsrecarray.Cl_meqPl[i]+self.obsrecarray.HCO3_meqPl[i]+self.obsrecarray.SO4_meqPl[i])
                if self.ms.settingsdict['piper_markers']=='type':
                    h.append(ax.plot(*rhomb.transform(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum), self.markerset[self.typedict[self.obsrecarray.obsid[i]]],label=self.typedict[self.obsrecarray.obsid[i]]))
                elif self.ms.settingsdict['piper_markers']=='obsid' or self.ms.settingsdict['piper_markers']=='obsid but no legend':
                    h.append(ax.plot(*rhomb.transform(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum), self.markerset[self.obsrecarray.obsid[i]],label=self.obsrecarray.obsid[i]))
                elif self.ms.settingsdict['piper_markers']=='date_time':
                    h.append(ax.plot(*rhomb.transform(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum), self.markerset[self.obsrecarray.date_time[i]], label=self.obsrecarray.date_time[i]))
                else:#filled black circle is default if no unique markers are selected
                    h.append(ax.plot(*rhomb.transform(100*self.obsrecarray.NaK_meqPl[i]/catsum, 100*(self.obsrecarray.SO4_meqPl[i]+self.obsrecarray.Cl_meqPl[i])/ansum), 'o',color="black"))



            ax.grid(False)
            plt.axis('off')
            ax.margins(0)

            self.fig.canvas.mpl_connect('resize_event', self.set_rotated_axes_labels)
            self.fig.canvas.mpl_connect('draw_event', self.set_rotated_axes_labels)

            fig.show()
            return


            plt.xlim(0,100)
            plt.ylim(0,100)
            plt.xlabel('Cl (% meq) =>')
            plt.ylabel('<= CO3+HCO3 (% meq)')
            self.right_ax = plt.gca()

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

            ax2.set_xlim(0,100)
            ax2.set_ylim(0,100)
            ax2.set_xlabel('Na+K (% meq) =>')
            ax2.set_ylabel('SO4+Cl (% meq) =>')
            ax2.set_title('<= Ca+Mg (% meq)')
            ax2b.set_ylabel('<= CO3+HCO3 (% meq)')
            ax2b.set_ylim(0,100)
            # next two lines needed to reverse 2nd y axis:
            ax2b.set_ylim(ax2b.get_ylim()[::-1])

            # Legend for Figures, use dummy plt.plots for proxy artist legend
            if self.ms.settingsdict['piper_markers']=='type':
                dummyplot=[]
                for tp in self.distincttypes:
                    dummyplot.append(ax1.plot(1000,1000,self.markerset[tp[0]], ls='',label=tp[0]))
                    ph,l = ax1.get_legend_handles_labels()
                leg = plt.figlegend(ph,l, ncol=6)
                try:
                    leg.set_draggable(state=True)
                except AttributeError:
                    # For older version of matplotlib
                    leg.draggable(state=True)
                frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_fill(False)    # set the frame face color transparent
            elif self.ms.settingsdict['piper_markers']=='obsid':
                dummyplot=[]
                for obs in self.observations:
                    dummyplot.append(ax1.plot(1000,1000,self.markerset[obs], ls='',label=obs))
                    ph,l = ax1.get_legend_handles_labels()
                leg = plt.figlegend(ph,l, ncol=6)
                try:
                    leg.set_draggable(state=True)
                except AttributeError:
                    # For older version of matplotlib
                    leg.draggable(state=True)
                frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_fill(False)    # set the frame face color transparent
            elif self.ms.settingsdict['piper_markers']=='date_time':
                dummyplot=[]
                for date_time in self.date_times:
                    dummyplot.append(ax1.plot(1000,1000,self.markerset[date_time[0]], ls='',label=date_time[0]))
                    ph,l = ax1.get_legend_handles_labels()
                leg = plt.figlegend(ph,l, ncol=6)
                try:
                    leg.set_draggable(state=True)
                except AttributeError:
                    # For older version of matplotlib
                    leg.draggable(state=True)
                frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_fill(False)    # set the frame face color transparent
            else:    #no legend if no unique markers
                pass

            self.set_rotated_axes_labels()
            self.fig = fig
            self.fig.canvas.mpl_connect('resize_event', self.set_rotated_axes_labels)
            self.fig.canvas.mpl_connect('draw_event', self.set_rotated_axes_labels)
            fig.show()

    def set_rotated_axes_labels(self, event=None):
        for l in self.labels_positive_rotation:
            l.set_rotation(get_rotation(self.ax, self.side_length))

        for l in self.labels_negative_rotation:
            l.set_rotation(-get_rotation(self.ax, self.side_length))


class TriangleGraph(object):
    def __init__(self, side_length, hspace, xmin, ymin, xlim, ylim):
        self.side_length = side_length
        self.hspace = hspace
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmin + side_length
        self.ymax = ymin + equilateral_height(hspace)
        self.xlim = xlim
        self.ylim = ylim
        self.reverse_x_factor = 1 if self.xlim[0] > self.xlim[1] else 1

    def transform(self, x, y):
        if isinstance(x, (list, tuple)):
            return zip(*[self._transform(x[idx], y[idx]) for idx in range(len(x))])
        else:
            return self._transform(x, y)

    def _transform(self, x, y):
        transformed_y = self.ymin + equilateral_height(self.side_length * ((y / (self.ylim[1] - self.ylim[0]))))
        transformed_x = self.xmin + self.side_length * ((x + self.reverse_x_factor*(y/2) - self.xlim[0]) / (self.xlim[1] - self.xlim[0]))
        return transformed_x, transformed_y

    def get_triangle_nodes(self, step):
        x_s = []
        y_s = []
        for xidx, x in enumerate(range(min(self.xlim), max(self.xlim) + step, step)):
            for yidx, y in enumerate(range(min(self.ylim), max(self.ylim) + step, step)):
                if x+y < self.ylim[1] + self.ylim[1]*0.5 - x/2:
                    x_t, y_t = self.transform(x, y)
                    x_s.append(x_t)
                    y_s.append(y_t)
        x = np.asarray(x_s)
        y = np.asarray(y_s)
        return x, y



class RhomboidGraph(object):
    def __init__(self, side_length, hspace, xmin, ymin, xlim, ylim):
        self.side_length = side_length
        self.hspace = hspace
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmin + side_length
        self.ymax = ymin + 2 * equilateral_height(side_length)
        self.xlim = xlim
        self.ylim = ylim

    def transform(self, x, y):
        if isinstance(x, (list, tuple)):
            return zip(*[self._transform(x[idx], y[idx]) for idx in range(len(x))])
        else:
            return self._transform(x, y)

    def _transform(self, x, y):
        transformed_y = self.ymin + equilateral_height(self.side_length) + \
                        equilateral_height(self.side_length * (y / (self.ylim[1] - self.ylim[0]))) - \
                        equilateral_height(self.side_length * (x / (self.xlim[1] - self.xlim[0])))
        transformed_x = self.xmin + self.side_length * \
                        (x / ((self.xlim[1] - self.xlim[0])*2) + y / ((self.ylim[1] - self.ylim[0]) * 2))
        return transformed_x, transformed_y

    def get_grid_lines(self, step):
        lines = []

        if mpl.rcParams['axes.grid.axis'] in ('both', 'x'):
            for y in range(min(self.ylim) + step, max(self.ylim), step):
                lines.append(self.transform([self.xlim[0], self.xlim[1]], [y, y]))
        if mpl.rcParams['axes.grid.axis'] in ('both', 'y'):
            for x in range(min(self.xlim) + step, max(self.xlim), step):
                lines.append(self.transform([x, x], [self.ylim[0], self.ylim[1]]))

        return lines

def equilateral_height(side_length):
    """height of equilateral triangle"""
    return math.sin(math.radians(60))*side_length


def _get_rotation(ax):
    bbox = ax.get_window_extent()
    width, height = bbox.width, bbox.height
    return math.degrees(math.atan(height / width))

def get_rotation(ax, side_length):
    #height = hspace + 2*equilateral_height(side_length)
    #width = side_length + 0.5*hspace
    bbox = ax.get_window_extent()
    width, height = bbox.width, bbox.height
    axes_ratio = height / width

    height = equilateral_height(side_length)*axes_ratio
    width = side_length/2
    return math.degrees(math.atan(height / width))