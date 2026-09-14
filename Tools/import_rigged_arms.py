import unreal as u

task = u.AssetImportTask()
task.filename = 'D:/LureGame/ArtSource/RiggedArms/SK_FishingArms.fbx'
task.destination_path = '/Game/FirstPerson'
task.destination_name = 'SK_FishingArms'
task.automated = True
task.replace_existing = True
task.save = True
options = u.FbxImportUI()
options.import_mesh = True
options.import_as_skeletal = True
options.mesh_type_to_import = u.FBXImportType.FBXIT_SKELETAL_MESH
options.import_materials = False
options.import_textures = False
options.import_animations = False
task.options = options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh = u.load_asset('/Game/FirstPerson/SK_FishingArms')
assert isinstance(mesh, u.SkeletalMesh), task.imported_object_paths
skeleton = mesh.get_editor_property('skeleton')
assert skeleton
component = u.new_object(u.SkeletalMeshComponent)
component.set_skeletal_mesh_asset(mesh)
for name in ['wrist_R', 'wrist_L', 'lowerarm01_R', 'lowerarm01_L']:
    assert component.get_bone_index(name) >= 0, name
assert u.EditorAssetLibrary.save_loaded_asset(mesh)
print('RIGGED_ARMS_IMPORT_PASS', mesh.get_path_name(), skeleton.get_path_name(), component.get_num_bones())
