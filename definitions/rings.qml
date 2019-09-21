<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyAlgorithm="0" version="3.8.3-Zanzibar" minScale="1e+8" simplifyDrawingHints="0" simplifyDrawingTol="1" maxScale="0" labelsEnabled="0" simplifyLocal="1" hasScaleBasedVisibilityFlag="0" readOnly="0" simplifyMaxScale="1" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 type="RuleRenderer" symbollevels="0" forceraster="0" enableorderby="1">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule symbol="0" label="Silt/Lera" filter="&quot;geoshort&quot; ILIKE '%silt%' OR &quot;geoshort&quot; ILIKE '%lera%'" key="{395384f7-3a82-4608-923f-4608ed955607}"/>
      <rule symbol="1" label="Morän" filter="&quot;geoshort&quot; ILIKE '%morän%'" key="{b603efe3-f131-499a-a979-5fbfcc9239d2}"/>
      <rule symbol="2" label="Finsand" filter="&quot;geoshort&quot; ILIKE '%finsand%'" key="{298db47b-39f0-42ab-b5d0-cfd3677b81af}"/>
      <rule symbol="3" label="Sand" filter="&quot;geoshort&quot; ILIKE '%sand%' AND &quot;geoshort&quot; NOT ILIKE '%finsand%'" key="{655d9d21-a61d-4001-9979-53fc26ab4cf3}"/>
      <rule symbol="4" label="Grus" filter="&quot;geoshort&quot; ilike '%grus%'" key="{ec35a35a-76ed-480d-b202-ab515a06b2e1}"/>
      <rule symbol="5" filter="ELSE" key="{0964502e-d185-44bc-933c-f9bf44bdd98c}"/>
      <rule symbol="6" label="Bergstopp" filter="&quot;drillstop&quot; ilike '%berg%'" key="{20759fd4-dddc-4723-9e06-bd70e71fbe9d}"/>
    </rules>
    <symbols>
      <symbol alpha="1" clip_to_extent="1" force_rhr="0" name="0" type="marker">
        <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="255,255,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="depthbot"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option name="exponent" type="double" value="0.57"/>
                      <Option name="maxSize" type="double" value="10"/>
                      <Option name="maxValue" type="double" value="54.3"/>
                      <Option name="minSize" type="double" value="1"/>
                      <Option name="minValue" type="double" value="0.1"/>
                      <Option name="nullSize" type="double" value="0"/>
                      <Option name="scaleType" type="int" value="2"/>
                    </Option>
                    <Option name="t" type="int" value="1"/>
                  </Option>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" force_rhr="0" name="1" type="marker">
        <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="0,255,255,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="depthbot"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option name="exponent" type="double" value="0.57"/>
                      <Option name="maxSize" type="double" value="10"/>
                      <Option name="maxValue" type="double" value="54.3"/>
                      <Option name="minSize" type="double" value="1"/>
                      <Option name="minValue" type="double" value="0.1"/>
                      <Option name="nullSize" type="double" value="0"/>
                      <Option name="scaleType" type="int" value="2"/>
                    </Option>
                    <Option name="t" type="int" value="1"/>
                  </Option>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" force_rhr="0" name="2" type="marker">
        <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="255,140,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="depthbot"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option name="exponent" type="double" value="0.57"/>
                      <Option name="maxSize" type="double" value="10"/>
                      <Option name="maxValue" type="double" value="54.3"/>
                      <Option name="minSize" type="double" value="1"/>
                      <Option name="minValue" type="double" value="0.1"/>
                      <Option name="nullSize" type="double" value="0"/>
                      <Option name="scaleType" type="int" value="2"/>
                    </Option>
                    <Option name="t" type="int" value="1"/>
                  </Option>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" force_rhr="0" name="3" type="marker">
        <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="0,180,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="depthbot"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option name="exponent" type="double" value="0.57"/>
                      <Option name="maxSize" type="double" value="10"/>
                      <Option name="maxValue" type="double" value="54.3"/>
                      <Option name="minSize" type="double" value="1"/>
                      <Option name="minValue" type="double" value="0.1"/>
                      <Option name="nullSize" type="double" value="0"/>
                      <Option name="scaleType" type="int" value="2"/>
                    </Option>
                    <Option name="t" type="int" value="1"/>
                  </Option>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" force_rhr="0" name="4" type="marker">
        <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="0,100,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="depthbot"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option name="exponent" type="double" value="0.57"/>
                      <Option name="maxSize" type="double" value="10"/>
                      <Option name="maxValue" type="double" value="54.3"/>
                      <Option name="minSize" type="double" value="1"/>
                      <Option name="minValue" type="double" value="0.1"/>
                      <Option name="nullSize" type="double" value="0"/>
                      <Option name="scaleType" type="int" value="2"/>
                    </Option>
                    <Option name="t" type="int" value="1"/>
                  </Option>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" force_rhr="0" name="5" type="marker">
        <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="114,114,114,140" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.2" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="depthbot"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option name="exponent" type="double" value="0.57"/>
                      <Option name="maxSize" type="double" value="10"/>
                      <Option name="maxValue" type="double" value="54.3"/>
                      <Option name="minSize" type="double" value="1"/>
                      <Option name="minValue" type="double" value="0.1"/>
                      <Option name="nullSize" type="double" value="0"/>
                      <Option name="scaleType" type="int" value="2"/>
                    </Option>
                    <Option name="t" type="int" value="1"/>
                  </Option>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" force_rhr="0" name="6" type="marker">
        <layer locked="0" enabled="1" pass="0" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="0,0,255,0" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.4" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="depthbot"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option name="exponent" type="double" value="0.57"/>
                      <Option name="maxSize" type="double" value="11"/>
                      <Option name="maxValue" type="double" value="54.3"/>
                      <Option name="minSize" type="double" value="1"/>
                      <Option name="minValue" type="double" value="0.1"/>
                      <Option name="nullSize" type="double" value="0"/>
                      <Option name="scaleType" type="int" value="2"/>
                    </Option>
                    <Option name="t" type="int" value="1"/>
                  </Option>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <orderby>
      <orderByClause nullsFirst="0" asc="0">"stratid"</orderByClause>
    </orderby>
  </renderer-v2>
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
    <DiagramCategory lineSizeScale="3x:0,0,0,0,0,0" minScaleDenominator="0" width="15" diagramOrientation="Up" enabled="0" scaleBasedVisibility="0" minimumSize="0" labelPlacementMethod="XHeight" opacity="1" penAlpha="255" penWidth="0" barWidth="5" height="15" backgroundAlpha="255" sizeScale="3x:0,0,0,0,0,0" rotationOffset="270" backgroundColor="#ffffff" scaleDependency="Area" lineSizeType="MM" maxScaleDenominator="1e+8" sizeType="MM" penColor="#000000">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute color="#000000" label="" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings obstacle="0" linePlacementFlags="18" priority="0" zIndex="0" dist="0" showAll="1" placement="0">
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
    <default expression="" applyOnUpdate="0" field="obsid"/>
    <default expression="" applyOnUpdate="0" field="maxdepthbot"/>
    <default expression="" applyOnUpdate="0" field="drillstop"/>
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
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="obsid"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="maxdepthbot"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="drillstop"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="stratid"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="depthtop"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="depthbot"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="geology"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="geoshort"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="capacity"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="development"/>
    <constraint exp_strength="0" constraints="0" notnull_strength="0" unique_strength="0" field="comment"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="obsid" exp=""/>
    <constraint desc="" field="maxdepthbot" exp=""/>
    <constraint desc="" field="drillstop" exp=""/>
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
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="&quot;geoshort&quot;">
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
      <column hidden="0" name="drillstop" width="-1" type="field"/>
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
    <field name="stratid" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
