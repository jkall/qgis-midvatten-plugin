<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.16.3-Hannover" minScale="100000000" hasScaleBasedVisibilityFlag="0" simplifyMaxScale="1" readOnly="0" maxScale="0" simplifyDrawingHints="0" simplifyLocal="1" labelsEnabled="1" styleCategories="AllStyleCategories" simplifyDrawingTol="1" simplifyAlgorithm="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal enabled="0" startField="" mode="0" durationUnit="min" accumulate="0" durationField="" endField="" endExpression="" startExpression="" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="nullSymbol"/>
  <labeling type="rule-based">
    <rules key="{b1539230-a04a-4344-9144-dcdad65e4499}">
      <rule key="{bfe2f486-4016-49d0-9e05-f2da94023384}" filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' ">
        <settings calloutType="simple">
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" capitalization="0" fontStrikeout="0" blendMode="0" fieldName="round(&quot;bedrock&quot;, 1)" fontUnderline="0" fontSizeUnit="Point" namedStyle="Italic" fontItalic="1" allowHtml="0" previewBkgrdColor="255,255,255,255" fontKerning="1" fontWordSpacing="0" textColor="255,1,1,255" fontLetterSpacing="0" textOpacity="1" multilineHeight="1" fontFamily="Noto Sans" fontWeight="50" useSubstitutions="0" fontSize="8" isExpression="1" textOrientation="horizontal">
            <text-buffer bufferBlendMode="0" bufferJoinStyle="128" bufferSizeUnits="MM" bufferColor="255,255,255,255" bufferNoFill="1" bufferSize="0.5" bufferOpacity="1" bufferDraw="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskOpacity="1" maskType="0" maskSize="0" maskEnabled="0" maskSizeUnits="MM" maskedSymbolLayers=""/>
            <background shapeSVGFile="" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="64" shapeOpacity="1" shapeOffsetY="0" shapeSizeType="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeSizeX="0" shapeSizeUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetUnit="MM" shapeOffsetX="0" shapeSizeY="0" shapeBorderWidthUnit="MM" shapeRotationType="0" shapeType="0" shapeRadiiUnit="MM" shapeFillColor="255,255,255,255" shapeBorderColor="128,128,128,255" shapeDraw="0" shapeBorderWidth="0">
              <symbol name="markerSymbol" alpha="1" type="marker" force_rhr="0" clip_to_extent="1">
                <layer enabled="1" locked="0" class="SimpleMarker" pass="0">
                  <prop v="0" k="angle"/>
                  <prop v="196,60,57,255" k="color"/>
                  <prop v="1" k="horizontal_anchor_point"/>
                  <prop v="bevel" k="joinstyle"/>
                  <prop v="circle" k="name"/>
                  <prop v="0,0" k="offset"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="35,35,35,255" k="outline_color"/>
                  <prop v="solid" k="outline_style"/>
                  <prop v="0" k="outline_width"/>
                  <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
                  <prop v="MM" k="outline_width_unit"/>
                  <prop v="diameter" k="scale_method"/>
                  <prop v="2" k="size"/>
                  <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
                  <prop v="MM" k="size_unit"/>
                  <prop v="1" k="vertical_anchor_point"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowRadiusAlphaOnly="0" shadowColor="0,0,0,255" shadowDraw="0" shadowScale="100" shadowUnder="0" shadowOffsetUnit="MM" shadowOffsetAngle="135" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadius="1.5" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowRadiusUnit="MM" shadowBlendMode="6" shadowOffsetDist="1"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format plussign="0" addDirectionSymbol="0" decimals="3" autoWrapLength="0" useMaxLineLengthForAutoWrap="1" wrapChar="" multilineAlign="3" formatNumbers="0" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" reverseDirectionSymbol="0" rightDirectionSymbol=">"/>
          <placement placementFlags="10" geometryGeneratorEnabled="0" repeatDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" quadOffset="2" distUnits="MM" polygonPlacementFlags="2" dist="0" priority="5" lineAnchorPercent="0.5" fitInPolygonOnly="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" preserveRotation="1" maxCurvedCharAngleOut="-25" overrunDistance="0" layerType="PointGeometry" placement="1" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistanceUnit="MM" rotationAngle="0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2 /**{xfactor}*/, Y($geometry)))" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MapUnit" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" centroidInside="0" geometryGeneratorType="PointGeometry" lineAnchorType="0" offsetType="0" repeatDistanceUnits="MM" yOffset="0" xOffset="0"/>
          <rendering fontMinPixelSize="3" minFeatureSize="0" drawLabels="1" fontMaxPixelSize="10000" obstacleFactor="1" scaleMax="0" maxNumLabels="2000" fontLimitPixelSize="0" scaleVisibility="0" obstacleType="0" displayAll="0" zIndex="0" obstacle="1" upsidedownLabels="0" mergeLines="0" limitNumLabels="0" labelPerPart="0" scaleMin="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="PositionX" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="X($geometry)+2 /**{xfactor}*/"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
                <Option name="PositionY" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="Y($geometry) - &quot;soildepth&quot; /**{yfactor}*/"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
                <Option name="Vali" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="'Half'"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; alpha=&quot;1&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot;>&lt;layer enabled=&quot;1&quot; locked=&quot;0&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule key="{27bc534a-32fc-4b3d-9c70-a8b0128c042c}" filter="ELSE">
        <settings calloutType="simple">
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" capitalization="0" fontStrikeout="0" blendMode="0" fieldName="'>' || round(&quot;bedrock&quot;, 1)" fontUnderline="0" fontSizeUnit="Point" namedStyle="Italic" fontItalic="1" allowHtml="0" previewBkgrdColor="255,255,255,255" fontKerning="1" fontWordSpacing="0" textColor="0,0,0,255" fontLetterSpacing="0" textOpacity="1" multilineHeight="1" fontFamily="Noto Sans" fontWeight="50" useSubstitutions="0" fontSize="8" isExpression="1" textOrientation="horizontal">
            <text-buffer bufferBlendMode="0" bufferJoinStyle="128" bufferSizeUnits="MM" bufferColor="255,255,255,255" bufferNoFill="1" bufferSize="0.5" bufferOpacity="1" bufferDraw="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskOpacity="1" maskType="0" maskSize="0" maskEnabled="0" maskSizeUnits="MM" maskedSymbolLayers=""/>
            <background shapeSVGFile="" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="64" shapeOpacity="1" shapeOffsetY="0" shapeSizeType="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeSizeX="0" shapeSizeUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetUnit="MM" shapeOffsetX="0" shapeSizeY="0" shapeBorderWidthUnit="MM" shapeRotationType="0" shapeType="0" shapeRadiiUnit="MM" shapeFillColor="255,255,255,255" shapeBorderColor="128,128,128,255" shapeDraw="0" shapeBorderWidth="0">
              <symbol name="markerSymbol" alpha="1" type="marker" force_rhr="0" clip_to_extent="1">
                <layer enabled="1" locked="0" class="SimpleMarker" pass="0">
                  <prop v="0" k="angle"/>
                  <prop v="196,60,57,255" k="color"/>
                  <prop v="1" k="horizontal_anchor_point"/>
                  <prop v="bevel" k="joinstyle"/>
                  <prop v="circle" k="name"/>
                  <prop v="0,0" k="offset"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="35,35,35,255" k="outline_color"/>
                  <prop v="solid" k="outline_style"/>
                  <prop v="0" k="outline_width"/>
                  <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
                  <prop v="MM" k="outline_width_unit"/>
                  <prop v="diameter" k="scale_method"/>
                  <prop v="2" k="size"/>
                  <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
                  <prop v="MM" k="size_unit"/>
                  <prop v="1" k="vertical_anchor_point"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowRadiusAlphaOnly="0" shadowColor="0,0,0,255" shadowDraw="0" shadowScale="100" shadowUnder="0" shadowOffsetUnit="MM" shadowOffsetAngle="135" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadius="1.5" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowRadiusUnit="MM" shadowBlendMode="6" shadowOffsetDist="1"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format plussign="0" addDirectionSymbol="0" decimals="3" autoWrapLength="0" useMaxLineLengthForAutoWrap="1" wrapChar="" multilineAlign="3" formatNumbers="0" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" reverseDirectionSymbol="0" rightDirectionSymbol=">"/>
          <placement placementFlags="10" geometryGeneratorEnabled="0" repeatDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" quadOffset="2" distUnits="MM" polygonPlacementFlags="2" dist="0" priority="5" lineAnchorPercent="0.5" fitInPolygonOnly="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" preserveRotation="1" maxCurvedCharAngleOut="-25" overrunDistance="0" layerType="PointGeometry" placement="1" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistanceUnit="MM" rotationAngle="0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2 /**{xfactor}*/, Y($geometry)))" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MapUnit" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" centroidInside="0" geometryGeneratorType="PointGeometry" lineAnchorType="0" offsetType="0" repeatDistanceUnits="MM" yOffset="0" xOffset="0"/>
          <rendering fontMinPixelSize="3" minFeatureSize="0" drawLabels="1" fontMaxPixelSize="10000" obstacleFactor="1" scaleMax="0" maxNumLabels="2000" fontLimitPixelSize="0" scaleVisibility="0" obstacleType="0" displayAll="0" zIndex="0" obstacle="1" upsidedownLabels="0" mergeLines="0" limitNumLabels="0" labelPerPart="0" scaleMin="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="PositionX" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="X($geometry)+2 /**{xfactor}*/"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
                <Option name="PositionY" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="Y($geometry) - &quot;soildepth&quot; /**{yfactor}*/"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
                <Option name="Vali" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="'Half'"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; alpha=&quot;1&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot;>&lt;layer enabled=&quot;1&quot; locked=&quot;0&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
  </labeling>
  <customproperties>
    <property key="dualview/previewExpressions" value="obsid"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory spacing="0" diagramOrientation="Up" minimumSize="0" opacity="1" rotationOffset="270" scaleBasedVisibility="0" backgroundColor="#ffffff" penWidth="0" direction="1" showAxis="0" penColor="#000000" height="15" barWidth="5" minScaleDenominator="0" scaleDependency="Area" enabled="0" maxScaleDenominator="1e+8" backgroundAlpha="255" penAlpha="255" labelPlacementMethod="XHeight" lineSizeScale="3x:0,0,0,0,0,0" width="15" spacingUnitScale="3x:0,0,0,0,0,0" sizeType="MM" spacingUnit="MM" sizeScale="3x:0,0,0,0,0,0" lineSizeType="MM">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" label="" color="#000000"/>
      <axisSymbol>
        <symbol name="" alpha="1" type="line" force_rhr="0" clip_to_extent="1">
          <layer enabled="1" locked="0" class="SimpleLine" pass="0">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings dist="0" priority="0" showAll="1" linePlacementFlags="18" obstacle="0" placement="0" zIndex="0">
    <properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties"/>
        <Option name="type" type="QString" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="rowid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="obsid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_toc" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_gs" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_tocags" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="length" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_syst" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="ground_surface" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="soildepth" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bedrock" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="drillstop" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bedrock_from_table" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" index="0" field="rowid"/>
    <alias name="" index="1" field="obsid"/>
    <alias name="" index="2" field="h_toc"/>
    <alias name="" index="3" field="h_gs"/>
    <alias name="" index="4" field="h_tocags"/>
    <alias name="" index="5" field="length"/>
    <alias name="" index="6" field="h_syst"/>
    <alias name="" index="7" field="ground_surface"/>
    <alias name="" index="8" field="soildepth"/>
    <alias name="" index="9" field="bedrock"/>
    <alias name="" index="10" field="drillstop"/>
    <alias name="" index="11" field="bedrock_from_table"/>
  </aliases>
  <defaults>
    <default field="rowid" applyOnUpdate="0" expression=""/>
    <default field="obsid" applyOnUpdate="0" expression=""/>
    <default field="h_toc" applyOnUpdate="0" expression=""/>
    <default field="h_gs" applyOnUpdate="0" expression=""/>
    <default field="h_tocags" applyOnUpdate="0" expression=""/>
    <default field="length" applyOnUpdate="0" expression=""/>
    <default field="h_syst" applyOnUpdate="0" expression=""/>
    <default field="ground_surface" applyOnUpdate="0" expression=""/>
    <default field="soildepth" applyOnUpdate="0" expression=""/>
    <default field="bedrock" applyOnUpdate="0" expression=""/>
    <default field="drillstop" applyOnUpdate="0" expression=""/>
    <default field="bedrock_from_table" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="rowid" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="obsid" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="h_toc" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="h_gs" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="h_tocags" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="length" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="h_syst" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="ground_surface" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="soildepth" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="bedrock" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="drillstop" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="bedrock_from_table" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="rowid" desc="" exp=""/>
    <constraint field="obsid" desc="" exp=""/>
    <constraint field="h_toc" desc="" exp=""/>
    <constraint field="h_gs" desc="" exp=""/>
    <constraint field="h_tocags" desc="" exp=""/>
    <constraint field="length" desc="" exp=""/>
    <constraint field="h_syst" desc="" exp=""/>
    <constraint field="ground_surface" desc="" exp=""/>
    <constraint field="soildepth" desc="" exp=""/>
    <constraint field="bedrock" desc="" exp=""/>
    <constraint field="drillstop" desc="" exp=""/>
    <constraint field="bedrock_from_table" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="1" sortExpression="&quot;soildepthh&quot;">
    <columns>
      <column name="obsid" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column name="drillstop" type="field" hidden="0" width="276"/>
      <column name="h_toc" type="field" hidden="0" width="-1"/>
      <column name="h_gs" type="field" hidden="0" width="-1"/>
      <column name="h_tocags" type="field" hidden="0" width="-1"/>
      <column name="length" type="field" hidden="0" width="-1"/>
      <column name="h_syst" type="field" hidden="0" width="-1"/>
      <column name="ground_surface" type="field" hidden="0" width="-1"/>
      <column name="bedrock" type="field" hidden="0" width="-1"/>
      <column name="bedrock_from_table" type="field" hidden="0" width="-1"/>
      <column name="soildepth" type="field" hidden="0" width="-1"/>
      <column name="rowid" type="field" hidden="0" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS formulär kan ha en Pythonfunktion som anropas när formuläret öppnas.

Använd denna funktion för att lägga till extra logik till dina formulär.

Skriv in namnet på funktionen i fältet "Python Init function".
Ett exempel nedan:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="bedrock" editable="1"/>
    <field name="bedrock_from_table" editable="1"/>
    <field name="capacity" editable="1"/>
    <field name="comment" editable="1"/>
    <field name="depthbot" editable="1"/>
    <field name="depthtop" editable="1"/>
    <field name="development" editable="1"/>
    <field name="drillstop" editable="1"/>
    <field name="geology" editable="1"/>
    <field name="geoshort" editable="1"/>
    <field name="ground_surface" editable="1"/>
    <field name="h_gs" editable="1"/>
    <field name="h_syst" editable="1"/>
    <field name="h_toc" editable="1"/>
    <field name="h_tocags" editable="1"/>
    <field name="length" editable="1"/>
    <field name="maxdepthbot" editable="1"/>
    <field name="obsid" editable="1"/>
    <field name="rowid" editable="1"/>
    <field name="soildepth" editable="1"/>
    <field name="soildepthh" editable="1"/>
    <field name="stratid" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="bedrock" labelOnTop="0"/>
    <field name="bedrock_from_table" labelOnTop="0"/>
    <field name="capacity" labelOnTop="0"/>
    <field name="comment" labelOnTop="0"/>
    <field name="depthbot" labelOnTop="0"/>
    <field name="depthtop" labelOnTop="0"/>
    <field name="development" labelOnTop="0"/>
    <field name="drillstop" labelOnTop="0"/>
    <field name="geology" labelOnTop="0"/>
    <field name="geoshort" labelOnTop="0"/>
    <field name="ground_surface" labelOnTop="0"/>
    <field name="h_gs" labelOnTop="0"/>
    <field name="h_syst" labelOnTop="0"/>
    <field name="h_toc" labelOnTop="0"/>
    <field name="h_tocags" labelOnTop="0"/>
    <field name="length" labelOnTop="0"/>
    <field name="maxdepthbot" labelOnTop="0"/>
    <field name="obsid" labelOnTop="0"/>
    <field name="rowid" labelOnTop="0"/>
    <field name="soildepth" labelOnTop="0"/>
    <field name="soildepthh" labelOnTop="0"/>
    <field name="stratid" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"obsid"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
