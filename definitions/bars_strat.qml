<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" simplifyLocal="1" simplifyMaxScale="1" version="3.8.3-Zanzibar" labelsEnabled="0" styleCategories="AllStyleCategories" simplifyDrawingTol="1" maxScale="0" simplifyAlgorithm="0" minScale="1e+8" simplifyDrawingHints="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="1" symbollevels="0" type="RuleRenderer" forceraster="0">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " symbol="0" key="{c3dbe822-681b-4001-8689-efe1cccb461b}" label="frame"/>
      <rule filter="ELSE" symbol="1" key="{49f89c60-14dd-4f60-9818-0f1ae27fffd0}"/>
    </rules>
    <symbols>
      <symbol name="0" clip_to_extent="1" type="marker" force_rhr="0" alpha="1">
        <layer pass="0" class="GeometryGenerator" enabled="1" locked="0">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8, %9 %10))', &#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale,&#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale,&#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry)))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@0@0" clip_to_extent="1" type="fill" force_rhr="0" alpha="1">
            <layer pass="0" class="SimpleFill" enabled="1" locked="0">
              <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
              <prop v="0,11,0,255" k="color"/>
              <prop v="miter" k="joinstyle"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="35,35,35,255" k="outline_color"/>
              <prop v="no" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="MapUnit" k="outline_width_unit"/>
              <prop v="solid" k="style"/>
              <effect type="effectStack" enabled="1">
                <effect type="dropShadow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2.9" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MapUnit" k="offset_unit"/>
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
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="1" clip_to_extent="1" type="marker" force_rhr="0" alpha="1">
        <layer pass="0" class="GeometryGenerator" enabled="1" locked="0">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8, %9 %10))', &#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry) - &quot;depthtop&quot;*0.001*@map_scale, &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry) - &quot;depthtop&quot;*0.001*@map_scale, &#xa;X($geometry)+1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale,&#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale,&#xa;X($geometry)-1.5*0.001*@map_scale, Y($geometry) - &quot;depthtop&quot;*0.001*@map_scale))&#xa;" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@1@0" clip_to_extent="1" type="fill" force_rhr="0" alpha="1">
            <layer pass="0" class="SimpleFill" enabled="1" locked="0">
              <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
              <prop v="255,255,255,255" k="color"/>
              <prop v="miter" k="joinstyle"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="255,255,255,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="MapUnit" k="outline_width_unit"/>
              <prop v="solid" k="style"/>
              <effect type="effectStack" enabled="0">
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
    <orderby>
      <orderByClause nullsFirst="0" asc="1">"maxdepthbot"</orderByClause>
      <orderByClause nullsFirst="0" asc="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style blendMode="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontUnderline="0" textOpacity="1" fontLetterSpacing="0" multilineHeight="1" fontSize="8" fontStrikeout="0" namedStyle="Italic" fontWeight="50" fontFamily="Noto Sans" previewBkgrdColor="#ffffff" fontWordSpacing="0" isExpression="1" fontCapitals="0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" textColor="0,0,0,255" fontSizeUnit="Point" useSubstitutions="0" fontItalic="1">
        <text-buffer bufferDraw="1" bufferNoFill="1" bufferSize="0.5" bufferBlendMode="0" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferJoinStyle="128" bufferColor="255,255,255,255" bufferOpacity="1"/>
        <background shapeBorderWidthUnit="MM" shapeRadiiY="0" shapeJoinStyle="64" shapeRadiiX="0" shapeFillColor="255,255,255,255" shapeSizeType="0" shapeBorderWidth="0" shapeSizeUnit="MM" shapeRadiiUnit="MM" shapeDraw="0" shapeOffsetX="0" shapeOffsetY="0" shapeBlendMode="0" shapeOffsetUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeRotationType="0" shapeSizeX="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderColor="128,128,128,255" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeY="0" shapeSVGFile="" shapeType="0" shapeRotation="0"/>
        <shadow shadowOffsetGlobal="1" shadowDraw="0" shadowOffsetUnit="MM" shadowOffsetDist="1" shadowRadius="1.5" shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowScale="100" shadowOffsetAngle="135" shadowBlendMode="6" shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusUnit="MM" shadowOpacity="0.7"/>
        <substitutions/>
      </text-style>
      <text-format autoWrapLength="0" reverseDirectionSymbol="0" formatNumbers="0" useMaxLineLengthForAutoWrap="1" placeDirectionSymbol="0" decimals="3" plussign="0" multilineAlign="3" addDirectionSymbol="0" wrapChar="" leftDirectionSymbol="&lt;" rightDirectionSymbol=">"/>
      <placement repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" dist="0" offsetUnits="RenderMetersInMapUnits" placementFlags="10" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" preserveRotation="1" xOffset="3" yOffset="0" centroidWhole="0" geometryGeneratorType="PointGeometry" distMapUnitScale="3x:0,0,0,0,0,0" centroidInside="0" offsetType="0" repeatDistanceUnits="MM" quadOffset="2" rotationAngle="0" maxCurvedCharAngleOut="-25" geometryGeneratorEnabled="0" repeatDistance="0" fitInPolygonOnly="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="MM" maxCurvedCharAngleIn="25" priority="5" placement="1" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR"/>
      <rendering fontMaxPixelSize="10000" scaleVisibility="0" zIndex="0" maxNumLabels="2000" obstacle="1" fontLimitPixelSize="0" scaleMin="0" scaleMax="0" mergeLines="0" upsidedownLabels="0" limitNumLabels="0" fontMinPixelSize="3" obstacleType="0" minFeatureSize="0" labelPerPart="0" displayAll="1" drawLabels="1" obstacleFactor="1"/>
      <dd_properties>
        <Option type="Map">
          <Option name="name" type="QString" value=""/>
          <Option name="properties"/>
          <Option name="type" type="QString" value="collection"/>
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
    <DiagramCategory penAlpha="255" lineSizeType="MM" scaleDependency="Area" barWidth="5" enabled="0" maxScaleDenominator="1e+8" labelPlacementMethod="XHeight" backgroundColor="#ffffff" penColor="#000000" lineSizeScale="3x:0,0,0,0,0,0" opacity="1" sizeType="MM" penWidth="0" height="15" diagramOrientation="Up" minScaleDenominator="0" sizeScale="3x:0,0,0,0,0,0" rotationOffset="270" scaleBasedVisibility="0" width="15" backgroundAlpha="255" minimumSize="0">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" label="" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings placement="0" dist="0" zIndex="0" linePlacementFlags="18" showAll="1" priority="0" obstacle="0">
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
    <default expression="" field="rowid" applyOnUpdate="0"/>
    <default expression="" field="obsid" applyOnUpdate="0"/>
    <default expression="" field="maxdepthbot" applyOnUpdate="0"/>
    <default expression="" field="stratid" applyOnUpdate="0"/>
    <default expression="" field="depthtop" applyOnUpdate="0"/>
    <default expression="" field="depthbot" applyOnUpdate="0"/>
    <default expression="" field="geology" applyOnUpdate="0"/>
    <default expression="" field="geoshort" applyOnUpdate="0"/>
    <default expression="" field="capacity" applyOnUpdate="0"/>
    <default expression="" field="development" applyOnUpdate="0"/>
    <default expression="" field="comment" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="rowid" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="obsid" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="maxdepthbot" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="stratid" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="depthtop" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="depthbot" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="geology" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="geoshort" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="capacity" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="development" notnull_strength="0"/>
    <constraint unique_strength="0" exp_strength="0" constraints="0" field="comment" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="rowid"/>
    <constraint exp="" desc="" field="obsid"/>
    <constraint exp="" desc="" field="maxdepthbot"/>
    <constraint exp="" desc="" field="stratid"/>
    <constraint exp="" desc="" field="depthtop"/>
    <constraint exp="" desc="" field="depthbot"/>
    <constraint exp="" desc="" field="geology"/>
    <constraint exp="" desc="" field="geoshort"/>
    <constraint exp="" desc="" field="capacity"/>
    <constraint exp="" desc="" field="development"/>
    <constraint exp="" desc="" field="comment"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;stratid&quot;" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column width="-1" name="obsid" type="field" hidden="0"/>
      <column width="-1" name="stratid" type="field" hidden="0"/>
      <column width="-1" name="depthtop" type="field" hidden="0"/>
      <column width="-1" name="depthbot" type="field" hidden="0"/>
      <column width="-1" name="geology" type="field" hidden="0"/>
      <column width="-1" name="geoshort" type="field" hidden="0"/>
      <column width="-1" name="capacity" type="field" hidden="0"/>
      <column width="-1" name="development" type="field" hidden="0"/>
      <column width="-1" name="comment" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" name="maxdepthbot" type="field" hidden="0"/>
      <column width="-1" name="rowid" type="field" hidden="0"/>
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
