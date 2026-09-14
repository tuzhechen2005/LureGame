import unreal as u
root = '/Game/LureArt'
for name in ['SM_AnatomicalRight', 'SM_AnatomicalLeft']:
    task = u.AssetImportTask()
    task.filename = 'D:/LureGame/ArtSource/Anatomical/' + name + '.fbx'
    task.destination_path = root
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = True
    options = u.FbxImportUI()
    options.import_mesh = True
    options.import_materials = False
    options.import_textures = False
    options.static_mesh_import_data.combine_meshes = True
    task.options = options
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh = u.load_asset(root + '/' + name)
    jacket_found = False
    for index, slot in enumerate(mesh.static_materials):
        jacket = 'OliveJacket' in str(slot.material_slot_name)
        jacket_found |= jacket
        material = u.load_asset(root + ('/M_PBR_Jacket' if jacket else '/M_AnatomicalSkin'))
        assert material
        mesh.set_material(index, material)
    assert jacket_found, name
    assert u.EditorAssetLibrary.save_loaded_asset(mesh)
    print('SLEEVED_HAND_IMPORTED', name)
