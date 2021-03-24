<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" hasScaleBasedVisibilityFlag="0" simplifyDrawingTol="1" version="3.16.3-Hannover" simplifyMaxScale="1" minScale="100000000" simplifyLocal="1" maxScale="0" labelsEnabled="1" simplifyDrawingHints="0" styleCategories="AllStyleCategories" simplifyAlgorithm="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal mode="0" durationField="" startField="" startExpression="" enabled="0" endExpression="" durationUnit="min" fixedDuration="0" endField="" accumulate="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="nullSymbol"/>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontFamily="Noto Sans" allowHtml="0" fontSize="8" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontKerning="1" fontWeight="50" textColor="0,0,0,255" blendMode="0" fieldName="round(level_masl, 3)" fontSizeUnit="Point" capitalization="0" isExpression="1" fontUnderline="0" fontWordSpacing="0" textOrientation="horizontal" useSubstitutions="0" fontItalic="0" multilineHeight="1" textOpacity="1" previewBkgrdColor="255,255,255,255" namedStyle="Regular" fontStrikeout="0" fontLetterSpacing="0">
        <text-buffer bufferColor="149,149,255,255" bufferOpacity="1" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferDraw="1" bufferSize="0.5" bufferNoFill="1" bufferBlendMode="0" bufferSizeUnits="MM"/>
        <text-mask maskSize="0" maskSizeUnits="MM" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskEnabled="0" maskOpacity="1" maskedSymbolLayers="" maskType="0"/>
        <background shapeDraw="0" shapeSizeUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeOffsetX="0" shapeRadiiX="0" shapeSVGFile="" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRotationType="0" shapeBorderWidthUnit="MM" shapeBorderWidth="0" shapeOffsetY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiUnit="MM" shapeBorderColor="128,128,128,255" shapeSizeY="0" shapeFillColor="255,255,255,255" shapeSizeType="0" shapeBlendMode="0" shapeRadiiY="0" shapeJoinStyle="64" shapeOpacity="1" shapeOffsetUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0">
          <symbol type="marker" name="markerSymbol" alpha="1" force_rhr="0" clip_to_extent="1">
            <layer class="SimpleMarker" locked="0" enabled="1" pass="0">
              <prop k="angle" v="0"/>
              <prop k="color" v="255,158,23,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="2"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowRadiusUnit="MM" shadowOffsetAngle="135" shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowUnder="0" shadowBlendMode="6" shadowDraw="0" shadowScale="100" shadowOpacity="0.7" shadowOffsetGlobal="1" shadowOffsetUnit="MM" shadowOffsetDist="1" shadowRadius="1.5" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format placeDirectionSymbol="0" addDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" reverseDirectionSymbol="0" wrapChar="" multilineAlign="3" rightDirectionSymbol=">" plussign="0" autoWrapLength="0" leftDirectionSymbol="&lt;" decimals="3" formatNumbers="0"/>
      <placement polygonPlacementFlags="2" centroidInside="0" layerType="PointGeometry" distMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" lineAnchorType="0" placement="1" offsetUnits="MapUnit" dist="0" rotationAngle="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" distUnits="MM" centroidWhole="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" geometryGeneratorType="PointGeometry" repeatDistanceUnits="MM" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" yOffset="0" offsetType="0" repeatDistance="0" geometryGeneratorEnabled="0" placementFlags="10" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2 /**{xfactor}*/, Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;) /**{yfactor}*/))" quadOffset="2" xOffset="0" maxCurvedCharAngleOut="-25" lineAnchorPercent="0.5" preserveRotation="1" priority="5" overrunDistanceUnit="MM" fitInPolygonOnly="0"/>
      <rendering minFeatureSize="0" displayAll="1" obstacle="1" upsidedownLabels="0" maxNumLabels="2000" mergeLines="0" fontMaxPixelSize="10000" scaleMin="0" drawLabels="1" obstacleType="0" limitNumLabels="0" scaleVisibility="0" obstacleFactor="1" fontLimitPixelSize="0" scaleMax="0" labelPerPart="0" fontMinPixelSize="3" zIndex="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option type="Map" name="properties">
            <Option type="Map" name="Italic">
              <Option type="bool" name="active" value="true"/>
              <Option type="QString" name="expression" value="1"/>
              <Option type="int" name="type" value="3"/>
            </Option>
            <Option type="Map" name="OffsetXY">
              <Option type="bool" name="active" value="false"/>
              <Option type="int" name="type" value="1"/>
              <Option type="QString" name="val" value=""/>
            </Option>
            <Option type="Map" name="PositionX">
              <Option type="bool" name="active" value="true"/>
              <Option type="QString" name="expression" value="X($geometry)+2 /**{xfactor}*/"/>
              <Option type="int" name="type" value="3"/>
            </Option>
            <Option type="Map" name="PositionY">
              <Option type="bool" name="active" value="true"/>
              <Option type="QString" name="expression" value="Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;) /**{yfactor}*/"/>
              <Option type="int" name="type" value="3"/>
            </Option>
          </Option>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" name="anchorPoint" value="pole_of_inaccessibility"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
          <Option type="bool" name="drawToAllParts" value="false"/>
          <Option type="QString" name="enabled" value="0"/>
          <Option type="QString" name="labelAnchorPoint" value="point_on_exterior"/>
          <Option type="QString" name="lineSymbol" value="&lt;symbol type=&quot;line&quot; name=&quot;symbol&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; locked=&quot;0&quot; enabled=&quot;1&quot; pass=&quot;0&quot;>&lt;prop k=&quot;align_dash_pattern&quot; v=&quot;0&quot;/>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;dash_pattern_offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;dash_pattern_offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;dash_pattern_offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;tweak_dash_pattern_on_corners&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
          <Option type="double" name="minLength" value="0"/>
          <Option type="QString" name="minLengthMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="minLengthUnit" value="MM"/>
          <Option type="double" name="offsetFromAnchor" value="0"/>
          <Option type="QString" name="offsetFromAnchorMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromAnchorUnit" value="MM"/>
          <Option type="double" name="offsetFromLabel" value="0"/>
          <Option type="QString" name="offsetFromLabelMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromLabelUnit" value="MM"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <customproperties>
    <property key="dualview/previewExpressions">
      <value>rowid</value>
      <value>"rowid"</value>
    </property>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory spacing="0" opacity="1" penWidth="0" lineSizeType="MM" backgroundAlpha="255" direction="1" enabled="0" labelPlacementMethod="XHeight" spacingUnitScale="3x:0,0,0,0,0,0" backgroundColor="#ffffff" lineSizeScale="3x:0,0,0,0,0,0" width="15" sizeScale="3x:0,0,0,0,0,0" spacingUnit="MM" penColor="#000000" scaleDependency="Area" barWidth="5" scaleBasedVisibility="0" showAxis="0" height="15" diagramOrientation="Up" maxScaleDenominator="1e+8" minScaleDenominator="0" minimumSize="0" rotationOffset="270" penAlpha="255" sizeType="MM">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute label="" field="" color="#000000"/>
      <axisSymbol>
        <symbol type="line" name="" alpha="1" force_rhr="0" clip_to_extent="1">
          <layer class="SimpleLine" locked="0" enabled="1" pass="0">
            <prop k="align_dash_pattern" v="0"/>
            <prop k="capstyle" v="square"/>
            <prop k="customdash" v="5;2"/>
            <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="customdash_unit" v="MM"/>
            <prop k="dash_pattern_offset" v="0"/>
            <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="dash_pattern_offset_unit" v="MM"/>
            <prop k="draw_inside_polygon" v="0"/>
            <prop k="joinstyle" v="bevel"/>
            <prop k="line_color" v="35,35,35,255"/>
            <prop k="line_style" v="solid"/>
            <prop k="line_width" v="0.26"/>
            <prop k="line_width_unit" v="MM"/>
            <prop k="offset" v="0"/>
            <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="offset_unit" v="MM"/>
            <prop k="ring_filter" v="0"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" obstacle="0" zIndex="0" dist="0" linePlacementFlags="18" priority="0" placement="0">
    <properties>
      <Option type="Map">
        <Option type="QString" name="name" value=""/>
        <Option name="properties"/>
        <Option type="QString" name="type" value="collection"/>
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
    <field name="date_time" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="meas" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="level_masl" configurationFlags="None">
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
  </fieldConfiguration>
  <aliases>
    <alias name="" field="rowid" index="0"/>
    <alias name="" field="obsid" index="1"/>
    <alias name="" field="date_time" index="2"/>
    <alias name="" field="meas" index="3"/>
    <alias name="" field="level_masl" index="4"/>
    <alias name="" field="h_tocags" index="5"/>
  </aliases>
  <defaults>
    <default field="rowid" expression="" applyOnUpdate="0"/>
    <default field="obsid" expression="" applyOnUpdate="0"/>
    <default field="date_time" expression="" applyOnUpdate="0"/>
    <default field="meas" expression="" applyOnUpdate="0"/>
    <default field="level_masl" expression="" applyOnUpdate="0"/>
    <default field="h_tocags" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" field="rowid" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint notnull_strength="0" field="obsid" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint notnull_strength="0" field="date_time" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint notnull_strength="0" field="meas" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint notnull_strength="0" field="level_masl" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint notnull_strength="0" field="h_tocags" exp_strength="0" unique_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="rowid" desc="" exp=""/>
    <constraint field="obsid" desc="" exp=""/>
    <constraint field="date_time" desc="" exp=""/>
    <constraint field="meas" desc="" exp=""/>
    <constraint field="level_masl" desc="" exp=""/>
    <constraint field="h_tocags" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="">
    <columns>
      <column type="field" name="rowid" hidden="0" width="-1"/>
      <column type="field" name="obsid" hidden="0" width="-1"/>
      <column type="field" name="date_time" hidden="0" width="-1"/>
      <column type="field" name="meas" hidden="0" width="-1"/>
      <column type="field" name="level_masl" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" name="h_tocags" hidden="0" width="-1"/>
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
    <field editable="1" name="date_time"/>
    <field editable="1" name="h_tocags"/>
    <field editable="1" name="level_masl"/>
    <field editable="1" name="meas"/>
    <field editable="1" name="obsid"/>
    <field editable="1" name="rowid"/>
  </editable>
  <labelOnTop>
    <field name="date_time" labelOnTop="0"/>
    <field name="h_tocags" labelOnTop="0"/>
    <field name="level_masl" labelOnTop="0"/>
    <field name="meas" labelOnTop="0"/>
    <field name="obsid" labelOnTop="0"/>
    <field name="rowid" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"rowid"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
