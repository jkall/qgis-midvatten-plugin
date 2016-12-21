<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.6.1-Brighton" minimumScale="-4.65661e-10" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="obsid">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="DateTime" name="date_time">
      <widgetv2config fieldEditable="1" calendar_popup="0" allow_null="0" display_format="yyyy-MM-dd HH:mm:ss" field_format="yyyy-MM-dd HH:mm:ss" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="comment">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="staff">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <featformsuppress>1</featformsuppress>
  <annotationform>.</annotationform>
  <editorlayout>tablayout</editorlayout>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeEditorForm>
    <attributeEditorContainer name="Comments">
      <attributeEditorField index="0" name="obsid"/>
      <attributeEditorField index="1" name="date_time"/>
      <attributeEditorField index="2" name="comment"/>
      <attributeEditorField index="3" name="staff"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <attributeactions/>
</qgis>