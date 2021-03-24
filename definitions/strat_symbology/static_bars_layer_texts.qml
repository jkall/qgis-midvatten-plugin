<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyMaxScale="1" version="3.16.3-Hannover" labelsEnabled="1" minScale="100000000" simplifyDrawingTol="1" simplifyLocal="1" simplifyAlgorithm="0" readOnly="0" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" maxScale="0" simplifyDrawingHints="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endField="" startExpression="" startField="" mode="0" fixedDuration="0" accumulate="0" enabled="0" endExpression="" durationField="" durationUnit="min">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="nullSymbol"/>
  <labeling type="rule-based">
    <rules key="{3bdc7e0c-a912-48e2-a7d2-1aac3c232814}">
      <rule key="{24db7592-513b-4156-b2a8-c0b13eae6a00}">
        <settings calloutType="simple">
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" textColor="0,0,0,255" textOrientation="horizontal" isExpression="0" fieldName="geology" fontSizeUnit="Point" fontKerning="1" previewBkgrdColor="255,255,255,255" fontSize="6" textOpacity="1" multilineHeight="1" allowHtml="0" fontWeight="50" fontStrikeout="0" useSubstitutions="0" namedStyle="Italic" fontFamily="Noto Sans" blendMode="0" fontWordSpacing="0" fontUnderline="0" fontItalic="1" fontLetterSpacing="0" capitalization="0">
            <text-buffer bufferDraw="1" bufferOpacity="1" bufferJoinStyle="128" bufferNoFill="1" bufferSize="0.5" bufferColor="255,255,255,255" bufferBlendMode="0" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <text-mask maskType="0" maskEnabled="0" maskSize="0" maskedSymbolLayers="" maskOpacity="1" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSizeUnits="MM" maskJoinStyle="128"/>
            <background shapeOffsetX="0" shapeType="0" shapeBorderColor="128,128,128,255" shapeBorderWidth="0" shapeOpacity="1" shapeSizeType="0" shapeSVGFile="" shapeOffsetY="0" shapeFillColor="255,255,255,255" shapeRadiiX="0" shapeOffsetUnit="MM" shapeDraw="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeRotation="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiUnit="MM" shapeSizeUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeRotationType="0" shapeBorderWidthUnit="MM" shapeRadiiY="0" shapeSizeX="0" shapeSizeY="0">
              <symbol force_rhr="0" alpha="1" clip_to_extent="1" type="marker" name="markerSymbol">
                <layer pass="0" locked="0" class="SimpleMarker" enabled="1">
                  <prop v="0" k="angle"/>
                  <prop v="152,125,183,255" k="color"/>
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
                      <Option type="QString" name="name" value=""/>
                      <Option name="properties"/>
                      <Option type="QString" name="type" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowRadius="1.5" shadowOpacity="0.7" shadowUnder="0" shadowOffsetDist="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowColor="0,0,0,255" shadowRadiusUnit="MM" shadowOffsetUnit="MM"/>
            <dd_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format reverseDirectionSymbol="0" placeDirectionSymbol="0" wrapChar="" rightDirectionSymbol=">" decimals="3" autoWrapLength="0" multilineAlign="3" useMaxLineLengthForAutoWrap="1" formatNumbers="0" plussign="0" addDirectionSymbol="0" leftDirectionSymbol="&lt;"/>
          <placement preserveRotation="1" maxCurvedCharAngleIn="25" centroidInside="0" distMapUnitScale="3x:0,0,0,0,0,0" placement="1" polygonPlacementFlags="2" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" rotationAngle="0" xOffset="3" dist="0" centroidWhole="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" lineAnchorPercent="0.5" lineAnchorType="0" layerType="PointGeometry" distUnits="MM" offsetType="0" repeatDistance="0" maxCurvedCharAngleOut="-25" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistanceUnit="MM" geometryGeneratorEnabled="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" geometryGeneratorType="PointGeometry" fitInPolygonOnly="0" offsetUnits="RenderMetersInMapUnits" priority="5" repeatDistanceUnits="MM" yOffset="0" overrunDistance="0" quadOffset="8"/>
          <rendering scaleMin="0" displayAll="1" fontMaxPixelSize="10000" scaleVisibility="0" limitNumLabels="0" obstacle="1" fontLimitPixelSize="0" scaleMax="0" upsidedownLabels="0" maxNumLabels="2000" labelPerPart="0" obstacleType="0" fontMinPixelSize="3" minFeatureSize="0" zIndex="0" mergeLines="0" drawLabels="1" obstacleFactor="1"/>
          <dd_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="Hali">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="expression" value="'Right'"/>
                  <Option type="int" name="type" value="3"/>
                </Option>
                <Option type="Map" name="PositionX">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="expression" value="X($geometry)-2 /**{xfactor}*/"/>
                  <Option type="int" name="type" value="3"/>
                </Option>
                <Option type="Map" name="PositionY">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="expression" value="Y($geometry) -  &quot;depthtop&quot;  /**{yfactor}*/"/>
                  <Option type="int" name="type" value="3"/>
                </Option>
                <Option type="Map" name="Vali">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="expression" value="'Top'"/>
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
              <Option type="QString" name="lineSymbol" value="&lt;symbol force_rhr=&quot;0&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot; type=&quot;line&quot; name=&quot;symbol&quot;>&lt;layer pass=&quot;0&quot; locked=&quot;0&quot; class=&quot;SimpleLine&quot; enabled=&quot;1&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
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
      </rule>
    </rules>
  </labeling>
  <customproperties>
    <property key="dualview/previewExpressions" value="&quot;obsid&quot;"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory backgroundAlpha="255" height="15" direction="1" penWidth="0" penAlpha="255" sizeScale="3x:0,0,0,0,0,0" barWidth="5" width="15" lineSizeType="MM" backgroundColor="#ffffff" spacing="0" opacity="1" diagramOrientation="Up" scaleBasedVisibility="0" enabled="0" showAxis="0" maxScaleDenominator="1e+8" sizeType="MM" minScaleDenominator="0" penColor="#000000" lineSizeScale="3x:0,0,0,0,0,0" spacingUnit="MM" scaleDependency="Area" rotationOffset="270" minimumSize="0" labelPlacementMethod="XHeight" spacingUnitScale="3x:0,0,0,0,0,0">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol force_rhr="0" alpha="1" clip_to_extent="1" type="line" name="">
          <layer pass="0" locked="0" class="SimpleLine" enabled="1">
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
  <DiagramLayerSettings priority="0" placement="0" showAll="1" zIndex="0" obstacle="0" linePlacementFlags="18" dist="0">
    <properties>
      <Option type="Map">
        <Option type="QString" name="name" value=""/>
        <Option name="properties"/>
        <Option type="QString" name="type" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
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
    <field name="maxdepthbot" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="stratid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="depthtop" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="depthbot" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="geology" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="geoshort" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="capacity" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="development" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="comment" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="rowid" index="0" name=""/>
    <alias field="obsid" index="1" name=""/>
    <alias field="maxdepthbot" index="2" name=""/>
    <alias field="stratid" index="3" name=""/>
    <alias field="depthtop" index="4" name=""/>
    <alias field="depthbot" index="5" name=""/>
    <alias field="geology" index="6" name=""/>
    <alias field="geoshort" index="7" name=""/>
    <alias field="capacity" index="8" name=""/>
    <alias field="development" index="9" name=""/>
    <alias field="comment" index="10" name=""/>
  </aliases>
  <defaults>
    <default expression="" field="rowid" applyOnUpdate="0"/>
    <default expression="" field="obsid" applyOnUpdate="0"/>
    <default expression="" field="maxdepthbot" applyOnUpdate="0"/>
    <default expression="" field="stratid" applyOnUpdate="0"/>
    <default expression="" field="depthtop" applyOnUpdate="0"/>
    <default expression="" field="depthbot" applyOnUpdate="0"/>
    <default expression="" field="geology" applyOnUpdate="0"/>
    <default expression="" field="geoshort" applyOnUpdate="0"/>
    <default expression="" field="capacity" applyOnUpdate="0"/>
    <default expression="" field="development" applyOnUpdate="0"/>
    <default expression="" field="comment" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="rowid" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="obsid" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="maxdepthbot" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="stratid" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="depthtop" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="depthbot" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="geology" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="geoshort" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="capacity" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="development" constraints="0"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" field="comment" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="rowid" desc="" exp=""/>
    <constraint field="obsid" desc="" exp=""/>
    <constraint field="maxdepthbot" desc="" exp=""/>
    <constraint field="stratid" desc="" exp=""/>
    <constraint field="depthtop" desc="" exp=""/>
    <constraint field="depthbot" desc="" exp=""/>
    <constraint field="geology" desc="" exp=""/>
    <constraint field="geoshort" desc="" exp=""/>
    <constraint field="capacity" desc="" exp=""/>
    <constraint field="development" desc="" exp=""/>
    <constraint field="comment" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="&quot;stratid&quot;" actionWidgetStyle="dropDown">
    <columns>
      <column hidden="0" type="field" width="-1" name="obsid"/>
      <column hidden="0" type="field" width="-1" name="stratid"/>
      <column hidden="0" type="field" width="-1" name="depthtop"/>
      <column hidden="0" type="field" width="-1" name="depthbot"/>
      <column hidden="0" type="field" width="-1" name="geology"/>
      <column hidden="0" type="field" width="-1" name="geoshort"/>
      <column hidden="0" type="field" width="-1" name="capacity"/>
      <column hidden="0" type="field" width="-1" name="development"/>
      <column hidden="0" type="field" width="-1" name="comment"/>
      <column hidden="1" type="actions" width="-1"/>
      <column hidden="0" type="field" width="-1" name="maxdepthbot"/>
      <column hidden="0" type="field" width="-1" name="rowid"/>
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
    <field editable="1" name="capacity"/>
    <field editable="1" name="comment"/>
    <field editable="1" name="depthbot"/>
    <field editable="1" name="depthtop"/>
    <field editable="1" name="development"/>
    <field editable="1" name="drillstop"/>
    <field editable="1" name="geology"/>
    <field editable="1" name="geoshort"/>
    <field editable="1" name="maxdepthbot"/>
    <field editable="1" name="obsid"/>
    <field editable="1" name="rowid"/>
    <field editable="1" name="stratid"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="capacity"/>
    <field labelOnTop="0" name="comment"/>
    <field labelOnTop="0" name="depthbot"/>
    <field labelOnTop="0" name="depthtop"/>
    <field labelOnTop="0" name="development"/>
    <field labelOnTop="0" name="drillstop"/>
    <field labelOnTop="0" name="geology"/>
    <field labelOnTop="0" name="geoshort"/>
    <field labelOnTop="0" name="maxdepthbot"/>
    <field labelOnTop="0" name="obsid"/>
    <field labelOnTop="0" name="rowid"/>
    <field labelOnTop="0" name="stratid"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"obsid"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
