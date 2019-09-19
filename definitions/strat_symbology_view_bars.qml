<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" maxScale="0" simplifyLocal="1" readOnly="0" simplifyAlgorithm="0" minScale="1e+8" simplifyDrawingTol="1" simplifyDrawingHints="0" version="3.8.3-Zanzibar" hasScaleBasedVisibilityFlag="0" labelsEnabled="1" simplifyMaxScale="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 type="RuleRenderer" forceraster="0" enableorderby="1" symbollevels="0">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule symbol="0" filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " label="frame" key="{c3dbe822-681b-4001-8689-efe1cccb461b}"/>
      <rule symbol="1" filter="ELSE" key="{e5417e67-e6c7-4369-936b-19eec0121d5d}"/>
      <rule symbol="2" filter="&quot;drillstop&quot; ILIKE '%berg%'" label="bedrock" key="{08ddf20b-93ef-46cb-9366-9b0f582d2fa4}"/>
    </rules>
    <symbols>
      <symbol type="marker" alpha="1" name="0" clip_to_extent="1" force_rhr="0">
        <layer enabled="1" pass="0" locked="0" class="GeometryGenerator">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry)+1, &#xa;X($geometry)+2, Y($geometry)+1, &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot; - 1,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot; - 1))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" alpha="1" name="@0@0" clip_to_extent="1" force_rhr="0">
            <layer enabled="1" pass="0" locked="0" class="SimpleFill">
              <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
              <prop v="0,11,0,255" k="color"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="35,35,35,137" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0.6" k="outline_width"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="solid" k="style"/>
              <effect type="effectStack" enabled="1">
                <effect type="dropShadow">
                  <prop v="13" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="35,35,35,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="outerGlow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,255,255" k="color1"/>
                  <prop v="0,255,0,255" k="color2"/>
                  <prop v="0" k="color_type"/>
                  <prop v="0" k="discrete"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="0" k="enabled"/>
                  <prop v="0.5" k="opacity"/>
                  <prop v="gradient" k="rampType"/>
                  <prop v="255,255,255,255" k="single_color"/>
                  <prop v="2" k="spread"/>
                  <prop v="MM" k="spread_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
                </effect>
                <effect type="drawSource">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="0" k="enabled"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="innerShadow">
                  <prop v="13" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="0" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="innerGlow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,255,255" k="color1"/>
                  <prop v="0,255,0,255" k="color2"/>
                  <prop v="0" k="color_type"/>
                  <prop v="0" k="discrete"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="0" k="enabled"/>
                  <prop v="0.5" k="opacity"/>
                  <prop v="gradient" k="rampType"/>
                  <prop v="255,255,255,255" k="single_color"/>
                  <prop v="2" k="spread"/>
                  <prop v="MM" k="spread_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
                </effect>
              </effect>
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
      <symbol type="marker" alpha="1" name="1" clip_to_extent="1" force_rhr="0">
        <layer enabled="1" pass="0" locked="0" class="GeometryGenerator">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot;))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" alpha="1" name="@1@0" clip_to_extent="1" force_rhr="0">
            <layer enabled="1" pass="0" locked="0" class="SimpleFill">
              <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
              <prop v="255,255,255,255" k="color"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="255,255,255,255" k="outline_color"/>
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
      <symbol type="marker" alpha="1" name="2" clip_to_extent="1" force_rhr="0">
        <layer enabled="1" pass="0" locked="0" class="GeometryGenerator">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6))', &#xa;X($geometry), Y($geometry) - &quot;depthbot&quot; + 0.5, &#xa;X($geometry)+1.5, Y($geometry) - &quot;depthbot&quot; - 1, &#xa;X($geometry)-1.5, Y($geometry) - &quot;depthbot&quot; - 1))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" alpha="1" name="@2@0" clip_to_extent="1" force_rhr="0">
            <layer enabled="1" pass="0" locked="0" class="SimpleFill">
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
    </symbols>
    <orderby>
      <orderByClause asc="1" nullsFirst="0">"maxdepthbot"</orderByClause>
      <orderByClause asc="0" nullsFirst="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontSize="8" fontFamily="Noto Sans" textOpacity="1" useSubstitutions="0" textColor="0,0,0,255" fontLetterSpacing="0" namedStyle="Italic" previewBkgrdColor="#ffffff" isExpression="1" fontSizeUnit="Point" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" fontItalic="1" fontUnderline="0" blendMode="0" fontCapitals="0" fontWeight="50" multilineHeight="1" fontWordSpacing="0" fontStrikeout="0">
        <text-buffer bufferOpacity="1" bufferDraw="1" bufferNoFill="1" bufferJoinStyle="128" bufferSize="0.5" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="255,255,255,255" bufferBlendMode="0" bufferSizeUnits="MM"/>
        <background shapeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM" shapeOffsetUnit="MM" shapeSizeType="0" shapeBorderWidth="0" shapeBlendMode="0" shapeSizeY="0" shapeRotation="0" shapeJoinStyle="64" shapeRadiiUnit="MM" shapeBorderColor="128,128,128,255" shapeSizeUnit="MM" shapeRotationType="0" shapeSVGFile="" shapeRadiiX="0" shapeRadiiY="0" shapeDraw="0" shapeOpacity="1" shapeFillColor="255,255,255,255" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0" shapeOffsetY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0"/>
        <shadow shadowOffsetAngle="135" shadowUnder="0" shadowRadiusUnit="MM" shadowDraw="0" shadowOffsetUnit="MM" shadowRadius="1.5" shadowBlendMode="6" shadowOffsetGlobal="1" shadowColor="0,0,0,255" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetDist="1" shadowOpacity="0.7" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0"/>
        <substitutions/>
      </text-style>
      <text-format useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" wrapChar="" leftDirectionSymbol="&lt;" formatNumbers="0" plussign="0" decimals="3" rightDirectionSymbol=">" placeDirectionSymbol="0" reverseDirectionSymbol="0" multilineAlign="3" autoWrapLength="0"/>
      <placement yOffset="0" offsetType="0" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" centroidWhole="0" distMapUnitScale="3x:0,0,0,0,0,0" centroidInside="0" geometryGeneratorType="PointGeometry" quadOffset="4" priority="5" geometryGeneratorEnabled="0" xOffset="0" distUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" repeatDistanceUnits="MM" geometryGenerator="" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" fitInPolygonOnly="0" maxCurvedCharAngleOut="-25" repeatDistance="0" maxCurvedCharAngleIn="25" offsetUnits="MM" placement="0" preserveRotation="1" dist="0"/>
      <rendering minFeatureSize="0" scaleMax="0" upsidedownLabels="0" obstacleFactor="1" maxNumLabels="2000" drawLabels="1" limitNumLabels="0" scaleMin="0" scaleVisibility="0" fontMinPixelSize="3" obstacleType="0" zIndex="0" displayAll="0" mergeLines="0" fontMaxPixelSize="10000" obstacle="1" labelPerPart="0" fontLimitPixelSize="0"/>
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
    <property value="obsid" key="dualview/previewExpressions"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory rotationOffset="270" penColor="#000000" lineSizeScale="3x:0,0,0,0,0,0" opacity="1" diagramOrientation="Up" minScaleDenominator="0" backgroundColor="#ffffff" scaleBasedVisibility="0" scaleDependency="Area" minimumSize="0" maxScaleDenominator="1e+8" barWidth="5" height="15" labelPlacementMethod="XHeight" backgroundAlpha="255" width="15" enabled="0" sizeScale="3x:0,0,0,0,0,0" penAlpha="255" lineSizeType="MM" sizeType="MM" penWidth="0">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute field="" color="#000000" label=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings obstacle="0" priority="0" dist="0" zIndex="0" showAll="1" placement="0" linePlacementFlags="18">
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
    <field name="maxdepthbot">
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
    <field name="stratid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="depthtop">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="depthbot">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="geology">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="geoshort">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="capacity">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="development">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="comment">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="obsid" index="0" name=""/>
    <alias field="maxdepthbot" index="1" name=""/>
    <alias field="drillstop" index="2" name=""/>
    <alias field="stratid" index="3" name=""/>
    <alias field="depthtop" index="4" name=""/>
    <alias field="depthbot" index="5" name=""/>
    <alias field="geology" index="6" name=""/>
    <alias field="geoshort" index="7" name=""/>
    <alias field="capacity" index="8" name=""/>
    <alias field="development" index="9" name=""/>
    <alias field="comment" index="10" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default field="obsid" applyOnUpdate="0" expression=""/>
    <default field="maxdepthbot" applyOnUpdate="0" expression=""/>
    <default field="drillstop" applyOnUpdate="0" expression=""/>
    <default field="stratid" applyOnUpdate="0" expression=""/>
    <default field="depthtop" applyOnUpdate="0" expression=""/>
    <default field="depthbot" applyOnUpdate="0" expression=""/>
    <default field="geology" applyOnUpdate="0" expression=""/>
    <default field="geoshort" applyOnUpdate="0" expression=""/>
    <default field="capacity" applyOnUpdate="0" expression=""/>
    <default field="development" applyOnUpdate="0" expression=""/>
    <default field="comment" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="obsid"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="maxdepthbot"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="drillstop"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="stratid"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="depthtop"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="depthbot"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="geology"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="geoshort"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="capacity"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="development"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" exp_strength="0" field="comment"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="obsid" desc=""/>
    <constraint exp="" field="maxdepthbot" desc=""/>
    <constraint exp="" field="drillstop" desc=""/>
    <constraint exp="" field="stratid" desc=""/>
    <constraint exp="" field="depthtop" desc=""/>
    <constraint exp="" field="depthbot" desc=""/>
    <constraint exp="" field="geology" desc=""/>
    <constraint exp="" field="geoshort" desc=""/>
    <constraint exp="" field="capacity" desc=""/>
    <constraint exp="" field="development" desc=""/>
    <constraint exp="" field="comment" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="&quot;geoshort&quot;">
    <columns>
      <column type="field" name="obsid" hidden="0" width="-1"/>
      <column type="field" name="stratid" hidden="0" width="-1"/>
      <column type="field" name="depthtop" hidden="0" width="-1"/>
      <column type="field" name="depthbot" hidden="0" width="-1"/>
      <column type="field" name="geology" hidden="0" width="-1"/>
      <column type="field" name="geoshort" hidden="0" width="-1"/>
      <column type="field" name="capacity" hidden="0" width="-1"/>
      <column type="field" name="development" hidden="0" width="-1"/>
      <column type="field" name="comment" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" name="maxdepthbot" hidden="0" width="-1"/>
      <column type="field" name="drillstop" hidden="0" width="-1"/>
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
    <field name="capacity" editable="1"/>
    <field name="comment" editable="1"/>
    <field name="depthbot" editable="1"/>
    <field name="depthtop" editable="1"/>
    <field name="development" editable="1"/>
    <field name="drillstop" editable="1"/>
    <field name="geology" editable="1"/>
    <field name="geoshort" editable="1"/>
    <field name="maxdepthbot" editable="1"/>
    <field name="obsid" editable="1"/>
    <field name="stratid" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="capacity" labelOnTop="0"/>
    <field name="comment" labelOnTop="0"/>
    <field name="depthbot" labelOnTop="0"/>
    <field name="depthtop" labelOnTop="0"/>
    <field name="development" labelOnTop="0"/>
    <field name="drillstop" labelOnTop="0"/>
    <field name="geology" labelOnTop="0"/>
    <field name="geoshort" labelOnTop="0"/>
    <field name="maxdepthbot" labelOnTop="0"/>
    <field name="obsid" labelOnTop="0"/>
    <field name="stratid" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
