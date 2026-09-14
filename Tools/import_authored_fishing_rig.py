import unreal as u, json
from pathlib import Path
source=Path('D:/LureGame/ArtSource/StandardArms')
destination='/Game/FirstPerson/AuthoredLegacy'
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
def run(filename,name,options):
    task=u.AssetImportTask()
    task.filename=str(source/filename); task.destination_path=destination; task.destination_name=name
    task.automated=True; task.replace_existing=True; task.save=True; task.options=options
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return [u.load_asset(p) for p in task.imported_object_paths]
opts=u.FbxImportUI(); opts.import_mesh=True; opts.import_as_skeletal=True
opts.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
opts.automated_import_should_detect_type=False
opts.import_materials=False; opts.import_textures=False; opts.import_animations=False
assets=run('SK_AuthoredFishingRig.fbx','SK_AuthoredFishingRig',opts)
mesh=next(a for a in assets if isinstance(a,u.SkeletalMesh))
skeleton=mesh.get_editor_property('skeleton')
assert skeleton,'Imported mesh must own a skeleton'
assert u.EditorAssetLibrary.save_loaded_asset(skeleton,only_if_is_dirty=False)
slots=mesh.get_editor_property('materials')
print('FISHING_RIG_SLOTS',[str(m.material_slot_name) for m in slots])
mapping={'Cork':'M_PBR_Cork','Metal':'M_PBR_Metal','Rubber':'Rubber','Carbon':'M_PBR_Carbon','Gold':'Gold','AnatomicalSkin':'M_AnatomicalSkin','OliveJacket':'M_PBR_Jacket','BassBelly':'BassBelly'}
for index,m in enumerate(slots):
    label=str(m.material_slot_name)
    chosen=next((v for k,v in mapping.items() if k.lower() in label.lower()),None)
    if chosen:
        material=u.load_asset('/Game/LureArt/'+chosen)
        if material:
            if isinstance(material,u.Material):
                material.set_editor_property('used_with_skeletal_mesh',True)
                u.MaterialEditingLibrary.recompile_material(material)
                u.EditorAssetLibrary.save_loaded_asset(material)
            m.material_interface=material
            slots[index]=m
mesh.set_editor_property('materials',slots)
assert all(m.material_interface for m in mesh.get_editor_property('materials'))
u.EditorAssetLibrary.save_loaded_asset(mesh)
opts=u.FbxImportUI(); opts.import_mesh=False; opts.import_animations=True
opts.skeleton=mesh.get_editor_property('skeleton')
opts.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION; opts.automated_import_should_detect_type=False
animations=run('A_AuthoredReel.fbx','A_AuthoredReel',opts)
animation=next(a for a in animations if isinstance(a,u.AnimSequence))
assert animation.get_editor_property('skeleton')==skeleton
assert u.EditorAssetLibrary.save_loaded_asset(animation,only_if_is_dirty=False)
assert u.EditorAssetLibrary.save_directory(destination,only_if_is_dirty=False,recursive=True)
component=u.new_object(u.SkeletalMeshComponent); component.set_skeletal_mesh_asset(mesh)
required=['hand_l','hand_r','FP_Rod','FP_Crank','FP_Tip','FP_View','FP_Aim','FP_Up']
for name in required:assert component.get_bone_index(name)>=0,name
result={'mesh':mesh.get_path_name(),'animation':animation.get_path_name(),
        'duration':animation.get_play_length(),'bones':component.get_num_bones(),
        'skeleton':skeleton.get_path_name(),
        'materials':[(str(m.material_slot_name),m.material_interface.get_path_name() if m.material_interface else None) for m in mesh.get_editor_property('materials')],
        'socket_positions_validation':'Requires a registered runtime component; see AUTHORED_RIG in the game log.'}
assert 1.9<animation.get_play_length()<2.1,result
(source/'UnrealRigImport.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('AUTHORED_FISHING_RIG_IMPORT_PASS',result)
