import unreal as u
root='/Game/LureArt';at=u.AssetToolsHelpers.get_asset_tools();lib=u.MaterialEditingLibrary
files=['D:/LureGame/ArtSource/Anatomical/SM_AnatomicalRight.fbx','D:/LureGame/ArtSource/Anatomical/SM_AnatomicalLeft.fbx']
texroot='D:/LureGame/ArtSource/HumanBase/Skins/skins/mindfront_aksel_skin/'
files += [texroot+n for n in ['Aksel_Skin_diffuse.png','Aksel_Skin_NRM.png','Aksel_Skin_SPEC.png']]
for file in files:
 t=u.AssetImportTask();t.filename=file;t.destination_path=root;t.automated=True;t.replace_existing=True;t.save=True
 if file.endswith('.fbx'):
  o=u.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;t.options=o
 at.import_asset_tasks([t])
m=at.create_asset('M_AnatomicalSkin',root,u.Material,u.MaterialFactoryNew());m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_SUBSURFACE)
for name,prop,kind in [('Aksel_Skin_diffuse',u.MaterialProperty.MP_BASE_COLOR,'color'),('Aksel_Skin_NRM',u.MaterialProperty.MP_NORMAL,'normal'),('Aksel_Skin_SPEC',u.MaterialProperty.MP_SPECULAR,'linear')]:
 tex=u.load_asset(root+'/'+name);tex.set_editor_property('srgb',kind=='color')
 if kind=='normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);tex.set_editor_property('flip_green_channel',True)
 u.EditorAssetLibrary.save_loaded_asset(tex)
 n=lib.create_material_expression(m,u.MaterialExpressionTextureSample,0,0);n.set_editor_property('texture',tex);n.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if kind=='normal' else u.MaterialSamplerType.SAMPLERTYPE_COLOR if kind=='color' else u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);lib.connect_material_property(n,'RGB' if kind!='linear' else 'R',prop)
for value,prop in [(.53,u.MaterialProperty.MP_ROUGHNESS),(.16,u.MaterialProperty.MP_OPACITY)]:
 n=lib.create_material_expression(m,u.MaterialExpressionConstant,0,0);n.set_editor_property('r',value);lib.connect_material_property(n,'',prop)
c=lib.create_material_expression(m,u.MaterialExpressionConstant3Vector,0,0);c.set_editor_property('constant',u.LinearColor(.35,.08,.04,1));lib.connect_material_property(c,'',u.MaterialProperty.MP_SUBSURFACE_COLOR)
lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
for name in ['SM_AnatomicalRight','SM_AnatomicalLeft']:
 mesh=u.load_asset(root+'/'+name)
 for i in range(len(mesh.static_materials)):mesh.set_material(i,m)
 u.EditorAssetLibrary.save_loaded_asset(mesh)
print('ANATOMICAL_IMPORT_COMPLETE')
