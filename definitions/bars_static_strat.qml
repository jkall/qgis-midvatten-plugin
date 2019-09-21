<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyAlgorithm="0" maxScale="0" styleCategories="AllStyleCategories" simplifyDrawingHints="0" simplifyDrawingTol="1" simplifyMaxScale="1" simplifyLocal="1" version="3.8.3-Zanzibar" hasScaleBasedVisibilityFlag="0" minScale="1e+8" readOnly="0" labelsEnabled="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="1" type="RuleRenderer" symbollevels="0" forceraster="0">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " label="frame" key="{c3dbe822-681b-4001-8689-efe1cccb461b}" symbol="0"/>
      <rule filter="ELSE" key="{49f89c60-14dd-4f60-9818-0f1ae27fffd0}" symbol="1"/>
    </rules>
    <symbols>
      <symbol clip_to_extent="1" alpha="1" name="0" type="marker" force_rhr="0">
        <layer enabled="1" class="GeometryGenerator" locked="0" pass="0">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry), &#xa;X($geometry)+2, Y($geometry), &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot;))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" alpha="1" name="@0@0" type="fill" force_rhr="0">
            <layer enabled="1" class="SimpleFill" locked="0" pass="0">
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
              <effect enabled="1" type="effectStack">
                <effect type="dropShadow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="0.7" k="opacity"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" alpha="1" name="1" type="marker" force_rhr="0">
        <layer enabled="1" class="GeometryGenerator" locked="0" pass="0">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot;))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" alpha="1" name="@1@0" type="fill" force_rhr="0">
            <layer enabled="1" class="SimpleFill" locked="0" pass="0">
              <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
              <prop v="255,255,255,255" k="color"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="255,255,255,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="MapUnit" k="outline_width_unit"/>
              <prop v="solid" k="style"/>
              <effect enabled="0" type="effectStack">
                <effect type="dropShadow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="0.7" k="opacity"/>
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
    <orderby>
      <orderByClause asc="1" nullsFirst="0">"maxdepthbot"</orderByClause>
      <orderByClause asc="0" nullsFirst="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style isExpression="1" blendMode="0" useSubstitutions="0" fontCapitals="0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" fontSize="8" fontSizeUnit="Point" fontWeight="50" namedStyle="Italic" fontUnderline="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" multilineHeight="1" previewBkgrdColor="#ffffff" fontLetterSpacing="0" fontFamily="Noto Sans" fontStrikeout="0" textOpacity="1" textColor="0,0,0,255" fontWordSpacing="0" fontItalic="1">
        <text-buffer bufferNoFill="1" bufferSize="0.5" bufferColor="255,255,255,255" bufferDraw="1" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferSizeUnits="MM" bufferJoinStyle="128" bufferOpacity="1"/>
        <background shapeType="0" shapeOffsetY="0" shapeBorderColor="128,128,128,255" shapeRadiiY="0" shapeBorderWidth="0" shapeBlendMode="0" shapeJoinStyle="64" shapeRadiiX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRotationType="0" shapeRadiiUnit="MM" shapeSizeType="0" shapeOpacity="1" shapeOffsetX="0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255" shapeBorderWidthUnit="MM" shapeRotation="0" shapeSVGFile="" shapeSizeUnit="MM" shapeSizeY="0"/>
        <shadow shadowColor="0,0,0,255" shadowRadiusAlphaOnly="0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadiusUnit="MM" shadowUnder="0" shadowOffsetDist="1" shadowScale="100" shadowDraw="0" shadowOffsetAngle="135" shadowOffsetUnit="MM" shadowRadius="1.5"/>
        <substitutions/>
      </text-style>
      <text-format decimals="3" plussign="0" wrapChar="" leftDirectionSymbol="&lt;" multilineAlign="3" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" autoWrapLength="0" addDirectionSymbol="0" rightDirectionSymbol=">" reverseDirectionSymbol="0" formatNumbers="0"/>
      <placement yOffset="0" xOffset="3" geometryGeneratorType="PointGeometry" distMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" offsetType="0" geometryGeneratorEnabled="0" fitInPolygonOnly="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="RenderMetersInMapUnits" maxCurvedCharAngleOut="-25" distUnits="MM" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" placement="1" centroidWhole="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" centroidInside="0" rotationAngle="0" priority="5" quadOffset="2" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" dist="0" preserveRotation="1" maxCurvedCharAngleIn="25" repeatDistanceUnits="MM"/>
      <rendering drawLabels="1" maxNumLabels="2000" minFeatureSize="0" obstacleFactor="1" scaleMin="0" scaleMax="0" fontMaxPixelSize="10000" upsidedownLabels="0" fontLimitPixelSize="0" limitNumLabels="0" mergeLines="0" zIndex="0" obstacle="1" fontMinPixelSize="3" obstacleType="0" displayAll="1" labelPerPart="0" scaleVisibility="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
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
    <DiagramCategory penWidth="0" sizeScale="3x:0,0,0,0,0,0" rotationOffset="270" lineSizeType="MM" lineSizeScale="3x:0,0,0,0,0,0" width="15" maxScaleDenominator="1e+8" backgroundAlpha="255" enabled="0" minScaleDenominator="0" labelPlacementMethod="XHeight" height="15" penColor="#000000" backgroundColor="#ffffff" sizeType="MM" scaleDependency="Area" diagramOrientation="Up" minimumSize="0" penAlpha="255" opacity="1" barWidth="5" scaleBasedVisibility="0">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" obstacle="0" placement="0" priority="0" showAll="1" zIndex="0" dist="0">
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
    <alias name="" index="0" field="rowid"/>
    <alias name="" index="1" field="obsid"/>
    <alias name="" index="2" field="maxdepthbot"/>
    <alias name="" index="3" field="stratid"/>
    <alias name="" index="4" field="depthtop"/>
    <alias name="" index="5" field="depthbot"/>
    <alias name="" index="6" field="geology"/>
    <alias name="" index="7" field="geoshort"/>
    <alias name="" index="8" field="capacity"/>
    <alias name="" index="9" field="development"/>
    <alias name="" index="10" field="comment"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" expression="" field="rowid"/>
    <default applyOnUpdate="0" expression="" field="obsid"/>
    <default applyOnUpdate="0" expression="" field="maxdepthbot"/>
    <default applyOnUpdate="0" expression="" field="stratid"/>
    <default applyOnUpdate="0" expression="" field="depthtop"/>
    <default applyOnUpdate="0" expression="" field="depthbot"/>
    <default applyOnUpdate="0" expression="" field="geology"/>
    <default applyOnUpdate="0" expression="" field="geoshort"/>
    <default applyOnUpdate="0" expression="" field="capacity"/>
    <default applyOnUpdate="0" expression="" field="development"/>
    <default applyOnUpdate="0" expression="" field="comment"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="rowid"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="obsid"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="maxdepthbot"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="stratid"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="depthtop"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="depthbot"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="geology"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="geoshort"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="capacity"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="development"/>
    <constraint unique_strength="0" exp_strength="0" notnull_strength="0" constraints="0" field="comment"/>
  </constraints>
  <constraintExpressions>
    <constraint field="rowid" exp="" desc=""/>
    <constraint field="obsid" exp="" desc=""/>
    <constraint field="maxdepthbot" exp="" desc=""/>
    <constraint field="stratid" exp="" desc=""/>
    <constraint field="depthtop" exp="" desc=""/>
    <constraint field="depthbot" exp="" desc=""/>
    <constraint field="geology" exp="" desc=""/>
    <constraint field="geoshort" exp="" desc=""/>
    <constraint field="capacity" exp="" desc=""/>
    <constraint field="development" exp="" desc=""/>
    <constraint field="comment" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="&quot;stratid&quot;">
    <columns>
      <column name="obsid" type="field" hidden="0" width="-1"/>
      <column name="stratid" type="field" hidden="0" width="-1"/>
      <column name="depthtop" type="field" hidden="0" width="-1"/>
      <column name="depthbot" type="field" hidden="0" width="-1"/>
      <column name="geology" type="field" hidden="0" width="-1"/>
      <column name="geoshort" type="field" hidden="0" width="-1"/>
      <column name="capacity" type="field" hidden="0" width="-1"/>
      <column name="development" type="field" hidden="0" width="-1"/>
      <column name="comment" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column name="maxdepthbot" type="field" hidden="0" width="-1"/>
      <column name="rowid" type="field" hidden="0" width="-1"/>
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
