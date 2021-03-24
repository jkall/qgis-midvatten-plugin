<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" simplifyDrawingTol="1" simplifyLocal="1" minScale="100000000" hasScaleBasedVisibilityFlag="0" readOnly="0" styleCategories="AllStyleCategories" simplifyAlgorithm="0" simplifyMaxScale="1" labelsEnabled="0" simplifyDrawingHints="0" version="3.16.3-Hannover">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal durationField="" enabled="0" endField="" durationUnit="min" startField="" accumulate="0" startExpression="" mode="0" fixedDuration="0" endExpression="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="RuleRenderer" forceraster="0" enableorderby="1" symbollevels="0">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule filter="ELSE" key="{49f89c60-14dd-4f60-9818-0f1ae27fffd0}" symbol="0"/>
    </rules>
    <symbols>
      <symbol type="marker" clip_to_extent="1" name="0" alpha="1" force_rhr="0">
        <layer enabled="1" class="GeometryGenerator" locked="0" pass="0">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8, %1 %2))', &#xa;X($geometry)-1.5 /**{map_scale}*/ /**{xfactor}*/, Y($geometry) - &quot;depthtop&quot; /**{map_scale}*/ /**{yfactor}*/, &#xa;X($geometry)+1.5 /**{map_scale}*/ /**{xfactor}*/, Y($geometry) - &quot;depthtop&quot; /**{map_scale}*/ /**{yfactor}*/, &#xa;X($geometry)+1.5 /**{map_scale}*/ /**{xfactor}*/, Y($geometry) - &quot;depthbot&quot; /**{map_scale}*/ /**{yfactor}*/,&#xa;X($geometry)-1.5 /**{map_scale}*/ /**{xfactor}*/, Y($geometry) - &quot;depthbot&quot; /**{map_scale}*/ /**{yfactor}*/))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" clip_to_extent="1" name="@0@0" alpha="1" force_rhr="0">
            <layer enabled="1" class="SimpleFill" locked="0" pass="0">
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
    <settings calloutType="simple">
      <text-style fontSizeUnit="Point" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontFamily="Noto Sans" fontLetterSpacing="0" useSubstitutions="0" textOrientation="horizontal" previewBkgrdColor="255,255,255,255" fontWeight="50" fontItalic="1" fontWordSpacing="0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" multilineHeight="1" fontKerning="1" isExpression="1" namedStyle="Italic" fontUnderline="0" fontSize="8" textColor="0,0,0,255" textOpacity="1" blendMode="0" fontStrikeout="0" allowHtml="0" capitalization="0">
        <text-buffer bufferJoinStyle="128" bufferBlendMode="0" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="255,255,255,255" bufferSize="0.5" bufferDraw="1" bufferNoFill="1" bufferOpacity="1"/>
        <text-mask maskJoinStyle="128" maskOpacity="1" maskSizeUnits="MM" maskEnabled="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskType="0" maskSize="0" maskedSymbolLayers=""/>
        <background shapeSizeY="0" shapeBorderColor="128,128,128,255" shapeOffsetY="0" shapeBlendMode="0" shapeOffsetUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeSizeX="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeRadiiUnit="MM" shapeBorderWidth="0" shapeSizeType="0" shapeOpacity="1" shapeFillColor="255,255,255,255" shapeSizeUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeSVGFile="" shapeType="0" shapeRadiiX="0" shapeRotation="0" shapeRotationType="0"/>
        <shadow shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowBlendMode="6" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowOffsetUnit="MM" shadowOffsetDist="1" shadowScale="100" shadowOffsetAngle="135" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowUnder="0" shadowDraw="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" reverseDirectionSymbol="0" autoWrapLength="0" wrapChar="" rightDirectionSymbol=">" placeDirectionSymbol="0" decimals="3" formatNumbers="0" multilineAlign="3" leftDirectionSymbol="&lt;" plussign="0"/>
      <placement labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" quadOffset="2" priority="5" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" centroidWhole="0" preserveRotation="1" overrunDistanceUnit="MM" maxCurvedCharAngleOut="-25" placementFlags="10" maxCurvedCharAngleIn="25" lineAnchorPercent="0.5" repeatDistance="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" layerType="UnknownGeometry" yOffset="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" placement="1" rotationAngle="0" polygonPlacementFlags="2" overrunDistance="0" lineAnchorType="0" geometryGeneratorType="PointGeometry" fitInPolygonOnly="0" centroidInside="0" dist="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" offsetUnits="RenderMetersInMapUnits" xOffset="3" repeatDistanceUnits="MM" distUnits="MM"/>
      <rendering displayAll="1" minFeatureSize="0" zIndex="0" mergeLines="0" upsidedownLabels="0" fontLimitPixelSize="0" scaleMax="0" obstacle="1" fontMinPixelSize="3" scaleVisibility="0" fontMaxPixelSize="10000" limitNumLabels="0" obstacleType="0" scaleMin="0" labelPerPart="0" maxNumLabels="2000" drawLabels="1" obstacleFactor="1"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" name="anchorPoint" value="pole_of_inaccessibility"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
          <Option type="bool" name="drawToAllParts" value="false"/>
          <Option type="QString" name="enabled" value="0"/>
          <Option type="QString" name="labelAnchorPoint" value="point_on_exterior"/>
          <Option type="QString" name="lineSymbol" value="&lt;symbol type=&quot;line&quot; clip_to_extent=&quot;1&quot; name=&quot;symbol&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot;>&lt;layer enabled=&quot;1&quot; class=&quot;SimpleLine&quot; locked=&quot;0&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
          <Option type="double" name="minLength" value="0"/>
          <Option type="QString" name="minLengthMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="minLengthUnit" value="MM"/>
          <Option type="double" name="offsetFromAnchor" value="0"/>
          <Option type="QString" name="offsetFromAnchorMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromAnchorUnit" value="MM"/>
          <Option type="double" name="offsetFromLabel" value="0"/>
          <Option type="QString" name="offsetFromLabelMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromLabelUnit" value="MM"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <customproperties>
    <property key="dualview/previewExpressions" value="obsid"/>
    <property key="embeddedWidgets/0/id" value="transparency"/>
    <property key="embeddedWidgets/count" value="1"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory scaleDependency="Area" diagramOrientation="Up" lineSizeScale="3x:0,0,0,0,0,0" spacingUnitScale="3x:0,0,0,0,0,0" penWidth="0" direction="1" scaleBasedVisibility="0" sizeType="MM" rotationOffset="270" sizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" minScaleDenominator="0" enabled="0" opacity="1" spacingUnit="MM" spacing="0" backgroundAlpha="255" penAlpha="255" lineSizeType="MM" width="15" penColor="#000000" backgroundColor="#ffffff" maxScaleDenominator="1e+8" height="15" showAxis="0" barWidth="5" minimumSize="0">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol type="line" clip_to_extent="1" name="" alpha="1" force_rhr="0">
          <layer enabled="1" class="SimpleLine" locked="0" pass="0">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
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
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" priority="0" zIndex="0" linePlacementFlags="18" dist="0" obstacle="0" placement="0">
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
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="rowid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="obsid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="maxdepthbot" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="stratid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="depthtop" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="depthbot" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="geology" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="geoshort" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="capacity" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="development" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="comment" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="rowid" name="" index="0"/>
    <alias field="obsid" name="" index="1"/>
    <alias field="maxdepthbot" name="" index="2"/>
    <alias field="stratid" name="" index="3"/>
    <alias field="depthtop" name="" index="4"/>
    <alias field="depthbot" name="" index="5"/>
    <alias field="geology" name="" index="6"/>
    <alias field="geoshort" name="" index="7"/>
    <alias field="capacity" name="" index="8"/>
    <alias field="development" name="" index="9"/>
    <alias field="comment" name="" index="10"/>
  </aliases>
  <defaults>
    <default field="rowid" expression="" applyOnUpdate="0"/>
    <default field="obsid" expression="" applyOnUpdate="0"/>
    <default field="maxdepthbot" expression="" applyOnUpdate="0"/>
    <default field="stratid" expression="" applyOnUpdate="0"/>
    <default field="depthtop" expression="" applyOnUpdate="0"/>
    <default field="depthbot" expression="" applyOnUpdate="0"/>
    <default field="geology" expression="" applyOnUpdate="0"/>
    <default field="geoshort" expression="" applyOnUpdate="0"/>
    <default field="capacity" expression="" applyOnUpdate="0"/>
    <default field="development" expression="" applyOnUpdate="0"/>
    <default field="comment" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="rowid" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="obsid" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="maxdepthbot" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="stratid" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="depthtop" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="depthbot" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="geology" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="geoshort" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="capacity" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="development" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
    <constraint field="comment" notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0"/>
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
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="&quot;stratid&quot;" actionWidgetStyle="dropDown">
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
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"obsid"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
