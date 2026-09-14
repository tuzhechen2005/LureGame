import unreal as u
task=u.AssetImportTask()
task.filename='D:/LureGame/ArtSource/RiggedArms/SM_ReelCrank_Transverse.fbx'
task.destination_path='/Game/LureArt'
task.destination_name='SM_ReelCrank_Transverse'
task.automated=True;task.replace_existing=True;task.save=True
options=u.FbxImportUI();options.import_mesh=True
options.import_materials=False;options.import_textures=False
options.static_mesh_import_data.combine_meshes=True
task.options=options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh=u.load_asset('/Game/LureArt/SM_ReelCrank_Transverse')
assert mesh
for i,slot in enumerate(mesh.static_materials):
    name='Rubber' if 'Rubber' in str(slot.material_slot_name) else 'Metal'
    material=u.load_asset('/Game/LureArt/'+name)
    assert material,name
    mesh.set_material(i,material)
assert u.EditorAssetLibrary.save_loaded_asset(mesh)
print('TRANSVERSE_CRANK_IMPORTED')
