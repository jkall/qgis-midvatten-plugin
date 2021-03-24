<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" simplifyMaxScale="1" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" readOnly="0" simplifyDrawingHints="0" simplifyAlgorithm="0" maxScale="0" version="3.16.3-Hannover" minScale="100000000" labelsEnabled="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal startField="" startExpression="" fixedDuration="0" endField="" durationField="" endExpression="" accumulate="0" enabled="0" durationUnit="min" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="RuleRenderer" forceraster="0" symbollevels="1" enableorderby="0">
    <rules key="{087190a1-de22-4689-b4ec-9dd48222d5cc}">
      <rule filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' " symbol="0" key="{64c51113-aacc-449d-bad6-e9b98563d6a7}" label="bedrock"/>
    </rules>
    <symbols>
      <symbol type="marker" force_rhr="0" clip_to_extent="1" name="0" alpha="1">
        <layer class="GeometryGenerator" locked="0" enabled="1" pass="1">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6))', &#xa;X($geometry), Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/ + 0.5*0.001*@map_scale /**{yfactor}*/, &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/ - 1*0.001*@map_scale /**{yfactor}*/, &#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/ - 1*0.001*@map_scale /**{yfactor}*/))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" force_rhr="0" clip_to_extent="1" name="@0@0" alpha="1">
            <layer class="SimpleFill" locked="0" enabled="1" pass="0">
              <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
              <prop v="227,26,28,255" k="color"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="RenderMetersInMapUnits" k="offset_unit"/>
              <prop v="35,35,35,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="solid" k="style"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <orderby>
      <orderByClause asc="1" nullsFirst="0">"maxdepthbot"</orderByClause>
      <orderByClause asc="0" nullsFirst="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style blendMode="0" fontFamily="Noto Sans" fontStrikeout="0" fieldName="obsid" fontKerning="1" textColor="0,0,0,255" multilineHeight="1" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" useSubstitutions="0" isExpression="0" fontWeight="50" previewBkgrdColor="255,255,255,255" fontSize="8" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontItalic="1" textOpacity="1" textOrientation="horizontal" namedStyle="" fontWordSpacing="0" fontUnderline="0" allowHtml="0">
        <text-buffer bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferSizeUnits="MM" bufferNoFill="1" bufferSize="0.5" bufferColor="255,255,255,255" bufferJoinStyle="128" bufferDraw="1" bufferOpacity="1"/>
        <text-mask maskJoinStyle="128" maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskEnabled="0" maskOpacity="1" maskType="0" maskedSymbolLayers="" maskSizeUnits="MM"/>
        <background shapeRotationType="0" shapeFillColor="255,255,255,255" shapeOffsetUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeSizeUnit="MM" shapeOffsetX="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeBlendMode="0" shapeJoinStyle="64" shapeSVGFile="" shapeOffsetY="0" shapeSizeY="0" shapeBorderWidthUnit="MM" shapeBorderWidth="0" shapeRadiiX="0" shapeRadiiY="0" shapeBorderColor="128,128,128,255" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeDraw="0" shapeSizeType="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiUnit="MM" shapeOpacity="1"/>
        <shadow shadowOffsetDist="1" shadowOffsetGlobal="1" shadowRadiusAlphaOnly="0" shadowRadiusUnit="MM" shadowColor="0,0,0,255" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetAngle="135" shadowDraw="0" shadowOffsetUnit="MM" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowScale="100" shadowUnder="0" shadowRadius="1.5"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option type="Map" name="properties">
              <Option type="Map" name="PositionX">
                <Option type="bool" value="true" name="active"/>
                <Option type="QString" value="X($geometry)+2*0.001*@map_scale /**{xfactor}*/" name="expression"/>
                <Option type="int" value="3" name="type"/>
              </Option>
              <Option type="Map" name="PositionY">
                <Option type="bool" value="true" name="active"/>
                <Option type="QString" value="Y($geometry)" name="expression"/>
                <Option type="int" value="3" name="type"/>
              </Option>
            </Option>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format plussign="0" multilineAlign="3" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" placeDirectionSymbol="0" formatNumbers="0" addDirectionSymbol="0" wrapChar="" autoWrapLength="0" rightDirectionSymbol=">" decimals="3" useMaxLineLengthForAutoWrap="1"/>
      <placement overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" distMapUnitScale="3x:0,0,0,0,0,0" quadOffset="2" xOffset="0" lineAnchorType="0" centroidInside="0" overrunDistance="0" offsetType="0" rotationAngle="0" maxCurvedCharAngleIn="25" layerType="UnknownGeometry" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" overrunDistanceUnit="MM" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2*0.001*@map_scale /**{xfactor}*/, Y($geometry)))" geometryGeneratorType="PointGeometry" dist="0" offsetUnits="MM" yOffset="0" placement="1" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" priority="5" polygonPlacementFlags="2" distUnits="MM" preserveRotation="1" lineAnchorPercent="0.5" placementFlags="10" fitInPolygonOnly="0" maxCurvedCharAngleOut="-25"/>
      <rendering obstacleFactor="1" maxNumLabels="2000" fontMinPixelSize="3" scaleVisibility="0" scaleMin="0" mergeLines="0" limitNumLabels="0" obstacleType="0" drawLabels="1" fontMaxPixelSize="10000" zIndex="0" upsidedownLabels="0" displayAll="1" obstacle="1" minFeatureSize="0" fontLimitPixelSize="0" labelPerPart="0" scaleMax="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" value="" name="name"/>
          <Option type="Map" name="properties">
            <Option type="Map" name="PositionX">
              <Option type="bool" value="true" name="active"/>
              <Option type="QString" value="X($geometry)+2*0.001*@map_scale /**{xfactor}*/" name="expression"/>
              <Option type="int" value="3" name="type"/>
            </Option>
            <Option type="Map" name="PositionY">
              <Option type="bool" value="true" name="active"/>
              <Option type="QString" value="Y($geometry)" name="expression"/>
              <Option type="int" value="3" name="type"/>
            </Option>
          </Option>
          <Option type="QString" value="collection" name="type"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" value="pole_of_inaccessibility" name="anchorPoint"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
          <Option type="bool" value="false" name="drawToAllParts"/>
          <Option type="QString" value="0" name="enabled"/>
          <Option type="QString" value="point_on_exterior" name="labelAnchorPoint"/>
          <Option type="QString" value="&lt;symbol type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; name=&quot;symbol&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; locked=&quot;0&quot; enabled=&quot;1&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol"/>
          <Option type="double" value="0" name="minLength"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale"/>
          <Option type="QString" value="MM" name="minLengthUnit"/>
          <Option type="double" value="0" name="offsetFromAnchor"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale"/>
          <Option type="QString" value="MM" name="offsetFromAnchorUnit"/>
          <Option type="double" value="0" name="offsetFromLabel"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale"/>
          <Option type="QString" value="MM" name="offsetFromLabelUnit"/>
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
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory opacity="1" barWidth="5" showAxis="0" backgroundAlpha="255" penAlpha="255" maxScaleDenominator="1e+8" minScaleDenominator="0" scaleBasedVisibility="0" penWidth="0" spacing="0" penColor="#000000" minimumSize="0" sizeScale="3x:0,0,0,0,0,0" diagramOrientation="Up" backgroundColor="#ffffff" spacingUnitScale="3x:0,0,0,0,0,0" width="15" scaleDependency="Area" direction="1" lineSizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" enabled="0" spacingUnit="MM" rotationOffset="270" height="15" sizeType="MM" lineSizeType="MM">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="" color="#000000" field=""/>
      <axisSymbol>
        <symbol type="line" force_rhr="0" clip_to_extent="1" name="" alpha="1">
          <layer class="SimpleLine" locked="0" enabled="1" pass="0">
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
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings zIndex="0" dist="0" placement="0" linePlacementFlags="18" showAll="1" obstacle="0" priority="0">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
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
    <field configurationFlags="None" name="rowid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="obsid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="h_toc">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="h_gs">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="h_tocags">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="length">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="h_syst">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="ground_surface">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="soildepth">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bedrock">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="drillstop">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bedrock_from_table">
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
    <alias index="2" name="" field="h_toc"/>
    <alias index="3" name="" field="h_gs"/>
    <alias index="4" name="" field="h_tocags"/>
    <alias index="5" name="" field="length"/>
    <alias index="6" name="" field="h_syst"/>
    <alias index="7" name="" field="ground_surface"/>
    <alias index="8" name="" field="soildepth"/>
    <alias index="9" name="" field="bedrock"/>
    <alias index="10" name="" field="drillstop"/>
    <alias index="11" name="" field="bedrock_from_table"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" expression="" field="rowid"/>
    <default applyOnUpdate="0" expression="" field="obsid"/>
    <default applyOnUpdate="0" expression="" field="h_toc"/>
    <default applyOnUpdate="0" expression="" field="h_gs"/>
    <default applyOnUpdate="0" expression="" field="h_tocags"/>
    <default applyOnUpdate="0" expression="" field="length"/>
    <default applyOnUpdate="0" expression="" field="h_syst"/>
    <default applyOnUpdate="0" expression="" field="ground_surface"/>
    <default applyOnUpdate="0" expression="" field="soildepth"/>
    <default applyOnUpdate="0" expression="" field="bedrock"/>
    <default applyOnUpdate="0" expression="" field="drillstop"/>
    <default applyOnUpdate="0" expression="" field="bedrock_from_table"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="rowid" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="obsid" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="h_toc" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="h_gs" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="h_tocags" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="length" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="h_syst" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="ground_surface" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="soildepth" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="bedrock" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="drillstop" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="bedrock_from_table" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="rowid"/>
    <constraint desc="" exp="" field="obsid"/>
    <constraint desc="" exp="" field="h_toc"/>
    <constraint desc="" exp="" field="h_gs"/>
    <constraint desc="" exp="" field="h_tocags"/>
    <constraint desc="" exp="" field="length"/>
    <constraint desc="" exp="" field="h_syst"/>
    <constraint desc="" exp="" field="ground_surface"/>
    <constraint desc="" exp="" field="soildepth"/>
    <constraint desc="" exp="" field="bedrock"/>
    <constraint desc="" exp="" field="drillstop"/>
    <constraint desc="" exp="" field="bedrock_from_table"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="&quot;soildepthh&quot;" sortOrder="1">
    <columns>
      <column type="field" hidden="0" name="obsid" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" hidden="0" name="drillstop" width="276"/>
      <column type="field" hidden="0" name="h_toc" width="-1"/>
      <column type="field" hidden="0" name="h_gs" width="-1"/>
      <column type="field" hidden="0" name="h_tocags" width="-1"/>
      <column type="field" hidden="0" name="length" width="-1"/>
      <column type="field" hidden="0" name="h_syst" width="-1"/>
      <column type="field" hidden="0" name="ground_surface" width="-1"/>
      <column type="field" hidden="0" name="bedrock" width="-1"/>
      <column type="field" hidden="0" name="bedrock_from_table" width="-1"/>
      <column type="field" hidden="0" name="soildepth" width="-1"/>
      <column type="field" hidden="0" name="rowid" width="-1"/>
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
    <field editable="1" name="bedrock"/>
    <field editable="1" name="bedrock_from_table"/>
    <field editable="1" name="capacity"/>
    <field editable="1" name="comment"/>
    <field editable="1" name="depthbot"/>
    <field editable="1" name="depthtop"/>
    <field editable="1" name="development"/>
    <field editable="1" name="drillstop"/>
    <field editable="1" name="geology"/>
    <field editable="1" name="geoshort"/>
    <field editable="1" name="ground_surface"/>
    <field editable="1" name="h_gs"/>
    <field editable="1" name="h_syst"/>
    <field editable="1" name="h_toc"/>
    <field editable="1" name="h_tocags"/>
    <field editable="1" name="length"/>
    <field editable="1" name="maxdepthbot"/>
    <field editable="1" name="obsid"/>
    <field editable="1" name="rowid"/>
    <field editable="1" name="soildepth"/>
    <field editable="1" name="soildepthh"/>
    <field editable="1" name="stratid"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="bedrock"/>
    <field labelOnTop="0" name="bedrock_from_table"/>
    <field labelOnTop="0" name="capacity"/>
    <field labelOnTop="0" name="comment"/>
    <field labelOnTop="0" name="depthbot"/>
    <field labelOnTop="0" name="depthtop"/>
    <field labelOnTop="0" name="development"/>
    <field labelOnTop="0" name="drillstop"/>
    <field labelOnTop="0" name="geology"/>
    <field labelOnTop="0" name="geoshort"/>
    <field labelOnTop="0" name="ground_surface"/>
    <field labelOnTop="0" name="h_gs"/>
    <field labelOnTop="0" name="h_syst"/>
    <field labelOnTop="0" name="h_toc"/>
    <field labelOnTop="0" name="h_tocags"/>
    <field labelOnTop="0" name="length"/>
    <field labelOnTop="0" name="maxdepthbot"/>
    <field labelOnTop="0" name="obsid"/>
    <field labelOnTop="0" name="rowid"/>
    <field labelOnTop="0" name="soildepth"/>
    <field labelOnTop="0" name="soildepthh"/>
    <field labelOnTop="0" name="stratid"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"obsid"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
