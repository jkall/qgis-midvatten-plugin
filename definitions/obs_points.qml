<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="1.9.0-Master" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <transparencyLevelInt>255</transparencyLevelInt>
  <renderer-v2 symbollevels="0" type="singleSymbol">
    <symbols>
      <symbol outputUnit="MM" alpha="1" type="marker" name="0">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="148,148,148,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="diamond"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="4"/>
        </layer>
      </symbol>
    </symbols>
    <rotation field=""/>
    <sizescale field=""/>
  </renderer-v2>
  <customproperties>
    <property key="labeling" value="pal"/>
    <property key="labeling/addDirectionSymbol" value="false"/>
    <property key="labeling/bufferColorB" value="255"/>
    <property key="labeling/bufferColorG" value="255"/>
    <property key="labeling/bufferColorR" value="255"/>
    <property key="labeling/bufferSize" value="1"/>
    <property key="labeling/dataDefinedProperty0" value=""/>
    <property key="labeling/dataDefinedProperty1" value=""/>
    <property key="labeling/dataDefinedProperty10" value=""/>
    <property key="labeling/dataDefinedProperty11" value=""/>
    <property key="labeling/dataDefinedProperty12" value=""/>
    <property key="labeling/dataDefinedProperty13" value=""/>
    <property key="labeling/dataDefinedProperty14" value=""/>
    <property key="labeling/dataDefinedProperty2" value=""/>
    <property key="labeling/dataDefinedProperty3" value=""/>
    <property key="labeling/dataDefinedProperty4" value=""/>
    <property key="labeling/dataDefinedProperty5" value=""/>
    <property key="labeling/dataDefinedProperty6" value=""/>
    <property key="labeling/dataDefinedProperty7" value=""/>
    <property key="labeling/dataDefinedProperty8" value=""/>
    <property key="labeling/dataDefinedProperty9" value=""/>
    <property key="labeling/decimals" value="0"/>
    <property key="labeling/dist" value="3"/>
    <property key="labeling/distInMapUnits" value="false"/>
    <property key="labeling/enabled" value="true"/>
    <property key="labeling/fieldName" value="obsid"/>
    <property key="labeling/fontFamily" value="MS Shell Dlg 2"/>
    <property key="labeling/fontItalic" value="false"/>
    <property key="labeling/fontSize" value="8.25"/>
    <property key="labeling/fontSizeInMapUnits" value="false"/>
    <property key="labeling/fontStrikeout" value="false"/>
    <property key="labeling/fontUnderline" value="false"/>
    <property key="labeling/fontWeight" value="50"/>
    <property key="labeling/formatNumbers" value="false"/>
    <property key="labeling/isExpression" value="false"/>
    <property key="labeling/labelPerPart" value="false"/>
    <property key="labeling/mergeLines" value="false"/>
    <property key="labeling/minFeatureSize" value="0"/>
    <property key="labeling/obstacle" value="true"/>
    <property key="labeling/placement" value="0"/>
    <property key="labeling/placementFlags" value="0"/>
    <property key="labeling/plussign" value="true"/>
    <property key="labeling/priority" value="5"/>
    <property key="labeling/scaleMax" value="0"/>
    <property key="labeling/scaleMin" value="0"/>
    <property key="labeling/textColorB" value="0"/>
    <property key="labeling/textColorG" value="0"/>
    <property key="labeling/textColorR" value="0"/>
    <property key="labeling/wrapChar" value=""/>
  </customproperties>
  <displayfield>&lt;style>
p {   margin-top: 0em;   margin-bottom: 0em; }
p.first { font-size: 8pt; font-weight: bold; color: black}
p.others { font-size: 8pt; font-weight: normal; color: black}
&lt;/style>
&lt;p class="first">[% "obsid" %] &lt;/p>
&lt;p class="others">[%   concat ('obstyp: ',tostring( "type"  ) )%]&lt;/p>
&lt;p class="others">[%   concat ('djup (m): ',tostring( "length"  ) )%]&lt;/p>
&lt;p class="others">[%   concat ('vg spetsnivå: ',tostring( "capacity"  ) )%]&lt;/p></displayfield>
  <label>0</label>
  <labelattributes>
    <label fieldname="" text="Label"/>
    <family fieldname="" name="MS Shell Dlg 2"/>
    <size fieldname="" units="pt" value="12"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="center"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <edittypes>
    <edittype type="0" name="drillstop"/>
    <edittype type="0" name="diam"/>
    <edittype type="0" name="length"/>
    <edittype type="0" name="length_ROR"/>
    <edittype type="0" name="east"/>
    <edittype type="0" name="comment"/>
    <edittype type="0" name="LAGER_JN"/>
    <edittype unchecked="0" type="7" checked="1" name="wlogg_yn"/>
    <edittype type="0" name="north"/>
    <edittype type="0" name="obsid"/>
    <edittype type="0" name="name"/>
    <edittype type="0" name="place"/>
    <edittype type="0" name="type"/>
    <edittype type="0" name="screen"/>
    <edittype type="0" name="h_gs"/>
    <edittype type="0" name="source"/>
    <edittype type="0" name="capacity"/>
    <edittype unchecked="0" type="7" checked="1" name="wmeas_yn"/>
    <edittype type="0" name="ne_source"/>
    <edittype type="0" name="ne_accur"/>
    <edittype type="0" name="XY_SYST"/>
    <edittype type="0" name="h_source"/>
    <edittype type="0" name="h_accur"/>
    <edittype type="0" name="h_toc"/>
    <edittype type="0" name="h_tocags"/>
    <edittype type="0" name="h_syst"/>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <annotationform>.</annotationform>
  <attributeactions/>
  <overlay display="false" type="diagram">
    <renderer item_interpretation="linear">
      <diagramitem size="0" value="0"/>
      <diagramitem size="0" value="0"/>
    </renderer>
    <factory sizeUnits="MM" type="Pie">
      <wellknownname>Pie</wellknownname>
      <classificationfield>0</classificationfield>
    </factory>
    <scalingAttribute>0</scalingAttribute>
  </overlay>
</qgis>
