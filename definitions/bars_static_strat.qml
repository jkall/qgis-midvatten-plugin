<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingHints="0" simplifyLocal="1" maxScale="0" version="3.8.3-Zanzibar" labelsEnabled="0" hasScaleBasedVisibilityFlag="0" minScale="1e+8" readOnly="0" simplifyAlgorithm="0" styleCategories="AllStyleCategories" simplifyDrawingTol="1" simplifyMaxScale="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" type="RuleRenderer" enableorderby="1" forceraster="0">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule key="{c3dbe822-681b-4001-8689-efe1cccb461b}" label="frame" filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " symbol="0"/>
      <rule key="{49f89c60-14dd-4f60-9818-0f1ae27fffd0}" filter="ELSE" symbol="1"/>
    </rules>
    <symbols>
      <symbol type="marker" alpha="1" name="0" force_rhr="0" clip_to_extent="1">
        <layer locked="0" class="GeometryGenerator" enabled="1" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry), &#xa;X($geometry)+2, Y($geometry), &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot;))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" alpha="1" name="@0@0" force_rhr="0" clip_to_extent="1">
            <layer locked="0" class="SimpleFill" enabled="1" pass="0">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="0,11,0,255"/>
              <prop k="joinstyle" v="miter"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="no"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_unit" v="MapUnit"/>
              <prop k="style" v="solid"/>
              <effect type="effectStack" enabled="1">
                <effect type="dropShadow">
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="2.9"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MapUnit"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="0.7"/>
                </effect>
                <effect type="outerGlow">
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
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
      <symbol type="marker" alpha="1" name="1" force_rhr="0" clip_to_extent="1">
        <layer locked="0" class="GeometryGenerator" enabled="1" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot;))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" alpha="1" name="@1@0" force_rhr="0" clip_to_extent="1">
            <layer locked="0" class="SimpleFill" enabled="1" pass="0">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="255,255,255,255"/>
              <prop k="joinstyle" v="miter"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="255,255,255,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_unit" v="MapUnit"/>
              <prop k="style" v="solid"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="0.7"/>
                </effect>
                <effect type="outerGlow">
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
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
      <orderByClause nullsFirst="0" asc="1">"maxdepthbot"</orderByClause>
      <orderByClause nullsFirst="0" asc="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontSize="8" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" namedStyle="Italic" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontWeight="50" fontLetterSpacing="0" textColor="0,0,0,255" useSubstitutions="0" fontUnderline="0" fontCapitals="0" fontItalic="1" textOpacity="1" fontStrikeout="0" multilineHeight="1" fontWordSpacing="0" blendMode="0" fontSizeUnit="Point" previewBkgrdColor="#ffffff" fontFamily="Noto Sans" isExpression="1">
        <text-buffer bufferColor="255,255,255,255" bufferSize="0.5" bufferNoFill="1" bufferJoinStyle="128" bufferBlendMode="0" bufferSizeUnits="MM" bufferOpacity="1" bufferDraw="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
        <background shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeBlendMode="0" shapeFillColor="255,255,255,255" shapeSVGFile="" shapeOpacity="1" shapeDraw="0" shapeRadiiUnit="MM" shapeBorderWidth="0" shapeOffsetUnit="MM" shapeSizeY="0" shapeRadiiY="0" shapeRadiiX="0" shapeOffsetX="0" shapeBorderWidthUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeBorderColor="128,128,128,255" shapeOffsetY="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeSizeType="0" shapeType="0"/>
        <shadow shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetDist="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadiusUnit="MM" shadowColor="0,0,0,255" shadowRadius="1.5" shadowDraw="0" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0" shadowScale="100" shadowUnder="0" shadowOpacity="0.7" shadowBlendMode="6" shadowOffsetUnit="MM"/>
        <substitutions/>
      </text-style>
      <text-format placeDirectionSymbol="0" rightDirectionSymbol=">" wrapChar="" formatNumbers="0" decimals="3" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" plussign="0" multilineAlign="3" autoWrapLength="0"/>
      <placement placementFlags="10" distUnits="MM" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" offsetType="0" maxCurvedCharAngleOut="-25" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" priority="5" preserveRotation="1" maxCurvedCharAngleIn="25" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placement="1" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" quadOffset="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" dist="0" rotationAngle="0" repeatDistance="0" xOffset="3" fitInPolygonOnly="0" centroidWhole="0" yOffset="0" distMapUnitScale="3x:0,0,0,0,0,0" centroidInside="0" offsetUnits="RenderMetersInMapUnits" geometryGeneratorType="PointGeometry"/>
      <rendering upsidedownLabels="0" obstacle="1" limitNumLabels="0" minFeatureSize="0" zIndex="0" drawLabels="1" scaleVisibility="0" obstacleType="0" fontMinPixelSize="3" fontMaxPixelSize="10000" displayAll="1" scaleMax="0" scaleMin="0" maxNumLabels="2000" mergeLines="0" labelPerPart="0" obstacleFactor="1" fontLimitPixelSize="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" value="" name="name"/>
          <Option name="properties"/>
          <Option type="QString" value="collection" name="type"/>
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
    <DiagramCategory penWidth="0" width="15" minScaleDenominator="0" maxScaleDenominator="1e+8" labelPlacementMethod="XHeight" scaleBasedVisibility="0" enabled="0" lineSizeScale="3x:0,0,0,0,0,0" opacity="1" backgroundColor="#ffffff" scaleDependency="Area" minimumSize="0" penColor="#000000" backgroundAlpha="255" lineSizeType="MM" sizeType="MM" height="15" sizeScale="3x:0,0,0,0,0,0" barWidth="5" rotationOffset="270" diagramOrientation="Up" penAlpha="255">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute label="" field="" color="#000000"/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings placement="0" linePlacementFlags="18" dist="0" obstacle="0" priority="0" showAll="1" zIndex="0">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
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
    <field name="maxdepthbot">
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
    <alias index="0" field="rowid" name=""/>
    <alias index="1" field="obsid" name=""/>
    <alias index="2" field="maxdepthbot" name=""/>
    <alias index="3" field="stratid" name=""/>
    <alias index="4" field="depthtop" name=""/>
    <alias index="5" field="depthbot" name=""/>
    <alias index="6" field="geology" name=""/>
    <alias index="7" field="geoshort" name=""/>
    <alias index="8" field="capacity" name=""/>
    <alias index="9" field="development" name=""/>
    <alias index="10" field="comment" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="rowid"/>
    <default expression="" applyOnUpdate="0" field="obsid"/>
    <default expression="" applyOnUpdate="0" field="maxdepthbot"/>
    <default expression="" applyOnUpdate="0" field="stratid"/>
    <default expression="" applyOnUpdate="0" field="depthtop"/>
    <default expression="" applyOnUpdate="0" field="depthbot"/>
    <default expression="" applyOnUpdate="0" field="geology"/>
    <default expression="" applyOnUpdate="0" field="geoshort"/>
    <default expression="" applyOnUpdate="0" field="capacity"/>
    <default expression="" applyOnUpdate="0" field="development"/>
    <default expression="" applyOnUpdate="0" field="comment"/>
  </defaults>
  <constraints>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="rowid" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="obsid" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="maxdepthbot" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="stratid" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="depthtop" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="depthbot" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="geology" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="geoshort" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="capacity" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="development" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="comment" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="rowid" desc="" exp=""/>
    <constraint field="obsid" desc="" exp=""/>
    <constraint field="maxdepthbot" desc="" exp=""/>
    <constraint field="stratid" desc="" exp=""/>
    <constraint field="depthtop" desc="" exp=""/>
    <constraint field="depthbot" desc="" exp=""/>
    <constraint field="geology" desc="" exp=""/>
    <constraint field="geoshort" desc="" exp=""/>
    <constraint field="capacity" desc="" exp=""/>
    <constraint field="development" desc="" exp=""/>
    <constraint field="comment" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;stratid&quot;" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="obsid"/>
      <column width="-1" type="field" hidden="0" name="stratid"/>
      <column width="-1" type="field" hidden="0" name="depthtop"/>
      <column width="-1" type="field" hidden="0" name="depthbot"/>
      <column width="-1" type="field" hidden="0" name="geology"/>
      <column width="-1" type="field" hidden="0" name="geoshort"/>
      <column width="-1" type="field" hidden="0" name="capacity"/>
      <column width="-1" type="field" hidden="0" name="development"/>
      <column width="-1" type="field" hidden="0" name="comment"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" type="field" hidden="0" name="maxdepthbot"/>
      <column width="-1" type="field" hidden="0" name="rowid"/>
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
    <field name="rowid" editable="1"/>
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
    <field name="rowid" labelOnTop="0"/>
    <field name="stratid" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
