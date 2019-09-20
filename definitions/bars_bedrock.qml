<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.8.3-Zanzibar" simplifyDrawingTol="1" minScale="1e+8" simplifyDrawingHints="0" simplifyLocal="1" simplifyAlgorithm="0" hasScaleBasedVisibilityFlag="0" readOnly="0" simplifyMaxScale="1" maxScale="0" labelsEnabled="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="1" forceraster="0" type="singleSymbol" symbollevels="0">
    <symbols>
      <symbol alpha="1" type="marker" name="0" force_rhr="0" clip_to_extent="1">
        <layer class="GeometryGenerator" locked="0" enabled="1" pass="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6))', &#xa;X($geometry),&#xa;Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale*0.5 + 0.5*0.001*@map_scale, &#xa;X($geometry)+1.5*0.001*@map_scale,&#xa;Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale*0.5 - 1*0.001*@map_scale, &#xa;X($geometry)-1.5*0.001*@map_scale,&#xa;Y($geometry) - &quot;soildepth&quot;*0.001*@map_scale*0.5 - 1*0.001*@map_scale))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" type="fill" name="@0@0" force_rhr="0" clip_to_extent="1">
            <layer class="SimpleFill" locked="0" enabled="1" pass="0">
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
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
    <orderby>
      <orderByClause asc="1" nullsFirst="0">"maxdepthbot"</orderByClause>
      <orderByClause asc="0" nullsFirst="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style textColor="0,0,0,255" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" isExpression="1" previewBkgrdColor="#ffffff" fontSizeUnit="Point" fontLetterSpacing="0" fontItalic="1" blendMode="0" fontWordSpacing="0" fontUnderline="0" useSubstitutions="0" multilineHeight="1" fontSize="8" textOpacity="1" fontWeight="50" fontCapitals="0" fontFamily="Noto Sans" namedStyle="Italic" fontStrikeout="0">
        <text-buffer bufferSize="0.5" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferJoinStyle="128" bufferNoFill="1" bufferDraw="1" bufferColor="255,255,255,255" bufferBlendMode="0" bufferSizeUnits="MM"/>
        <background shapeBorderColor="128,128,128,255" shapeOpacity="1" shapeRadiiY="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeSVGFile="" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidth="0" shapeSizeX="0" shapeJoinStyle="64" shapeBlendMode="0" shapeSizeY="0" shapeRadiiX="0" shapeRadiiUnit="MM" shapeOffsetX="0" shapeFillColor="255,255,255,255" shapeSizeUnit="MM" shapeRotationType="0" shapeOffsetUnit="MM" shapeSizeType="0" shapeBorderWidthUnit="MM" shapeType="0" shapeDraw="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0"/>
        <shadow shadowOffsetUnit="MM" shadowRadiusAlphaOnly="0" shadowDraw="0" shadowUnder="0" shadowOffsetGlobal="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOpacity="0.7" shadowOffsetDist="1" shadowOffsetAngle="135" shadowBlendMode="6" shadowRadiusUnit="MM" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5" shadowColor="0,0,0,255"/>
        <substitutions/>
      </text-style>
      <text-format placeDirectionSymbol="0" addDirectionSymbol="0" plussign="0" useMaxLineLengthForAutoWrap="1" formatNumbers="0" multilineAlign="3" reverseDirectionSymbol="0" decimals="3" wrapChar="" leftDirectionSymbol="&lt;" rightDirectionSymbol=">" autoWrapLength="0"/>
      <placement rotationAngle="0" centroidInside="0" offsetType="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" fitInPolygonOnly="0" offsetUnits="MM" geometryGenerator="" geometryGeneratorEnabled="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" distUnits="MM" maxCurvedCharAngleIn="25" distMapUnitScale="3x:0,0,0,0,0,0" xOffset="0" dist="0" quadOffset="4" maxCurvedCharAngleOut="-25" geometryGeneratorType="PointGeometry" centroidWhole="0" placementFlags="10" placement="0" repeatDistance="0" priority="5" repeatDistanceUnits="MM" preserveRotation="1" yOffset="0"/>
      <rendering fontLimitPixelSize="0" labelPerPart="0" scaleMax="0" zIndex="0" displayAll="0" maxNumLabels="2000" scaleMin="0" upsidedownLabels="0" minFeatureSize="0" scaleVisibility="0" fontMaxPixelSize="10000" mergeLines="0" drawLabels="1" limitNumLabels="0" obstacleFactor="1" obstacle="1" fontMinPixelSize="3" obstacleType="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" type="QString" name="name"/>
          <Option name="properties"/>
          <Option value="collection" type="QString" name="type"/>
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
    <DiagramCategory opacity="1" minScaleDenominator="0" minimumSize="0" rotationOffset="270" penColor="#000000" diagramOrientation="Up" maxScaleDenominator="1e+8" backgroundAlpha="255" height="15" scaleBasedVisibility="0" lineSizeType="MM" scaleDependency="Area" lineSizeScale="3x:0,0,0,0,0,0" backgroundColor="#ffffff" labelPlacementMethod="XHeight" width="15" enabled="0" sizeScale="3x:0,0,0,0,0,0" penAlpha="255" sizeType="MM" penWidth="0" barWidth="5">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" label="" color="#000000"/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" showAll="1" dist="0" zIndex="0" placement="0" priority="0" obstacle="0">
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
    <field name="soildepthh">
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
    <alias index="0" field="obsid" name=""/>
    <alias index="1" field="h_toc" name=""/>
    <alias index="2" field="h_gs" name=""/>
    <alias index="3" field="h_tocags" name=""/>
    <alias index="4" field="length" name=""/>
    <alias index="5" field="h_syst" name=""/>
    <alias index="6" field="ground_surface" name=""/>
    <alias index="7" field="soildepthh" name=""/>
    <alias index="8" field="bedrock" name=""/>
    <alias index="9" field="drillstop" name=""/>
    <alias index="10" field="bedrock_from_table" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="obsid" applyOnUpdate="0"/>
    <default expression="" field="h_toc" applyOnUpdate="0"/>
    <default expression="" field="h_gs" applyOnUpdate="0"/>
    <default expression="" field="h_tocags" applyOnUpdate="0"/>
    <default expression="" field="length" applyOnUpdate="0"/>
    <default expression="" field="h_syst" applyOnUpdate="0"/>
    <default expression="" field="ground_surface" applyOnUpdate="0"/>
    <default expression="" field="soildepthh" applyOnUpdate="0"/>
    <default expression="" field="bedrock" applyOnUpdate="0"/>
    <default expression="" field="drillstop" applyOnUpdate="0"/>
    <default expression="" field="bedrock_from_table" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" notnull_strength="0" field="obsid" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="h_toc" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="h_gs" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="h_tocags" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="length" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="h_syst" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="ground_surface" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="soildepthh" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="bedrock" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="drillstop" constraints="0" exp_strength="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="bedrock_from_table" constraints="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="obsid" exp=""/>
    <constraint desc="" field="h_toc" exp=""/>
    <constraint desc="" field="h_gs" exp=""/>
    <constraint desc="" field="h_tocags" exp=""/>
    <constraint desc="" field="length" exp=""/>
    <constraint desc="" field="h_syst" exp=""/>
    <constraint desc="" field="ground_surface" exp=""/>
    <constraint desc="" field="soildepthh" exp=""/>
    <constraint desc="" field="bedrock" exp=""/>
    <constraint desc="" field="drillstop" exp=""/>
    <constraint desc="" field="bedrock_from_table" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="1" actionWidgetStyle="dropDown" sortExpression="&quot;soildepthh&quot;">
    <columns>
      <column width="-1" hidden="0" type="field" name="obsid"/>
      <column width="-1" hidden="1" type="actions"/>
      <column width="-1" hidden="0" type="field" name="drillstop"/>
      <column width="-1" hidden="0" type="field" name="h_toc"/>
      <column width="-1" hidden="0" type="field" name="h_gs"/>
      <column width="-1" hidden="0" type="field" name="h_tocags"/>
      <column width="-1" hidden="0" type="field" name="length"/>
      <column width="-1" hidden="0" type="field" name="h_syst"/>
      <column width="-1" hidden="0" type="field" name="ground_surface"/>
      <column width="-1" hidden="0" type="field" name="soildepthh"/>
      <column width="-1" hidden="0" type="field" name="bedrock"/>
      <column width="-1" hidden="0" type="field" name="bedrock_from_table"/>
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
    <field labelOnTop="0" name="soildepthh"/>
    <field labelOnTop="0" name="stratid"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
