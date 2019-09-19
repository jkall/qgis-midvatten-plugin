<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.8.3-Zanzibar" styleCategories="AllStyleCategories" maxScale="0" simplifyAlgorithm="0" minScale="1e+8" readOnly="0" labelsEnabled="0" simplifyDrawingHints="0" simplifyMaxScale="1" simplifyDrawingTol="1" simplifyLocal="1" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="0" symbollevels="0" type="singleSymbol" forceraster="0">
    <symbols>
      <symbol alpha="1" force_rhr="0" name="0" clip_to_extent="1" type="marker">
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <prop v="Line" k="SymbolType"/>
          <prop v="geom_from_wkt( format('LINESTRING(%1 %2, %3 %4)', &#xa;X($geometry)-0.002*@map_scale, Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;)*@map_scale*0.001*0.5, &#xa;X($geometry)+0.002*@map_scale, Y($geometry) - (&quot;meas&quot; - &quot;h_tocags&quot;)*@map_scale*0.001*0.5))" k="geometryModifier"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" force_rhr="0" name="@0@0" clip_to_extent="1" type="line">
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="0,0,255,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="0.46" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property key="dualview/previewExpressions">
      <value>rowid</value>
      <value>"rowid"</value>
    </property>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory penWidth="0" barWidth="5" width="15" lineSizeScale="3x:0,0,0,0,0,0" scaleBasedVisibility="0" minimumSize="0" height="15" backgroundAlpha="255" penColor="#000000" minScaleDenominator="0" rotationOffset="270" backgroundColor="#ffffff" maxScaleDenominator="1e+8" enabled="0" opacity="1" penAlpha="255" lineSizeType="MM" labelPlacementMethod="XHeight" sizeType="MM" diagramOrientation="Up" scaleDependency="Area" sizeScale="3x:0,0,0,0,0,0">
      <fontProperties description="Noto Sans,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings zIndex="0" linePlacementFlags="18" priority="0" showAll="1" dist="0" obstacle="0" placement="0">
    <properties>
      <Option type="Map">
        <Option name="name" value="" type="QString"/>
        <Option name="properties"/>
        <Option name="type" value="collection" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
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
    <field name="date_time">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="meas">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="level_masl">
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
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="rowid" name=""/>
    <alias index="1" field="obsid" name=""/>
    <alias index="2" field="date_time" name=""/>
    <alias index="3" field="meas" name=""/>
    <alias index="4" field="level_masl" name=""/>
    <alias index="5" field="h_tocags" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="rowid"/>
    <default expression="" applyOnUpdate="0" field="obsid"/>
    <default expression="" applyOnUpdate="0" field="date_time"/>
    <default expression="" applyOnUpdate="0" field="meas"/>
    <default expression="" applyOnUpdate="0" field="level_masl"/>
    <default expression="" applyOnUpdate="0" field="h_tocags"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="rowid" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="obsid" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="date_time" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="meas" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="level_masl" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="h_tocags" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="rowid"/>
    <constraint exp="" desc="" field="obsid"/>
    <constraint exp="" desc="" field="date_time"/>
    <constraint exp="" desc="" field="meas"/>
    <constraint exp="" desc="" field="level_masl"/>
    <constraint exp="" desc="" field="h_tocags"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column name="rowid" hidden="0" width="-1" type="field"/>
      <column name="obsid" hidden="0" width="-1" type="field"/>
      <column name="date_time" hidden="0" width="-1" type="field"/>
      <column name="meas" hidden="0" width="-1" type="field"/>
      <column name="level_masl" hidden="0" width="-1" type="field"/>
      <column hidden="1" width="-1" type="actions"/>
      <column name="h_tocags" hidden="0" width="-1" type="field"/>
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
    <field editable="1" name="date_time"/>
    <field editable="1" name="h_tocags"/>
    <field editable="1" name="level_masl"/>
    <field editable="1" name="meas"/>
    <field editable="1" name="obsid"/>
    <field editable="1" name="rowid"/>
  </editable>
  <labelOnTop>
    <field name="date_time" labelOnTop="0"/>
    <field name="h_tocags" labelOnTop="0"/>
    <field name="level_masl" labelOnTop="0"/>
    <field name="meas" labelOnTop="0"/>
    <field name="obsid" labelOnTop="0"/>
    <field name="rowid" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>rowid</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
