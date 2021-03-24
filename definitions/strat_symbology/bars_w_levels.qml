<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis minScale="100000000" simplifyDrawingHints="0" simplifyAlgorithm="0" readOnly="0" simplifyDrawingTol="1" maxScale="0" styleCategories="AllStyleCategories" version="3.16.3-Hannover" labelsEnabled="0" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal enabled="0" fixedDuration="0" endExpression="" durationUnit="min" accumulate="0" startField="" endField="" startExpression="" durationField="" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 enableorderby="0" type="singleSymbol" symbollevels="0" forceraster="0">
    <symbols>
      <symbol name="0" force_rhr="0" alpha="1" type="marker" clip_to_extent="1">
        <layer enabled="1" class="GeometryGenerator" locked="0" pass="0">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4)', &#xa;X($geometry)-2 /**{map_scale}*/  /**{xfactor}*/, Y($geometry) - (&quot;meas&quot; /**{map_scale}*/ - &quot;h_tocags&quot; /**{map_scale}*/) /**{yfactor}*/, &#xa;X($geometry)+2 /**{map_scale}*/  /**{xfactor}*/, Y($geometry) - (&quot;meas&quot; /**{map_scale}*/ - &quot;h_tocags&quot; /**{map_scale}*/) /**{yfactor}*/))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@0@0" force_rhr="0" alpha="1" type="line" clip_to_extent="1">
            <layer enabled="1" class="SimpleLine" locked="0" pass="0">
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
              <prop k="line_color" v="0,0,255,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.46"/>
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
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
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
      <text-style fontLetterSpacing="0" fontFamily="Noto Sans" textColor="0,0,0,255" blendMode="0" multilineHeight="1" capitalization="0" fontSizeUnit="Point" fontSize="8" fontStrikeout="0" textOpacity="1" namedStyle="" useSubstitutions="0" fontUnderline="0" fontKerning="1" allowHtml="0" fieldName="round(level_masl, 3)" fontItalic="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" textOrientation="horizontal" fontWordSpacing="0" fontWeight="50" previewBkgrdColor="255,255,255,255" isExpression="1">
        <text-buffer bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="1" bufferSize="0.5" bufferNoFill="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferJoinStyle="128" bufferColor="149,149,255,255" bufferOpacity="1"/>
        <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskedSymbolLayers="" maskSize="0" maskOpacity="1" maskEnabled="0" maskType="0" maskJoinStyle="128" maskSizeUnits="MM"/>
        <background shapeSVGFile="" shapeSizeX="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM" shapeDraw="0" shapeBorderWidth="0" shapeOffsetY="0" shapeRotationType="0" shapeJoinStyle="64" shapeBlendMode="0" shapeSizeY="0" shapeOpacity="1" shapeSizeUnit="MM" shapeBorderColor="128,128,128,255" shapeRadiiUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeFillColor="255,255,255,255" shapeOffsetUnit="MM" shapeSizeType="0" shapeRadiiY="0" shapeOffsetX="0" shapeRadiiX="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0"/>
        <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetDist="1" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowScale="100" shadowOpacity="0.7" shadowRadius="1.5" shadowRadiusUnit="MM" shadowColor="0,0,0,255" shadowUnder="0" shadowBlendMode="6" shadowDraw="0" shadowOffsetUnit="MM" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0"/>
        <dd_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties" type="Map">
              <Option name="Italic" type="Map">
                <Option name="active" type="bool" value="true"/>
                <Option name="expression" type="QString" value="1"/>
                <Option name="type" type="int" value="3"/>
              </Option>
              <Option name="OffsetXY" type="Map">
                <Option name="active" type="bool" value="false"/>
                <Option name="type" type="int" value="1"/>
                <Option name="val" type="QString" value=""/>
              </Option>
              <Option name="PositionX" type="Map">
                <Option name="active" type="bool" value="true"/>
                <Option name="expression" type="QString" value="X($geometry)+1.5/**{map_scale}*/ /**{xfactor}*/"/>
                <Option name="type" type="int" value="3"/>
              </Option>
              <Option name="PositionY" type="Map">
                <Option name="active" type="bool" value="true"/>
                <Option name="expression" type="QString" value="Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;)/**{map_scale}*/ /**{yfactor}*/"/>
                <Option name="type" type="int" value="3"/>
              </Option>
            </Option>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" autoWrapLength="0" leftDirectionSymbol="&lt;" multilineAlign="3" reverseDirectionSymbol="0" placeDirectionSymbol="0" plussign="0" rightDirectionSymbol=">" decimals="3" wrapChar="" formatNumbers="0"/>
      <placement maxCurvedCharAngleOut="-25" distUnits="MM" maxCurvedCharAngleIn="25" geometryGeneratorType="PointGeometry" xOffset="0" fitInPolygonOnly="0" overrunDistanceUnit="MM" layerType="UnknownGeometry" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" dist="0" repeatDistance="0" placementFlags="10" centroidWhole="0" yOffset="0" priority="5" lineAnchorType="0" overrunDistance="0" centroidInside="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" offsetUnits="MM" preserveRotation="1" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+1.5/**{map_scale}*/ /**{xfactor}*/, Y($geometry) - (&quot;meas&quot;/**{map_scale}*/ - &quot;h_tocags&quot;/**{map_scale}*/) /**{yfactor}*/))&#xa;" offsetType="0" geometryGeneratorEnabled="0" distMapUnitScale="3x:0,0,0,0,0,0" polygonPlacementFlags="2" repeatDistanceUnits="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" placement="1" quadOffset="2"/>
      <rendering obstacleType="0" drawLabels="1" maxNumLabels="2000" limitNumLabels="0" fontMaxPixelSize="10000" obstacle="1" scaleMax="0" scaleMin="0" upsidedownLabels="0" scaleVisibility="0" fontLimitPixelSize="0" mergeLines="0" minFeatureSize="0" displayAll="1" fontMinPixelSize="3" labelPerPart="0" zIndex="0" obstacleFactor="1"/>
      <dd_properties>
        <Option type="Map">
          <Option name="name" type="QString" value=""/>
          <Option name="properties" type="Map">
            <Option name="Italic" type="Map">
              <Option name="active" type="bool" value="true"/>
              <Option name="expression" type="QString" value="1"/>
              <Option name="type" type="int" value="3"/>
            </Option>
            <Option name="OffsetXY" type="Map">
              <Option name="active" type="bool" value="false"/>
              <Option name="type" type="int" value="1"/>
              <Option name="val" type="QString" value=""/>
            </Option>
            <Option name="PositionX" type="Map">
              <Option name="active" type="bool" value="true"/>
              <Option name="expression" type="QString" value="X($geometry)+1.5/**{map_scale}*/ * 1.0"/>
              <Option name="type" type="int" value="3"/>
            </Option>
            <Option name="PositionY" type="Map">
              <Option name="active" type="bool" value="true"/>
              <Option name="expression" type="QString" value="Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;)/**{map_scale}*/ * 1.0"/>
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
          <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; force_rhr=&quot;0&quot; alpha=&quot;1&quot; type=&quot;line&quot; clip_to_extent=&quot;1&quot;>&lt;layer enabled=&quot;1&quot; class=&quot;SimpleLine&quot; locked=&quot;0&quot; pass=&quot;0&quot;>&lt;prop k=&quot;align_dash_pattern&quot; v=&quot;0&quot;/>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;dash_pattern_offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;dash_pattern_offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;dash_pattern_offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;tweak_dash_pattern_on_corners&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
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
    <DiagramCategory minScaleDenominator="0" lineSizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" backgroundAlpha="255" sizeType="MM" width="15" direction="1" enabled="0" penAlpha="255" lineSizeType="MM" minimumSize="0" spacing="0" penColor="#000000" spacingUnitScale="3x:0,0,0,0,0,0" height="15" scaleDependency="Area" showAxis="0" penWidth="0" diagramOrientation="Up" rotationOffset="270" opacity="1" backgroundColor="#ffffff" sizeScale="3x:0,0,0,0,0,0" barWidth="5" scaleBasedVisibility="0" spacingUnit="MM" maxScaleDenominator="1e+8">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
      <axisSymbol>
        <symbol name="" force_rhr="0" alpha="1" type="line" clip_to_extent="1">
          <layer enabled="1" class="SimpleLine" locked="0" pass="0">
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
  <DiagramLayerSettings obstacle="0" zIndex="0" placement="0" priority="0" dist="0" showAll="1" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties"/>
        <Option name="type" type="QString" value="collection"/>
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
    <alias index="0" name="" field="rowid"/>
    <alias index="1" name="" field="obsid"/>
    <alias index="2" name="" field="date_time"/>
    <alias index="3" name="" field="meas"/>
    <alias index="4" name="" field="level_masl"/>
    <alias index="5" name="" field="h_tocags"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" expression="" field="rowid"/>
    <default applyOnUpdate="0" expression="" field="obsid"/>
    <default applyOnUpdate="0" expression="" field="date_time"/>
    <default applyOnUpdate="0" expression="" field="meas"/>
    <default applyOnUpdate="0" expression="" field="level_masl"/>
    <default applyOnUpdate="0" expression="" field="h_tocags"/>
  </defaults>
  <constraints>
    <constraint constraints="0" exp_strength="0" field="rowid" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="obsid" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="date_time" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="meas" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="level_masl" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="h_tocags" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="rowid"/>
    <constraint exp="" desc="" field="obsid"/>
    <constraint exp="" desc="" field="date_time"/>
    <constraint exp="" desc="" field="meas"/>
    <constraint exp="" desc="" field="level_masl"/>
    <constraint exp="" desc="" field="h_tocags"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column name="rowid" type="field" width="-1" hidden="0"/>
      <column name="obsid" type="field" width="-1" hidden="0"/>
      <column name="date_time" type="field" width="-1" hidden="0"/>
      <column name="meas" type="field" width="-1" hidden="0"/>
      <column name="level_masl" type="field" width="-1" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
      <column name="h_tocags" type="field" width="-1" hidden="0"/>
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
