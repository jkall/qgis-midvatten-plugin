<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.1.0-Master" minimumScale="-4.65661e-10" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype labelontop="0" editable="1" type="0" name="comment"/>
    <edittype labelontop="0" editable="1" type="0" name="date_time"/>
    <edittype labelontop="0" editable="1" type="0" name="flow_lpm"/>
    <edittype labelontop="0" editable="1" type="0" name="instrument"/>
    <edittype labelontop="0" editable="1" type="0" name="obsid"/>
    <edittype labelontop="0" editable="1" type="0" name="parameter"/>
    <edittype labelontop="0" editable="1" type="0" name="reading_num"/>
    <edittype labelontop="0" editable="1" type="0" name="reading_txt"/>
    <edittype labelontop="0" editable="1" type="0" name="staff"/>
    <edittype labelontop="0" editable="1" type="0" name="unit"/>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <featformsuppress>1</featformsuppress>
  <annotationform></annotationform>
  <editorlayout>tablayout</editorlayout>
  <aliases>
    <alias field="date_time" index="2" name="date and time"/>
    <alias field="flow_lpm" index="8" name="sampling water flow (l/m)"/>
    <alias field="reading_num" index="5" name="reading, numerical value"/>
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
