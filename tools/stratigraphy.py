# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin is more or less just a small tweak of
 the ARPAT plugin developed by Martin Dobias for Faunalia:

# Copyright 2006-2007 by ARPAT-SIRA (www.arpat.toscana.it http://sira.arpat.toscana.it/sira/)
# Licenced under GNU GPL (General Public License) v2
# Developed by Martin Dobias for Faunalia (www.faunalia.it)
# For details send a mail to PFR_SIRA@arpat.toscana.it
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation (www.fsf.org); version 2 of the License, or any later version.
#
#
# Copyright 2006-2007 di ARPAT-SIRA (www.arpat.toscana.it http://sira.arpat.toscana.it/sira/)
# Rilasciato sotto licenza GNU GPL (General Public License) v2
# Sviluppato da Martin Dobias per Faunalia (www.faunalia.it)
# Per ulteriori informazioni inviare una mail a PFR_SIRA@arpat.toscana.it
#
# Questo programma rientra nel software libero; possibile redistribuirlo e/o modificarlo
# sotto i termini della licenza GNU General Public License come pubblicato da
# Free Software Foundation (www.fsf.org); versione 2 o superiore della licenza.
 
 ---------- THE ARPAT PLUGIN IS INCLUDED IN MIDVATTEN PLUGIN AND MODIFIED FOR SQLITE DATA BY:
        begin                : 2012-03-06
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import unicodedata  # To normalize some special national characters to regular international characters
from functools import partial  # only to get combobox signals to work

import PyQt4
from PyQt4.QtCore import QCoreApplication

import db_utils
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from midvatten_utils import returnunicode as ru


class Stratigraphy:

    def __init__(self, iface, layer=None, settingsdict={}):
        self.iface = iface
        self.stratitable = defs.stratigraphy_table()  #no longer an option to select other tables than 'stratigraphy'
        self.layer = layer
        self.store = None
        #self.showSurvey()
        self.w = None

    def initStore(self):
        try: # return from SurveyStore is stored in self.store only if no object belonging to DataError class is created
            self.store = SurveyStore(self.stratitable)
        except DataError, e: # if an object 'e' belonging to DataError is created, then do following
            try:
                print "Load failed due: " + e.problem
            except:
                pass
            self.store = None

    def showSurvey(self):
        #lyr = self.iface.activeLayer() # THIS IS TSPLOT-method, GETS THE SELECTED LAYER
        lyr = self.layer
        ids = lyr.selectedFeaturesIds()
        if len(ids) == 0:
            utils.pop_up_info(ru(QCoreApplication.translate(u' Stratigraphy', u"No selection")), ru(QCoreApplication.translate(u' Stratigraphy', u"No features are selected")))
            return
        # initiate the datastore if not yet done   
        self.initStore()   
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)  # Sets the mouse cursor to wait symbol
        try:  # return from store.getData is stored in data only if no object belonging to DataSanityError class is created
            self.data = self.store.getData(ids, lyr)    # added lyr as an argument!!!
        except DataSanityError, e: # if an object 'e' belonging to DataSanityError is created, then do following
            print("DataSanityError %s"%str(e))
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            utils.pop_up_info(ru(QCoreApplication.translate(u' Stratigraphy', u"Data sanity problem, obsid: %s\n%s")) % (e.sond_id, e.message))
            return
        except Exception as e: # if an object 'e' belonging to DataSanityError is created, then do following
            print("exception : %s"%str(e))
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u' Stratigraphy', u"The stratigraphy plot failed, check Midvatten plugin settings and your data!")))
            return
        PyQt4.QtGui.QApplication.restoreOverrideCursor()  # Restores the mouse cursor to normal symbol
        # show widget
        w = SurveyDialog()
        #w.widget.setData2_nosorting(data)  #THIS IS IF DATA IS NOT TO BE SORTED!!
        w.widget.setData(self.data)  #THIS IS ONLY TO SORT DATA!!
        w.show()
        self.w = w # save reference so it doesn't get deleted immediately        This has to be done both here and also in midvatten instance

class SurveyInfo:   # This class is to define the data structure... 
    
    def __init__(self, obsid='', top_lvl=0, coord=None, strata=None):  #_CHANGE_ added obsid
        self.obsid = obsid # _CHANGE_
        self.top_lvl = top_lvl
        self.coord = coord
        if strata == None:
            strata = []
        self.strata = strata
    def __repr__(self):   # _INFO_ : A class can control what this function returns for its instances by defining a __repr__() method.
        return "SURVEY('%s', %f, '%s')" % (unicode(self.obsid), self.top_lvl, self.coord) # _CHANGE_

class StrataInfo:
    def __init__(self, stratid=0, depthTop=0, depthBot=0, geology='',  geo_short='', hydro='', Comment='', development=''):
        self.stratid = stratid  # This is id no for the geological information (1 = uppermost stratigraphy layer)
        self.geology = geology # This is full text description of stratigraphy (the geologic descripition, e.g. "sandy till")
        self.depthTop = depthTop  # This is depth to top of the stratigraphy layer
        self.depthBot = depthBot # This is depth to bottom for the stratigraphy layer
        self.geo_short = geo_short # This is short name for the geology of the stratigraphy layer, also used for symbology and color
        self.comment = Comment # Comment for the stratigraphy layer
        self.hydro = hydro # Water loss or similar measurement of layer permeability, given as 1, 2, 3, etc, see below
        self.development = development 
    def __repr__(self):
        return "strata(%d, '%s', '%s', '%s', %f-%f)" % (self.stratid, self.hydro, self.geology, self.geo_short, self.depthTop, self.depthBot)

class SurveyStore:
    def __init__(self, stratitable):
        self.stratitable = stratitable
        self.warning_popup = True

    def getData(self, featureIds, vectorlayer):  # THIS FUNCTION IS ONLY CALLED FROM ARPATPLUGIN/SHOWSURVEY
        """ get data from databases for array of features specified by their IDs  """
        surveys = self._getDataStep1(featureIds, vectorlayer)
        try:
            DataLoadingStatus, surveys = self._getDataStep2(surveys)
        except:
            DataLoadingStatus = False
        if DataLoadingStatus == True:
            surveys = self.sanityCheck(surveys)
            return surveys  
        else:
            DataSanityError(Exception)
        
    def _getDataStep1(self, featureIds, vlayer):
        """ STEP 1: get data from selected layer"""  # _CHANGE_ Completely revised to TSPLot method
        provider = vlayer.dataProvider()  #_CHANGE_  THIS IS TSPLOT-method, we do not use the db loadeds by ARPAT _init_ surveystore
        obsid_ColNo = provider.fieldNameIndex('obsid') # _CHANGE_  THIS IS TSPLOT-method To find the column named 'obsid'
        if obsid_ColNo == -1:
            obsid_ColNo = provider.fieldNameIndex('OBSID') # backwards compatibility
        h_gs_ColNo = provider.fieldNameIndex('h_gs') # _CHANGE_  THIS IS TSPLOT-method To find the column named 'h_gs'
        h_toc_ColNo = provider.fieldNameIndex('h_toc') # _CHANGE_  THIS IS TSPLOT-method To find the column named 'h_toc'
        if h_gs_ColNo == -1 and h_toc_ColNo == -1:
            h_gs_ColNo = provider.fieldNameIndex('SURF_LVL') # backwards compatibility
        surveys = {}
        strata = {}
        if(vlayer):
            nF = vlayer.selectedFeatureCount()
            if (nF > 0):
                # Load all selected observation points
                ob = vlayer.selectedFeatures()
                obsid_list=[None]*nF # List for obsid
                toplvl_list=[None]*nF # List for top_lvl
                coord_list=[None]*nF # List for coordinates
                for i, k in enumerate(ob):    # Loop through all selected objects, a plot is added for each one of the observation points (i.e. selected objects)
                    attributes = ob[i]
                    obsid = ru(attributes[obsid_ColNo])
                    obsid_list[i] = obsid # Copy value in column obsid in the attribute list
                    h_gs = ru(attributes[h_gs_ColNo])

                    level_val = None

                    error_msg = False

                    if h_gs:
                        try:
                            level_val = float(h_gs)
                        except ValueError:
                            error_msg = ru(QCoreApplication.translate(u'Stratigraphy', u'Converting to float failed.'))
                        except Exception as e:
                            error_msg = e

                    if level_val is None:
                        h_toc = ru(attributes[h_toc_ColNo])
                        try:
                            level_val = float(h_toc)
                        except:
                            using = u'-1'
                            level_val = -1
                        else:
                            using = u'h_toc'

                        utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'Stratigraphy', u"Obsid %s: using h_gs '%s' failed, using '%s' instead.")) % (obsid, h_gs, using),
                                                       log_msg=ru(QCoreApplication.translate(u'Stratigraphy', u'%s'))%error_msg,
                                                       duration=90)

                        if self.warning_popup:
                            utils.pop_up_info(ru(QCoreApplication.translate(u'Stratigraphy', u'Warning, h_gs is missing. See messagebar.')))
                            self.warning_popup = False

                    toplvl_list[i] = level_val

                    coord_list[i]= k.geometry().asPoint()
                    # add to array
                    surveys[obsid_list[i]] = SurveyInfo(obsid_list[i], toplvl_list[i], coord_list[i])
        else:
            utils.pop_up_info(ru(QCoreApplication.translate(u'Stratigraphy', u"getDataStep1 failed")))  # _CHANGE_ for debugging

        return surveys

    def _getDataStep2(self, surveys):
        """ STEP 2: get strata information for every point """
        dbconnection = db_utils.DbConnectionManager()
        for (obsid, survey) in surveys.iteritems():
            sql =r"""SELECT stratid, depthtop, depthbot, geology, lower(geoshort), capacity, comment, development FROM """
            sql += self.stratitable #MacOSX fix1
            sql += r""" WHERE obsid = '"""
            sql += str(obsid)   # THIS IS WHERE THE KEY IS GIVEN TO LOAD STRATIGRAPHY FOR CHOOSEN obsid
            sql += """' ORDER BY stratid"""
            recs = dbconnection.execute_and_fetchall(sql)
            # parse attributes
            prev_depthbot = 0
            for record in recs:
                if utils.isinteger(record[0]) and utils.isfloat(record[1]) and utils.isfloat(record[2]):
                    stratigaphy_id = record[0]  # Stratigraphy layer no
                    depthtotop = record[1]  # depth to top of stratrigraphy layer
                    depthtobot = record[2]  # depth to bottom of stratrigraphy layer
                else:
                    raise DataSanityError(str(obsid), ru(QCoreApplication.translate(u'SurveyStore', u"Something bad with stratid, depthtop or depthbot!")))
                    stratigaphy_id = 1  # when something went wrong, put it into first layer
                    depthtotop = 0
                    depthtobot = 999#default value when something went wrong
                if record[3]: # Must check since it is not possible to print null values as text in qt widget
                    geology = record[3]  # Geology full text
                else:
                    geology = " "
                geo_short_txt = record[4]  # geo_short might contain national special characters
                if geo_short_txt:   # Must not try to encode an empty field
                    geo_short = unicodedata.normalize('NFKD', geo_short_txt).encode('ascii','ignore')  # geo_short normalized for symbols and color
                else:  # If the field is empty, then store an empty string
                    geo_short = ''
                hydro = record[5] # waterloss (hydrogeo parameter) for color
                if record[6]:  # Must check since it is not possible to print null values as text in qt widget
                    comment = record[6] #
                else:
                    comment = " "
                if record[7]:  # Must check since it is not possible to print null values as text in qt widget
                    development = record[7] #
                else:
                    development = " "

                #Add layer if there is a gap
                if depthtotop != prev_depthbot:
                    stratid = len(survey.strata) + 1
                    st = StrataInfo(stratid, prev_depthbot, depthtotop)
                    survey.strata.append(st)

                stratid = len(survey.strata) + 1
                st = StrataInfo(stratid, depthtotop, depthtobot, geology, geo_short, hydro, comment, development)
                survey.strata.append(st)
                prev_depthbot = depthtobot

            DataLoadingStatus = True
        dbconnection.closedb()
        return DataLoadingStatus, surveys

        
    def sanityCheck(self, _surveys):
        """ does a sanity check on retreived data """
        surveys = {}
        for (obsid, survey) in _surveys.iteritems():
            # check whether there's at least one strata information
            if len(survey.strata) == 0:
                #raise DataSanityError(str(obsid), "No strata information")
                try:
                    print(str(obsid) + " has no strata information")
                except:
                    pass
                continue
                #del surveys[obsid]#simply remove the item without strata info
            else:
                # check whether the depths are valid
                top1 = survey.strata[0].depthTop
                bed1 = survey.strata[0].depthBot
                for strato in survey.strata[1:]:
                    # top (n) < top (n+1)
                    if top1 > strato.depthTop:
                        raise DataSanityError(str(obsid), ru(QCoreApplication.translate(u'SurveyStore', u"Top depth is incorrect (%.2f > %.2f)")) % (top1, strato.depthTop))
                    # bed (n) < bed (n+1)
                    if bed1 > strato.depthBot:
                        raise DataSanityError(str(obsid), ru(QCoreApplication.translate(u'SurveyStore', u"Bed depth is incorrect (%.2f > %.2f)")) % (bed1, strato.depthBot))
                    # bed (n) = top (n+1)
                    if bed1 != strato.depthTop:
                        raise DataSanityError(str(obsid), ru(QCoreApplication.translate(u'SurveyStore', u"Top and bed depth don't match (%.2f != %.2f)")) % (bed1, strato.depthTop))
                    
                    top1 = strato.depthTop
                    bed1 = strato.depthBot
            surveys[obsid] = survey
        return surveys

class SurveyWidget(PyQt4.QtGui.QFrame):

    def __init__(self, parent = None):
        PyQt4.QtGui.QFrame.__init__(self, parent)
        self.setFrameShape(PyQt4.QtGui.QFrame.StyledPanel)
        self.setLineWidth(3)
        self.sondaggio = {}
        # In the original ARPAT plugin the following convention was used F = points, T = vertical lines and  C = horizontal lines
        """  Following standard Qt Colors exist
            Qt.white            White (#ffffff)
            Qt.black            Black (#000000)
            Qt.red            Red (#ff0000)
            Qt.darkRed            Dark red (#800000)
            Qt.green            Green (#00ff00)
            Qt.darkGreen            Dark green (#008000)
            Qt.blue            Blue (#0000ff)
            Qt.darkBlue            Dark blue (#000080)
            Qt.cyan            Cyan (#00ffff)
            Qt.darkCyan            Dark cyan (#008080)
            Qt.magenta            Magenta (#ff00ff)
            Qt.darkMagenta            Dark magenta (#800080)
            Qt.yellow            Yellow (#ffff00)
            Qt.darkYellow            Dark yellow (#808000)
            Qt.gray            Gray (#a0a0a4)
            Qt.darkGray            Dark gray (#808080)
            Qt.lightGray            Light gray (#c0c0c0)
            Qt.transparent    a transparent black value (i.e., PySide.QtGui.QColor (0, 0, 0, 0))
        """
        #------------------Please note!---------------------
        # Due to unicode normalize in getData function below, swedish national characters will be 
        # transformed to a, a, and o when read from the stratigraphy table
        self.geoColorSymbols = defs.geocolorsymbols()
        #print(self.geoColorSymbols)#debug
        self.hydroColors = defs.hydrocolors()
        #print(self.hydroColors)#debug
        self.switchGeoHydro = 0        #Default is to show colors according to geo
        self.GeoOrComment = "geology"     #Default is that text =  geology description
        self.showDesc = True        #Default is to show text
        
    def setData(self, sondaggio): 
        self.sondaggio = sondaggio
        # find out whether the overall distance is bigger on x or y axis
        # so columns will be sorted by their x or y coordinate
        inf = 999999999
        (xMin, yMin, xMax, yMax) = (inf, inf, -inf, -inf)
        for s in sondaggio.itervalues():
            (x, y) = (s.coord.x(), s.coord.y())
            if x < xMin: xMin = x
            if y < yMin: yMin = y
            if x > xMax: xMax = x
            if y > yMax: yMax = y
        
        if xMax - xMin > yMax - yMin:
            # sort using x coordinate
            cc = lambda a,b: cmp(a.coord.x(), b.coord.x())
        else:
            # sort using y coordinate
            cc = lambda a,b: cmp(a.coord.y(), b.coord.y())
        
        order = sorted(self.sondaggio.itervalues(), cc)
        self.order = order  # THIS SHOULD BE REPLACED BY 2L BELOW
        #for o in order:
        #    self.order.append(o.obsid)   # _CHANGE_  Should be fixed 

    def setData2_nosorting(self, sondaggio):  #Without sorting
        self.order = []
        for s in sondaggio.itervalues():
            self.order.append(s)

    def setType(self, switchGeoHydro):
        """ sets whether fill columns with Geo colors (0) or Hydro colors (1) """
        self.switchGeoHydro = switchGeoHydro
        self.update()

    def setGeoOrComment(self, GeoOrComment):
        """ sets whether to print geology ("geology") or Comment ("comment") """
        self.GeoOrComment = GeoOrComment
        self.update()
        
    def setShowDesc(self, show):
        self.showDesc = show
        self.update()

    def paintEvent(self, event):
        """ redraws the whole widget's area """
        
        PyQt4.QtGui.QFrame.paintEvent(self,event)

        # check whether there's a survey to show
        if len(self.sondaggio) == 0:
            p = PyQt4.QtGui.QPainter(self)
            p.drawText(self.rect(), PyQt4.QtCore.Qt.AlignCenter | PyQt4.QtCore.Qt.AlignVCenter, ru(QCoreApplication.translate(u'SurveyWidget', u"No data to display")))
            return

        painter = PyQt4.QtGui.QPainter(self)

        self.drawSurveys(self.rect(), painter)

    def drawSurveys(self, rect, painter):
        """ draw surveys to specified rect with specified painter """
        surveys = len(self.sondaggio)
        surveyWidth = rect.width() / surveys
        surveyHeight = rect.height()
        #columnWidth = rect.width() * 0.05
        columnWidth = rect.width() * 0.03
        x = 0
        margin = 4
        
        # find out depth interval
        depthBot, depthTop = 999999, -999999
        for survey in self.order:
            sond = self.sondaggio[survey.obsid]
            try:
                dTop = survey.top_lvl - survey.strata[0].depthTop
                dBed = survey.top_lvl - survey.strata[-1].depthBot
                
                if dTop > depthTop: depthTop = dTop
                if dBed < depthBot: depthBot = dBed
            except:
                pass
                
        # draw surveys
        for survey in self.order:
            r = PyQt4.QtCore.QRect(x + margin, 0 + margin, surveyWidth - 2*margin, surveyHeight - 2*margin)
            x += surveyWidth
            sond = self.sondaggio[survey.obsid]
            # draw the survey
            try:
                self.drawSurvey(painter, sond, r, columnWidth, (depthBot, depthTop))
            except:
                pass

    def drawSurvey(self, p, sond, sRect, columnWidth, interval):   
        """ draws one survey to rectangle in widget specified by sRect """
        depthTop = sond.top_lvl
        depthBot = depthTop - sond.strata[-1].depthBot
        
        fm = PyQt4.QtGui.QFontMetrics(p.font())
        nameHeight = fm.height()
        depthHeight = fm.height()
        
        # draw obsid 'name'
        labelRect = PyQt4.QtCore.QRect(sRect.left(),sRect.top(),sRect.width(),nameHeight)
        p.drawText(labelRect, PyQt4.QtCore.Qt.AlignVCenter, sond.obsid)
        
        scale = (sRect.height() - nameHeight - depthHeight*2) / (interval[1]-interval[0])
        
        top = sRect.top()+nameHeight+depthHeight
        yTop = top + (interval[1]-depthTop)*scale
        yBed = top + (interval[1]-depthBot)*scale
        
        # top depth
        depthRect = PyQt4.QtCore.QRect(sRect.left(),yTop-depthHeight,sRect.width(),depthHeight)
        p.drawText(depthRect, PyQt4.QtCore.Qt.AlignVCenter, "%.1f m" % depthTop)
        
        # bed depth
        depthRect = PyQt4.QtCore.QRect(sRect.left(),yBed+1,sRect.width(),depthHeight)
        p.drawText(depthRect, PyQt4.QtCore.Qt.AlignVCenter, "%.1f m" % depthBot)
        
        
        dRect = PyQt4.QtCore.QRect(PyQt4.QtCore.QPoint(sRect.left(), yTop),
                             PyQt4.QtCore.QPoint(sRect.left()+columnWidth, yBed))
    
        p.drawRect(dRect)
    
        scale = dRect.height() / (depthTop - depthBot)
        y = dRect.top()


        for layer in sond.strata:
            y2 = (layer.depthBot - layer.depthTop) * scale
            # column rectangle
            cRect = PyQt4.QtCore.QRect(PyQt4.QtCore.QPoint(dRect.left(), y),
                                 PyQt4.QtCore.QPoint(dRect.right(), y+y2-1))

            # text rectangle
            tRect = PyQt4.QtCore.QRect(PyQt4.QtCore.QPoint(dRect.right()+10, y),
                                 PyQt4.QtCore.QPoint(sRect.right(), y+y2))

            bType = self.geoToSymbol(layer.geo_short)  # select brush pattern depending on the geo_short 
            # select brush pattern depending on usage of geo or hydro
            if self.switchGeoHydro == 0:
                color = self.textToColor(layer.geo_short, 'geo')
            else:
                color = self.textToColor(layer.hydro, 'hydro')
            # draw column with background color
            p.setBrush(color)
            p.drawRect(cRect)

            # draw column with specified hatch
            p.setBrush(PyQt4.QtGui.QBrush(PyQt4.QtCore.Qt.black, bType))
            p.drawRect(cRect)

            # draw associated text
            if self.showDesc:
                if self.GeoOrComment == "geology":
                    p.drawText(tRect, PyQt4.QtCore.Qt.AlignVCenter, '' if layer.geology=='NULL' else layer.geology)#'Yes' if fruit == 'Apple' else 'No'
                elif self.GeoOrComment == "comment":
                    p.drawText(tRect, PyQt4.QtCore.Qt.AlignVCenter, '' if layer.comment=='NULL' else layer.comment)
                elif self.GeoOrComment == "geoshort":
                    p.drawText(tRect, PyQt4.QtCore.Qt.AlignVCenter, '' if layer.geo_short=='NULL' else layer.geo_short)
                elif self.GeoOrComment == "hydro":
                    p.drawText(tRect, PyQt4.QtCore.Qt.AlignVCenter, '' if layer.hydro=='NULL' else layer.hydro)
                elif self.GeoOrComment == "hydro explanation":
                    if layer.hydro is None or layer.hydro=='NULL':
                        hydr = ''
                    else:
                        hydr = self.hydroColors.get(layer.hydro, '')[0]
                    p.drawText(tRect, PyQt4.QtCore.Qt.AlignVCenter, hydr)

                else:
                    p.drawText(tRect, PyQt4.QtCore.Qt.AlignVCenter, '' if layer.development=='NULL' else layer.development)

            y += y2

    def textToColor(self, id='', type=''):    # _ DEFINE (in the class method) AND USE (in this function) A DICTIONARY INSTEAD
        """ returns QColor from the specified text """

        if type == 'hydro':
            if id in self.hydroColors:
                #return eval("PyQt4.QtCore.Qt" + self.hydroColors[id][2])    # Less sofisticated method to create a function call from a string (function syntax is in the string)
                return getattr(PyQt4.QtCore.Qt, self.hydroColors[id][1])  # getattr is to combine a function and a string to a combined function
            else:
                return PyQt4.QtCore.Qt.white
        elif type == 'geo':
            #if id.lower() in self.geoColorSymbols:
            if id in self.geoColorSymbols:
                try:# first we assume it is a predefined Qt color, hence use PyQt4.QtCore.Qt  
                    #return getattr(PyQt4.QtCore.Qt, self.geoColorSymbols[id.lower()][1])
                    return getattr(PyQt4.QtCore.Qt, self.geoColorSymbols[id][1])
                except: # otherwise it must be a SVG 1.0 color name, then it must be created by QtGui.QColor instead
                    return PyQt4.QtGui.QColor(self.geoColorSymbols[id][1])
            else:
                return PyQt4.QtCore.Qt.white

    def geoToSymbol(self, id=''):    # A function to return fill type for the box representing the stratigraphy layer
        """ returns Symbol from the specified text """
        #if id.lower() in self.geoColorSymbols:

        if id in self.geoColorSymbols:
            #return getattr(PyQt4.QtCore.Qt, self.geoColorSymbols[id.lower()][0])   # Or possibly [0]?
            return getattr(PyQt4.QtCore.Qt, self.geoColorSymbols[id][0])   # Or possibly [0]?
        else:
            return PyQt4.QtCore.Qt.NoBrush
        
    def printDiagram(self):
        """ outputs the diagram to the printer (or PDF) """
        printer = PyQt4.QtGui.QPrinter(PyQt4.QtGui.QPrinter.HighResolution)
        
        # set defaults
        printer.setOrientation(PyQt4.QtGui.QPrinter.Landscape)

    # setting output file name results in not opening print dialog on Win
        #printer.setOutputFileName("arpat.pdf")
        
        # show print dialog
        dlg = PyQt4.QtGui.QPrintDialog(printer, self)
        if dlg.exec_() != PyQt4.QtGui.QDialog.Accepted:
            return
        
        p = PyQt4.QtGui.QPainter()
        p.begin(printer)
        
        rect = printer.pageRect()
        #print "rect: ", rect.left(), rect.top(), rect.width(), rect.height()

        self.drawSurveys(rect, p)
        
        p.end()

class SurveyDialog(PyQt4.QtGui.QDialog):
    
    def __init__(self, parent=None):
        PyQt4.QtGui.QDialog.__init__(self, parent)
        
        self.resize(PyQt4.QtCore.QSize(500,250))
        self.setWindowFlags(PyQt4.QtCore.Qt.Window | PyQt4.QtCore.Qt.WindowMinimizeButtonHint | PyQt4.QtCore.Qt.WindowMaximizeButtonHint | PyQt4.QtCore.Qt.WindowCloseButtonHint);

        self.setWindowTitle(ru(QCoreApplication.translate(u'SurveyDialog', u"Identify Results")))
        
        self.layout = PyQt4.QtGui.QVBoxLayout(self)
        self.layout.setMargin(5)
        
        self.layout2 = PyQt4.QtGui.QHBoxLayout()
        
        self.widget = SurveyWidget()
        self.layout.addWidget(self.widget)
        
        self.radGeo = PyQt4.QtGui.QRadioButton("Geo")
        self.radGeo.setChecked(True)    #Default is to show colors as per geo
        self.layout2.addWidget(self.radGeo)
        self.radHydro = PyQt4.QtGui.QRadioButton("Hydro")
        #self.radHydro.setChecked(False)  #Default is NOT to show colors as per hydro
        self.layout2.addWidget(self.radHydro)
        
        spacerItem = PyQt4.QtGui.QSpacerItem(100,0)
        self.layout2.addItem(spacerItem)
        
        self.chkShowDesc = PyQt4.QtGui.QCheckBox(ru(QCoreApplication.translate(u'SurveyDialog', u"Show text")))
        self.chkShowDesc.setChecked(True)
        self.layout2.addWidget(self.chkShowDesc)

        self.GeologyOrCommentCBox = PyQt4.QtGui.QComboBox(self)
        self.GeologyOrCommentCBox.addItem('geology')
        self.GeologyOrCommentCBox.addItem('comment')
        self.GeologyOrCommentCBox.addItem('geoshort')
        self.GeologyOrCommentCBox.addItem('hydro')
        self.GeologyOrCommentCBox.addItem('hydro explanation')
        self.GeologyOrCommentCBox.addItem('development')
        self.layout2.addWidget(self.GeologyOrCommentCBox)
        


        self.btnPrint = PyQt4.QtGui.QPushButton(ru(QCoreApplication.translate(u'SurveyDialog', u"Print")))
        self.layout2.addWidget(self.btnPrint)
        
        self.btnClose = PyQt4.QtGui.QPushButton(ru(QCoreApplication.translate(u'SurveyDialog', u"Close")))
        self.layout2.addWidget(self.btnClose)
        
        self.layout.addLayout(self.layout2)

        self.connect(self.btnClose, PyQt4.QtCore.SIGNAL("clicked()"), self.close)
        self.connect(self.btnPrint, PyQt4.QtCore.SIGNAL("clicked()"), self.widget.printDiagram)
        self.connect(self.radGeo, PyQt4.QtCore.SIGNAL("toggled(bool)"), self.typeToggled)
        self.connect(self.radHydro, PyQt4.QtCore.SIGNAL("toggled(bool)"), self.typeToggled)
        self.connect(self.chkShowDesc, PyQt4.QtCore.SIGNAL("toggled(bool)"), self.widget.setShowDesc)
        self.connect(self.GeologyOrCommentCBox, PyQt4.QtCore.SIGNAL("currentIndexChanged(int)"), partial(self.ComboBoxUpdated)) 
        # whenever the combobox is changed, function partial is used due to problems with currentindexChanged and Combobox)
        
    def close(self):
        self.accept()
    
    def typeToggled(self):
        if self.radGeo.isChecked():
            self.widget.setType(0)
        else:
            self.widget.setType(1)

    def ComboBoxUpdated(self):
        text = self.GeologyOrCommentCBox.currentText()
        self.widget.setGeoOrComment(text)
            


class DataSanityError(Exception):  # Instances of this class is created whenever some data sanity checks fails
    """ exception raised when data don't comply with some constraints """
    
    def __init__(self, sond_id, message):
        self.sond_id = sond_id
        self.message = message
    def __str__(self):
        return "Sond_ID %s: %s" % (self.sond_id, self.message)

class DataError(Exception):  # Instances of this class is created whenever some data accessing (by SurveyStore) fails
    """ exception raised on problems accessing data """
    def __init__(self, problem):
        self.problem = problem
    def __str__(self):
        return self.problem

