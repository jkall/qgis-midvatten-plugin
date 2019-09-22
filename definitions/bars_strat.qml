<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.8.3-Zanzibar" hasScaleBasedVisibilityFlag="0" simplifyDrawingHints="0" simplifyMaxScale="1" readOnly="0" simplifyDrawingTol="1" labelsEnabled="0" minScale="1e+8" styleCategories="AllStyleCategories" simplifyAlgorithm="0" maxScale="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 type="RuleRenderer" forceraster="0" enableorderby="1" symbollevels="0">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule key="{c3dbe822-681b-4001-8689-efe1cccb461b}" symbol="0" filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " label="frame"/>
      <rule key="{49f89c60-14dd-4f60-9818-0f1ae27fffd0}" symbol="1" filter="ELSE"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" clip_to_extent="1" type="marker" name="0" alpha="1">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale,&#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale))"/>
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
              <effect enabled="1" type="effectStack">
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
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" clip_to_extent="1" type="marker" name="1" alpha="1">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry) - &quot;depthtop&quot;*0.001*@map_scale, &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry) - &quot;depthtop&quot;*0.001*@map_scale, &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale,&#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" clip_to_extent="1" type="fill" name="@1@0" alpha="1">
            <layer class="SimpleFill" enabled="1" locked="0" pass="0">
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
              <effect enabled="0" type="effectStack">
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
      <text-style fontSizeUnit="Point" fontStrikeout="0" isExpression="1" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" blendMode="0" fontItalic="1" fontCapitals="0" fontWordSpacing="0" namedStyle="Italic" fontWeight="50" fontSize="8" textColor="0,0,0,255" previewBkgrdColor="#ffffff" fontFamily="Noto Sans" fontUnderline="0" useSubstitutions="0" textOpacity="1" multilineHeight="1">
        <text-buffer bufferColor="255,255,255,255" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferSize="0.5" bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="1" bufferOpacity="1"/>
        <background shapeSizeY="0" shapeOffsetY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeRadiiY="0" shapeRadiiX="0" shapeOffsetX="0" shapeOpacity="1" shapeSVGFile="" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeSizeType="0" shapeBorderWidthUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetUnit="MM" shapeRadiiUnit="MM" shapeBlendMode="0" shapeBorderWidth="0" shapeDraw="0" shapeFillColor="255,255,255,255" shapeBorderColor="128,128,128,255" shapeJoinStyle="64" shapeRotationType="0"/>
        <shadow shadowRadiusAlphaOnly="0" shadowDraw="0" shadowOffsetDist="1" shadowBlendMode="6" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowScale="100" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadius="1.5"/>
        <substitutions/>
      </text-style>
      <text-format formatNumbers="0" plussign="0" multilineAlign="3" autoWrapLength="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0" leftDirectionSymbol="&lt;" wrapChar="" decimals="3" reverseDirectionSymbol="0" useMaxLineLengthForAutoWrap="1"/>
      <placement repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" xOffset="3" maxCurvedCharAngleIn="25" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" fitInPolygonOnly="0" distUnits="MM" placement="1" centroidInside="0" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" centroidWhole="0" preserveRotation="1" dist="0" offsetType="0" priority="5" geometryGeneratorType="PointGeometry" offsetUnits="RenderMetersInMapUnits" rotationAngle="0" distMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" maxCurvedCharAngleOut="-25" yOffset="0" quadOffset="2"/>
      <rendering fontMinPixelSize="3" scaleMin="0" scaleMax="0" drawLabels="1" zIndex="0" obstacleType="0" upsidedownLabels="0" scaleVisibility="0" obstacleFactor="1" maxNumLabels="2000" fontLimitPixelSize="0" labelPerPart="0" mergeLines="0" obstacle="1" fontMaxPixelSize="10000" displayAll="1" limitNumLabels="0" minFeatureSize="0"/>
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
    <property key="dualview/previewExpressions" value="obsid"/>
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
    <alias name="" field="rowid" index="0"/>
    <alias name="" field="obsid" index="1"/>
    <alias name="" field="maxdepthbot" index="2"/>
    <alias name="" field="stratid" index="3"/>
    <alias name="" field="depthtop" index="4"/>
    <alias name="" field="depthbot" index="5"/>
    <alias name="" field="geology" index="6"/>
    <alias name="" field="geoshort" index="7"/>
    <alias name="" field="capacity" index="8"/>
    <alias name="" field="development" index="9"/>
    <alias name="" field="comment" index="10"/>
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
    <constraint constraints="0" exp_strength="0" field="rowid" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="obsid" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="maxdepthbot" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="stratid" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="depthtop" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="depthbot" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="geology" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="geoshort" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="capacity" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="development" notnull_strength="0" unique_strength="0"/>
    <constraint constraints="0" exp_strength="0" field="comment" notnull_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="rowid" exp=""/>
    <constraint desc="" field="obsid" exp=""/>
    <constraint desc="" field="maxdepthbot" exp=""/>
    <constraint desc="" field="stratid" exp=""/>
    <constraint desc="" field="depthtop" exp=""/>
    <constraint desc="" field="depthbot" exp=""/>
    <constraint desc="" field="geology" exp=""/>
    <constraint desc="" field="geoshort" exp=""/>
    <constraint desc="" field="capacity" exp=""/>
    <constraint desc="" field="development" exp=""/>
    <constraint desc="" field="comment" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;stratid&quot;" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" hidden="0" type="field" name="obsid"/>
      <column width="-1" hidden="0" type="field" name="stratid"/>
      <column width="-1" hidden="0" type="field" name="depthtop"/>
      <column width="-1" hidden="0" type="field" name="depthbot"/>
      <column width="-1" hidden="0" type="field" name="geology"/>
      <column width="-1" hidden="0" type="field" name="geoshort"/>
      <column width="-1" hidden="0" type="field" name="capacity"/>
      <column width="-1" hidden="0" type="field" name="development"/>
      <column width="-1" hidden="0" type="field" name="comment"/>
      <column width="-1" hidden="1" type="actions"/>
      <column width="-1" hidden="0" type="field" name="maxdepthbot"/>
      <column width="-1" hidden="0" type="field" name="rowid"/>
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
    <field editable="1" name="capacity"/>
    <field editable="1" name="comment"/>
    <field editable="1" name="depthbot"/>
    <field editable="1" name="depthtop"/>
    <field editable="1" name="development"/>
    <field editable="1" name="drillstop"/>
    <field editable="1" name="geology"/>
    <field editable="1" name="geoshort"/>
    <field editable="1" name="maxdepthbot"/>
    <field editable="1" name="obsid"/>
    <field editable="1" name="rowid"/>
    <field editable="1" name="stratid"/>
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
