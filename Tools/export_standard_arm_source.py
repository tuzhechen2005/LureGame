"""Export the installed Epic mannequin and control frames for arm authoring."""
import unreal as u
import json
from pathlib import Path
out=Path('D:/LureGame/ArtSource/StandardArms')
out.mkdir(exist_ok=True)
mesh=u.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
assert isinstance(mesh,u.SkeletalMesh)
task=u.AssetExportTask();task.object=mesh
task.filename=str(out/'MannyReference.fbx');task.automated=True
task.prompt=False;task.replace_identical=True
task.options=u.FbxExportOption()
assert u.Exporter.run_asset_export_task(task)
rig=u.load_asset('/Game/Characters/Mannequins/Rigs/CR_Mannequin_Body')
h=rig.get_editor_property('hierarchy')
frames=[]
for key in h.get_all_keys():
    name=str(key.name)
    if not any(part in name for part in ('hand_','upperarm_','lowerarm_','thumb_','index_','middle_','ring_','pinky_')):
        continue
    t=h.get_global_transform(key,initial=True)
    frames.append({'name':name,'type':str(key.type),
                   'translation_cm':[t.translation.x,t.translation.y,t.translation.z],
                   'quaternion_xyzw':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]})
(out/'ControlFrames.json').write_text(json.dumps(frames,indent=2),encoding='utf-8')
print('STANDARD_ARM_SOURCE_EXPORTED',len(frames),task.filename)
