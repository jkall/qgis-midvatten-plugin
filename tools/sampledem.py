#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is where a DEM is sampled along a vector polyline 
                             -------------------
        begin                : 2014-08-22
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/
"""
"""
This code is inspired from the PointSamplingTool plugin Copyright (C) 2008 Borys Jurgiel
and qchainage plugin (C) 2012 by Werner Macho
"""
import PyQt4.QtCore
import PyQt4.QtGui
from qgis.core import *

def qchain(sectionlinelayer, distance): #original start function from qchainage
    layer = sectionlinelayer
    layerout = 'temporary_memory_layer'
    startpoint = 0
    endpoint = 0
    #selectedOnly = self.selectOnlyRadioBtn.isChecked()

    projectionSettingKey = "Projections/defaultBehaviour"
    qgisSettings = PyQt4.QtCore.QSettings()
    oldProjectionSetting = qgisSettings.value(projectionSettingKey)
    qgisSettings.setValue(projectionSettingKey, "useGlobal")
    qgisSettings.sync()

    virt_layer, xarray = points_along_line(
        layerout,
        startpoint,
        endpoint,
        distance,
        layer)#,
        #selectedOnly)
    qgisSettings.setValue(projectionSettingKey, oldProjectionSetting)
    
    return virt_layer, xarray

def create_points_at(startpoint, endpoint, distance, geom, fid,unit): #original function from qchainage
    """Creating Points at coordinates along the line
    """
    length = geom.length()
    current_distance = distance
    feats = []

    if endpoint > 0:
        length = endpoint

    # set the first point at startpoint
    point = geom.interpolate(startpoint)

    field_id = QgsField(name="id", type=PyQt4.QtCore.QVariant.Int)
    field = QgsField(name="dist", type=PyQt4.QtCore.QVariant.Double)
    field2 = QgsField(name="unit", type=PyQt4.QtCore.QVariant.String)
    fields = QgsFields()

    fields.append(field_id)
    fields.append(field)
    fields.append(field2)

    feature = QgsFeature(fields)
    feature['dist'] = startpoint
    feature['id'] = fid
    feature['unit'] = unit

    feature.setGeometry(point)
    feats.append(feature)
    xarray=[]

    while startpoint + current_distance <= length:
        # Get a point along the line at the current distance
        point = geom.interpolate(startpoint + current_distance)
        # Create a new QgsFeature and assign it the new geometry
        feature = QgsFeature(fields)
        feature['dist'] = (startpoint + current_distance)
        feature['id'] = fid
        feature['unit'] = unit
        feature.setGeometry(point)
        feats.append(feature)
        xarray.append( feature['dist'])
        # Increase the distance
        current_distance = current_distance + distance

    return feats, xarray

def points_along_line(layerout, startpoint, endpoint, distance, layer):#,selected_only=True):#more from qchainage
    """Adding Points along the line"""
    # Create a new memory layer and add a distance attribute self.layerNameLine
    #layer_crs = virt_layer.setCrs(layer.crs())
    virt_layer = QgsVectorLayer("Point?crs=%s" % layer.crs().authid(),layerout,"memory")
    provider = virt_layer.dataProvider()
    virt_layer.startEditing()   # actually writes attributes
    units = layer.crs().mapUnits()
    unit_dic = {
        QGis.Degrees: 'Degrees',
        QGis.Meters: 'Meters',
        QGis.Feet: 'Feet',
        QGis.UnknownUnit: 'Unknown'}
    unit = unit_dic.get(units, 'Unknown')
    provider.addAttributes([QgsField("fid", PyQt4.QtCore.QVariant.Int)])
    provider.addAttributes([QgsField("cum_dist", PyQt4.QtCore.QVariant.Int)])
    provider.addAttributes([QgsField("unit", PyQt4.QtCore.QVariant.String)])


    def get_features():
        """Getting the features
        """
        # only selected feature!!!
        return layer.selectedFeatures()
        """
        if selected_only:
            return layer.selectedFeatures()
        else:
            return layer.getFeatures()
        """

    # Loop through all (selected) features
    for feature in get_features():
        geom = feature.geometry()
        # Add feature ID of selected feature
        fid = feature.id()
        if not geom:
            QgsMessageLog.logMessage("No geometry", "QChainage")
            continue

        features, xarray = create_points_at(startpoint, endpoint, distance, geom, fid,unit)
        provider.addFeatures(features)
        virt_layer.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayers([virt_layer])
    virt_layer.commitChanges()
    virt_layer.reload()
    virt_layer.triggerRepaint()
    return virt_layer, xarray

def sampling(pointsamplinglayer, rastersamplinglayer): # main process from pointsamplingtool #so far not changed at all from original plugin
    # open sampling points layer
    pointLayer = pointsamplinglayer
    pointProvider = pointLayer.dataProvider()
    allAttrs = pointProvider.attributeIndexes()
    sRs = pointProvider.crs()
    """
    #THIS IS TO BE USED LATER ON
    # create destination layer: first create list of selected fields
    fieldList = QgsFields()
    for i in range(len(self.fields)):
        if self.fields[i][0] == "point": #copying fields from source layer
            field = pointProvider.fields()[pointProvider.fieldNameIndex(self.sampItems[self.fields[i][1]][self.fields[i][2]][0])]
            field.setName(self.sampItems[self.fields[i][1]][self.fields[i][2]][1])
        elif self.fields[i][0] == "poly": #copying fields from polygon layers
            polyLayer = self.polyItems[self.fields[i][1]][0]
            polyProvider = polyLayer.dataProvider()
            field = polyProvider.fields()[polyProvider.fieldNameIndex(self.polyItems[self.fields[i][1]][self.fields[i][2]][0])]
            field.setName(self.polyItems[self.fields[i][1]][self.fields[i][2]][1])
        else: #creating fields for raster layers
            field = QgsField(self.rastItems[self.fields[i][1]][self.fields[i][2]][1], QVariant.Double, "real", 20, 5, "")
            ##### Better data type fit will be implemented in next versions
        fieldList.append(field)
    """

    """
    "This is not to be used
    # create destination layer
    writer = QgsVectorFileWriter(outPath, "UTF-8", fieldList, pointProvider.geometryType(), sRs)
    self.statusLabel.setText("Writing data to the new layer...")
    self.repaint()
    """
    # process raster after raster and point after point...
    pointFeat = QgsFeature()#??????????????????
    np = 0
    snp = pointProvider.featureCount()
    DEMLEV = []
    for pointFeat in pointProvider.getFeatures():
        np += 1
        #if snp<100 or ( snp<5000 and ( np // 10.0 == np / 10.0 ) ) or ( np // 100.0 == np / 100.0 ): # display each or every 10th or every 100th point:
        #    print("Processing point %s of %s" % (np, snp))#debug
        #    #self.repaint()
        # convert multipoint[0] to point
        pointGeom = pointFeat.geometry()
        if pointGeom.wkbType() == QGis.WKBMultiPoint:
            pointPoint = pointGeom.asMultiPoint()[0]
        else:
            pointPoint = pointGeom.asPoint()
        outFeat = QgsFeature()
        outFeat.setGeometry(pointGeom)
        """
        # ...and next loop inside: field after field
        bBox = QgsRectangle(pointPoint.x()-0.001,pointPoint.y()-0.001,pointPoint.x()+0.001,pointPoint.y()+0.001) # reuseable rectangle buffer around the point feature
        previousPolyLayer = None  # reuse previous feature if it's still the same layer
        previousPolyFeat = None   # reuse previous feature if it's still the same layer
        previousRastLayer = None  # reuse previous raster multichannel sample if it's still the same layer
        previousRastSample = None # reuse previous raster multichannel sample if it's still the same layer
        attrs = []
        for i in range(len(self.fields)):
            field = self.fields[i]
            if field[0] == "point":
                attr = pointFeat.attributes()[pointProvider.fieldNameIndex(self.sampItems[field[1]][field[2]][0])]
                attrs += [attr]
            elif field[0] == "poly":
                polyLayer = self.polyItems[field[1]][0]
                polyProvider = polyLayer.dataProvider()
                if polyLayer == previousPolyLayer:
                    polyFeat = previousPolyFeat
                else:
                    polyFeat = None
                    pointGeom = QgsGeometry().fromPoint(pointPoint)
                    for iFeat in polyProvider.getFeatures(QgsFeatureRequest().setFilterRect(bBox)):
                        if pointGeom.intersects(iFeat.geometry()):
                            polyFeat = iFeat
                if polyFeat:
                    attr = polyFeat.attributes()[polyProvider.fieldNameIndex(self.polyItems[field[1]][field[2]][0])]
                else:
                    attr = None
                attrs += [attr] #only last one if more polygons overlaps!! This way we avoid attribute list overflow
                previousPolyLayer = polyLayer
                previousPolyFeat = polyFeat
            else: # field source is raster
                rastLayer = self.rastItems[field[1]][0]
                if rastLayer == previousRastLayer:
                    rastSample = previousRastSample
                else:
                    rastSample = rastLayer.dataProvider().identify(pointPoint, QgsRaster.IdentifyFormatValue).results()
                try:
                    #bandName = self.rastItems[field[1]][field[2]][0] #depreciated
                    bandNo = field[2]
                    attr = float(rastSample[bandNo]) ##### !! float() - I HAVE TO IMPLEMENT RASTER TYPE HANDLING!!!!
                except: # point is out of raster extent
                    attr = None
                attrs += [attr]
                previousRastLayer = rastLayer
                previousRastSample = rastSample
        outFeat.initAttributes(len(attrs))
        outFeat.setAttributes(attrs)
        writer.addFeature(outFeat)
        """

        rastSample = rastersamplinglayer.dataProvider().identify(pointPoint, QgsRaster.IdentifyFormatValue).results()
        if snp<100 or ( snp<5000 and ( np // 10.0 == np / 10.0 ) ) or ( np // 100.0 == np / 100.0 ): # display each or every 10th or every 100th point:
            print(rastSample)
            #print (float(rastSample[0]))
            print (float(rastSample[1]))
        if np > 1:
            try:
                DEMLEV.append(float(rastSample[1])) ##### !! float() - I HAVE TO IMPLEMENT RASTER TYPE HANDLING!!!!
            except: # point is out of raster extent
                DEMLEV.append(None)

    #del writer
    return DEMLEV
