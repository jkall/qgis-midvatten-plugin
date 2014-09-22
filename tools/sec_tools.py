
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.core import QgsMapLayerRegistry, QgsMapLayer, QGis, QgsFeature, \
                      QgsCoordinateTransform, QgsPoint
from qgis.gui import *

def loaded_layers():
    
    return QgsMapLayerRegistry.instance().mapLayers().values()

    
def loaded_vector_layers():
 
    return filter( lambda layer: layer.type() == QgsMapLayer.VectorLayer, 
                   loaded_layers() )
    
            
def loaded_line_layers():        
    
    return filter( lambda layer: layer.geometryType() == QGis.Line, 
                          loaded_vector_layers() )


def loaded_point_layers():

    return filter( lambda layer: layer.geometryType() == QGis.Point, 
                          loaded_vector_layers() )
    
 
def loaded_raster_layers( ):        
          
    return filter( lambda layer: layer.type() == QgsMapLayer.RasterLayer, 
                          loaded_layers() )


def loaded_monoband_raster_layers( ):        
          
    return filter( lambda layer: layer.bandCount() == 1, 
                   loaded_raster_layers() )
       
           
def pt_geoms_attrs( pt_layer, field_list = [] ):
    
    if pt_layer.selectedFeatureCount() > 0:
        features = pt_layer.selectedFeatures()
    else:
        features = pt_layer.getFeatures() 
    
    provider = pt_layer.dataProvider()    
    field_indices = [ provider.fieldNameIndex( field_name ) for field_name in field_list ]

    # retrieve selected features with their geometry and relevant attributes
    rec_list = [] 
    for feature in features:
             
        # fetch point geometry
        pt = feature.geometry().asPoint()

        attrs = feature.fields().toList() 

        # creates feature attribute list
        feat_list = [ pt.x(), pt.y() ]
        for field_ndx in field_indices:
            feat_list.append( str( feature.attribute( attrs[ field_ndx ].name() ) ) )

        # add to result list
        rec_list.append( feat_list )
        
    return rec_list


def line_geoms_attrs( line_layer, field_list = [] ):
    """
    return: lines, list
    """
    
    lines = []
    
    if line_layer.selectedFeatureCount() > 0:
        features = line_layer.selectedFeatures()
    else:
        features = line_layer.getFeatures()

    provider = line_layer.dataProvider() 
    field_indices = [ provider.fieldNameIndex( field_name ) for field_name in field_list ]
                
    for feature in features:
        geom = feature.geometry()
        if geom.isMultipart():
            rec_geom = multipolyline_to_xytuple_list2( geom.asMultiPolyline() )
        else:
            rec_geom = [ polyline_to_xytuple_list( geom.asPolyline() ) ]
            
        attrs = feature.fields().toList()
        rec_data = [ str( feature.attribute( attrs[ field_ndx ].name() ) ) for field_ndx in field_indices ]
            
        lines.append( [ rec_geom, rec_data ] )
            
    return lines
           
       
def line_geoms_with_id( line_layer, curr_field_ndx ):    
        
    lines = []
    progress_ids = [] 
    dummy_progressive = 0 
      
    line_iterator = line_layer.getFeatures()
   
    for feature in line_iterator:
        try:
            progress_ids.append( int( feature[ curr_field_ndx ] ) )
        except:
            dummy_progressive += 1
            progress_ids.append( dummy_progressive )
             
        geom = feature.geometry()         
        if geom.isMultipart():
            lines.append( 'multiline', multipolyline_to_xytuple_list2( geom.asMultiPolyline() ) ) # typedef QVector<QgsPolyline>
            # now is a list of list of (x,y) tuples
        else:           
            lines.append( ( 'line', polyline_to_xytuple_list( geom.asPolyline() ) ) ) # typedef QVector<QgsPoint>
                         
    return lines, progress_ids
              
                   
def polyline_to_xytuple_list( qgsline):
    
    assert len( qgsline ) > 0    
    return [ ( qgspoint.x(), qgspoint.y() ) for qgspoint in qgsline ]


def multipolyline_to_xytuple_list2( qgspolyline ):
    
    return [ polyline_to_xytuple_list( qgsline) for qgsline in qgspolyline ] 


def field_values( layer, curr_field_ndx ): 
    
    values = []
    iterator = layer.getFeatures()
    
    for feature in iterator:
        values.append( feature.attributes()[ curr_field_ndx ] ) 
            
    return values
    
    
def vect_attrs( layer, field_list):
    
    if layer.selectedFeatureCount() > 0:
        features = layer.selectedFeatures()
    else:
        features = layer.getFeatures()
        
    provider = layer.dataProvider()   
    field_indices = [ provider.fieldNameIndex( field_name ) for field_name in field_list ]

    # retrieve (selected) attributes features
    data_list = [] 
    for feature in features:        
        attrs = feature.fields().toList()     
        data_list.append( [ feature.attribute( attrs[ field_ndx ].name() ) for field_ndx in field_indices ] )
        
    return data_list    
    
    
def raster_qgis_params( raster_layer ):
    
    name = raster_layer.name()
                  
    rows = raster_layer.height()
    cols = raster_layer.width()
    
    extent = raster_layer.extent()
    
    xMin = extent.xMinimum()
    xMax = extent.xMaximum()        
    yMin = extent.yMinimum()
    yMax = extent.yMaximum()
        
    cellsizeEW = (xMax-xMin) / float(cols)
    cellsizeNS = (yMax-yMin) / float(rows)
    
    #TODO: get real no data value from QGIS
    if raster_layer.dataProvider().srcHasNoDataValue(1):
        nodatavalue = raster_layer.dataProvider().srcNoDataValue ( 1 )
    else:
        nodatavalue = np.nan
    
    try:
        crs = raster_layer.crs()
    except:
        crs = None
    
    return name, cellsizeEW, cellsizeNS, rows, cols, xMin, xMax, yMin, yMax, nodatavalue, crs    

