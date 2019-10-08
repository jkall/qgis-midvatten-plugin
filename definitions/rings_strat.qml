<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" labelsEnabled="0" minScale="1e+8" simplifyDrawingHints="0" simplifyMaxScale="1" version="3.8.3-Zanzibar" readOnly="0" styleCategories="AllStyleCategories" maxScale="0" simplifyDrawingTol="1" simplifyAlgorithm="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" symbollevels="0" enableorderby="1" type="RuleRenderer">
    <rules key="{bfd218d5-2585-4c17-adf9-e31adb5db8c9}">
      <rule filter="ELSE" symbol="0" key="{0964502e-d185-44bc-933c-f9bf44bdd98c}"/>
    </rules>
    <symbols>
      <symbol alpha="1" name="0" force_rhr="0" type="marker" clip_to_extent="1">
        <layer class="SimpleMarker" enabled="1" locked="0" pass="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="255,255,255,255"/>
          <prop k="outline_style" v="no"/>
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
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="depthbot" name="field" type="QString"/>
                  <Option name="transformer" type="Map">
                    <Option name="d" type="Map">
                      <Option value="1" name="exponent" type="double"/>
                      <Option value="10" name="maxSize" type="double"/>
                      <Option value="54.3" name="maxValue" type="double"/>
                      <Option value="1" name="minSize" type="double"/>
                      <Option value="0.1" name="minValue" type="double"/>
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
      <orderByClause asc="0" nullsFirst="0">"stratid"</orderByClause>
    </orderby>
  </renderer-v2>
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
    <constraint unique_strength="0" field="rowid" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="obsid" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="maxdepthbot" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="stratid" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="depthtop" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="depthbot" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="geology" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="geoshort" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="capacity" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="development" notnull_strength="0" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="comment" notnull_strength="0" exp_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="rowid" desc=""/>
    <constraint exp="" field="obsid" desc=""/>
    <constraint exp="" field="maxdepthbot" desc=""/>
    <constraint exp="" field="stratid" desc=""/>
    <constraint exp="" field="depthtop" desc=""/>
    <constraint exp="" field="depthbot" desc=""/>
    <constraint exp="" field="geology" desc=""/>
    <constraint exp="" field="geoshort" desc=""/>
    <constraint exp="" field="capacity" desc=""/>
    <constraint exp="" field="development" desc=""/>
    <constraint exp="" field="comment" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="&quot;geoshort&quot;">
    <columns>
      <column name="obsid" hidden="0" type="field" width="-1"/>
      <column name="stratid" hidden="0" type="field" width="-1"/>
      <column name="depthtop" hidden="0" type="field" width="-1"/>
      <column name="depthbot" hidden="0" type="field" width="-1"/>
      <column name="geology" hidden="0" type="field" width="-1"/>
      <column name="geoshort" hidden="0" type="field" width="-1"/>
      <column name="capacity" hidden="0" type="field" width="-1"/>
      <column name="development" hidden="0" type="field" width="-1"/>
      <column name="comment" hidden="0" type="field" width="-1"/>
      <column hidden="1" type="actions" width="-1"/>
      <column name="maxdepthbot" hidden="0" type="field" width="-1"/>
      <column name="rowid" hidden="0" type="field" width="-1"/>
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
    <field name="rowid" editable="1"/>
    <field name="stratid" editable="1"/>
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
  <widgets/>
  <previewExpression>obsid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
