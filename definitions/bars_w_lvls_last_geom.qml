<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.8.3-Zanzibar" hasScaleBasedVisibilityFlag="0" simplifyDrawingHints="0" simplifyMaxScale="1" readOnly="0" simplifyDrawingTol="1" labelsEnabled="1" minScale="1e+8" styleCategories="AllStyleCategories" simplifyAlgorithm="0" maxScale="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 type="singleSymbol" forceraster="0" enableorderby="0" symbollevels="0">
    <symbols>
      <symbol force_rhr="0" clip_to_extent="1" type="marker" name="0" alpha="1">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4)', &#xa;X($geometry)-2*0.001*@map_scale, Y($geometry) - &quot;meas&quot;*0.001*@map_scale + &quot;h_tocags&quot;*0.001*@map_scale, &#xa;X($geometry)+2*0.001*@map_scale, Y($geometry) - &quot;meas&quot;*0.001*@map_scale + &quot;h_tocags&quot;*0.001*@map_scale))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" clip_to_extent="1" type="line" name="@0@0" alpha="1">
            <layer class="SimpleLine" enabled="1" locked="0" pass="0">
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="0,0,255,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.46"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
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
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontSizeUnit="Point" fontStrikeout="0" isExpression="1" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" fieldName="round(level_masl, 3)" blendMode="0" fontItalic="0" fontCapitals="0" fontWordSpacing="0" namedStyle="Regular" fontWeight="50" fontSize="8" textColor="0,0,0,255" previewBkgrdColor="#ffffff" fontFamily="Noto Sans" fontUnderline="0" useSubstitutions="0" textOpacity="1" multilineHeight="1">
        <text-buffer bufferColor="149,149,255,255" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferSize="0.5" bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="1" bufferOpacity="1"/>
        <background shapeSizeY="0" shapeOffsetY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeRadiiY="0" shapeRadiiX="0" shapeOffsetX="0" shapeOpacity="1" shapeSVGFile="" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeSizeType="0" shapeBorderWidthUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetUnit="MM" shapeRadiiUnit="MM" shapeBlendMode="0" shapeBorderWidth="0" shapeDraw="0" shapeFillColor="255,255,255,255" shapeBorderColor="128,128,128,255" shapeJoinStyle="64" shapeRotationType="0"/>
        <shadow shadowRadiusAlphaOnly="0" shadowDraw="0" shadowOffsetDist="1" shadowBlendMode="6" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowScale="100" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadius="1.5"/>
        <substitutions/>
      </text-style>
      <text-format formatNumbers="0" plussign="0" multilineAlign="3" autoWrapLength="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0" leftDirectionSymbol="&lt;" wrapChar="" decimals="3" reverseDirectionSymbol="0" useMaxLineLengthForAutoWrap="1"/>
      <placement repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" xOffset="2" maxCurvedCharAngleIn="25" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot;*0.001*@map_scale + &quot;h_tocags&quot;*0.001*@map_scale))" fitInPolygonOnly="0" distUnits="MM" placement="1" centroidInside="0" repeatDistanceUnits="MM" geometryGeneratorEnabled="1" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" centroidWhole="0" preserveRotation="1" dist="0" offsetType="0" priority="5" geometryGeneratorType="PointGeometry" offsetUnits="MM" rotationAngle="0" distMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" maxCurvedCharAngleOut="-25" yOffset="0" quadOffset="2"/>
      <rendering fontMinPixelSize="3" scaleMin="0" scaleMax="0" drawLabels="1" zIndex="0" obstacleType="0" upsidedownLabels="0" scaleVisibility="0" obstacleFactor="1" maxNumLabels="2000" fontLimitPixelSize="0" labelPerPart="0" mergeLines="0" obstacle="1" fontMaxPixelSize="10000" displayAll="1" limitNumLabels="0" minFeatureSize="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
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
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory scaleBasedVisibility="0" width="15" backgroundColor="#ffffff" lineSizeScale="3x:0,0,0,0,0,0" sizeScale="3x:0,0,0,0,0,0" sizeType="MM" labelPlacementMethod="XHeight" height="15" penWidth="0" opacity="1" penAlpha="255" backgroundAlpha="255" diagramOrientation="Up" minimumSize="0" minScaleDenominator="0" barWidth="5" penColor="#000000" scaleDependency="Area" enabled="0" maxScaleDenominator="1e+8" lineSizeType="MM" rotationOffset="270">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" field="" label=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings priority="0" zIndex="0" obstacle="0" showAll="1" dist="0" linePlacementFlags="18" placement="0">
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
  <fieldConfiguration>
    <field name="rowid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="obsid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="date_time">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="meas">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="level_masl">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_tocags">
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
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="rowid"/>
    <default expression="" applyOnUpdate="0" field="obsid"/>
    <default expression="" applyOnUpdate="0" field="date_time"/>
    <default expression="" applyOnUpdate="0" field="meas"/>
    <default expression="" applyOnUpdate="0" field="level_masl"/>
    <default expression="" applyOnUpdate="0" field="h_tocags"/>
  </defaults>
  <constraints>
    <constraint constraints="0" exp_strength="0" field="rowid" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="obsid" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="date_time" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="meas" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="level_masl" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="h_tocags" notnull_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="rowid" exp=""/>
    <constraint desc="" field="obsid" exp=""/>
    <constraint desc="" field="date_time" exp=""/>
    <constraint desc="" field="meas" exp=""/>
    <constraint desc="" field="level_masl" exp=""/>
    <constraint desc="" field="h_tocags" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" hidden="0" type="field" name="rowid"/>
      <column width="-1" hidden="0" type="field" name="obsid"/>
      <column width="-1" hidden="0" type="field" name="date_time"/>
      <column width="-1" hidden="0" type="field" name="meas"/>
      <column width="-1" hidden="0" type="field" name="level_masl"/>
      <column width="-1" hidden="1" type="actions"/>
      <column width="-1" hidden="0" type="field" name="h_tocags"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
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
  <widgets/>
  <previewExpression>rowid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
