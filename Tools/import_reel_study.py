import unreal as u
mesh = u.load_asset('/Game/FirstPerson/SK_FishingArms')
task = u.AssetImportTask()
task.filename = 'D:/LureGame/ArtSource/RiggedArms/A_ReelStudy.fbx'
task.destination_path = '/Game/FirstPerson'
task.destination_name = 'A_ReelStudy'
task.automated = True
task.replace_existing = True
task.save = True
options = u.FbxImportUI()
options.import_mesh = False
options.import_animations = True
options.skeleton = mesh.get_editor_property('skeleton')
options.mesh_type_to_import = u.FBXImportType.FBXIT_ANIMATION
options.automated_import_should_detect_type = False
task.options = options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
animations = [u.load_asset(p) for p in task.imported_object_paths]
animations = [a for a in animations if isinstance(a, u.AnimSequence)]
assert animations, task.imported_object_paths
for animation in animations:
    assert animation.get_play_length() > 1.9
    print('REEL_ANIMATION_IMPORTED', animation.get_path_name(), animation.get_play_length())
