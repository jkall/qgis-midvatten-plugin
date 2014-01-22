#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is where a section plot is created 
 NOTE - if using this file, it has to be imported by midvatten.py
                             -------------------
        begin                : 2013-11-27
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/
"""
"""
SAKNAS:
1. input för water level dates
2. input för floating bar width 
3. (input och plottning av seismik, vlf etc längs med linjen) - efter release alpha
3. ((input och plottning av markyta från DEM)) - efter release beta
Sen bör man göra nån smart "re-plot" från plot-fönstret så man slipper göra om allt hela tiden, elle så sk-ter man i det för att tiden inte finns.
"""
import PyQt4.QtCore
import PyQt4.QtGui
#from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np
import sys
import locale
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import pyspatialite.dbapi2 as sqlite #needed since spatialite-specific sql will be used during polyline layer import
#import PyQt4.uic
import midvatten_utils as utils
from ui.secplotdialog_ui import Ui_SecPlotWindow

class sectionplot(PyQt4.QtGui.QDialog, Ui_SecPlotWindow):#the Ui_SecPlotWindow  is created instantaniously as this is created
    def __init__(self,parent,s_dict,OBSIDtuplein,SectionLineLayer):#Please note, self.selected_obsids must be a tuple
        self.s_dict=s_dict
        #super(sectionplot, self).saveSettings()
        PyQt4.QtGui.QDialog.__init__(self)
        #Ui_SecPlotWindow.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        self.setWindowTitle("Midvatten plugin - section plot") # Set the title for the dialog
        self.initUI()

        self.FillComboBoxes()        # Comboboxes are filled with relevant information

        self.show()
        #class variables
        self.geology_txt = []
        self.geoshort_txt = []
        self.capacity_txt = []
        self.development_txt = []
        self.comment_txt = []
        self.x_txt = [] #created by self.PlotGeology and used by self.WriteAnnotation
        self.z_txt = []#created by self.PlotGeology and used by self.WriteAnnotation
        self.temptableName = 'temporary_section_line'
        self.sectionlinelayer = SectionLineLayer        
        
        
        #upload vector line layer as temporary table in sqlite db
        crs = self.sectionlinelayer.crs()
        ok = self.uploadQgisVectorLayer(self.sectionlinelayer, crs.postgisSrid(), True, False)#loads qgis polyline layer into sqlite table
        if ok==True:
            print 'ok'#debug
        else:
            print 'something went wrong with the line layer import'#debug
        # get sorted obsid and distance along section from sqlite db
        nF = len(OBSIDtuplein)#number of Features
        LengthAlongTable = self.GetLengthAlong(OBSIDtuplein)#GetLengthAlong returns a numpy view, values are returned by LengthAlongTable.obs_id or LengthAlongTable.length
        self.selected_obsids = LengthAlongTable.obs_id
        self.LengthAlong = LengthAlongTable.length
        
        #drop temporary table
        sql = r"""DROP TABLE %s"""%self.temptableName
        ok = utils.sql_alter_db(sql)
        sql = r"""DELETE FROM geometry_columns WHERE "f_table_name"='%s'"""%self.temptableName
        ok = utils.sql_alter_db(sql)
        
        
        #draw plot
        self.DrawPlot()

    def initUI(self):
        #connect signal
        self.pushButton.clicked.connect(self.DrawPlot)
        
        # Create a plot window with one single subplot
        self.secfig = plt.figure()
        self.secax = self.secfig.add_subplot( 111 )
        self.canvas = FigureCanvas( self.secfig )
        self.mpltoolbar = NavigationToolbar( self.canvas, self.plotareawidget )
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.mplplotlayout.addWidget( self.canvas )
        self.mplplotlayout.addWidget( self.mpltoolbar )

    def FillComboBoxes(self): # This method populates all table-comboboxes with the tables inside the database
        # Execute a query in SQLite to return all available tables (sql syntax excludes some of the predefined tables)
        # start with cleaning comboboxes before filling with new entries
        # clear comboboxes etc
        self.wlvltableComboBox.clear()  
        self.colorComboBox.clear()  
        self.textcolComboBox.clear()  
        self.datetimetextEdit.clear()
        self.drillstoplineEdit.clear()

        #Fill comboxes, lineedits etc
        query = (r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name in('obs_points',
        'obs_lines',
        'obs_p_w_lvl',
        'obs_p_w_qual_field',
        'obs_p_w_qual_lab',
        'obs_p_w_strat',
        'seismic_data',
        'sqlite_stat3',
        'vlf_data',
        'w_flow',
        'w_qual_field_geom',
        'zz_flowtype',
        'w_qual_lab',
        'w_qual_field',
        'stratigraphy',
        'about_db',
        'geom_cols_ref_sys',
        'geometry_columns',
        'geometry_columns_time',
        'spatial_ref_sys',
        'spatialite_history',
        'vector_layers',
        'views_geometry_columns',
        'virts_geometry_columns',
        'geometry_columns_auth',
        'geometry_columns_fields_infos',
        'geometry_columns_statistics',
        'sql_statements_log',
        'layer_statistics',
        'sqlite_sequence',
        'sqlite_stat1' ,
        'views_layer_statistics',
        'virts_layer_statistics',
        'vector_layers_auth',
        'vector_layers_field_infos',
        'vector_layers_statistics',
        'views_geometry_columns_auth',
        'views_geometry_columns_field_infos',
        'views_geometry_columns_statistics',
        'virts_geometry_columns_auth',
        'virts_geometry_columns_field_infos',
        'virts_geometry_columns_statistics' ,
        'geometry_columns',
        'spatialindex',
        'SpatialIndex')) ORDER BY tbl_name""" )  #SQL statement to get the relevant tables in the spatialite database
        tabeller = utils.sql_load_fr_db(query)
        #self.dbTables = {} 
        self.wlvltableComboBox.addItem('')         
        for tabell in tabeller:
            self.wlvltableComboBox.addItem(tabell[0])
        coloritems=['geoshort','capacity']
        for item in coloritems:
            self.colorComboBox.addItem(item)
        textitems=['geology','geoshort','capacity','development','comment']
        for item in textitems:
            self.textcolComboBox.addItem(item)
        self.drillstoplineEdit.setText(self.s_dict['secplotdrillstop'])
        #FILL THE LIST OF DATES AS WELL
        for datum in self.s_dict['secplotdates']:
            print 'loading ' + datum
            self.datetimetextEdit.append(datum)

        #then select what was selected last time (according to midvatten settings)
        
        """
        MUST FIX

        DATES - SETTINGS AND PLOT ETC
        """
        if len(str(self.s_dict['secplotwlvltab'])):#If there is a last selected wlvsl
            notfound=0 
            i=0
            while notfound==0:    # Loop until the last selected tstable is found
                self.wlvltableComboBox.setCurrentIndex(i)
                if unicode(self.wlvltableComboBox.currentText()) == unicode(self.s_dict['secplotwlvltab']):#The index count stops when last selected table is found #MacOSX fix1
                    notfound=1
                elif i> len(self.wlvltableComboBox):
                    notfound=1
                i = i + 1
        if len(str(self.s_dict['secplotcolor'])):#If there is a last selected field for coloring  
            notfound=0 
            i=0
            while notfound==0:    # Loop until the last selected tstable is found
                self.colorComboBox.setCurrentIndex(i)
                if unicode(self.colorComboBox.currentText()) == unicode(self.s_dict['secplotcolor']):#The index count stops when last selected table is found #MacOSX fix1
                    notfound=1
                elif i> len(self.colorComboBox):
                    notfound=1
                i = i + 1
        if len(str(self.s_dict['secplottext'])):#If there is a last selected field for annotation in graph
            notfound=0 
            i=0
            while notfound==0:    # Loop until the last selected tstable is found
                self.textcolComboBox.setCurrentIndex(i)
                if unicode(self.textcolComboBox.currentText()) == unicode(self.s_dict['secplottext']):#The index count stops when last selected table is found #MacOSX fix1
                    notfound=1
                elif i> len(self.textcolComboBox):
                    notfound=1
                i = i + 1
        print self.s_dict['secplotbw']
        if self.s_dict['secplotbw'] !=0:
            self.barwidthdoubleSpinBox.setValue(self.s_dict['secplotbw'])            
        else:
            self.barwidthdoubleSpinBox.setValue(2)
        self.drillstoplineEdit.setText(self.s_dict['secplotdrillstop']) 
        
    def DrawPlot(self):
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))#show the user this may take a long time...
        self.secax.clear()
        self.p=[]
        self.Labels = []
        #load user settings from the ui
        self.s_dict['secplotwlvltab'] = unicode(self.wlvltableComboBox.currentText())
        temporarystring = self.datetimetextEdit.toPlainText() #this needs some cleanup
        self.s_dict['secplotdates']=temporarystring.split()
        print type(self.s_dict['secplotdates'])#debug
        print self.s_dict['secplotdates']#debug
        self.s_dict['secplotcolor']=self.colorComboBox.currentText()
        self.s_dict['secplottext'] = self.textcolComboBox.currentText()
        self.s_dict['secplotbw'] = self.barwidthdoubleSpinBox.value()
        self.s_dict['secplotdrillstop'] = self.drillstoplineEdit.text()
        #fix Floating Bar Width in percents of xmax - xmin
        xmax, xmin =float(max(self.LengthAlong)), float(min(self.LengthAlong))
        self.barwidth = (self.s_dict['secplotbw']/100.0)*(xmax -xmin)
        
        #PLOT ALL MAIN GEOLOGY TYPES AS SINGLE FLOATING BAR SERIES
        self.PlotGeology()
        #WRITE TEXT BY ALL GEOLOGY TYPES, ADJACENT TO FLOATING BAR SERIES
        self.WriteAnnotation()
        #PLOT Water Levels
        self.PlotWaterLevel()
        #write obsid at top of each stratigraphy floating bar plot
        self.WriteOBSID()
        #labels, grid, legend etc.
        self.FinishPlot()
        self.saveSettings()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def PlotGeology(self):
        l=0 #counter fro unique obs, stratid and typ
        PlotTypes = self.PlotTypesDict()
        Hatches = self.PlotHatchDict()
        Colors = self.PlotColorDict()
        for Typ in PlotTypes:#Adding a plot for each "geoshort" that is identified
            i=0 #counter for unique obs and stratid
            k=0 #counter for unique Typ 
            x = []
            z_gs=[]
            BarLength=[]
            Bottom = []
            for obs in self.selected_obsids:
                sql=u'select "depthbot"-"depthtop", stratid, geology, geoshort, capacity, development, comment from stratigraphy where obsid = "' + obs + u'" and geoshort ' + PlotTypes[Typ] + u" order by stratid"
                if utils.sql_load_fr_db(sql):
                    recs = utils.sql_load_fr_db(sql)#[0][0]
                    for rec in recs:
                        BarLength.append(rec[0])
                    j=0#counter for unique stratid
                    while j < len(recs):
                        x.append(float(self.LengthAlong[k]) - self.barwidth/2)
                        if utils.sql_load_fr_db(u'select "h_gs" from obs_points where obsid = "' + obs + u'"')[0][0]>0:
                            z_gs.append(utils.sql_load_fr_db(u'select "h_gs" from obs_points where obsid = "' + obs + u'"')[0][0])
                        elif utils.sql_load_fr_db(u'select "h_toc" from obs_points where obsid = "' + obs + u'"')[0][0]>0:
                            z_gs.append(utils.sql_load_fr_db(u'select "h_toc" from obs_points where obsid = "' + obs + u'"')[0][0])
                        else:
                            z_gs.append(0)
                        Bottom.append(z_gs[i]- utils.sql_load_fr_db(u'select "depthbot" from stratigraphy where obsid = "' + obs + u'" and stratid = ' + str(recs[j][1])+ u' and geoshort ' + PlotTypes[Typ])[0][0])
                        #lists for plotting annotation 
                        self.x_txt.append(x[i]+ self.barwidth/2)
                        self.z_txt.append(Bottom[i] + recs[j][0]/2)
                        self.geology_txt.append(self.returnunicode(recs[j][2]))
                        self.geoshort_txt.append(self.returnunicode(recs[j][3]))
                        self.capacity_txt.append(self.returnunicode(recs[j][4]))
                        self.development_txt.append(self.returnunicode(recs[j][5]))
                        self.comment_txt.append(self.returnunicode(recs[j][6]))
                        #print obs + " " + Typ + " " + self.geology_txt[l] + " " + self.geoshort_txt[l] + " " + self.capacity_txt[l] + " " + self.development_txt[l] + " " + self.comment_txt[l]
                        
                        i +=1
                        j +=1
                        l +=1
                    del recs
                k +=1
                    
            if len(x)>0:
                #print Typ,Colors[Typ], Hatches[Typ]
                #print x, BarLength, Bottom
                self.p.append(self.secax.bar(x,BarLength, color=Colors[Typ], edgecolor='black', hatch=Hatches[Typ], width = self.barwidth, bottom=Bottom))
                self.Labels.append(Typ)

    def WriteAnnotation(self):
        if self.s_dict['secplottext'] == 'geology':
            annotate_txt = self.geology_txt
        elif self.s_dict['secplottext'] == 'geoshort':
            annotate_txt = self.geoshort_txt
        elif self.s_dict['secplottext'] == 'capacity':
            annotate_txt = self.capacity_txt
        elif self.s_dict['secplottext'] == 'development':
            annotate_txt = self.development_txt
        else:
            annotate_txt = self.comment_txt
        for m,n,o in zip(self.x_txt,self.z_txt,annotate_txt):#change last arg to the one to be written in plot
            self.secax.annotate(o,xy=(m,n),xytext=(3*self.barwidth/4,0), textcoords='offset points',ha = 'left', va = 'center',bbox = dict(boxstyle = 'square,pad=0.05', fc = 'white', edgecolor='white', alpha = 0.45))

    def PlotWaterLevel(self):
        if self.s_dict['secplotdates'] and len(self.s_dict['secplotdates'])>0:    # Adding a plot for each water level date identified
            #datumlista = str(self.s_dict['secplotdates']).splitlines
            #print datumlista
            #print type(datumlista)
            #for datum in datumlista:
            #    print datum
            for datum in self.s_dict['secplotdates']:
            #for datum in self.s_dict['secplotdates'].split('\n')
                print datum
                WL = []
                x_wl=[]
                k=0
                for obs in self.selected_obsids:
                    query = u'select level_masl from w_levels where obsid = "' + obs + '" and date_time like "' + datum  +'%"' 
                    if utils.sql_load_fr_db(query):
                        WL.append(utils.sql_load_fr_db(query)[0][0])
                        x_wl.append(float(self.LengthAlong[k]))
                    k += 1
                lineplot,=self.secax.plot(x_wl, WL,  'v-', markersize = 6)#The comma is terribly annoying and also different from a bar plot, see http://stackoverflow.com/questions/11983024/matplotlib-legends-not-working and http://stackoverflow.com/questions/10422504/line-plotx-sinx-what-does-comma-stand-for?rq=1
                self.p.append(lineplot)
                self.Labels.append(datum)
        
    def WriteOBSID(self):
        x_id = []
        z_id=[]
        q=0# a new counter per self.selected_obsids
        for obs in self.selected_obsids:#Finally adding obsid at top of stratigraphy
            x_id.append(float(self.LengthAlong[q]))
            recs = utils.sql_load_fr_db(u'select h_toc, h_gs from obs_points where obsid = "' + obs + u'"')
            if recs[0][1]>0:
                z_id.append(recs[0][1])
            elif recs[0][0]>0:
                z_id.append(recs[0][0])
            else:
                z_id.append(0)
            q +=1
            del recs
        for m,n,o in zip(x_id,z_id,self.selected_obsids):#change last arg to the one to be written in plot
            self.secax.annotate(o,xy=(m,n),xytext=(0,10), textcoords='offset points',ha = 'center', va = 'top')#,bbox = dict(boxstyle = 'square,pad=0', fc = 'white', alpha = 0.25))
        del x_id, z_id, q

    def FinishPlot(self):
        leg = self.secax.legend(self.p, self.Labels )
        leg.draggable(state=True)
        frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
        frame.set_facecolor('1')    # set the frame face color to white                
        frame.set_fill(False)    # set the frame face color to white                
        for t in leg.get_texts():
            t.set_fontsize(10) 

        self.secax.grid(b=True, which='both', color='0.65',linestyle='-')
        self.secax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        self.secax.set_ylabel(unicode("Level, masl",'utf-8'))  #This is the method - can now write 'åäö' in console and it works (since console is in utf-8 I guess)
        self.secax.set_xlabel(unicode("Distance along section",'utf-8'))  #This is the method - can now write 'åäö' in console and it works (since console is in utf-8 I guess)
        for label in self.secax.xaxis.get_ticklabels():
            label.set_fontsize(10)
        for label in self.secax.yaxis.get_ticklabels():
            label.set_fontsize(10)
        self.canvas.draw()
        
    def uploadQgisVectorLayer(self, layer, srid=None,selected=False, mapinfo=True,Attributes=False): #from qspatialite, with a few  changes LAST ARGUMENT IS USED TO SKIP ARGUMENTS SINCE WE ONLY WANT THE GEOMETRY TO CALCULATE DISTANCES
        """Upload layer (QgsMapLayer) (optionnaly only selected values ) into current DB, in self.temptableName (string) with desired SRID (default layer srid if None) - user can desactivate mapinfo compatibility Date importation. Return True if operation succesfull or false in all other cases"""
        selected_ids=[]
        if selected==True :
            if layer.selectedFeatureCount()==0:
                utils.pop_up_info("No selected item in Qgis layer: %s)"%layer.name(),self.parent)
                return False
            select_ids=layer.selectedFeaturesIds()
        #Create name for table if not provided by user
        if self.temptableName in (None,''):
            self.temptableName=layer.name()
        #Verify if self.temptableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #ExistingNames=[table.name for table in self.tables]
            #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.temptableName): #if so, propose to rename the temporary import-table
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Table name confusion",'''Note, the plugin needs to store a temporary table in the database and tried '%s'.\nHowever, this is already in use in the database, it might be the result of a failed section plot attempt.\nPlease check your database. Meanwhile, would you like to rename the temporary table '%s' as '%s_2' '''%(self.temptableName,self.temptableName,self.temptableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.temptableName='%s_2'%self.temptableName
                else:
                    return False
        #Get data charset
        provider=layer.dataProvider()
        #charset=provider.encoding()
    
        #Get fields with corresponding types
        fields=[]
        fieldsNames=[]
        mapinfoDAte=[]
        for id,name in enumerate(provider.fields().toList()):
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldTypeName=='DATE' and unicode(provider.storageType()).lower()==u'mapinfo file'and mapinfo==True: # Mapinfo DATE compatibility
                fldType='DATE'
                mapinfoDAte.append([id,fldName]) #stock id and name of DATE field for MAPINFO layers
            elif fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is TEXT
                fldLength=name.length()
                fldType='TEXT(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool,PyQt4.QtCore.QVariant.Int,PyQt4.QtCore.QVariant.LongLong,PyQt4.QtCore.QVariant.UInt,PyQt4.QtCore.QVariant.ULongLong): # field type is INTEGER
                fldType='INTEGER'
            elif fldType==PyQt4.QtCore.QVariant.Double: # field type is DOUBLE
                fldType='REAL'
            else: # field type is not recognized by SQLITE
                fldType=fldTypeName
            fields.append(""" "%s" %s """%(fldName,fldType))
            fieldsNames.append(fldName.upper())

        # is it a geometric table ?
        geometry=False
        if layer.hasGeometryType():
            #Get geometry type
            geom=['MULTIPOINT','MULTILINESTRING','MULTIPOLYGON','UnknownGeometry']
            geometry=geom[layer.geometryType()]
            #Project to new SRID if specified by user:
            if srid==None:
                srid=layer.crs().postgisSrid()
            else:
                Qsrid = QgsCoordinateReferenceSystem()
                Qsrid.createFromId(srid)
                if not Qsrid.isValid(): #check if crs is ok
                    utils.pop_up_info("Destination SRID isn't valid for table %s"%layer.name(),self.parent)
                    return False
                layer.setCrs(Qsrid)

        #select attributes to import (remove Pkuid if already exists):
        allAttrs = provider.attributeIndexes()
        fldDesc = provider.fieldNameIndex("PKUID")
        if fldDesc != -1:
            print "Pkuid already exists and will be replaced!"
            del allAttrs[fldDesc] #remove pkuid Field
            del fields[fldDesc] #remove pkuid Field
        #provider.select(allAttrs)
        #request=QgsFeatureRequest()
        #request.setSubsetOfAttributes(allAttrs).setFlags(QgsFeatureRequest.SubsetOfAttributes)
        
        #Create new table in DB
        if Attributes == False:
            fields=[]
        if geometry:
            fields.insert(0,"Geometry %s"%geometry)
        
        fields=','.join(fields)
        if len(fields)>0:
            fields=', %s'%fields

        self.connection()
        query="""CREATE TABLE "%s" ( PKUID INTEGER PRIMARY KEY AUTOINCREMENT %s )"""%(self.temptableName, fields)
        print query#debug
        header,data=self.executeQuery(query)
        if self.queryPb:
            return
    
        #Recover Geometry Column:
        if geometry:
            header,data=self.executeQuery("""SELECT RecoverGeometryColumn("%s",'Geometry',%s,'%s',2)"""%(self.temptableName,srid,geometry,))
            print 'recovered geometry'#debug
        
        # Retreive every feature
        for feat in layer.getFeatures():
            # selected features:
            if selected and feat.id()not in select_ids:
                continue 
        
            #PKUID and Geometry        
            values_auto=['NULL'] #PKUID value
            if geometry:
                geom = feat.geometry()
                #WKB=geom.asWkb()
                WKT=geom.exportToWkt()
                values_auto.append('CastToMulti(GeomFromText("%s",%s))'%(WKT,srid))
        
            # show all attributes and their values
            values_perso=[]
            for val in allAttrs: # All except PKUID
                values_perso.append(feat[val])
            
            #Create line in DB table         ---------------------SOME PROBLEMS HERE WHEN THERE ARE NO ATTRIBUTES , GÅR BRA OM MAN HAR MINST ETT PAR ATTRIBUT
            #MEN VI KAN LIKA GÄRNA STRUNTA I ATTRIBUTEN
            if Attributes == True:
                if len(fields)>0:
                    query="""INSERT INTO "%s" VALUES (%s,%s)"""%(self.temptableName,','.join([unicode(value).encode('utf-8') for value in values_auto]),','.join('?'*len(values_perso)))
                    #print 'attr datas'
                    #print query
                    header,data=self.executeQuery(query,tuple([unicode(value) for value in values_perso]))
                else: #no attribute Datas
                    query="""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join([unicode(value).encode('utf-8') for value in values_auto]))
                    header,data=self.executeQuery(query)
                    #print 'no attr datas'
                    #print query
            else:
                query="""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join([unicode(value).encode('utf-8') for value in values_auto]))
                #print 'no attr datas'
                #print query
                header,data=self.executeQuery(query)
        for date in mapinfoDAte: #mapinfo compatibility: convert date in SQLITE format (2010/02/11 -> 2010-02-11 ) or rollback if any error
            header,data=self.executeQuery("""UPDATE OR ROLLBACK "%s" set '%s'=replace( "%s", '/' , '-' )  """%(self.temptableName,date[1],date[1]))
    
        #Commit DB connection:
        self.connectionObject.commit()
        self.connectionObject.close()#THIS WAS NOT IN QSPATIALITE CODE!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # reload tables
        return True

    def connection(self):#from qspatialite, it is only used by self.uploadQgisVectorLayer
        """ Create connexion if not yet connected and Return connexion object for the current DB"""
        try:
            return self.connectionObject
        except:
            try:
                dbpath = QgsProject.instance().readEntry("Midvatten","database")
                self.connectionObject=sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
                return self.connectionObject
            except sqlite.OperationalError, Msg:
                utils.pop_up_info("Can't connect to DataBase: %s\nError %s"%(self.path,Msg))
             
    def executeQuery(self,query,params=(),commit=False):#from qspatialite, it is only used by self.uploadQgisVectorLayer
        """Execute query (string) with given parameters (tuple) (optionnaly perform commit to save Db) and return resultset [header,data] or [flase,False] if error"""
        query=unicode(query)
        self.queryPb=False
        header=[]
        data=[]
        cursor=self.connectionObject.cursor()
        try:
            cursor.execute(query,params)
            if (cursor.description is not None):
                header = [item[0] for item in cursor.description]
            data = [row for row in cursor]
            if commit:
                self.connectionObject.commit()
        except sqlite.OperationalError, Msg:
            self.connectionObject.rollback()
            #print "An error occured while executing query :\n",query,"\nError:\n",Msg
            utils.pop_up_info("The SQL query\n %s\n seems to be invalid.\n\n%s" %(query,Msg),None)
            self.queryPb=True #Indicates pb with current query
            
        return header,data
        
    def GetLengthAlong(self,obsidtuple):#returns a numpy recarray with attributes obs_id and length 
        #------------First a sql clause that returns a table, but that is not what we need
        sql = r"""SELECT obsid AS "obsid",
        GLength(l.geometry)*ST_Line_Locate_Point(l.geometry, p.geometry) AS "abs_dist"
        FROM %s AS l, (select * from obs_points where obsid in %s) AS p
        GROUP BY obsid ORDER BY ST_Line_Locate_Point(l.geometry, p.geometry);"""%(self.temptableName,obsidtuple)
        data = utils.sql_load_fr_db(sql)
        My_format = [('obs_id', np.str_, 16),('length', float)] 
        npdata = np.array(data, dtype=My_format)  #NDARRAY
        LengthAlongTable=npdata.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write self.LengthAlong.obs_id and self.LengthAlong.length
        del data, npdata
        return LengthAlongTable

    def PlotTypesDict(self):
        if  locale.getdefaultlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
            Dict = {u"Okänt" : u"not in ('berg','Berg','BERG','B','Rock','rock','Ro','ro','grovgrus','Grovgrus','Grg','grg','Coarse Gravel','coarse Gravel','coarse gravel','CGr','Cgr','cGr','cgr','grus','Grus','GRUS','Gr','gr','Gravel','gravel','mellangrus','Mellangrus','MELLANGRUS','Grm','grm','Medium Gravel','medium Gravel','medium gravel','MGr','mGr','Mgr','mgr','fingrus','Fingrus','FINGRUS','Grf','grf','Fine Gravel','fine Gravel','fine gravel','FGr','Fgr','fGr','fgr','grovsand','Grovsand','GROVSAND','Sag','sag','Coarse Sand','coarse Sand','coarse sand','CSa','Csa','cSa','csa','sand','Sand','SAND','Sa','sa','SA','mellansand','Mellansand','MELLANSAND','Sam','sam','Medium Sand','medium Sand','medium sand','MSa','Msa','msa','mSa','finsand','Finsand','FINSAND','Saf','saf','Fine Sand','fine Sand','fine Sand','FSa','Fsa','fSa','fsa','silt','Silt','SILT','Si','si','lera','Lera','LERA','Le','le','Clay','clay','Cl','cl','moran','Moran','MORAN','Mn','mn','Till','till','Ti','ti','torv','Torv','TORV','T','Peat','peat','Pt','pt','t','fyll','Fyll','FYLL','fyllning','Fyllning','FYLLNING','F','f','Made Ground','Made ground','mage ground','MG','Mg','mg')",
            "Berg"  : u"in ('berg','Berg','BERG','B','Rock','rock','Ro','ro')",
            "Grovgrus" : u"in ('grovgrus','Grovgrus','Grg','grg','Coarse Gravel','coarse Gravel','coarse gravel','CGr','Cgr','cGr','cgr')",
            "Grus" : u"in ('grus','Grus','GRUS','Gr','gr','Gravel','gravel')",
            "Mellangrus" : u"in ('mellangrus','Mellangrus','MELLANGRUS','Grm','grm','Medium Gravel','medium Gravel','medium gravel','MGr','mGr','Mgr','mgr')",
            "Fingrus" : u"in ('fingrus','Fingrus','FINGRUS','Grf','grf','Fine Gravel','fine Gravel','fine gravel','FGr','Fgr','fGr','fgr')",
            "Grovsand" : u"in ('grovsand','Grovsand','GROVSAND','Sag','sag','Coarse Sand','coarse Sand','coarse sand','CSa','Csa','cSa','csa')",
            "Sand" : u"in ('sand','Sand','SAND','Sa','sa','SA')",
            "Mellansand" : u"in ('mellansand','Mellansand','MELLANSAND','Sam','sam','Medium Sand','medium Sand','medium sand','MSa','Msa','msa','mSa')",
            "Finsand" : u"in ('finsand','Finsand','FINSAND','Saf','saf','Fine Sand','fine Sand','fine Sand','FSa','Fsa','fSa','fsa')",
            "Silt" : u"in ('silt','Silt','SILT','Si','si')",
            "Lera" : u"in ('lera','Lera','LERA','Le','le','Clay','clay','Cl','cl')",
            "Moran" : u"in ('moran','Moran','MORAN','Mn','mn','Till','till','Ti','ti')",
            "Torv" : u"in ('torv','Torv','TORV','T','Peat','peat','Pt','pt','t')",
            "Fyll":u"in ('fyll','Fyll','FYLL','fyllning','Fyllning','FYLLNING','F','f','Made Ground','Made ground','mage ground','MG','Mg','mg')"}
        else:
            Dict = {u"Unknown" : u"not in ('berg','Berg','BERG','B','Rock','rock','Ro','ro','grovgrus','Grovgrus','Grg','grg','Coarse Gravel','coarse Gravel','coarse gravel','CGr','Cgr','cGr','cgr','grus','Grus','GRUS','Gr','gr','Gravel','gravel','mellangrus','Mellangrus','MELLANGRUS','Grm','grm','Medium Gravel','medium Gravel','medium gravel','MGr','mGr','Mgr','mgr','fingrus','Fingrus','FINGRUS','Grf','grf','Fine Gravel','fine Gravel','fine gravel','FGr','Fgr','fGr','fgr','grovsand','Grovsand','GROVSAND','Sag','sag','Coarse Sand','coarse Sand','coarse sand','CSa','Csa','cSa','csa','sand','Sand','SAND','Sa','sa','SA','mellansand','Mellansand','MELLANSAND','Sam','sam','Medium Sand','medium Sand','medium sand','MSa','Msa','msa','mSa','finsand','Finsand','FINSAND','Saf','saf','Fine Sand','fine Sand','fine Sand','FSa','Fsa','fSa','fsa','silt','Silt','SILT','Si','si','lera','Lera','LERA','Le','le','Clay','clay','Cl','cl','moran','Moran','MORAN','Mn','mn','Till','till','Ti','ti','torv','Torv','TORV','T','Peat','peat','Pt','pt','t','fyll','Fyll','FYLL','fyllning','Fyllning','FYLLNING','F','f','Made Ground','Made ground','mage ground','MG','Mg','mg')",
            "Rock"  : u"in ('berg','Berg','BERG','B','Rock','rock','Ro','ro')",
            "Coarse gravel" : u"in ('grovgrus','Grovgrus','Grg','grg','Coarse Gravel','coarse Gravel','coarse gravel','CGr','Cgr','cGr','cgr')",
            "Gravel" : u"in ('grus','Grus','GRUS','Gr','gr','Gravel','gravel')",
            "Medium gravel" : u"in ('mellangrus','Mellangrus','MELLANGRUS','Grm','grm','Medium Gravel','medium Gravel','medium gravel','MGr','mGr','Mgr','mgr')",
            "Fine gravel" : u"in ('fingrus','Fingrus','FINGRUS','Grf','grf','Fine Gravel','fine Gravel','fine gravel','FGr','Fgr','fGr','fgr')",
            "Coarse sand" : u"in ('grovsand','Grovsand','GROVSAND','Sag','sag','Coarse Sand','coarse Sand','coarse sand','CSa','Csa','cSa','csa')",
            "Sand" : u"in ('sand','Sand','SAND','Sa','sa','SA')",
            "Medium sand" : u"in ('mellansand','Mellansand','MELLANSAND','Sam','sam','Medium Sand','medium Sand','medium sand','MSa','Msa','msa','mSa')",
            "Fine sand" : u"in ('finsand','Finsand','FINSAND','Saf','saf','Fine Sand','fine Sand','fine Sand','FSa','Fsa','fSa','fsa')",
            "Silt" : u"in ('silt','Silt','SILT','Si','si')",
            "Clay" : u"in ('lera','Lera','LERA','Le','le','Clay','clay','Cl','cl')",
            "Till" : u"in ('moran','Moran','MORAN','Mn','mn','Till','till','Ti','ti')",
            "Peat" : u"in ('torv','Torv','TORV','T','Peat','peat','Pt','pt','t')",
            "Fill":u"in ('fyll','Fyll','FYLL','fyllning','Fyllning','FYLLNING','F','f','Made Ground','Made ground','mage ground','MG','Mg','mg')"}
        return Dict

    def PlotColorDict(self):
        if  locale.getdefaultlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
            Dict = {u"Okänt" : u"white",
            "Berg"  : u"red",
            "Grovgrus" : u"DarkGreen",
            "Grus" : u"DarkGreen",
            "Mellangrus" : u"DarkGreen",
            "Fingrus" : u"DarkGreen",
            "Grovsand" : u"green",
            "Sand" : u"green",
            "Mellansand" : u"green",
            "Finsand" : u"yellow",
            "Silt" : u"yellow",
            "Lera" : u"DarkOrange",
            "Moran" : u"cyan",
            "Torv" : u"DarkGray",
            "Fyll":u"white"}
        else:
            Dict = {u"Unknown" : u"white",
            "Rock"  : u"red",
            "Coarse gravel" : u"DarkGreen",
            "Gravel" : u"DarkGreen",
            "Medium gravel" : u"DarkGreen",
            "Fine gravel" : u"DarkGreen",
            "Coarse sand" : u"green",
            "Sand" : u"green",
            "Medium sand" : u"green",
            "Fine sand" : u"yellow",
            "Silt" : u"yellow",
            "Clay" : u"DarkOrange",
            "Till" : u"cyan",
            "Peat" : u"DarkGray",
            "Fill":u"white"}            
        return Dict

    def PlotHatchDict(self):
        # hatch patterns : ('-', '+', 'x', '\\', '*', 'o', 'O', '.','/')
        if  locale.getdefaultlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
            Dict = {u"Okänt" : u"",
            "Berg"  : u"x",
            "Grovgrus" : u"O",
            "Grus" : u"O",
            "Mellangrus" : u"o",
            "Fingrus" : u"o",
            "Grovsand" : u"*",
            "Sand" : u"*",
            "Mellansand" : u".",
            "Finsand" : u".",
            "Silt" : u"\\",
            "Lera" : u"-",
            "Moran" : u"/",
            "Torv" : u"+",
            "Fyll":u"+"}
        else:
            Dict = {u"Unknown" : u"",
            "Rock"  : u"x",
            "Coarse gravel" : u"O",
            "Gravel" : u"O",
            "Medium gravel" : u"o",
            "Fine gravel" : u"o",
            "Coarse sand" : u"*",
            "Sand" : u"*",
            "Medium sand" : u".",
            "Fine sand" : u".",
            "Silt" : u"\\",
            "Clay" : u"-",
            "Till" : u"/",
            "Peat" : u"+",
            "Fill":u"+"}
        return Dict
        
    def returnunicode(self,anything): #takes an input and tries to return it as unicode
        if type(anything) == type(None):
            text = unicode('')
        elif type(anything) == type(unicode('unicodetextstring')):
            text = anything 
        elif (type(anything) == type (1)) or (type(anything) == type (1.1)):
            text = unicode(str(anything))
        elif type(anything) == type('ordinary_textstring'):
            text = unicode(anything)
        else:
            try:
                text = unicode(str(anything))
            except:
                text = unicode('data type unknown, check database')
        return text 

    def saveSettings(self):# settingsdict is a dictionary belonging to instance midvatten. This is a quick-fix, should call parent method instead.
        QgsProject.instance().writeEntry("Midvatten",'secplotwlvltab', self.s_dict['secplotwlvltab'] )
        QgsProject.instance().writeEntry("Midvatten",'secplotdates', self.s_dict['secplotdates'] )
        QgsProject.instance().writeEntry("Midvatten",'secplottext', self.s_dict['secplottext'] )
        QgsProject.instance().writeEntry("Midvatten",'secplotcolor', self.s_dict['secplotcolor'] )
        QgsProject.instance().writeEntry("Midvatten",'secplotdrillstop', self.s_dict['secplotdrillstop'] )
        QgsProject.instance().writeEntry("Midvatten",'secplotbw', self.s_dict['secplotbw'] )
