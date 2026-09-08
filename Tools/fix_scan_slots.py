import unreal as u,json
r='/Game/LureArt';d=json.load(open('D:/LureGame/ArtSource/Realistic/manifest.json'))
for name,slots in d.items():
 if not isinstance(slots,list):continue
 mesh=u.load_asset(r+'/'+name)
 for i,n in enumerate(slots):
  mat=u.load_asset(r+'/M_Real_'+n) or u.load_asset(r+'/'+n)
  mesh.set_material(i,mat)
 u.EditorAssetLibrary.save_loaded_asset(mesh)
for n in ['tree_small_02_leaves','grass_medium_01']:
 m=u.load_asset(r+'/M_Real_'+n) or u.load_asset(r+'/'+n)
 if isinstance(m,u.Material):
  m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
  c=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,0,0);c.set_editor_property('constant',u.LinearColor(.10,.19,.04,1));u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_SUBSURFACE_COLOR)
  u.MaterialEditingLibrary.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
exec(compile(open('D:/LureGame/Tools/shore_material.py',encoding='utf-8').read(),'shore_material.py','exec'))
print('SCAN_SLOTS_COMPLETE')
