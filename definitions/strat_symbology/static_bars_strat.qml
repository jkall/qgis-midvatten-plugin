<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" simplifyLocal="1" simplifyMaxScale="1" simplifyDrawingHints="0" version="3.16.3-Hannover" labelsEnabled="0" hasScaleBasedVisibilityFlag="0" minScale="100000000" simplifyAlgorithm="0" simplifyDrawingTol="1" maxScale="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal mode="0" startExpression="" durationField="" accumulate="0" endField="" enabled="0" startField="" endExpression="" durationUnit="min" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 symbollevels="0" enableorderby="1" type="RuleRenderer" forceraster="0">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule filter="ELSE" symbol="0" key="{49f89c60-14dd-4f60-9818-0f1ae27fffd0}"/>
    </rules>
    <symbols>
      <symbol alpha="1" force_rhr="0" name="0" type="marker" clip_to_extent="1">
        <layer enabled="1" pass="0" locked="0" class="GeometryGenerator">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8, %9 %10))', &#xa;X($geometry)-2 /**{xfactor}*/, Y($geometry) - &quot;depthtop&quot; /**{yfactor}*/, &#xa;X($geometry)+2 /**{xfactor}*/, Y($geometry) - &quot;depthtop&quot; /**{yfactor}*/, &#xa;X($geometry)+2 /**{xfactor}*/, Y($geometry) - &quot;depthbot&quot; /**{yfactor}*/,&#xa;X($geometry)-2 /**{xfactor}*/, Y($geometry) - &quot;depthbot&quot; /**{yfactor}*/,&#xa;X($geometry)-2 /**{xfactor}*/, Y($geometry) - &quot;depthtop&quot; /**{yfactor}*/))&#xa;"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" force_rhr="0" name="@0@0" type="fill" clip_to_extent="1">
            <layer enabled="1" pass="0" locked="0" class="SimpleFill">
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
    <settings calloutType="simple">
      <text-style fontItalic="1" capitalization="0" fieldName="CASE WHEN  &quot;stratid&quot; = 1 THEN &quot;obsid&quot; ELSE '' END" isExpression="1" fontUnderline="0" blendMode="0" textOpacity="1" fontKerning="1" fontLetterSpacing="0" fontFamily="Noto Sans" multilineHeight="1" namedStyle="Italic" textOrientation="horizontal" allowHtml="0" fontStrikeout="0" useSubstitutions="0" fontSize="8" fontWordSpacing="0" textColor="0,0,0,255" previewBkgrdColor="255,255,255,255" fontSizeUnit="Point" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontWeight="50">
        <text-buffer bufferOpacity="1" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferDraw="1" bufferColor="255,255,255,255" bufferJoinStyle="128" bufferSize="0.5" bufferNoFill="1" bufferBlendMode="0"/>
        <text-mask maskedSymbolLayers="" maskSizeUnits="MM" maskJoinStyle="128" maskEnabled="0" maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskOpacity="1" maskType="0"/>
        <background shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeSizeX="0" shapeSVGFile="" shapeSizeY="0" shapeFillColor="255,255,255,255" shapeOffsetX="0" shapeBlendMode="0" shapeType="0" shapeBorderWidthUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeJoinStyle="64" shapeSizeUnit="MM" shapeRadiiY="0" shapeRadiiX="0" shapeRadiiUnit="MM" shapeBorderColor="128,128,128,255" shapeRotation="0" shapeOffsetY="0" shapeOffsetUnit="MM" shapeRotationType="0" shapeSizeType="0" shapeBorderWidth="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0"/>
        <shadow shadowOffsetDist="1" shadowRadius="1.5" shadowScale="100" shadowColor="0,0,0,255" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowBlendMode="6" shadowOffsetGlobal="1" shadowOffsetUnit="MM" shadowOpacity="0.7" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0"/>
        <dd_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format formatNumbers="0" multilineAlign="3" decimals="3" addDirectionSymbol="0" reverseDirectionSymbol="0" wrapChar="" rightDirectionSymbol=">" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" autoWrapLength="0" useMaxLineLengthForAutoWrap="1" plussign="0"/>
      <placement placementFlags="10" geometryGeneratorEnabled="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" offsetType="0" preserveRotation="1" distMapUnitScale="3x:0,0,0,0,0,0" priority="5" overrunDistance="0" placement="1" quadOffset="2" centroidWhole="0" lineAnchorPercent="0.5" centroidInside="0" fitInPolygonOnly="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleOut="-25" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" repeatDistance="0" lineAnchorType="0" geometryGeneratorType="PointGeometry" distUnits="MM" rotationAngle="0" dist="0" polygonPlacementFlags="2" repeatDistanceUnits="MM" xOffset="3" geometryGenerator="geom_from_wkt( format('POINT(%1 %2)', &#xa;X($geometry), Y($geometry) - &quot;meas&quot; + &quot;h_tocags&quot;))" yOffset="0" offsetUnits="RenderMetersInMapUnits" maxCurvedCharAngleIn="25" layerType="UnknownGeometry"/>
      <rendering maxNumLabels="2000" displayAll="1" drawLabels="1" obstacleFactor="1" obstacle="1" minFeatureSize="0" scaleMin="0" scaleMax="0" fontMaxPixelSize="10000" scaleVisibility="0" mergeLines="0" upsidedownLabels="0" obstacleType="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" limitNumLabels="0" zIndex="0"/>
      <dd_properties>
        <Option type="Map">
          <Option name="name" type="QString" value=""/>
          <Option name="properties"/>
          <Option name="type" type="QString" value="collection"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
          <Option name="ddProperties" type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
          <Option name="drawToAllParts" type="bool" value="false"/>
          <Option name="enabled" type="QString" value="0"/>
          <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
          <Option name="lineSymbol" type="QString" value="&lt;symbol alpha=&quot;1&quot; force_rhr=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; clip_to_extent=&quot;1&quot;>&lt;layer enabled=&quot;1&quot; pass=&quot;0&quot; locked=&quot;0&quot; class=&quot;SimpleLine&quot;>&lt;prop k=&quot;align_dash_pattern&quot; v=&quot;0&quot;/>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;dash_pattern_offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;dash_pattern_offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;dash_pattern_offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;tweak_dash_pattern_on_corners&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
          <Option name="minLength" type="double" value="0"/>
          <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
          <Option name="minLengthUnit" type="QString" value="MM"/>
          <Option name="offsetFromAnchor" type="double" value="0"/>
          <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
          <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
          <Option name="offsetFromLabel" type="double" value="0"/>
          <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
          <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
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
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory penAlpha="255" spacingUnit="MM" direction="1" maxScaleDenominator="1e+8" opacity="1" rotationOffset="270" backgroundColor="#ffffff" sizeScale="3x:0,0,0,0,0,0" diagramOrientation="Up" penWidth="0" scaleDependency="Area" spacing="0" penColor="#000000" labelPlacementMethod="XHeight" spacingUnitScale="3x:0,0,0,0,0,0" showAxis="0" enabled="0" backgroundAlpha="255" minimumSize="0" width="15" minScaleDenominator="0" lineSizeScale="3x:0,0,0,0,0,0" scaleBasedVisibility="0" lineSizeType="MM" barWidth="5" sizeType="MM" height="15">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" field="" label=""/>
      <axisSymbol>
        <symbol alpha="1" force_rhr="0" name="" type="line" clip_to_extent="1">
          <layer enabled="1" pass="0" locked="0" class="SimpleLine">
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
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" priority="0" linePlacementFlags="18" obstacle="0" dist="0" placement="0" zIndex="0">
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
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="rowid" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="obsid" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="maxdepthbot" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="stratid" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="depthtop" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="depthbot" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="geology" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="geoshort" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="capacity" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="development" unique_strength="0"/>
    <constraint notnull_strength="0" constraints="0" exp_strength="0" field="comment" unique_strength="0"/>
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
