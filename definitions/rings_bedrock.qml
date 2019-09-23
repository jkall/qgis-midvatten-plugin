<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" labelsEnabled="1" minScale="1e+8" simplifyDrawingHints="0" simplifyMaxScale="1" version="3.8.3-Zanzibar" readOnly="0" styleCategories="AllStyleCategories" maxScale="0" simplifyDrawingTol="1" simplifyAlgorithm="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" symbollevels="1" enableorderby="0" type="RuleRenderer">
    <rules key="{087190a1-de22-4689-b4ec-9dd48222d5cc}">
      <rule filter="LOWER(&quot;drillstop&quot;) LIKE '%berg%' OR LOWER(&quot;drillstop&quot;) LIKE '%rock%'" label="closed ending" symbol="0" key="{eea648b8-39d7-4ba5-af39-202732daa572}"/>
      <rule filter="LOWER(&quot;drillstop&quot;) NOT LIKE '%berg%' AND LOWER(&quot;drillstop&quot;) NOT LIKE '%rock%'  OR &quot;drillstop&quot; IS NULL" label="open ended" symbol="1" key="{3418ae43-cb27-43b5-a5cd-6e3e042ef004}"/>
    </rules>
    <symbols>
      <symbol alpha="0.85" name="0" force_rhr="0" type="marker" clip_to_extent="1">
        <layer class="SimpleMarker" enabled="1" locked="0" pass="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,255,255,0"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="round"/>
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
          <prop k="size" v="4"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="soildepth" name="field" type="QString"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option value="1" name="exponent" type="double"/>
                      <Option value="10" name="maxSize" type="double"/>
                      <Option value="54.3" name="maxValue" type="double"/>
                      <Option value="1" name="minSize" type="double"/>
                      <Option value="1" name="minValue" type="double"/>
                      <Option value="0" name="nullSize" type="double"/>
                      <Option value="0" name="scaleType" type="int"/>
                    </Option>
                    <Option value="1" name="t" type="int"/>
                  </Option>
                  <Option value="2" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="0.85" name="1" force_rhr="0" type="marker" clip_to_extent="1">
        <layer class="SimpleMarker" enabled="1" locked="0" pass="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,255,255,0"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="round"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="dot"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="4"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="soildepth" name="field" type="QString"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option value="1" name="exponent" type="double"/>
                      <Option value="10" name="maxSize" type="double"/>
                      <Option value="54.3" name="maxValue" type="double"/>
                      <Option value="1" name="minSize" type="double"/>
                      <Option value="1" name="minValue" type="double"/>
                      <Option value="0" name="nullSize" type="double"/>
                      <Option value="0" name="scaleType" type="int"/>
                    </Option>
                    <Option value="1" name="t" type="int"/>
                  </Option>
                  <Option value="2" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
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
      <text-style blendMode="0" isExpression="0" fontFamily="Noto Sans" fontSizeMapUnitScale="3x:0,0,0,0,0,0" previewBkgrdColor="#ffffff" namedStyle="Italic" fontWordSpacing="0" fontStrikeout="0" fontSize="8" textColor="0,0,0,255" fontUnderline="0" multilineHeight="1" fontCapitals="0" fontWeight="50" useSubstitutions="0" fontItalic="1" fontLetterSpacing="0" textOpacity="1" fieldName="obsid" fontSizeUnit="Point">
        <text-buffer bufferSize="0.5" bufferSizeUnits="MM" bufferDraw="1" bufferJoinStyle="128" bufferColor="255,255,255,255" bufferNoFill="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferBlendMode="0"/>
        <background shapeRotationType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeJoinStyle="64" shapeBorderWidth="0" shapeSizeY="0" shapeOffsetY="0" shapeDraw="0" shapeType="0" shapeFillColor="255,255,255,255" shapeOffsetX="0" shapeRadiiUnit="MM" shapeRadiiX="0" shapeSizeType="0" shapeBorderColor="128,128,128,255" shapeSVGFile="" shapeRotation="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeSizeX="0" shapeOpacity="1" shapeSizeUnit="MM"/>
        <shadow shadowScale="100" shadowUnder="0" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowColor="0,0,0,255" shadowBlendMode="6" shadowOffsetDist="1" shadowOffsetGlobal="1" shadowOpacity="0.7" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetUnit="MM"/>
        <substitutions/>
      </text-style>
      <text-format wrapChar="" plussign="0" reverseDirectionSymbol="0" formatNumbers="0" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" autoWrapLength="0" placeDirectionSymbol="0" leftDirectionSymbol="&lt;" decimals="3" multilineAlign="3" rightDirectionSymbol=">"/>
      <placement rotationAngle="0" distMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" xOffset="0" offsetType="0" dist="0" maxCurvedCharAngleOut="-25" distUnits="MM" preserveRotation="1" yOffset="0" centroidInside="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" quadOffset="2" maxCurvedCharAngleIn="25" repeatDistanceUnits="MM" geometryGeneratorType="PointGeometry" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" repeatDistance="0" geometryGenerator="" centroidWhole="0" geometryGeneratorEnabled="0" priority="5" fitInPolygonOnly="0" offsetUnits="MM" placement="6"/>
      <rendering scaleMax="0" fontMinPixelSize="3" minFeatureSize="0" upsidedownLabels="0" displayAll="0" limitNumLabels="0" labelPerPart="0" mergeLines="0" maxNumLabels="2000" drawLabels="1" fontMaxPixelSize="10000" scaleMin="0" obstacleFactor="1" zIndex="0" obstacleType="0" obstacle="1" fontLimitPixelSize="0" scaleVisibility="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties" type="Map">
            <Option name="LabelDistance" type="Map">
              <Option value="false" name="active" type="bool"/>
              <Option value="array((&quot;soildepth&quot;/MAX( &quot;soildepth&quot;))*5, 0)" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
            <Option name="OffsetXY" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="array((&quot;soildepth&quot;/MAX( &quot;soildepth&quot;))*5 + 1000, 0)" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
          </Option>
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
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory scaleBasedVisibility="0" height="15" penAlpha="255" rotationOffset="270" enabled="0" labelPlacementMethod="XHeight" sizeScale="3x:0,0,0,0,0,0" penWidth="0" diagramOrientation="Up" minScaleDenominator="0" minimumSize="0" lineSizeScale="3x:0,0,0,0,0,0" scaleDependency="Area" width="15" opacity="1" sizeType="MM" barWidth="5" lineSizeType="MM" penColor="#000000" maxScaleDenominator="1e+8" backgroundColor="#ffffff" backgroundAlpha="255">
      <fontProperties style="" description="Noto Sans,9,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" field="" label=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings priority="0" showAll="1" placement="0" linePlacementFlags="18" obstacle="0" dist="0" zIndex="0">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
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
    <field name="soildepth">
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
    <alias field="obsid" index="0" name=""/>
    <alias field="h_toc" index="1" name=""/>
    <alias field="h_gs" index="2" name=""/>
    <alias field="h_tocags" index="3" name=""/>
    <alias field="length" index="4" name=""/>
    <alias field="h_syst" index="5" name=""/>
    <alias field="ground_surface" index="6" name=""/>
    <alias field="soildepth" index="7" name=""/>
    <alias field="bedrock" index="8" name=""/>
    <alias field="drillstop" index="9" name=""/>
    <alias field="bedrock_from_table" index="10" name=""/>
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
    <default expression="" field="soildepth" applyOnUpdate="0"/>
    <default expression="" field="bedrock" applyOnUpdate="0"/>
    <default expression="" field="drillstop" applyOnUpdate="0"/>
    <default expression="" field="bedrock_from_table" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" field="obsid" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="h_toc" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="h_gs" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="h_tocags" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="length" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="h_syst" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="ground_surface" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="soildepth" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="bedrock" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="drillstop" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="bedrock_from_table" notnull_strength="0" exp_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="obsid" desc=""/>
    <constraint exp="" field="h_toc" desc=""/>
    <constraint exp="" field="h_gs" desc=""/>
    <constraint exp="" field="h_tocags" desc=""/>
    <constraint exp="" field="length" desc=""/>
    <constraint exp="" field="h_syst" desc=""/>
    <constraint exp="" field="ground_surface" desc=""/>
    <constraint exp="" field="soildepth" desc=""/>
    <constraint exp="" field="bedrock" desc=""/>
    <constraint exp="" field="drillstop" desc=""/>
    <constraint exp="" field="bedrock_from_table" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="1" actionWidgetStyle="dropDown" sortExpression="&quot;soildepthh&quot;">
    <columns>
      <column name="obsid" hidden="0" type="field" width="-1"/>
      <column hidden="1" type="actions" width="-1"/>
      <column name="drillstop" hidden="0" type="field" width="276"/>
      <column name="h_toc" hidden="0" type="field" width="-1"/>
      <column name="h_gs" hidden="0" type="field" width="-1"/>
      <column name="h_tocags" hidden="0" type="field" width="-1"/>
      <column name="length" hidden="0" type="field" width="-1"/>
      <column name="h_syst" hidden="0" type="field" width="-1"/>
      <column name="ground_surface" hidden="0" type="field" width="-1"/>
      <column name="bedrock" hidden="0" type="field" width="-1"/>
      <column name="bedrock_from_table" hidden="0" type="field" width="-1"/>
      <column name="soildepth" hidden="0" type="field" width="-1"/>
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
    <field name="bedrock" editable="1"/>
    <field name="bedrock_from_table" editable="1"/>
    <field name="capacity" editable="1"/>
    <field name="comment" editable="1"/>
    <field name="depthbot" editable="1"/>
    <field name="depthtop" editable="1"/>
    <field name="development" editable="1"/>
    <field name="drillstop" editable="1"/>
    <field name="geology" editable="1"/>
    <field name="geoshort" editable="1"/>
    <field name="ground_surface" editable="1"/>
    <field name="h_gs" editable="1"/>
    <field name="h_syst" editable="1"/>
    <field name="h_toc" editable="1"/>
    <field name="h_tocags" editable="1"/>
    <field name="length" editable="1"/>
    <field name="maxdepthbot" editable="1"/>
    <field name="obsid" editable="1"/>
    <field name="soildepth" editable="1"/>
    <field name="soildepthh" editable="1"/>
    <field name="stratid" editable="1"/>
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
    <field labelOnTop="0" name="soildepth"/>
    <field labelOnTop="0" name="soildepthh"/>
    <field labelOnTop="0" name="stratid"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
