<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.6.1-Brighton" minimumScale="-4.65661e-10" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="obsid">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="stratid">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="depthtop">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="depthbot">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="geology">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="geoshort">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="capacity">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="development">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="comment">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
  </edittypes>
  <editform>.</editform>
  <editforminit>form_logics.stratigraphy_form_open</editforminit>
  <featformsuppress>1</featformsuppress>
  <annotationform>.</annotationform>
  <editorlayout>tablayout</editorlayout>
  <aliases>
    <alias field="capacity" index="6" name="VG, 1-6"/>
    <alias field="comment" index="8" name="kommentar"/>
    <alias field="depthbot" index="3" name="till djup under my (m)"/>
    <alias field="depthtop" index="2" name="från djup under my (m)"/>
    <alias field="development" index="7" name="stänger, J/N"/>
    <alias field="geology" index="4" name="jordart, fullständig beskrivning inkl tillägg mm"/>
    <alias field="geoshort" index="5" name="jordart, huvudfraktion"/>
    <alias field="stratid" index="1" name="lager nr"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeEditorForm>
    <attributeEditorContainer name="stratigraphy">
      <attributeEditorField index="0" name="obsid"/>
      <attributeEditorField index="1" name="stratid"/>
      <attributeEditorField index="2" name="depthtop"/>
      <attributeEditorField index="3" name="depthbot"/>
      <attributeEditorField index="4" name="geology"/>
      <attributeEditorField index="5" name="geoshort"/>
      <attributeEditorField index="6" name="capacity"/>
      <attributeEditorField index="7" name="development"/>
      <attributeEditorField index="8" name="comment"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <attributeactions/>
</qgis>
