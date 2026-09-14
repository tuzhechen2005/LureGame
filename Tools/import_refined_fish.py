import unreal as u
root = '/Game/LureArt'
for species in ['Bass', 'Perch', 'Pike', 'Trout']:
    name = 'SM_' + species + 'Body'
    task = u.AssetImportTask()
    task.filename = 'D:/LureGame/ArtSource/Realistic/' + name + '.fbx'
    task.destination_path = root
    task.destination_name = name + '_Refined'
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
    mesh = u.load_asset(root + '/' + name + '_Refined')
    for index, slot in enumerate(mesh.static_materials):
        key = str(slot.material_slot_name)
        if 'Fin' in key:
            material_name = 'M_FinRealistic'
        elif 'Pupil' in key:
            material_name = 'Pupil'
        elif 'Iris' in key:
            material_name = 'Iris'
        else:
            material_name = 'M_PBR_M_' + species + 'Skin'
        material = u.load_asset(root + '/' + material_name)
        assert material
        mesh.set_material(index, material)
    assert u.EditorAssetLibrary.save_loaded_asset(mesh)
    print('REFINED_FISH_IMPORTED', name, task.filename)
