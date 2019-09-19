<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingHints="0" simplifyAlgorithm="0" styleCategories="AllStyleCategories" simplifyMaxScale="1" readOnly="0" labelsEnabled="1" hasScaleBasedVisibilityFlag="0" simplifyDrawingTol="1" maxScale="0" simplifyLocal="1" version="3.8.3-Zanzibar" minScale="1e+8">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" enableorderby="1" symbollevels="0" type="RuleRenderer">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule symbol="0" label="frame" filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " key="{c3dbe822-681b-4001-8689-efe1cccb461b}"/>
      <rule symbol="1" label="bedrock" filter="&quot;geoshort&quot; in ('berg', 'b', 'rock', 'ro')" key="{08ddf20b-93ef-46cb-9366-9b0f582d2fa4}"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" name="0" clip_to_extent="1" type="marker" alpha="1">
        <layer locked="0" class="GeometryGenerator" enabled="1" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', &#xa;X($geometry)-2, Y($geometry)+1, &#xa;X($geometry)+2, Y($geometry)+1, &#xa;X($geometry)+2, Y($geometry) - &quot;depthbot&quot; - 1,&#xa;X($geometry)-2, Y($geometry) - &quot;depthbot&quot; - 1))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" name="@0@0" clip_to_extent="1" type="fill" alpha="1">
            <layer locked="0" class="SimpleFill" enabled="1" pass="0">
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
              <effect enabled="1" type="effectStack">
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" name="1" clip_to_extent="1" type="marker" alpha="1">
        <layer locked="0" class="GeometryGenerator" enabled="1" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6))', &#xa;X($geometry), Y($geometry) - &quot;depthbot&quot; + 0.5, &#xa;X($geometry)+1.5, Y($geometry) - &quot;depthbot&quot; - 1, &#xa;X($geometry)-1.5, Y($geometry) - &quot;depthbot&quot; - 1))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" name="@1@0" clip_to_extent="1" type="fill" alpha="1">
            <layer locked="0" class="SimpleFill" enabled="1" pass="0">
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
      <text-style fontLetterSpacing="0" fontSizeUnit="Point" fontSize="8" fontItalic="1" blendMode="0" fontUnderline="0" isExpression="1" fontFamily="Noto Sans" useSubstitutions="0" textOpacity="1" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontStrikeout="0" fontWordSpacing="0" multilineHeight="1" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" previewBkgrdColor="#ffffff" fontCapitals="0" namedStyle="Italic" textColor="0,0,0,255" fontWeight="50">
        <text-buffer bufferDraw="1" bufferColor="255,255,255,255" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferSizeUnits="MM" bufferNoFill="1" bufferSize="0.5" bufferBlendMode="0"/>
        <background shapeRadiiX="0" shapeBorderWidth="0" shapeSizeType="0" shapeJoinStyle="64" shapeOffsetY="0" shapeSizeX="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeRotationType="0" shapeOffsetX="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiUnit="MM" shapeSizeUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeOffsetUnit="MM" shapeRadiiY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeRotation="0" shapeSizeY="0" shapeBorderWidthUnit="MM" shapeFillColor="255,255,255,255" shapeDraw="0" shapeBorderColor="128,128,128,255" shapeBlendMode="0"/>
        <shadow shadowRadiusAlphaOnly="0" shadowBlendMode="6" shadowOffsetUnit="MM" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowOffsetAngle="135" shadowScale="100" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusUnit="MM" shadowOpacity="0.7" shadowOffsetDist="1" shadowOffsetGlobal="1" shadowColor="0,0,0,255" shadowUnder="0" shadowRadius="1.5"/>
        <substitutions/>
      </text-style>
      <text-format plussign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" rightDirectionSymbol=">" formatNumbers="0" decimals="3" multilineAlign="3" reverseDirectionSymbol="0" addDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" placeDirectionSymbol="0" wrapChar=""/>
      <placement distUnits="MM" offsetType="0" repeatDistanceUnits="MM" priority="5" fitInPolygonOnly="0" maxCurvedCharAngleIn="25" xOffset="0" placementFlags="10" geometryGenerator="" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" distMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" repeatDistance="0" quadOffset="4" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" dist="0" offsetUnits="MM" maxCurvedCharAngleOut="-25" preserveRotation="1" geometryGeneratorType="PointGeometry" placement="0" centroidInside="0" centroidWhole="0" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" yOffset="0"/>
      <rendering fontMaxPixelSize="10000" minFeatureSize="0" mergeLines="0" obstacleType="0" upsidedownLabels="0" obstacleFactor="1" labelPerPart="0" zIndex="0" displayAll="0" fontMinPixelSize="3" drawLabels="1" scaleMax="0" scaleVisibility="0" fontLimitPixelSize="0" limitNumLabels="0" obstacle="1" scaleMin="0" maxNumLabels="2000"/>
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
    <DiagramCategory penWidth="0" enabled="0" sizeScale="3x:0,0,0,0,0,0" maxScaleDenominator="1e+8" width="15" backgroundAlpha="255" penAlpha="255" lineSizeScale="3x:0,0,0,0,0,0" height="15" minScaleDenominator="0" minimumSize="0" lineSizeType="MM" penColor="#000000" scaleBasedVisibility="0" backgroundColor="#ffffff" opacity="1" scaleDependency="Area" diagramOrientation="Up" barWidth="5" sizeType="MM" rotationOffset="270" labelPlacementMethod="XHeight">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings dist="0" placement="0" showAll="1" obstacle="0" priority="0" zIndex="0" linePlacementFlags="18">
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
    <alias index="0" field="obsid" name=""/>
    <alias index="1" field="maxdepthbot" name=""/>
    <alias index="2" field="drillstop" name=""/>
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
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="obsid"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="maxdepthbot"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="drillstop"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="stratid"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="depthtop"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="depthbot"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="geology"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="geoshort"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="capacity"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="development"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="comment"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="obsid"/>
    <constraint desc="" exp="" field="maxdepthbot"/>
    <constraint desc="" exp="" field="drillstop"/>
    <constraint desc="" exp="" field="stratid"/>
    <constraint desc="" exp="" field="depthtop"/>
    <constraint desc="" exp="" field="depthbot"/>
    <constraint desc="" exp="" field="geology"/>
    <constraint desc="" exp="" field="geoshort"/>
    <constraint desc="" exp="" field="capacity"/>
    <constraint desc="" exp="" field="development"/>
    <constraint desc="" exp="" field="comment"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="&quot;geoshort&quot;" sortOrder="0">
    <columns>
      <column hidden="0" width="-1" name="obsid" type="field"/>
      <column hidden="0" width="-1" name="stratid" type="field"/>
      <column hidden="0" width="-1" name="depthtop" type="field"/>
      <column hidden="0" width="-1" name="depthbot" type="field"/>
      <column hidden="0" width="-1" name="geology" type="field"/>
      <column hidden="0" width="-1" name="geoshort" type="field"/>
      <column hidden="0" width="-1" name="capacity" type="field"/>
      <column hidden="0" width="-1" name="development" type="field"/>
      <column hidden="0" width="-1" name="comment" type="field"/>
      <column hidden="1" width="-1" type="actions"/>
      <column hidden="0" width="-1" name="maxdepthbot" type="field"/>
      <column hidden="0" width="-1" name="drillstop" type="field"/>
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
