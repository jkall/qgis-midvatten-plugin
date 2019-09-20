<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.8.3-Zanzibar" simplifyDrawingTol="1" minScale="1e+8" simplifyDrawingHints="0" simplifyLocal="1" simplifyAlgorithm="0" hasScaleBasedVisibilityFlag="0" readOnly="0" simplifyMaxScale="1" maxScale="0" labelsEnabled="1" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="0" forceraster="0" type="singleSymbol" symbollevels="0">
    <symbols>
      <symbol alpha="1" type="marker" name="0" force_rhr="0" clip_to_extent="1">
        <layer class="GeometryGenerator" locked="0" enabled="1" pass="0">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4)', &#xa;X($geometry)-3, Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;, &#xa;X($geometry)+3, Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" type="line" name="@0@0" force_rhr="0" clip_to_extent="1">
            <layer class="SimpleLine" locked="0" enabled="1" pass="0">
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
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
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
      <text-style textColor="0,0,0,255" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fieldName="round(level_masl, 3)" isExpression="1" previewBkgrdColor="#ffffff" fontSizeUnit="Point" fontLetterSpacing="0" fontItalic="0" blendMode="0" fontWordSpacing="0" fontUnderline="0" useSubstitutions="0" multilineHeight="1" fontSize="8" textOpacity="1" fontWeight="50" fontCapitals="0" fontFamily="Noto Sans" namedStyle="Regular" fontStrikeout="0">
        <text-buffer bufferSize="0.5" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferJoinStyle="128" bufferNoFill="1" bufferDraw="1" bufferColor="149,149,255,255" bufferBlendMode="0" bufferSizeUnits="MM"/>
        <background shapeBorderColor="128,128,128,255" shapeOpacity="1" shapeRadiiY="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeSVGFile="" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidth="0" shapeSizeX="0" shapeJoinStyle="64" shapeBlendMode="0" shapeSizeY="0" shapeRadiiX="0" shapeRadiiUnit="MM" shapeOffsetX="0" shapeFillColor="255,255,255,255" shapeSizeUnit="MM" shapeRotationType="0" shapeOffsetUnit="MM" shapeSizeType="0" shapeBorderWidthUnit="MM" shapeType="0" shapeDraw="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0"/>
        <shadow shadowOffsetUnit="MM" shadowRadiusAlphaOnly="0" shadowDraw="0" shadowUnder="0" shadowOffsetGlobal="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOpacity="0.7" shadowOffsetDist="1" shadowOffsetAngle="135" shadowBlendMode="6" shadowRadiusUnit="MM" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5" shadowColor="0,0,0,255"/>
        <substitutions/>
      </text-style>
      <text-format placeDirectionSymbol="0" addDirectionSymbol="0" plussign="0" useMaxLineLengthForAutoWrap="1" formatNumbers="0" multilineAlign="3" reverseDirectionSymbol="0" decimals="3" wrapChar="" leftDirectionSymbol="&lt;" rightDirectionSymbol=">" autoWrapLength="0"/>
      <placement rotationAngle="0" centroidInside="0" offsetType="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" fitInPolygonOnly="0" offsetUnits="RenderMetersInMapUnits" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" geometryGeneratorEnabled="1" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" distUnits="MM" maxCurvedCharAngleIn="25" distMapUnitScale="3x:0,0,0,0,0,0" xOffset="3" dist="0" quadOffset="2" maxCurvedCharAngleOut="-25" geometryGeneratorType="PointGeometry" centroidWhole="0" placementFlags="10" placement="1" repeatDistance="0" priority="5" repeatDistanceUnits="MM" preserveRotation="1" yOffset="0"/>
      <rendering fontLimitPixelSize="0" labelPerPart="0" scaleMax="0" zIndex="0" displayAll="1" maxNumLabels="2000" scaleMin="0" upsidedownLabels="0" minFeatureSize="0" scaleVisibility="0" fontMaxPixelSize="10000" mergeLines="0" drawLabels="1" limitNumLabels="0" obstacleFactor="1" obstacle="1" fontMinPixelSize="3" obstacleType="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" type="QString" name="name"/>
          <Option name="properties"/>
          <Option value="collection" type="QString" name="type"/>
        </Option>
      </dd_properties>
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
    <DiagramCategory opacity="1" minScaleDenominator="0" minimumSize="0" rotationOffset="270" penColor="#000000" diagramOrientation="Up" maxScaleDenominator="1e+8" backgroundAlpha="255" height="15" scaleBasedVisibility="0" lineSizeType="MM" scaleDependency="Area" lineSizeScale="3x:0,0,0,0,0,0" backgroundColor="#ffffff" labelPlacementMethod="XHeight" width="15" enabled="0" sizeScale="3x:0,0,0,0,0,0" penAlpha="255" sizeType="MM" penWidth="0" barWidth="5">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" label="" color="#000000"/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" showAll="1" dist="0" zIndex="0" placement="0" priority="0" obstacle="0">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
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
    <alias index="0" field="rowid" name=""/>
    <alias index="1" field="obsid" name=""/>
    <alias index="2" field="date_time" name=""/>
    <alias index="3" field="meas" name=""/>
    <alias index="4" field="level_masl" name=""/>
    <alias index="5" field="h_tocags" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="rowid" applyOnUpdate="0"/>
    <default expression="" field="obsid" applyOnUpdate="0"/>
    <default expression="" field="date_time" applyOnUpdate="0"/>
    <default expression="" field="meas" applyOnUpdate="0"/>
    <default expression="" field="level_masl" applyOnUpdate="0"/>
    <default expression="" field="h_tocags" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" notnull_strength="0" field="rowid" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="obsid" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="date_time" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="meas" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="level_masl" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="h_tocags" constraints="0" exp_strength="0"/>
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
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="">
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
    <field labelOnTop="0" name="date_time"/>
    <field labelOnTop="0" name="h_tocags"/>
    <field labelOnTop="0" name="level_masl"/>
    <field labelOnTop="0" name="meas"/>
    <field labelOnTop="0" name="obsid"/>
    <field labelOnTop="0" name="rowid"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>rowid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
