<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" readOnly="0" version="3.8.3-Zanzibar" simplifyMaxScale="1" minScale="1e+8" hasScaleBasedVisibilityFlag="0" simplifyAlgorithm="0" styleCategories="AllStyleCategories" labelsEnabled="1" simplifyDrawingHints="0" simplifyLocal="1" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" type="RuleRenderer" forceraster="0" enableorderby="1">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule symbol="0" key="{c3dbe822-681b-4001-8689-efe1cccb461b}" filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " label="Ram"/>
      <rule symbol="1" key="{e5417e67-e6c7-4369-936b-19eec0121d5d}" filter="ELSE"/>
      <rule symbol="2" key="{08ddf20b-93ef-46cb-9366-9b0f582d2fa4}" filter="&quot;drillstop&quot; ILIKE '%berg%'" label="Bergstopp"/>
    </rules>
    <symbols>
      <symbol type="marker" force_rhr="0" alpha="1" clip_to_extent="1" name="0">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry)+1, &#xa;X($geometry)+2, Y($geometry)+1, &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot; - 1,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot; - 1))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" force_rhr="0" alpha="1" clip_to_extent="1" name="@0@0">
            <layer class="SimpleFill" enabled="1" locked="0" pass="0">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="0,11,0,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,137"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.6"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
              <effect type="effectStack" enabled="1">
                <effect type="dropShadow">
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="35,35,35,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
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
      <symbol type="marker" force_rhr="0" alpha="1" clip_to_extent="1" name="1">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthtop&quot;, &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot;,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot;))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" force_rhr="0" alpha="1" clip_to_extent="1" name="@1@0">
            <layer class="SimpleFill" enabled="1" locked="0" pass="0">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="255,255,255,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="255,255,255,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
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
      <symbol type="marker" force_rhr="0" alpha="1" clip_to_extent="1" name="2">
        <layer class="GeometryGenerator" enabled="1" locked="0" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6))', &#xa;X($geometry), Y($geometry) - &quot;depthbot&quot; + 0.5, &#xa;X($geometry)+1.5, Y($geometry) - &quot;depthbot&quot; - 1, &#xa;X($geometry)-1.5, Y($geometry) - &quot;depthbot&quot; - 1))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" force_rhr="0" alpha="1" clip_to_extent="1" name="@2@0">
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
      <text-style fontUnderline="0" previewBkgrdColor="#ffffff" multilineHeight="1" fontLetterSpacing="0" fontItalic="1" fontFamily="Noto Sans" fontSize="8" namedStyle="Italic" isExpression="1" textOpacity="1" useSubstitutions="0" fontWordSpacing="0" fontStrikeout="0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" textColor="0,0,0,255" fontCapitals="0" blendMode="0" fontWeight="50" fontSizeUnit="Point" fontSizeMapUnitScale="3x:0,0,0,0,0,0">
        <text-buffer bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="255,255,255,255" bufferDraw="1" bufferOpacity="1" bufferBlendMode="0" bufferSizeUnits="MM" bufferSize="0.5"/>
        <background shapeRotationType="0" shapeRadiiUnit="MM" shapeSizeY="0" shapeOffsetUnit="MM" shapeRadiiX="0" shapeType="0" shapeBorderColor="128,128,128,255" shapeSizeUnit="MM" shapeOffsetY="0" shapeBorderWidth="0" shapeJoinStyle="64" shapeDraw="0" shapeSizeType="0" shapeSVGFile="" shapeFillColor="255,255,255,255" shapeRotation="0" shapeBorderWidthUnit="MM" shapeOffsetX="0" shapeSizeX="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1"/>
        <shadow shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowOpacity="0.7" shadowScale="100" shadowRadius="1.5" shadowRadiusUnit="MM" shadowDraw="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetDist="1" shadowOffsetAngle="135" shadowOffsetUnit="MM" shadowRadiusAlphaOnly="0" shadowBlendMode="6" shadowOffsetGlobal="1"/>
        <substitutions/>
      </text-style>
      <text-format wrapChar="" useMaxLineLengthForAutoWrap="1" multilineAlign="3" addDirectionSymbol="0" reverseDirectionSymbol="0" placeDirectionSymbol="0" leftDirectionSymbol="&lt;" rightDirectionSymbol=">" decimals="3" plussign="0" autoWrapLength="0" formatNumbers="0"/>
      <placement quadOffset="4" geometryGeneratorEnabled="0" preserveRotation="1" centroidInside="0" placementFlags="10" maxCurvedCharAngleOut="-25" rotationAngle="0" distMapUnitScale="3x:0,0,0,0,0,0" priority="5" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorType="PointGeometry" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" distUnits="MM" fitInPolygonOnly="0" offsetUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" repeatDistance="0" yOffset="0" placement="0" offsetType="0" dist="0" repeatDistanceUnits="MM" geometryGenerator="" centroidWhole="0"/>
      <rendering fontMinPixelSize="3" scaleMin="0" fontMaxPixelSize="10000" maxNumLabels="2000" zIndex="0" upsidedownLabels="0" drawLabels="1" scaleMax="0" minFeatureSize="0" obstacleFactor="1" fontLimitPixelSize="0" obstacle="1" limitNumLabels="0" displayAll="0" scaleVisibility="0" obstacleType="0" labelPerPart="0" mergeLines="0"/>
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
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory penAlpha="255" scaleDependency="Area" enabled="0" barWidth="5" backgroundAlpha="255" lineSizeScale="3x:0,0,0,0,0,0" diagramOrientation="Up" backgroundColor="#ffffff" width="15" minScaleDenominator="0" opacity="1" lineSizeType="MM" maxScaleDenominator="1e+8" rotationOffset="270" labelPlacementMethod="XHeight" penWidth="0" minimumSize="0" scaleBasedVisibility="0" sizeType="MM" height="15" sizeScale="3x:0,0,0,0,0,0" penColor="#000000">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings obstacle="0" dist="0" priority="0" placement="0" showAll="1" zIndex="0" linePlacementFlags="18">
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
    <alias index="0" name="" field="obsid"/>
    <alias index="1" name="" field="maxdepthbot"/>
    <alias index="2" name="" field="drillstop"/>
    <alias index="3" name="" field="stratid"/>
    <alias index="4" name="" field="depthtop"/>
    <alias index="5" name="" field="depthbot"/>
    <alias index="6" name="" field="geology"/>
    <alias index="7" name="" field="geoshort"/>
    <alias index="8" name="" field="capacity"/>
    <alias index="9" name="" field="development"/>
    <alias index="10" name="" field="comment"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="obsid" applyOnUpdate="0"/>
    <default expression="" field="maxdepthbot" applyOnUpdate="0"/>
    <default expression="" field="drillstop" applyOnUpdate="0"/>
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
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="obsid"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="maxdepthbot"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="drillstop"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="stratid"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="depthtop"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="depthbot"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="geology"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="geoshort"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="capacity"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="development"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" exp_strength="0" field="comment"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="obsid"/>
    <constraint exp="" desc="" field="maxdepthbot"/>
    <constraint exp="" desc="" field="drillstop"/>
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
  <attributetableconfig sortExpression="&quot;geoshort&quot;" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column type="field" width="-1" hidden="0" name="obsid"/>
      <column type="field" width="-1" hidden="0" name="stratid"/>
      <column type="field" width="-1" hidden="0" name="depthtop"/>
      <column type="field" width="-1" hidden="0" name="depthbot"/>
      <column type="field" width="-1" hidden="0" name="geology"/>
      <column type="field" width="-1" hidden="0" name="geoshort"/>
      <column type="field" width="-1" hidden="0" name="capacity"/>
      <column type="field" width="-1" hidden="0" name="development"/>
      <column type="field" width="-1" hidden="0" name="comment"/>
      <column type="actions" width="-1" hidden="1"/>
      <column type="field" width="-1" hidden="0" name="maxdepthbot"/>
      <column type="field" width="-1" hidden="0" name="drillstop"/>
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
    <field editable="1" name="stratid"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="capacity"/>
    <field labelOnTop="0" name="comment"/>
    <field labelOnTop="0" name="depthbot"/>
    <field labelOnTop="0" name="depthtop"/>
    <field labelOnTop="0" name="development"/>
    <field labelOnTop="0" name="drillstop"/>
    <field labelOnTop="0" name="geology"/>
    <field labelOnTop="0" name="geoshort"/>
    <field labelOnTop="0" name="maxdepthbot"/>
    <field labelOnTop="0" name="obsid"/>
    <field labelOnTop="0" name="stratid"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
