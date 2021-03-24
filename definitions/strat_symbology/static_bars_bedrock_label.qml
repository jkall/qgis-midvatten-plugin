<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyLocal="1" simplifyDrawingHints="0" simplifyMaxScale="1" minScale="100000000" readOnly="0" simplifyDrawingTol="1" maxScale="0" hasScaleBasedVisibilityFlag="0" labelsEnabled="1" simplifyAlgorithm="0" version="3.16.3-Hannover" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal startField="" endExpression="" fixedDuration="0" mode="0" enabled="0" endField="" durationField="" accumulate="0" startExpression="" durationUnit="min">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="nullSymbol"/>
  <labeling type="rule-based">
    <rules key="{ca14e00b-be60-4354-9ec9-6c1c33efc8a3}">
      <rule filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' " key="{a5a3fbaa-18e3-46d2-9146-ab49d84ca9f1}">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" fontSize="8" multilineHeight="1" capitalization="0" fieldName="round(&quot;bedrock&quot;, 1)" useSubstitutions="0" fontWeight="50" fontUnderline="0" blendMode="0" fontItalic="1" fontSizeUnit="Point" namedStyle="Italic" fontKerning="1" textOpacity="1" fontFamily="Noto Sans" previewBkgrdColor="255,255,255,255" fontStrikeout="0" textOrientation="horizontal" fontWordSpacing="0" allowHtml="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" textColor="255,1,1,255" isExpression="1">
            <text-buffer bufferOpacity="1" bufferBlendMode="0" bufferNoFill="1" bufferJoinStyle="128" bufferDraw="1" bufferSize="0.5" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="255,255,255,255"/>
            <text-mask maskType="0" maskOpacity="1" maskSizeUnits="MM" maskedSymbolLayers="" maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskEnabled="0" maskJoinStyle="128"/>
            <background shapeOffsetX="0" shapeRadiiUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM" shapeBorderColor="128,128,128,255" shapeBorderWidth="0" shapeType="0" shapeSizeY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeRotationType="0" shapeSizeX="0" shapeSVGFile="" shapeSizeType="0" shapeOpacity="1" shapeDraw="0" shapeJoinStyle="64" shapeRotation="0" shapeOffsetUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeOffsetY="0" shapeRadiiX="0">
              <symbol force_rhr="0" type="marker" clip_to_extent="1" alpha="1" name="markerSymbol">
                <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
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
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowRadiusAlphaOnly="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowScale="100" shadowRadiusUnit="MM" shadowOffsetGlobal="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5" shadowOpacity="0.7" shadowUnder="0" shadowOffsetDist="1" shadowOffsetUnit="MM" shadowBlendMode="6" shadowOffsetAngle="135" shadowColor="0,0,0,255"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format plussign="0" rightDirectionSymbol=">" leftDirectionSymbol="&lt;" useMaxLineLengthForAutoWrap="1" formatNumbers="0" wrapChar="" autoWrapLength="0" addDirectionSymbol="0" placeDirectionSymbol="0" multilineAlign="3" reverseDirectionSymbol="0" decimals="3"/>
          <placement xOffset="0" yOffset="0" distMapUnitScale="3x:0,0,0,0,0,0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2 /**{xfactor}*/, Y($geometry)))" geometryGeneratorEnabled="0" lineAnchorPercent="0.5" overrunDistance="0" placement="1" offsetUnits="MapUnit" centroidInside="0" lineAnchorType="0" centroidWhole="0" priority="5" layerType="PointGeometry" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" distUnits="MM" repeatDistanceUnits="MM" geometryGeneratorType="PointGeometry" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" fitInPolygonOnly="0" maxCurvedCharAngleOut="-25" repeatDistance="0" polygonPlacementFlags="2" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" dist="0" quadOffset="2" preserveRotation="1" overrunDistanceUnit="MM" placementFlags="10" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR"/>
          <rendering maxNumLabels="2000" obstacle="1" zIndex="0" drawLabels="1" fontLimitPixelSize="0" limitNumLabels="0" obstacleType="0" fontMaxPixelSize="10000" mergeLines="0" minFeatureSize="0" labelPerPart="0" upsidedownLabels="0" scaleMin="0" obstacleFactor="1" displayAll="0" scaleVisibility="0" scaleMax="0" fontMinPixelSize="3"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="PositionX">
                  <Option value="true" type="bool" name="active"/>
                  <Option value="X($geometry)+2 /**{xfactor}*/" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
                <Option type="Map" name="PositionY">
                  <Option value="true" type="bool" name="active"/>
                  <Option value="Y($geometry) - &quot;soildepth&quot; /**{yfactor}*/" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
              </Option>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol force_rhr=&quot;0&quot; type=&quot;line&quot; clip_to_extent=&quot;1&quot; alpha=&quot;1&quot; name=&quot;symbol&quot;>&lt;layer locked=&quot;0&quot; enabled=&quot;1&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
  </labeling>
  <customproperties>
    <property value="obsid" key="dualview/previewExpressions"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory spacing="0" width="15" height="15" penColor="#000000" penWidth="0" scaleDependency="Area" maxScaleDenominator="1e+8" spacingUnitScale="3x:0,0,0,0,0,0" lineSizeScale="3x:0,0,0,0,0,0" sizeType="MM" labelPlacementMethod="XHeight" opacity="1" lineSizeType="MM" barWidth="5" minimumSize="0" showAxis="0" backgroundAlpha="255" direction="1" sizeScale="3x:0,0,0,0,0,0" backgroundColor="#ffffff" scaleBasedVisibility="0" spacingUnit="MM" minScaleDenominator="0" diagramOrientation="Up" enabled="0" penAlpha="255" rotationOffset="270">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute color="#000000" label="" field=""/>
      <axisSymbol>
        <symbol force_rhr="0" type="line" clip_to_extent="1" alpha="1" name="">
          <layer locked="0" enabled="1" pass="0" class="SimpleLine">
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
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings dist="0" priority="0" obstacle="0" placement="0" showAll="1" zIndex="0" linePlacementFlags="18">
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
    <alias index="0" field="rowid" name=""/>
    <alias index="1" field="obsid" name=""/>
    <alias index="2" field="h_toc" name=""/>
    <alias index="3" field="h_gs" name=""/>
    <alias index="4" field="h_tocags" name=""/>
    <alias index="5" field="length" name=""/>
    <alias index="6" field="h_syst" name=""/>
    <alias index="7" field="ground_surface" name=""/>
    <alias index="8" field="soildepth" name=""/>
    <alias index="9" field="bedrock" name=""/>
    <alias index="10" field="drillstop" name=""/>
    <alias index="11" field="bedrock_from_table" name=""/>
  </aliases>
  <defaults>
    <default expression="" field="rowid" applyOnUpdate="0"/>
    <default expression="" field="obsid" applyOnUpdate="0"/>
    <default expression="" field="h_toc" applyOnUpdate="0"/>
    <default expression="" field="h_gs" applyOnUpdate="0"/>
    <default expression="" field="h_tocags" applyOnUpdate="0"/>
    <default expression="" field="length" applyOnUpdate="0"/>
    <default expression="" field="h_syst" applyOnUpdate="0"/>
    <default expression="" field="ground_surface" applyOnUpdate="0"/>
    <default expression="" field="soildepth" applyOnUpdate="0"/>
    <default expression="" field="bedrock" applyOnUpdate="0"/>
    <default expression="" field="drillstop" applyOnUpdate="0"/>
    <default expression="" field="bedrock_from_table" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" unique_strength="0" field="rowid" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="obsid" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="h_toc" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="h_gs" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="h_tocags" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="length" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="h_syst" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="ground_surface" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="soildepth" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="bedrock" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="drillstop" constraints="0" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" field="bedrock_from_table" constraints="0" exp_strength="0"/>
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
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;soildepthh&quot;" sortOrder="1" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" type="field" name="obsid" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="276" type="field" name="drillstop" hidden="0"/>
      <column width="-1" type="field" name="h_toc" hidden="0"/>
      <column width="-1" type="field" name="h_gs" hidden="0"/>
      <column width="-1" type="field" name="h_tocags" hidden="0"/>
      <column width="-1" type="field" name="length" hidden="0"/>
      <column width="-1" type="field" name="h_syst" hidden="0"/>
      <column width="-1" type="field" name="ground_surface" hidden="0"/>
      <column width="-1" type="field" name="bedrock" hidden="0"/>
      <column width="-1" type="field" name="bedrock_from_table" hidden="0"/>
      <column width="-1" type="field" name="soildepth" hidden="0"/>
      <column width="-1" type="field" name="rowid" hidden="0"/>
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
