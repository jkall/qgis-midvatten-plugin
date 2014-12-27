<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.6.1-Brighton" minimumScale="-4.65661e-10" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="obsid">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="staff">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="DateTime" name="date_time">
      <widgetv2config fieldEditable="1" calendar_popup="0" allow_null="0" display_format="yyyy-MM-dd HH:mm:ss" field_format="yyyy-MM-dd HH:mm:ss" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="instrument">
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
    <edittype widgetv2type="TextEdit" name="flow_lpm">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="comment">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <featformsuppress>1</featformsuppress>
  <annotationform></annotationform>
  <editorlayout>tablayout</editorlayout>
  <aliases>
    <alias field="date_time" index="2" name="date and time"/>
    <alias field="flow_lpm" index="8" name="sampling water flow (l/m)"/>
    <alias field="reading_num" index="5" name="reading, numerical"/>
    <alias field="reading_txt" index="6" name="reading, text (incl. &lt; > etc )"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeEditorForm>
    <attributeEditorContainer name="water quality from field">
      <attributeEditorContainer name="general">
        <attributeEditorField index="0" name="obsid"/>
        <attributeEditorField index="1" name="staff"/>
        <attributeEditorField index="2" name="date_time"/>
      </attributeEditorContainer>
      <attributeEditorContainer name="measurement/analysis">
        <attributeEditorField index="3" name="instrument"/>
        <attributeEditorField index="4" name="parameter"/>
        <attributeEditorField index="5" name="reading_num"/>
        <attributeEditorField index="6" name="reading_txt"/>
        <attributeEditorField index="7" name="unit"/>
      </attributeEditorContainer>
      <attributeEditorContainer name="sampling info">
        <attributeEditorField index="8" name="flow_lpm"/>
        <attributeEditorField index="9" name="comment"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
  </attributeEditorForm>
  <attributeactions/>
</qgis>
