import unreal as u
for name in ['tree_small_02_leaves','grass_medium_01']:
 m=u.load_asset('/Game/LureArt/M_PBR_'+name)
 m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
 c=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,0,0);c.set_editor_property('constant',u.LinearColor(.1,.19,.04,1));u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_SUBSURFACE_COLOR)
 u.MaterialEditingLibrary.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
print('FOLIAGE_COMPLETE')
