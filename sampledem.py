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

def accept(self): #original start function from qchainage
    layer = self.get_current_layer()
    label = self.autoLabelCheckBox.isChecked()
    layerout = self.layerNameLine.text()
    distance = self.distanceSpinBox.value()
    startpoint = self.startSpinBox.value()
    endpoint = self.endSpinBox.value()
    selectedOnly = self.selectOnlyRadioBtn.isChecked()

    projectionSettingKey = "Projections/defaultBehaviour"
    oldProjectionSetting = self.qgisSettings.value(projectionSettingKey)
    self.qgisSettings.setValue(projectionSettingKey, "useGlobal")
    self.qgisSettings.sync()

    points_along_line(
        layerout,
        startpoint,
        endpoint,
        distance,
        label,
        layer,
        selectedOnly)
    self.qgisSettings.setValue(projectionSettingKey, oldProjectionSetting)

def create_points_at(startpoint, endpoint, distance, geom, fid): #original function from qchainage
    """Creating Points at coordinates along the line
    """
    length = geom.length()
    current_distance = distance
    feats = []

    if endpoint > 0:
        length = endpoint

    # set the first point at startpoint
    point = geom.interpolate(startpoint)

    field_id = QgsField(name="id", type=QVariant.Int)
    field = QgsField(name="dist", type=QVariant.Double)
    fields = QgsFields()

    fields.append(field_id)
    fields.append(field)

    feature = QgsFeature(fields)
    feature['dist'] = startpoint
    feature['id'] = fid

    feature.setGeometry(point)
    feats.append(feature)

    while startpoint + current_distance <= length:
        # Get a point along the line at the current distance
        point = geom.interpolate(startpoint + current_distance)
        # Create a new QgsFeature and assign it the new geometry
        feature = QgsFeature(fields)
        feature['dist'] = (startpoint + current_distance)
        feature['id'] = fid
        feature.setGeometry(point)
        feats.append(feature)
        # Increase the distance
        current_distance = current_distance + distance

    return feat

def points_along_line(layerout,
                      startpoint,
                      endpoint,
                      distance,
                      label,
                      layer,
                      selected_only=True):#more from qchainage
    """Adding Points along the line
    """
    # Create a new memory layer and add a distance attribute self.layerNameLine
    #layer_crs = virt_layer.setCrs(layer.crs())
    virt_layer = QgsVectorLayer("Point?crs=%s" % layer.crs().authid(),
                                layerout,
                                "memory")
    provider = virt_layer.dataProvider()
    virt_layer.startEditing()   # actually writes attributes
    units = layer.crs().mapUnits()
    unit_dic = {
        QGis.Degrees: 'Degrees',
        QGis.Meters: 'Meters',
        QGis.Feet: 'Feet',
        QGis.UnknownUnit: 'Unknown'}
    unit = unit_dic.get(units, 'Unknown')
    provider.addAttributes([QgsField("fid", QVariant.Int)])
    provider.addAttributes([QgsField("cng_("+unit+")", QVariant.Int)])


    def get_features():
        """Getting the features
        """
        if selected_only:
            return layer.selectedFeatures()
        else:
            return layer.getFeatures()

    # Loop through all (selected) features
    for feature in get_features():
        geom = feature.geometry()
        # Add feature ID of selected feature
        fid = feature.id()
        if not geom:
            QgsMessageLog.logMessage("No geometry", "QChainage")
            continue

        features = create_points_at(startpoint, endpoint, distance, geom, fid)
        provider.addFeatures(features)
        virt_layer.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayers([virt_layer])
    virt_layer.commitChanges()
    virt_layer.reload()

    #from here Add labeling
    #generic labeling properties
    if label:
        virt_layer.setCustomProperty("labeling", "pal")
        virt_layer.setCustomProperty("labeling/enabled", "true")
        virt_layer.setCustomProperty("labeling/fieldName", "cng_("+unit+")")
        virt_layer.setCustomProperty("labeling/fontSize", "10")
        virt_layer.setCustomProperty("labeling/multiLineLabels", "true")

        #virt_layer.setCustomProperty("labeling/Size", "5")
    # symbol = QgsMarkerSymbolV2.createSimple({"name": "capital"})
    # virt_layer.setRendererV2(QgsSingleSymbolRendererV2(symbol))
    virt_layer.triggerRepaint()
    return

def sampling(self, outPath): # main process from pointsamplingtool #so far not changed at all from original plugin
    # open sampling points layer
    pointLayer = self.sampItems[unicode(self.inSample.currentText())][0]
    pointProvider = pointLayer.dataProvider()
    allAttrs = pointProvider.attributeIndexes()
    sRs = pointProvider.crs()
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
    # create destination layer
    writer = QgsVectorFileWriter(outPath, "UTF-8", fieldList, pointProvider.geometryType(), sRs)
    self.statusLabel.setText("Writing data to the new layer...")
    self.repaint()
    # process point after point...
    pointFeat = QgsFeature()
    np = 0
    snp = pointProvider.featureCount()
    for pointFeat in pointProvider.getFeatures():
        np += 1
        if snp<100 or ( snp<5000 and ( np // 10.0 == np / 10.0 ) ) or ( np // 100.0 == np / 100.0 ): # display each or every 10th or every 100th point:
            self.statusLabel.setText("Processing point %s of %s" % (np, snp))
            self.repaint()
        # convert multipoint[0] to point
        pointGeom = pointFeat.geometry()
        if pointGeom.wkbType() == QGis.WKBMultiPoint:
            pointPoint = pointGeom.asMultiPoint()[0]
        else:
            pointPoint = pointGeom.asPoint()
        outFeat = QgsFeature()
        outFeat.setGeometry(pointGeom)
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

    del writer
    self.statusLabel.setText("The new layer has been created.")
