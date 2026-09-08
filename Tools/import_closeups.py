import unreal as u
root='/Game/LureArt';at=u.AssetToolsHelpers.get_asset_tools();lib=u.MaterialEditingLibrary
names=['SM_RightArm','SM_LeftArm']+['SM_'+s+'Body' for s in ['Bass','Perch','Pike','Trout']]
for name in names:
 t=u.AssetImportTask();t.filename='D:/LureGame/ArtSource/Realistic/'+name+'.fbx';t.destination_path=root;t.automated=True;t.replace_existing=True;t.save=True
 o=u.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;t.options=o;at.import_asset_tasks([t])
 mesh=u.load_asset(root+'/'+name)
 species=name.removeprefix('SM_').removesuffix('Body')
 for i,slot in enumerate(mesh.static_materials):
  n=str(slot.material_slot_name);n=n.split('.')[0]
  print('CLOSEUP_SLOT',name,i,n)
  if n in ['Skin','Jacket']:mat=u.load_asset(root+'/M_PBR_'+n)
  elif 'Body' in name and n in ['BassSide','BassBack','BassBelly','BassStripe']:mat=u.load_asset(root+'/M_PBR_M_'+species+'Skin')
  else:mat=u.load_asset(root+'/'+n)
  if mat:mesh.set_material(i,mat)
 u.EditorAssetLibrary.save_loaded_asset(mesh)
m=at.create_asset('M_FinRealistic',root,u.Material,u.MaterialFactoryNew());m.set_editor_property('two_sided',True)
c=lib.create_material_expression(m,u.MaterialExpressionConstant3Vector,0,0);c.set_editor_property('constant',u.LinearColor(.11,.17,.065,1));lib.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
r=lib.create_material_expression(m,u.MaterialExpressionConstant,0,0);r.set_editor_property('r',.45);lib.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS);lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
for name in names[2:]+['SM_BassTail']:
 mesh=u.load_asset(root+'/'+name)
 for i,slot in enumerate(mesh.static_materials):
  if str(slot.material_slot_name)=='BassFin':mesh.set_material(i,m)
 u.EditorAssetLibrary.save_loaded_asset(mesh)
m=u.load_asset(root+'/M_PBR_M_BassSkin')
for n in lib.get_material_expressions(m):
 if isinstance(n,u.MaterialExpressionCustom):n.set_editor_property('code',n.get_editor_property('code').replace('sin(P.x*2.8)','sin(P.x*.6)'))
lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
print('CLOSEUPS_COMPLETE')

