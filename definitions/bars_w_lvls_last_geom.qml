<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" labelsEnabled="1" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories" simplifyDrawingHints="0" version="3.8.3-Zanzibar" minScale="1e+8" simplifyDrawingTol="1" simplifyLocal="1" readOnly="0" simplifyAlgorithm="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" forceraster="0" type="singleSymbol" enableorderby="0">
    <symbols>
      <symbol alpha="1" force_rhr="0" name="0" clip_to_extent="1" type="marker">
        <layer enabled="1" locked="0" class="GeometryGenerator" pass="0">
          <prop v="Line" k="SymbolType"/>
          <prop v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4)', &#xa;X($geometry)-2*0.001*@map_scale  /**{xfactor}*/, Y($geometry) - (&quot;meas&quot;*0.001*@map_scale - &quot;h_tocags&quot;*0.001*@map_scale) /**{yfactor}*/, &#xa;X($geometry)+2*0.001*@map_scale  /**{xfactor}*/, Y($geometry) - (&quot;meas&quot;*0.001*@map_scale - &quot;h_tocags&quot;*0.001*@map_scale) /**{yfactor}*/))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" force_rhr="0" name="@0@0" clip_to_extent="1" type="line">
            <layer enabled="1" locked="0" class="SimpleLine" pass="0">
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
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
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
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
      <text-style blendMode="0" fontStrikeout="0" multilineHeight="1" isExpression="1" fontSizeUnit="Point" fontSizeMapUnitScale="3x:0,0,0,0,0,0" useSubstitutions="0" fieldName="round(level_masl, 3)" fontUnderline="0" textColor="0,0,0,255" previewBkgrdColor="#ffffff" fontLetterSpacing="0" fontCapitals="0" namedStyle="" fontWeight="50" textOpacity="1" fontFamily="Noto Sans" fontItalic="0" fontWordSpacing="0" fontSize="8">
        <text-buffer bufferBlendMode="0" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferSize="0.5" bufferOpacity="1" bufferDraw="1" bufferJoinStyle="128" bufferNoFill="1" bufferColor="149,149,255,255"/>
        <background shapeSizeUnit="MM" shapeBorderWidthUnit="MM" shapeFillColor="255,255,255,255" shapeOffsetY="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeRadiiUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRadiiY="0" shapeOffsetUnit="MM" shapeBorderColor="128,128,128,255" shapeJoinStyle="64" shapeSizeY="0" shapeRotation="0" shapeSVGFile="" shapeBorderWidth="0" shapeOpacity="1" shapeRadiiX="0" shapeBlendMode="0" shapeType="0" shapeRotationType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0"/>
        <shadow shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowDraw="0" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowOffsetGlobal="1" shadowColor="0,0,0,255" shadowOffsetUnit="MM" shadowOffsetDist="1" shadowRadius="1.5" shadowRadiusAlphaOnly="0" shadowScale="100"/>
        <substitutions/>
      </text-style>
      <text-format addDirectionSymbol="0" formatNumbers="0" reverseDirectionSymbol="0" autoWrapLength="0" multilineAlign="3" wrapChar="" rightDirectionSymbol=">" plussign="0" useMaxLineLengthForAutoWrap="1" placeDirectionSymbol="0" decimals="3" leftDirectionSymbol="&lt;"/>
      <placement placement="1" repeatDistance="0" dist="0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2*0.001*@map_scale /**{xfactor}*/, Y($geometry) - (&quot;meas&quot;*0.001*@map_scale - &quot;h_tocags&quot;*0.001*@map_scale) /**{yfactor}*/))&#xa;" offsetUnits="MM" xOffset="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" distMapUnitScale="3x:0,0,0,0,0,0" fitInPolygonOnly="0" geometryGeneratorType="PointGeometry" distUnits="MM" centroidInside="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" quadOffset="2" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maxCurvedCharAngleIn="25" maxCurvedCharAngleOut="-25" offsetType="0" preserveRotation="1" repeatDistanceUnits="MM" priority="5" centroidWhole="0" yOffset="0" placementFlags="10"/>
      <rendering drawLabels="1" labelPerPart="0" fontMaxPixelSize="10000" maxNumLabels="2000" upsidedownLabels="0" mergeLines="0" displayAll="1" obstacleType="0" limitNumLabels="0" fontLimitPixelSize="0" minFeatureSize="0" zIndex="0" obstacleFactor="1" scaleMax="0" scaleVisibility="0" fontMinPixelSize="3" scaleMin="0" obstacle="1"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties" type="Map">
            <Option name="Italic" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="1" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
            <Option name="OffsetXY" type="Map">
              <Option value="false" name="active" type="bool"/>
              <Option value="1" name="type" type="int"/>
              <Option value="" name="val" type="QString"/>
            </Option>
            <Option name="PositionX" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="X($geometry)+2*0.001*@map_scale /**{xfactor}*/" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
            <Option name="PositionY" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;)*0.001*@map_scale /**{yfactor}*/" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
          </Option>
          <Option value="collection" name="type" type="QString"/>
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
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory height="15" labelPlacementMethod="XHeight" sizeScale="3x:0,0,0,0,0,0" rotationOffset="270" backgroundColor="#ffffff" lineSizeScale="3x:0,0,0,0,0,0" penAlpha="255" penColor="#000000" penWidth="0" scaleDependency="Area" barWidth="5" minScaleDenominator="0" minimumSize="0" opacity="1" enabled="0" lineSizeType="MM" diagramOrientation="Up" sizeType="MM" backgroundAlpha="255" width="15" scaleBasedVisibility="0" maxScaleDenominator="1e+8">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute color="#000000" field="" label=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings priority="0" zIndex="0" dist="0" linePlacementFlags="18" placement="0" showAll="1" obstacle="0">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
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
    <alias index="0" name="" field="rowid"/>
    <alias index="1" name="" field="obsid"/>
    <alias index="2" name="" field="date_time"/>
    <alias index="3" name="" field="meas"/>
    <alias index="4" name="" field="level_masl"/>
    <alias index="5" name="" field="h_tocags"/>
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
    <constraint notnull_strength="0" field="rowid" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" field="obsid" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" field="date_time" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" field="meas" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" field="level_masl" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" field="h_tocags" constraints="0" unique_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="rowid" desc=""/>
    <constraint exp="" field="obsid" desc=""/>
    <constraint exp="" field="date_time" desc=""/>
    <constraint exp="" field="meas" desc=""/>
    <constraint exp="" field="level_masl" desc=""/>
    <constraint exp="" field="h_tocags" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column name="rowid" hidden="0" type="field" width="-1"/>
      <column name="obsid" hidden="0" type="field" width="-1"/>
      <column name="date_time" hidden="0" type="field" width="-1"/>
      <column name="meas" hidden="0" type="field" width="-1"/>
      <column name="level_masl" hidden="0" type="field" width="-1"/>
      <column hidden="1" type="actions" width="-1"/>
      <column name="h_tocags" hidden="0" type="field" width="-1"/>
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
