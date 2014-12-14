<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.1.0-Master" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype labelontop="0" editable="1" type="0" name="anameth"/>
    <edittype labelontop="0" editable="1" type="0" name="comment"/>
    <edittype labelontop="0" editable="1" type="0" name="date_time"/>
    <edittype labelontop="0" editable="1" type="0" name="depth"/>
    <edittype labelontop="0" editable="1" type="0" name="obsid"/>
    <edittype labelontop="0" editable="1" type="0" name="parameter"/>
    <edittype labelontop="0" editable="1" type="0" name="project"/>
    <edittype labelontop="0" editable="1" type="0" name="reading_num"/>
    <edittype labelontop="0" editable="1" type="0" name="reading_txt"/>
    <edittype labelontop="0" editable="1" type="0" name="report"/>
    <edittype labelontop="0" editable="1" type="0" name="staff"/>
    <edittype labelontop="0" editable="1" type="0" name="unit"/>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <featformsuppress>1</featformsuppress>
  <annotationform></annotationform>
  <editorlayout>tablayout</editorlayout>
  <aliases>
    <alias field="anameth" index="6" name="analysis method"/>
    <alias field="date_time" index="5" name="date and time"/>
    <alias field="reading_num" index="8" name="reading, numerical"/>
    <alias field="reading_txt" index="9" name="reading, text (incl &lt;> etc)"/>
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
