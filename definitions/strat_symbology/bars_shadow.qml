<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="0" simplifyDrawingHints="0" hasScaleBasedVisibilityFlag="0" readOnly="0" version="3.16.3-Hannover" simplifyDrawingTol="1" simplifyAlgorithm="0" simplifyLocal="1" styleCategories="AllStyleCategories" simplifyMaxScale="1" maxScale="0" minScale="100000000">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endField="" durationUnit="min" fixedDuration="0" mode="0" accumulate="0" startExpression="" enabled="0" endExpression="" startField="" durationField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 enableorderby="1" forceraster="0" symbollevels="0" type="RuleRenderer">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule label="shadow" filter=" &quot;maxdepthbot&quot;  =  &quot;depthbot&quot; " symbol="0" key="{c3dbe822-681b-4001-8689-efe1cccb461b}"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" alpha="1" clip_to_extent="1" name="0" type="marker">
        <layer pass="0" class="GeometryGenerator" locked="0" enabled="1">
          <prop v="Fill" k="SymbolType"/>
          <prop v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8, %9 %10))', &#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry), &#xa;X($geometry)+1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale /**{yfactor}*/,&#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry) - &quot;depthbot&quot;*0.001*@map_scale /**{yfactor}*/,&#xa;X($geometry)-1.5*0.001*@map_scale /**{xfactor}*/, Y($geometry)))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" alpha="1" clip_to_extent="1" name="@0@0" type="fill">
            <layer pass="0" class="SimpleFill" locked="0" enabled="1">
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
              <effect enabled="1" type="effectStack">
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
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="0.4" k="opacity"/>
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
      <orderByClause nullsFirst="0" asc="1">"maxdepthbot"</orderByClause>
      <orderByClause nullsFirst="0" asc="0">"depthbot"</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontWordSpacing="0" namedStyle="Italic" multilineHeight="1" fontSizeUnit="Point" fontKerning="1" useSubstitutions="0" fontSize="8" fontUnderline="0" capitalization="0" blendMode="0" fontFamily="Noto Sans" textColor="0,0,0,255" isExpression="1" textOrientation="horizontal" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" fontStrikeout="0" fontItalic="1" textOpacity="1" allowHtml="0" fontWeight="50" fontLetterSpacing="0" previewBkgrdColor="255,255,255,255">
        <text-buffer bufferSize="0.5" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="255,255,255,255" bufferDraw="1" bufferOpacity="1" bufferJoinStyle="128" bufferSizeUnits="MM" bufferBlendMode="0"/>
        <text-mask maskEnabled="0" maskSizeUnits="MM" maskOpacity="1" maskedSymbolLayers="" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskType="0" maskSize="0" maskJoinStyle="128"/>
        <background shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeFillColor="255,255,255,255" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeRotation="0" shapeSizeY="0" shapeOffsetUnit="MM" shapeSizeUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeType="0" shapeBorderWidthUnit="MM" shapeType="0" shapeOpacity="1" shapeBlendMode="0" shapeSVGFile="" shapeRadiiY="0" shapeJoinStyle="64" shapeBorderColor="128,128,128,255" shapeOffsetX="0" shapeBorderWidth="0" shapeRotationType="0" shapeOffsetY="0" shapeSizeX="0"/>
        <shadow shadowScale="100" shadowUnder="0" shadowOffsetDist="1" shadowColor="0,0,0,255" shadowBlendMode="6" shadowOffsetGlobal="1" shadowRadiusAlphaOnly="0" shadowRadiusUnit="MM" shadowOffsetAngle="135" shadowRadius="1.5" shadowDraw="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetUnit="MM" shadowOpacity="0.7" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0"/>
        <dd_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format decimals="3" reverseDirectionSymbol="0" formatNumbers="0" useMaxLineLengthForAutoWrap="1" plussign="0" addDirectionSymbol="0" wrapChar="" placeDirectionSymbol="0" leftDirectionSymbol="&lt;" multilineAlign="3" rightDirectionSymbol=">" autoWrapLength="0"/>
      <placement labelOffsetMapUnitScale="3x:0,0,0,0,0,0" polygonPlacementFlags="2" maxCurvedCharAngleIn="25" geometryGeneratorType="PointGeometry" offsetType="0" geometryGeneratorEnabled="0" lineAnchorType="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" yOffset="0" fitInPolygonOnly="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" dist="0" offsetUnits="RenderMetersInMapUnits" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" layerType="UnknownGeometry" centroidInside="0" overrunDistanceUnit="MM" lineAnchorPercent="0.5" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" preserveRotation="1" distMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" overrunDistance="0" xOffset="3" distUnits="MM" repeatDistanceUnits="MM" centroidWhole="0" maxCurvedCharAngleOut="-25" quadOffset="2" rotationAngle="0" placement="1" priority="5"/>
      <rendering obstacleFactor="1" maxNumLabels="2000" obstacle="1" zIndex="0" displayAll="1" minFeatureSize="0" fontMinPixelSize="3" mergeLines="0" scaleMax="0" upsidedownLabels="0" fontLimitPixelSize="0" scaleMin="0" scaleVisibility="0" fontMaxPixelSize="10000" labelPerPart="0" obstacleType="0" limitNumLabels="0" drawLabels="1"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
          <Option name="ddProperties" type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
          <Option value="false" name="drawToAllParts" type="bool"/>
          <Option value="0" name="enabled" type="QString"/>
          <Option value="point_on_exterior" name="labelAnchorPoint" type="QString"/>
          <Option value="&lt;symbol force_rhr=&quot;0&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot; name=&quot;symbol&quot; type=&quot;line&quot;>&lt;layer pass=&quot;0&quot; class=&quot;SimpleLine&quot; locked=&quot;0&quot; enabled=&quot;1&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol" type="QString"/>
          <Option value="0" name="minLength" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale" type="QString"/>
          <Option value="MM" name="minLengthUnit" type="QString"/>
          <Option value="0" name="offsetFromAnchor" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromAnchorUnit" type="QString"/>
          <Option value="0" name="offsetFromLabel" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromLabelUnit" type="QString"/>
        </Option>
      </callout>
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
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory sizeScale="3x:0,0,0,0,0,0" enabled="0" maxScaleDenominator="1e+8" spacingUnitScale="3x:0,0,0,0,0,0" sizeType="MM" height="15" penColor="#000000" lineSizeType="MM" direction="1" penAlpha="255" opacity="1" scaleDependency="Area" backgroundColor="#ffffff" scaleBasedVisibility="0" backgroundAlpha="255" rotationOffset="270" spacingUnit="MM" labelPlacementMethod="XHeight" penWidth="0" lineSizeScale="3x:0,0,0,0,0,0" showAxis="0" diagramOrientation="Up" minimumSize="0" barWidth="5" minScaleDenominator="0" width="15" spacing="0">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
      <axisSymbol>
        <symbol force_rhr="0" alpha="1" clip_to_extent="1" name="" type="line">
          <layer pass="0" class="SimpleLine" locked="0" enabled="1">
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
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" showAll="1" priority="0" dist="0" placement="0" obstacle="0" zIndex="0">
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
    <alias index="0" name="" field="rowid"/>
    <alias index="1" name="" field="obsid"/>
    <alias index="2" name="" field="maxdepthbot"/>
    <alias index="3" name="" field="stratid"/>
    <alias index="4" name="" field="depthtop"/>
    <alias index="5" name="" field="depthbot"/>
    <alias index="6" name="" field="geology"/>
    <alias index="7" name="" field="geoshort"/>
    <alias index="8" name="" field="capacity"/>
    <alias index="9" name="" field="development"/>
    <alias index="10" name="" field="comment"/>
  </aliases>
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
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="rowid"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="obsid"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="maxdepthbot"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="stratid"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="depthtop"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="depthbot"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="geology"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="geoshort"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="capacity"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="development"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0" field="comment"/>
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
  <attributetableconfig sortExpression="&quot;stratid&quot;" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column hidden="0" name="obsid" width="-1" type="field"/>
      <column hidden="0" name="stratid" width="-1" type="field"/>
      <column hidden="0" name="depthtop" width="-1" type="field"/>
      <column hidden="0" name="depthbot" width="-1" type="field"/>
      <column hidden="0" name="geology" width="-1" type="field"/>
      <column hidden="0" name="geoshort" width="-1" type="field"/>
      <column hidden="0" name="capacity" width="-1" type="field"/>
      <column hidden="0" name="development" width="-1" type="field"/>
      <column hidden="0" name="comment" width="-1" type="field"/>
      <column hidden="1" width="-1" type="actions"/>
      <column hidden="0" name="maxdepthbot" width="-1" type="field"/>
      <column hidden="0" name="rowid" width="-1" type="field"/>
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
