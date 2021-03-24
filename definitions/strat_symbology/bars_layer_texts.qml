<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" minScale="100000000" labelsEnabled="1" version="3.16.3-Hannover" simplifyDrawingTol="1" styleCategories="AllStyleCategories" simplifyAlgorithm="0" readOnly="0" simplifyLocal="1" simplifyDrawingHints="0" hasScaleBasedVisibilityFlag="0" simplifyMaxScale="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal enabled="0" durationField="" accumulate="0" startExpression="" endField="" startField="" endExpression="" fixedDuration="0" mode="0" durationUnit="min">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="nullSymbol"/>
  <labeling type="rule-based">
    <rules key="{d4c53ed6-10be-4587-bc74-3b31f51fbc7c}">
      <rule key="{014bc626-1e19-48f1-a6b2-3a2675c5217b}">
        <settings calloutType="simple">
          <text-style previewBkgrdColor="255,255,255,255" allowHtml="0" isExpression="0" fontSizeUnit="Point" fontStrikeout="0" fontWordSpacing="0" multilineHeight="1" capitalization="0" fontWeight="50" fontKerning="1" textOpacity="1" fieldName="geology" fontLetterSpacing="0" blendMode="0" textOrientation="horizontal" fontItalic="1" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSize="6" fontUnderline="0" textColor="0,0,0,255" useSubstitutions="0" namedStyle="Italic" fontFamily="Noto Sans">
            <text-buffer bufferSizeUnits="MM" bufferOpacity="1" bufferJoinStyle="128" bufferDraw="1" bufferColor="255,255,255,255" bufferNoFill="1" bufferBlendMode="0" bufferSize="0.5" bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <text-mask maskSize="0" maskEnabled="0" maskJoinStyle="128" maskSizeUnits="MM" maskOpacity="1" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskType="0" maskedSymbolLayers=""/>
            <background shapeOffsetUnit="MM" shapeRadiiUnit="MM" shapeType="0" shapeBorderWidthUnit="MM" shapeOffsetY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeY="0" shapeBorderWidth="0" shapeSVGFile="" shapeSizeType="0" shapeDraw="0" shapeBlendMode="0" shapeOffsetX="0" shapeRotationType="0" shapeSizeUnit="MM" shapeJoinStyle="64" shapeSizeX="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderColor="128,128,128,255" shapeRotation="0" shapeRadiiX="0" shapeRadiiY="0" shapeFillColor="255,255,255,255">
              <symbol alpha="1" force_rhr="0" type="marker" clip_to_extent="1" name="markerSymbol">
                <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
                  <prop k="angle" v="0"/>
                  <prop k="color" v="225,89,137,255"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="name" v="circle"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="scale_method" v="diameter"/>
                  <prop k="size" v="2"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="MM"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowDraw="0" shadowUnder="0" shadowOffsetGlobal="1" shadowOffsetUnit="MM" shadowOffsetDist="1" shadowBlendMode="6" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowRadius="1.5" shadowRadiusUnit="MM" shadowColor="0,0,0,255" shadowOffsetAngle="135" shadowOpacity="0.7" shadowScale="100" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0"/>
            <dd_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format wrapChar="" rightDirectionSymbol=">" formatNumbers="0" decimals="3" useMaxLineLengthForAutoWrap="1" plussign="0" addDirectionSymbol="0" placeDirectionSymbol="0" autoWrapLength="0" multilineAlign="3" reverseDirectionSymbol="0" leftDirectionSymbol="&lt;"/>
          <placement labelOffsetMapUnitScale="3x:0,0,0,0,0,0" priority="5" xOffset="3" offsetType="0" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" distUnits="MM" polygonPlacementFlags="2" fitInPolygonOnly="0" repeatDistance="0" lineAnchorPercent="0.5" layerType="PointGeometry" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="RenderMetersInMapUnits" quadOffset="2" placement="1" centroidInside="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" maxCurvedCharAngleIn="25" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" yOffset="0" repeatDistanceUnits="MM" preserveRotation="1" overrunDistance="0" dist="0" maxCurvedCharAngleOut="-25" geometryGeneratorType="PointGeometry" placementFlags="10" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" rotationAngle="0" geometryGeneratorEnabled="0" overrunDistanceUnit="MM"/>
          <rendering fontMinPixelSize="3" drawLabels="1" displayAll="1" minFeatureSize="0" upsidedownLabels="0" zIndex="0" obstacleType="0" scaleVisibility="0" mergeLines="0" scaleMax="0" fontMaxPixelSize="10000" labelPerPart="0" limitNumLabels="0" obstacleFactor="1" fontLimitPixelSize="0" obstacle="1" scaleMin="0" maxNumLabels="2000"/>
          <dd_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="Hali">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="'Right'" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
                <Option type="Map" name="PositionX">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="X($geometry)-2*0.001*@map_scale /**{xfactor}*/" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
                <Option type="Map" name="PositionY">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="Y($geometry) - ( &quot;depthtop&quot; )*0.001*@map_scale /**{yfactor}*/" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
                <Option type="Map" name="Vali">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="'Top'" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
              </Option>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option type="QString" value="pole_of_inaccessibility" name="anchorPoint"/>
              <Option type="Map" name="ddProperties">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
              <Option type="bool" value="false" name="drawToAllParts"/>
              <Option type="QString" value="0" name="enabled"/>
              <Option type="QString" value="point_on_exterior" name="labelAnchorPoint"/>
              <Option type="QString" value="&lt;symbol alpha=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; clip_to_extent=&quot;1&quot; name=&quot;symbol&quot;>&lt;layer locked=&quot;0&quot; enabled=&quot;1&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot;>&lt;prop k=&quot;align_dash_pattern&quot; v=&quot;0&quot;/>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;dash_pattern_offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;dash_pattern_offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;dash_pattern_offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;tweak_dash_pattern_on_corners&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol"/>
              <Option type="double" value="0" name="minLength"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale"/>
              <Option type="QString" value="MM" name="minLengthUnit"/>
              <Option type="double" value="0" name="offsetFromAnchor"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale"/>
              <Option type="QString" value="MM" name="offsetFromAnchorUnit"/>
              <Option type="double" value="0" name="offsetFromLabel"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale"/>
              <Option type="QString" value="MM" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
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
    <DiagramCategory rotationOffset="270" spacingUnit="MM" labelPlacementMethod="XHeight" opacity="1" scaleDependency="Area" enabled="0" showAxis="0" penWidth="0" lineSizeScale="3x:0,0,0,0,0,0" spacingUnitScale="3x:0,0,0,0,0,0" penColor="#000000" spacing="0" penAlpha="255" barWidth="5" backgroundAlpha="255" height="15" sizeScale="3x:0,0,0,0,0,0" direction="1" backgroundColor="#ffffff" maxScaleDenominator="1e+8" width="15" minScaleDenominator="0" diagramOrientation="Up" scaleBasedVisibility="0" sizeType="MM" lineSizeType="MM" minimumSize="0">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol alpha="1" force_rhr="0" type="line" clip_to_extent="1" name="">
          <layer locked="0" enabled="1" class="SimpleLine" pass="0">
            <prop k="align_dash_pattern" v="0"/>
            <prop k="capstyle" v="square"/>
            <prop k="customdash" v="5;2"/>
            <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="customdash_unit" v="MM"/>
            <prop k="dash_pattern_offset" v="0"/>
            <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="dash_pattern_offset_unit" v="MM"/>
            <prop k="draw_inside_polygon" v="0"/>
            <prop k="joinstyle" v="bevel"/>
            <prop k="line_color" v="35,35,35,255"/>
            <prop k="line_style" v="solid"/>
            <prop k="line_width" v="0.26"/>
            <prop k="line_width_unit" v="MM"/>
            <prop k="offset" v="0"/>
            <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="offset_unit" v="MM"/>
            <prop k="ring_filter" v="0"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings priority="0" obstacle="0" zIndex="0" showAll="1" placement="0" dist="0" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="rowid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="obsid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="maxdepthbot">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="stratid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="depthtop">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="depthbot">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="geology">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="geoshort">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="capacity">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="development">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="comment">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="rowid" index="0" name=""/>
    <alias field="obsid" index="1" name=""/>
    <alias field="maxdepthbot" index="2" name=""/>
    <alias field="stratid" index="3" name=""/>
    <alias field="depthtop" index="4" name=""/>
    <alias field="depthbot" index="5" name=""/>
    <alias field="geology" index="6" name=""/>
    <alias field="geoshort" index="7" name=""/>
    <alias field="capacity" index="8" name=""/>
    <alias field="development" index="9" name=""/>
    <alias field="comment" index="10" name=""/>
  </aliases>
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
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="rowid" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="obsid" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="maxdepthbot" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="stratid" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="depthtop" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="depthbot" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="geology" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="geoshort" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="capacity" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="development" exp_strength="0"/>
    <constraint constraints="0" notnull_strength="0" unique_strength="0" field="comment" exp_strength="0"/>
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
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="&quot;stratid&quot;">
    <columns>
      <column type="field" hidden="0" name="obsid" width="-1"/>
      <column type="field" hidden="0" name="stratid" width="-1"/>
      <column type="field" hidden="0" name="depthtop" width="-1"/>
      <column type="field" hidden="0" name="depthbot" width="-1"/>
      <column type="field" hidden="0" name="geology" width="-1"/>
      <column type="field" hidden="0" name="geoshort" width="-1"/>
      <column type="field" hidden="0" name="capacity" width="-1"/>
      <column type="field" hidden="0" name="development" width="-1"/>
      <column type="field" hidden="0" name="comment" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" hidden="0" name="maxdepthbot" width="-1"/>
      <column type="field" hidden="0" name="rowid" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
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
    <field labelOnTop="0" name="rowid"/>
    <field labelOnTop="0" name="stratid"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"obsid"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
