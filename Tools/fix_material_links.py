import unreal as u
lib=u.MaterialEditingLibrary
for path in u.EditorAssetLibrary.list_assets('/Game/LureArt',recursive=False):
 if '/M_PBR_' not in path:continue
 m=u.load_asset(path)
 expressions=lib.get_material_expressions(m)
 src=next((n for n in expressions if isinstance(n,u.MaterialExpressionPreSkinnedPosition)),None)
 v=next((n for n in expressions if isinstance(n,u.MaterialExpressionVertexInterpolator)),None)
 if src and v:assert lib.connect_material_expressions(src,'',v,'VS')
 m.set_editor_property('used_with_instanced_static_meshes',True)
 lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
 print('FIXED_MATERIAL',path)
print('MATERIAL_LINKS_COMPLETE')
