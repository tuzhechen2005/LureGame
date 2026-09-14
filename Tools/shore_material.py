import unreal as u
root='/Game/LureArt';src='D:/LureGame/ArtSource/Realistic/';at=u.AssetToolsHelpers.get_asset_tools();ml=u.MaterialEditingLibrary
m=u.load_asset(root+'/M_Shore');ml.delete_all_material_expressions(m)
pos=ml.create_material_expression(m,u.MaterialExpressionWorldPosition,0,0)
uv=ml.create_material_expression(m,u.MaterialExpressionCustom,0,0);uv.set_editor_property('code','return P.xy/240.;');uv.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT2)
a=u.CustomInput();a.set_editor_property('input_name','P');uv.set_editor_property('inputs',[a]);ml.connect_material_expressions(pos,'',uv,'P')
for suffix,prop in [('diff',u.MaterialProperty.MP_BASE_COLOR),('nor_gl',u.MaterialProperty.MP_NORMAL),('rough',u.MaterialProperty.MP_ROUGHNESS)]:
 name='brown_mud_leaves_01_'+suffix+'_2k';t=u.AssetImportTask();t.filename=src+name+'.jpg';t.destination_path=root;t.automated=True;t.replace_existing=True;t.save=True;at.import_asset_tasks([t])
 tex=u.load_asset(root+'/'+name);tex.set_editor_property('srgb',suffix=='diff')
 if suffix=='nor_gl':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);tex.set_editor_property('flip_green_channel',True)
 u.EditorAssetLibrary.save_loaded_asset(tex)
 n=ml.create_material_expression(m,u.MaterialExpressionTextureSample,0,0);n.set_editor_property('texture',tex);n.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if suffix=='nor_gl' else u.MaterialSamplerType.SAMPLERTYPE_COLOR if suffix=='diff' else u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
 assert ml.connect_material_expressions(uv,'',n,'UVs')
 assert ml.connect_material_property(n,'R' if suffix=='rough' else 'RGB',prop)
ml.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
print('SHORE_COMPLETE')
