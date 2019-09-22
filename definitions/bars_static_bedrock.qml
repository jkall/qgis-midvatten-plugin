<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.8.3-Zanzibar" hasScaleBasedVisibilityFlag="0" simplifyDrawingHints="0" simplifyMaxScale="1" readOnly="0" simplifyDrawingTol="1" labelsEnabled="1" minScale="1e+8" styleCategories="AllStyleCategories" simplifyAlgorithm="0" maxScale="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 type="RuleRenderer" forceraster="0" enableorderby="0" symbollevels="1">
    <rules key="{087190a1-de22-4689-b4ec-9dd48222d5cc}">
      <rule key="{64c51113-aacc-449d-bad6-e9b98563d6a7}" symbol="0" filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' OR LOWER(&quot;drillstop&quot;) LIKE '%rock%'" label="bedrock"/>
      <rule key="{eea648b8-39d7-4ba5-af39-202732daa572}" symbol="1" filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' OR LOWER(&quot;drillstop&quot;) LIKE '%rock%'" label="closed ending"/>
      <rule key="{04ea8482-b939-4daa-ab34-7b79a5a59a2a}" symbol="2" filter="LOWER(&quot;drillstop&quot;) NOT LIKE '%berg%' AND LOWER(&quot;drillstop&quot;) NOT LIKE '%rock%' OR &quot;drillstop&quot; IS NULL" label="open ended"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" clip_to_extent="1" type="marker" name="0" alpha="1">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="1">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6))', &#xa;X($geometry), Y($geometry) - &quot;soildepth&quot; + 0.5, &#xa;X($geometry)+1.5, Y($geometry) - &quot;soildepth&quot; - 1, &#xa;X($geometry)-1.5, Y($geometry) - &quot;soildepth&quot; - 1))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" clip_to_extent="1" type="fill" name="@0@0" alpha="1">
            <layer class="SimpleFill" enabled="1" locked="0" pass="0">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="227,26,28,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="RenderMetersInMapUnits"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
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
      <symbol force_rhr="0" clip_to_extent="1" type="marker" name="1" alpha="0.85">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4, %5 %6, %7 %8, %9 %10)', &#xa;X($geometry)-2, Y($geometry), &#xa;X($geometry)+2, Y($geometry), &#xa;X($geometry)+2, Y($geometry) - &quot;soildepth&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;soildepth&quot;,&#xa;X($geometry)-2, Y($geometry)))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" clip_to_extent="1" type="line" name="@1@0" alpha="1">
            <layer class="SimpleLine" enabled="1" locked="0" pass="0">
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="miter"/>
              <prop k="line_color" v="35,35,35,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0"/>
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
      <symbol force_rhr="0" clip_to_extent="1" type="marker" name="2" alpha="0.85">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4, %5 %6, %7 %8)', &#xa;X($geometry)-2, Y($geometry) - &quot;soildepth&quot;,&#xa;X($geometry)-2, Y($geometry), &#xa;X($geometry)+2, Y($geometry), &#xa;X($geometry)+2, Y($geometry) - &quot;soildepth&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;soildepth&quot;))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" clip_to_extent="1" type="line" name="@2@0" alpha="1">
            <layer class="SimpleLine" enabled="1" locked="0" pass="0">
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="miter"/>
              <prop k="line_color" v="35,35,35,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0"/>
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
    <orderby>
      <orderByClause nullsFirst="0" asc="1">"maxdepthbot"</orderByClause>
      <orderByClause nullsFirst="0" asc="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontSizeUnit="Point" fontStrikeout="0" isExpression="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" fieldName="obsid" blendMode="0" fontItalic="1" fontCapitals="0" fontWordSpacing="0" namedStyle="Italic" fontWeight="50" fontSize="8" textColor="0,0,0,255" previewBkgrdColor="#ffffff" fontFamily="Noto Sans" fontUnderline="0" useSubstitutions="0" textOpacity="1" multilineHeight="1">
        <text-buffer bufferColor="255,255,255,255" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferSize="0.5" bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="1" bufferOpacity="1"/>
        <background shapeSizeY="0" shapeOffsetY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeRadiiY="0" shapeRadiiX="0" shapeOffsetX="0" shapeOpacity="1" shapeSVGFile="" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeSizeType="0" shapeBorderWidthUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetUnit="MM" shapeRadiiUnit="MM" shapeBlendMode="0" shapeBorderWidth="0" shapeDraw="0" shapeFillColor="255,255,255,255" shapeBorderColor="128,128,128,255" shapeJoinStyle="64" shapeRotationType="0"/>
        <shadow shadowRadiusAlphaOnly="0" shadowDraw="0" shadowOffsetDist="1" shadowBlendMode="6" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowScale="100" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadius="1.5"/>
        <substitutions/>
      </text-style>
      <text-format formatNumbers="0" plussign="0" multilineAlign="3" autoWrapLength="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0" leftDirectionSymbol="&lt;" wrapChar="" decimals="3" reverseDirectionSymbol="0" useMaxLineLengthForAutoWrap="1"/>
      <placement repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" xOffset="2" maxCurvedCharAngleIn="25" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" geometryGenerator="" fitInPolygonOnly="0" distUnits="MM" placement="1" centroidInside="0" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" centroidWhole="0" preserveRotation="1" dist="0" offsetType="0" priority="5" geometryGeneratorType="PointGeometry" offsetUnits="MapUnit" rotationAngle="0" distMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" maxCurvedCharAngleOut="-25" yOffset="0" quadOffset="2"/>
      <rendering fontMinPixelSize="3" scaleMin="0" scaleMax="0" drawLabels="1" zIndex="0" obstacleType="0" upsidedownLabels="0" scaleVisibility="0" obstacleFactor="1" maxNumLabels="2000" fontLimitPixelSize="0" labelPerPart="0" mergeLines="0" obstacle="1" fontMaxPixelSize="10000" displayAll="0" limitNumLabels="0" minFeatureSize="0"/>
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
      <value>obsid</value>
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
    <field name="obsid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_toc">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_gs">
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
    <field name="length">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="h_syst">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="ground_surface">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="soildepth">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bedrock">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="drillstop">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bedrock_from_table">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" field="obsid" index="0"/>
    <alias name="" field="h_toc" index="1"/>
    <alias name="" field="h_gs" index="2"/>
    <alias name="" field="h_tocags" index="3"/>
    <alias name="" field="length" index="4"/>
    <alias name="" field="h_syst" index="5"/>
    <alias name="" field="ground_surface" index="6"/>
    <alias name="" field="soildepth" index="7"/>
    <alias name="" field="bedrock" index="8"/>
    <alias name="" field="drillstop" index="9"/>
    <alias name="" field="bedrock_from_table" index="10"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="obsid"/>
    <default expression="" applyOnUpdate="0" field="h_toc"/>
    <default expression="" applyOnUpdate="0" field="h_gs"/>
    <default expression="" applyOnUpdate="0" field="h_tocags"/>
    <default expression="" applyOnUpdate="0" field="length"/>
    <default expression="" applyOnUpdate="0" field="h_syst"/>
    <default expression="" applyOnUpdate="0" field="ground_surface"/>
    <default expression="" applyOnUpdate="0" field="soildepth"/>
    <default expression="" applyOnUpdate="0" field="bedrock"/>
    <default expression="" applyOnUpdate="0" field="drillstop"/>
    <default expression="" applyOnUpdate="0" field="bedrock_from_table"/>
  </defaults>
  <constraints>
    <constraint constraints="0" exp_strength="0" field="obsid" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="h_toc" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="h_gs" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="h_tocags" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="length" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="h_syst" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="ground_surface" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="soildepth" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="bedrock" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="drillstop" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="bedrock_from_table" notnull_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="obsid" exp=""/>
    <constraint desc="" field="h_toc" exp=""/>
    <constraint desc="" field="h_gs" exp=""/>
    <constraint desc="" field="h_tocags" exp=""/>
    <constraint desc="" field="length" exp=""/>
    <constraint desc="" field="h_syst" exp=""/>
    <constraint desc="" field="ground_surface" exp=""/>
    <constraint desc="" field="soildepth" exp=""/>
    <constraint desc="" field="bedrock" exp=""/>
    <constraint desc="" field="drillstop" exp=""/>
    <constraint desc="" field="bedrock_from_table" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;soildepthh&quot;" sortOrder="1" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" hidden="0" type="field" name="obsid"/>
      <column width="-1" hidden="1" type="actions"/>
      <column width="276" hidden="0" type="field" name="drillstop"/>
      <column width="-1" hidden="0" type="field" name="h_toc"/>
      <column width="-1" hidden="0" type="field" name="h_gs"/>
      <column width="-1" hidden="0" type="field" name="h_tocags"/>
      <column width="-1" hidden="0" type="field" name="length"/>
      <column width="-1" hidden="0" type="field" name="h_syst"/>
      <column width="-1" hidden="0" type="field" name="ground_surface"/>
      <column width="-1" hidden="0" type="field" name="bedrock"/>
      <column width="-1" hidden="0" type="field" name="bedrock_from_table"/>
      <column width="-1" hidden="0" type="field" name="soildepth"/>
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
    <field editable="1" name="soildepth"/>
    <field editable="1" name="soildepthh"/>
    <field editable="1" name="stratid"/>
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
    <field name="soildepth" labelOnTop="0"/>
    <field name="soildepthh" labelOnTop="0"/>
    <field name="stratid" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
