<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" labelsEnabled="1" simplifyMaxScale="1" simplifyDrawingHints="0" maxScale="0" simplifyAlgorithm="0" styleCategories="AllStyleCategories" minScale="100000000" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" simplifyDrawingTol="1" version="3.16.3-Hannover">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endExpression="" durationUnit="min" fixedDuration="0" accumulate="0" mode="0" durationField="" enabled="0" startField="" endField="" startExpression="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="nullSymbol"/>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style textColor="0,0,0,255" textOrientation="horizontal" fontSize="8" textOpacity="1" namedStyle="Italic" fontLetterSpacing="0" previewBkgrdColor="255,255,255,255" fontKerning="1" fontFamily="Noto Sans" capitalization="0" allowHtml="0" fontWordSpacing="0" useSubstitutions="0" fontUnderline="0" fontWeight="50" fontStrikeout="0" fieldName="obsid" blendMode="0" fontItalic="1" multilineHeight="1" isExpression="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSizeUnit="Point">
        <text-buffer bufferNoFill="1" bufferJoinStyle="128" bufferDraw="1" bufferSize="0.5" bufferSizeUnits="MM" bufferOpacity="1" bufferColor="255,255,255,255" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0"/>
        <text-mask maskOpacity="1" maskEnabled="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskedSymbolLayers="" maskType="0" maskJoinStyle="128" maskSize="0" maskSizeUnits="MM"/>
        <background shapeRotationType="0" shapeRadiiY="0" shapeDraw="0" shapeSizeY="0" shapeOffsetY="0" shapeBorderColor="128,128,128,255" shapeBorderWidth="0" shapeJoinStyle="64" shapeSVGFile="" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0" shapeSizeX="0" shapeOffsetUnit="MM" shapeSizeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeRotation="0" shapeBorderWidthUnit="MM" shapeRadiiX="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiUnit="MM" shapeType="0" shapeOpacity="1" shapeBlendMode="0">
          <symbol name="markerSymbol" clip_to_extent="1" type="marker" force_rhr="0" alpha="1">
            <layer locked="0" pass="0" enabled="1" class="SimpleMarker">
              <prop v="0" k="angle"/>
              <prop v="243,166,178,255" k="color"/>
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
        <shadow shadowOffsetUnit="MM" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowOffsetDist="1" shadowBlendMode="6" shadowUnder="0" shadowRadius="1.5" shadowColor="0,0,0,255" shadowOffsetAngle="135" shadowScale="100" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowOpacity="0.7"/>
        <dd_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format wrapChar="" useMaxLineLengthForAutoWrap="1" placeDirectionSymbol="0" rightDirectionSymbol=">" leftDirectionSymbol="&lt;" addDirectionSymbol="0" multilineAlign="3" formatNumbers="0" decimals="3" autoWrapLength="0" reverseDirectionSymbol="0" plussign="0"/>
      <placement lineAnchorType="0" offsetUnits="MM" rotationAngle="0" yOffset="0" offsetType="0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2*0.001*@map_scale /**{xfactor}*/, Y($geometry)))" priority="5" placement="1" placementFlags="10" fitInPolygonOnly="0" centroidInside="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maxCurvedCharAngleOut="-25" geometryGeneratorType="PointGeometry" distUnits="MM" geometryGeneratorEnabled="0" distMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" repeatDistance="0" repeatDistanceUnits="MM" centroidWhole="0" quadOffset="2" dist="0" overrunDistance="0" xOffset="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorPercent="0.5" preserveRotation="1" polygonPlacementFlags="2" overrunDistanceUnit="MM" layerType="PointGeometry"/>
      <rendering obstacle="1" scaleVisibility="0" displayAll="1" upsidedownLabels="0" labelPerPart="0" obstacleFactor="1" drawLabels="1" mergeLines="0" fontMinPixelSize="3" fontMaxPixelSize="10000" maxNumLabels="2000" limitNumLabels="0" obstacleType="0" minFeatureSize="0" scaleMax="0" scaleMin="0" zIndex="0" fontLimitPixelSize="0"/>
      <dd_properties>
        <Option type="Map">
          <Option name="name" type="QString" value=""/>
          <Option name="properties" type="Map">
            <Option name="PositionX" type="Map">
              <Option name="active" type="bool" value="true"/>
              <Option name="expression" type="QString" value="X($geometry)+2*0.001*@map_scale /**{xfactor}*/"/>
              <Option name="type" type="int" value="3"/>
            </Option>
            <Option name="PositionY" type="Map">
              <Option name="active" type="bool" value="true"/>
              <Option name="expression" type="QString" value="Y($geometry)"/>
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
          <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; alpha=&quot;1&quot;>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; enabled=&quot;1&quot; class=&quot;SimpleLine&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
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
    <property key="dualview/previewExpressions" value="obsid"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory showAxis="0" sizeType="MM" penColor="#000000" minScaleDenominator="0" spacingUnit="MM" diagramOrientation="Up" spacing="0" scaleBasedVisibility="0" spacingUnitScale="3x:0,0,0,0,0,0" scaleDependency="Area" barWidth="5" labelPlacementMethod="XHeight" width="15" enabled="0" rotationOffset="270" lineSizeScale="3x:0,0,0,0,0,0" height="15" direction="1" penWidth="0" penAlpha="255" lineSizeType="MM" backgroundColor="#ffffff" backgroundAlpha="255" minimumSize="0" maxScaleDenominator="1e+8" opacity="1" sizeScale="3x:0,0,0,0,0,0">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" label="" field=""/>
      <axisSymbol>
        <symbol name="" clip_to_extent="1" type="line" force_rhr="0" alpha="1">
          <layer locked="0" pass="0" enabled="1" class="SimpleLine">
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
  <DiagramLayerSettings showAll="1" priority="0" obstacle="0" linePlacementFlags="18" zIndex="0" placement="0" dist="0">
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
    <alias name="" field="rowid" index="0"/>
    <alias name="" field="obsid" index="1"/>
    <alias name="" field="h_toc" index="2"/>
    <alias name="" field="h_gs" index="3"/>
    <alias name="" field="h_tocags" index="4"/>
    <alias name="" field="length" index="5"/>
    <alias name="" field="h_syst" index="6"/>
    <alias name="" field="ground_surface" index="7"/>
    <alias name="" field="soildepth" index="8"/>
    <alias name="" field="bedrock" index="9"/>
    <alias name="" field="drillstop" index="10"/>
    <alias name="" field="bedrock_from_table" index="11"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="rowid" expression=""/>
    <default applyOnUpdate="0" field="obsid" expression=""/>
    <default applyOnUpdate="0" field="h_toc" expression=""/>
    <default applyOnUpdate="0" field="h_gs" expression=""/>
    <default applyOnUpdate="0" field="h_tocags" expression=""/>
    <default applyOnUpdate="0" field="length" expression=""/>
    <default applyOnUpdate="0" field="h_syst" expression=""/>
    <default applyOnUpdate="0" field="ground_surface" expression=""/>
    <default applyOnUpdate="0" field="soildepth" expression=""/>
    <default applyOnUpdate="0" field="bedrock" expression=""/>
    <default applyOnUpdate="0" field="drillstop" expression=""/>
    <default applyOnUpdate="0" field="bedrock_from_table" expression=""/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" field="rowid" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="obsid" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="h_toc" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="h_gs" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="h_tocags" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="length" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="h_syst" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="ground_surface" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="soildepth" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="bedrock" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="drillstop" constraints="0" unique_strength="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="bedrock_from_table" constraints="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="rowid"/>
    <constraint exp="" desc="" field="obsid"/>
    <constraint exp="" desc="" field="h_toc"/>
    <constraint exp="" desc="" field="h_gs"/>
    <constraint exp="" desc="" field="h_tocags"/>
    <constraint exp="" desc="" field="length"/>
    <constraint exp="" desc="" field="h_syst"/>
    <constraint exp="" desc="" field="ground_surface"/>
    <constraint exp="" desc="" field="soildepth"/>
    <constraint exp="" desc="" field="bedrock"/>
    <constraint exp="" desc="" field="drillstop"/>
    <constraint exp="" desc="" field="bedrock_from_table"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="1" sortExpression="&quot;soildepthh&quot;" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" name="obsid" hidden="0" type="field"/>
      <column width="-1" hidden="1" type="actions"/>
      <column width="276" name="drillstop" hidden="0" type="field"/>
      <column width="-1" name="h_toc" hidden="0" type="field"/>
      <column width="-1" name="h_gs" hidden="0" type="field"/>
      <column width="-1" name="h_tocags" hidden="0" type="field"/>
      <column width="-1" name="length" hidden="0" type="field"/>
      <column width="-1" name="h_syst" hidden="0" type="field"/>
      <column width="-1" name="ground_surface" hidden="0" type="field"/>
      <column width="-1" name="bedrock" hidden="0" type="field"/>
      <column width="-1" name="bedrock_from_table" hidden="0" type="field"/>
      <column width="-1" name="soildepth" hidden="0" type="field"/>
      <column width="-1" name="rowid" hidden="0" type="field"/>
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
