<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" simplifyDrawingTol="1" styleCategories="AllStyleCategories" simplifyAlgorithm="0" labelsEnabled="1" simplifyDrawingHints="0" simplifyMaxScale="1" version="3.8.3-Zanzibar" minScale="1e+8" hasScaleBasedVisibilityFlag="0" readOnly="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="1" type="RuleRenderer" forceraster="0" enableorderby="0">
    <rules key="{087190a1-de22-4689-b4ec-9dd48222d5cc}">
      <rule symbol="0" label="bedrock" key="{64c51113-aacc-449d-bad6-e9b98563d6a7}" filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' "/>
      <rule symbol="1" label="closed ending" key="{eea648b8-39d7-4ba5-af39-202732daa572}" filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' "/>
      <rule symbol="2" label="open ended" key="{04ea8482-b939-4daa-ab34-7b79a5a59a2a}" filter="LOWER(&quot;drillstop&quot;) NOT LIKE '%berg%' OR &quot;drillstop&quot; IS NULL "/>
    </rules>
    <symbols>
      <symbol type="marker" force_rhr="0" alpha="1" clip_to_extent="1" name="0">
        <layer locked="0" pass="1" enabled="1" class="GeometryGenerator">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6))', &#xa;X($geometry), Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/ + 0.5*0.001*@map_scale /**{yfactor}*/, &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/ - 1*0.001*@map_scale /**{yfactor}*/, &#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/ - 1*0.001*@map_scale /**{yfactor}*/))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" force_rhr="0" alpha="1" clip_to_extent="1" name="@0@0">
            <layer locked="0" pass="0" enabled="1" class="SimpleFill">
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
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="marker" force_rhr="0" alpha="0.85" clip_to_extent="1" name="1">
        <layer locked="0" pass="0" enabled="1" class="GeometryGenerator">
          <prop v="Line" k="SymbolType"/>
          <prop v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4, %5 %6, %7 %8, %9 %10)', &#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/,&#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/,&#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry)))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="line" force_rhr="0" alpha="1" clip_to_extent="1" name="@1@0">
            <layer locked="0" pass="0" enabled="1" class="SimpleLine">
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="miter" k="joinstyle"/>
              <prop v="35,35,35,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="0" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
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
      <symbol type="marker" force_rhr="0" alpha="0.85" clip_to_extent="1" name="2">
        <layer locked="0" pass="0" enabled="1" class="GeometryGenerator">
          <prop v="Line" k="SymbolType"/>
          <prop v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4, %5 %6, %7 %8)', &#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/,&#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/,&#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale /**{yfactor}*/))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="line" force_rhr="0" alpha="1" clip_to_extent="1" name="@2@0">
            <layer locked="0" pass="0" enabled="1" class="SimpleLine">
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="miter" k="joinstyle"/>
              <prop v="35,35,35,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="0" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
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
    <orderby>
      <orderByClause nullsFirst="0" asc="1">"maxdepthbot"</orderByClause>
      <orderByClause nullsFirst="0" asc="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontStrikeout="0" fontWordSpacing="0" isExpression="0" textColor="0,0,0,255" namedStyle="" fontItalic="1" useSubstitutions="0" textOpacity="1" previewBkgrdColor="#ffffff" fontSize="8" fontSizeUnit="Point" fontFamily="Noto Sans" fieldName="obsid" blendMode="0" fontWeight="50" multilineHeight="1" fontCapitals="0" fontUnderline="0" fontLetterSpacing="0">
        <text-buffer bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferDraw="1" bufferSize="0.5" bufferColor="255,255,255,255" bufferJoinStyle="128" bufferSizeUnits="MM" bufferNoFill="1"/>
        <background shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeSVGFile="" shapeDraw="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeOffsetY="0" shapeType="0" shapeBorderColor="128,128,128,255" shapeRotationType="0" shapeBorderWidth="0" shapeRadiiUnit="MM" shapeBorderWidthUnit="MM" shapeFillColor="255,255,255,255" shapeSizeType="0" shapeOffsetUnit="MM" shapeSizeY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0" shapeRadiiX="0" shapeOpacity="1" shapeSizeX="0" shapeBlendMode="0"/>
        <shadow shadowOpacity="0.7" shadowUnder="0" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowDraw="0" shadowOffsetDist="1" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5" shadowRadiusUnit="MM" shadowColor="0,0,0,255" shadowScale="100" shadowBlendMode="6" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0"/>
        <substitutions/>
      </text-style>
      <text-format multilineAlign="3" rightDirectionSymbol=">" reverseDirectionSymbol="0" placeDirectionSymbol="0" formatNumbers="0" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" decimals="3" plussign="0" wrapChar="" leftDirectionSymbol="&lt;" autoWrapLength="0"/>
      <placement rotationAngle="0" centroidInside="0" distMapUnitScale="3x:0,0,0,0,0,0" dist="0" maxCurvedCharAngleIn="25" centroidWhole="0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry)+2*0.001*@map_scale /**{xfactor}*/, Y($geometry)))" offsetType="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" offsetUnits="MM" repeatDistanceUnits="MM" fitInPolygonOnly="0" quadOffset="2" priority="5" placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" yOffset="0" maxCurvedCharAngleOut="-25" geometryGeneratorType="PointGeometry" preserveRotation="1" geometryGeneratorEnabled="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="MM" xOffset="0" placement="1" repeatDistance="0"/>
      <rendering obstacle="1" scaleMin="0" minFeatureSize="0" fontMaxPixelSize="10000" zIndex="0" limitNumLabels="0" scaleVisibility="0" upsidedownLabels="0" obstacleType="0" maxNumLabels="2000" drawLabels="1" fontMinPixelSize="3" labelPerPart="0" mergeLines="0" scaleMax="0" obstacleFactor="1" fontLimitPixelSize="0" displayAll="1"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option type="Map" name="properties">
            <Option type="Map" name="PositionX">
              <Option type="bool" name="active" value="true"/>
              <Option type="QString" name="expression" value="X($geometry)+2*0.001*@map_scale /**{xfactor}*/"/>
              <Option type="int" name="type" value="3"/>
            </Option>
            <Option type="Map" name="PositionY">
              <Option type="bool" name="active" value="true"/>
              <Option type="QString" name="expression" value="Y($geometry)"/>
              <Option type="int" name="type" value="3"/>
            </Option>
          </Option>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
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
    <DiagramCategory penWidth="0" backgroundColor="#ffffff" rotationOffset="270" sizeType="MM" barWidth="5" penAlpha="255" lineSizeScale="3x:0,0,0,0,0,0" height="15" backgroundAlpha="255" labelPlacementMethod="XHeight" minScaleDenominator="0" maxScaleDenominator="1e+8" diagramOrientation="Up" opacity="1" sizeScale="3x:0,0,0,0,0,0" scaleDependency="Area" lineSizeType="MM" width="15" minimumSize="0" enabled="0" scaleBasedVisibility="0" penColor="#000000">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings zIndex="0" priority="0" placement="0" obstacle="0" dist="0" linePlacementFlags="18" showAll="1">
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
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="rowid"/>
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
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="rowid" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="obsid" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="h_toc" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="h_gs" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="h_tocags" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="length" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="h_syst" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="ground_surface" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="soildepth" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="bedrock" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="drillstop" exp_strength="0"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" field="bedrock_from_table" exp_strength="0"/>
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
  <attributetableconfig sortExpression="&quot;soildepthh&quot;" actionWidgetStyle="dropDown" sortOrder="1">
    <columns>
      <column type="field" hidden="0" width="-1" name="obsid"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" hidden="0" width="276" name="drillstop"/>
      <column type="field" hidden="0" width="-1" name="h_toc"/>
      <column type="field" hidden="0" width="-1" name="h_gs"/>
      <column type="field" hidden="0" width="-1" name="h_tocags"/>
      <column type="field" hidden="0" width="-1" name="length"/>
      <column type="field" hidden="0" width="-1" name="h_syst"/>
      <column type="field" hidden="0" width="-1" name="ground_surface"/>
      <column type="field" hidden="0" width="-1" name="bedrock"/>
      <column type="field" hidden="0" width="-1" name="bedrock_from_table"/>
      <column type="field" hidden="0" width="-1" name="soildepth"/>
      <column type="field" hidden="0" width="-1" name="rowid"/>
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
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
