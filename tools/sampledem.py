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

import PyQt4
from qgis.core import QGis, QgsFeature, QgsField, QgsFields, QgsMapLayerRegistry, QgsMessageLog, QgsRaster, QgsVectorLayer


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
        # only selected feature!!!
        return layer.selectedFeatures()

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

    # process raster after raster and point after point...
    pointFeat = QgsFeature()#??????????????????
    np = 0
    snp = pointProvider.featureCount()
    DEMLEV = []
    for pointFeat in pointProvider.getFeatures():
        np += 1
        pointGeom = pointFeat.geometry()
        if pointGeom.wkbType() == QGis.WKBMultiPoint:
            pointPoint = pointGeom.asMultiPoint()[0]
        else:
            pointPoint = pointGeom.asPoint()
        outFeat = QgsFeature()
        outFeat.setGeometry(pointGeom)

        rastSample = rastersamplinglayer.dataProvider().identify(pointPoint, QgsRaster.IdentifyFormatValue).results()
        """
        if snp<100 or ( snp<5000 and ( np // 10.0 == np / 10.0 ) ) or ( np // 100.0 == np / 100.0 ): # display each or every 10th or every 100th point:
            print(rastSample)
            #print (float(rastSample[0]))
            print (float(rastSample[1]))
        """
        if np > 1:
            try:
                DEMLEV.append(float(rastSample[1])) ##### !! float() - I HAVE TO IMPLEMENT RASTER TYPE HANDLING!!!!
            except: # point is out of raster extent
                DEMLEV.append(None)

    return DEMLEV
