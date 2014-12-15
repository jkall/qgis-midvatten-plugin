<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.6.1-Brighton" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="obsid">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="instrumentid">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="flowtype">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="DateTime" name="date_time">
      <widgetv2config fieldEditable="1" calendar_popup="0" allow_null="0" display_format="yyyy-MM-dd HH:mm:ss" field_format="yyyy-MM-dd HH:mm:ss" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="reading">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="unit">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="comment">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="1"/>
    </edittype>
  </edittypes>
  <editform></editform>
  <editforminit>form_logics.w_flow_form_open</editforminit>
  <featformsuppress>1</featformsuppress>
  <annotationform></annotationform>
  <editorlayout>tablayout</editorlayout>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeEditorForm>
    <attributeEditorContainer name="water flow measurement">
      <attributeEditorField index="0" name="obsid"/>
      <attributeEditorField index="1" name="instrumentid"/>
      <attributeEditorField index="2" name="flowtype"/>
      <attributeEditorField index="3" name="date_time"/>
      <attributeEditorField index="4" name="reading"/>
      <attributeEditorField index="5" name="unit"/>
      <attributeEditorField index="6" name="comment"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <attributeactions/>
</qgis>
