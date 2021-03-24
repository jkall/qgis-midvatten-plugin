<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" simplifyDrawingTol="1" simplifyLocal="1" minScale="100000000" hasScaleBasedVisibilityFlag="0" readOnly="0" styleCategories="AllStyleCategories" simplifyAlgorithm="0" simplifyMaxScale="1" labelsEnabled="0" simplifyDrawingHints="0" version="3.16.3-Hannover">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal durationField="" enabled="0" endField="" durationUnit="min" startField="" accumulate="0" startExpression="" mode="0" fixedDuration="0" endExpression="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="singleSymbol" forceraster="0" enableorderby="0" symbollevels="0">
    <symbols>
      <symbol type="marker" clip_to_extent="1" name="0" alpha="1" force_rhr="0">
        <layer enabled="1" class="GeometryGenerator" locked="0" pass="0">
          <prop v="Line" k="SymbolType"/>
          <prop v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4)', &#xa;X($geometry)-2 /**{map_scale}*/  /**{xfactor}*/, Y($geometry) - (&quot;meas&quot; /**{map_scale}*/ - &quot;h_tocags&quot; /**{map_scale}*/ /**{yfactor}*/, &#xa;X($geometry)+2 /**{map_scale}*/  /**{xfactor}*/, Y($geometry) - (&quot;meas&quot; /**{map_scale}*/ - &quot;h_tocags&quot; /**{map_scale}*/ /**{yfactor}*/))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="line" clip_to_extent="1" name="@0@0" alpha="1" force_rhr="0">
            <layer enabled="1" class="SimpleLine" locked="0" pass="0">
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
              <prop v="0,0,255,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="0.46" k="line_width"/>
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
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontSizeUnit="Point" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontFamily="Noto Sans" fontLetterSpacing="0" useSubstitutions="0" textOrientation="horizontal" previewBkgrdColor="255,255,255,255" fontWeight="50" fontItalic="0" fontWordSpacing="0" fieldName="round(level_masl, 3)" multilineHeight="1" fontKerning="1" isExpression="1" namedStyle="" fontUnderline="0" fontSize="8" textColor="0,0,0,255" textOpacity="1" blendMode="0" fontStrikeout="0" allowHtml="0" capitalization="0">
        <text-buffer bufferJoinStyle="128" bufferBlendMode="0" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="149,149,255,255" bufferSize="0.5" bufferDraw="1" bufferNoFill="1" bufferOpacity="1"/>
        <text-mask maskJoinStyle="128" maskOpacity="1" maskSizeUnits="MM" maskEnabled="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskType="0" maskSize="0" maskedSymbolLayers=""/>
        <background shapeSizeY="0" shapeBorderColor="128,128,128,255" shapeOffsetY="0" shapeBlendMode="0" shapeOffsetUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeSizeX="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeRadiiUnit="MM" shapeBorderWidth="0" shapeSizeType="0" shapeOpacity="1" shapeFillColor="255,255,255,255" shapeSizeUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeSVGFile="" shapeType="0" shapeRadiiX="0" shapeRotation="0" shapeRotationType="0"/>
        <shadow shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowBlendMode="6" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowOffsetUnit="MM" shadowOffsetDist="1" shadowScale="100" shadowOffsetAngle="135" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowUnder="0" shadowDraw="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5"/>
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
                <Option type="QString" name="expression" value="X($geometry)+2/**{map_scale}*/ /**{xfactor}*/"/>
                <Option type="int" name="type" value="3"/>
              </Option>
              <Option type="Map" name="PositionY">
                <Option type="bool" name="active" value="true"/>
                <Option type="QString" name="expression" value="Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;)/**{map_scale}*/ /**{yfactor}*/"/>
                <Option type="int" name="type" value="3"/>
              </Option>
            </Option>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" reverseDirectionSymbol="0" autoWrapLength="0" wrapChar="" rightDirectionSymbol=">" placeDirectionSymbol="0" decimals="3" formatNumbers="0" multilineAlign="3" leftDirectionSymbol="&lt;" plussign="0"/>
      <placement labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" quadOffset="2" priority="5" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2/**{map_scale}*/ /**{xfactor}*/, Y($geometry) - (&quot;meas&quot;/**{map_scale}*/ - &quot;h_tocags&quot;/**{map_scale}*/) /**{yfactor}*/))&#xa;" centroidWhole="0" preserveRotation="1" overrunDistanceUnit="MM" maxCurvedCharAngleOut="-25" placementFlags="10" maxCurvedCharAngleIn="25" lineAnchorPercent="0.5" repeatDistance="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" layerType="UnknownGeometry" yOffset="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" placement="1" rotationAngle="0" polygonPlacementFlags="2" overrunDistance="0" lineAnchorType="0" geometryGeneratorType="PointGeometry" fitInPolygonOnly="0" centroidInside="0" dist="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" offsetUnits="MM" xOffset="0" repeatDistanceUnits="MM" distUnits="MM"/>
      <rendering displayAll="1" minFeatureSize="0" zIndex="0" mergeLines="0" upsidedownLabels="0" fontLimitPixelSize="0" scaleMax="0" obstacle="1" fontMinPixelSize="3" scaleVisibility="0" fontMaxPixelSize="10000" limitNumLabels="0" obstacleType="0" scaleMin="0" labelPerPart="0" maxNumLabels="2000" drawLabels="1" obstacleFactor="1"/>
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
              <Option type="QString" name="expression" value="X($geometry)+2/**{map_scale}*/ * 1.0"/>
              <Option type="int" name="type" value="3"/>
            </Option>
            <Option type="Map" name="PositionY">
              <Option type="bool" name="active" value="true"/>
              <Option type="QString" name="expression" value="Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;)/**{map_scale}*/ * 1.0"/>
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
          <Option type="QString" name="lineSymbol" value="&lt;symbol type=&quot;line&quot; clip_to_extent=&quot;1&quot; name=&quot;symbol&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot;>&lt;layer enabled=&quot;1&quot; class=&quot;SimpleLine&quot; locked=&quot;0&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
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
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory scaleDependency="Area" diagramOrientation="Up" lineSizeScale="3x:0,0,0,0,0,0" spacingUnitScale="3x:0,0,0,0,0,0" penWidth="0" direction="1" scaleBasedVisibility="0" sizeType="MM" rotationOffset="270" sizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" minScaleDenominator="0" enabled="0" opacity="1" spacingUnit="MM" spacing="0" backgroundAlpha="255" penAlpha="255" lineSizeType="MM" width="15" penColor="#000000" backgroundColor="#ffffff" maxScaleDenominator="1e+8" height="15" showAxis="0" barWidth="5" minimumSize="0">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol type="line" clip_to_extent="1" name="" alpha="1" force_rhr="0">
          <layer enabled="1" class="SimpleLine" locked="0" pass="0">
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
  <DiagramLayerSettings showAll="1" priority="0" zIndex="0" linePlacementFlags="18" dist="0" obstacle="0" placement="0">
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
    <alias field="rowid" name="" index="0"/>
    <alias field="obsid" name="" index="1"/>
    <alias field="date_time" name="" index="2"/>
    <alias field="meas" name="" index="3"/>
    <alias field="level_masl" name="" index="4"/>
    <alias field="h_tocags" name="" index="5"/>
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
    <constraint field="rowid" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="obsid" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="date_time" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="meas" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="level_masl" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="h_tocags" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="rowid" exp="" desc=""/>
    <constraint field="obsid" exp="" desc=""/>
    <constraint field="date_time" exp="" desc=""/>
    <constraint field="meas" exp="" desc=""/>
    <constraint field="level_masl" exp="" desc=""/>
    <constraint field="h_tocags" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" hidden="0" name="rowid" width="-1"/>
      <column type="field" hidden="0" name="obsid" width="-1"/>
      <column type="field" hidden="0" name="date_time" width="-1"/>
      <column type="field" hidden="0" name="meas" width="-1"/>
      <column type="field" hidden="0" name="level_masl" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" hidden="0" name="h_tocags" width="-1"/>
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
    <field name="date_time" editable="1"/>
    <field name="h_tocags" editable="1"/>
    <field name="level_masl" editable="1"/>
    <field name="meas" editable="1"/>
    <field name="obsid" editable="1"/>
    <field name="rowid" editable="1"/>
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
