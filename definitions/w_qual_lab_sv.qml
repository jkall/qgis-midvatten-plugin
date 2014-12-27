<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.6.1-Brighton" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="obsid">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="depth">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="report">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="project">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="staff">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="DateTime" name="date_time">
      <widgetv2config fieldEditable="1" calendar_popup="0" allow_null="0" display_format="yyyy-MM-dd HH:mm:ss" field_format="yyyy-MM-dd HH:mm:ss" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="anameth">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="parameter">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="reading_num">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="reading_txt">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="unit">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="comment">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
  </edittypes>
  <editform>.</editform>
  <editforminit>form_logics.w_qual_lab_form_open</editforminit>
  <featformsuppress>1</featformsuppress>
  <annotationform>.</annotationform>
  <editorlayout>tablayout</editorlayout>
  <aliases>
    <alias field="anameth" index="6" name="analysmetod"/>
    <alias field="comment" index="11" name="kommentar"/>
    <alias field="date_time" index="5" name="datum och tid"/>
    <alias field="depth" index="1" name="djup/nivå"/>
    <alias field="project" index="3" name="projekt"/>
    <alias field="reading_num" index="8" name="analysvärde numeriskt"/>
    <alias field="reading_txt" index="9" name="analysvärde text (inkl &lt;> etc)"/>
    <alias field="report" index="2" name="labrapportnr"/>
    <alias field="staff" index="4" name="fältpersonal"/>
    <alias field="unit" index="10" name="enhet"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeEditorForm>
    <attributeEditorContainer name="water quality from laboratory analysis">
      <attributeEditorContainer name="general">
        <attributeEditorField index="0" name="obsid"/>
        <attributeEditorField index="1" name="depth"/>
        <attributeEditorField index="2" name="report"/>
        <attributeEditorField index="3" name="project"/>
        <attributeEditorField index="4" name="staff"/>
        <attributeEditorField index="5" name="date_time"/>
      </attributeEditorContainer>
      <attributeEditorContainer name="parameter">
        <attributeEditorField index="6" name="anameth"/>
        <attributeEditorField index="7" name="parameter"/>
        <attributeEditorField index="8" name="reading_num"/>
        <attributeEditorField index="9" name="reading_txt"/>
        <attributeEditorField index="10" name="unit"/>
        <attributeEditorField index="11" name="comment"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
  </attributeEditorForm>
  <attributeactions/>
</qgis>
