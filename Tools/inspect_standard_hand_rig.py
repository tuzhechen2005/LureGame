import unreal as u
import json
from pathlib import Path
root='/Game/Characters/Mannequins'
skeleton=u.load_asset(root+'/Meshes/SK_Mannequin')
assert isinstance(skeleton,u.Skeleton)
names=[str(x) for x in skeleton.get_reference_pose().get_bone_names()]
required=['upperarm_r','lowerarm_r','hand_r','upperarm_l','lowerarm_l','hand_l']
assert all(n in names for n in required)
result={'skeleton':skeleton.get_path_name(),
        'arm_bones':required,'finger_bones':[n for n in names if n.startswith(('thumb_','index_','middle_','ring_','pinky_'))]}
rig=u.load_asset(root+'/Rigs/CR_Mannequin_Body')
assert rig,'Standard body Control Rig must load'
hierarchy=rig.get_editor_property('hierarchy')
result['control_rig']=rig.get_path_name()
result['hand_controls']=[str(k.name) for k in hierarchy.get_all_keys() if any(x in str(k.name).lower() for x in ('hand','finger','thumb','index','middle','ring','pinky'))]
Path('D:/LureGame/ArtSource/RiggedArms/StandardRigInspection.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('STANDARD_HAND_RIG_INSPECTED',json.dumps(result))
