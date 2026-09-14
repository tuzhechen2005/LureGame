import bpy
from pathlib import Path
root=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(root/'MannyReference.fbx'),automatic_bone_orientation=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
assert all(name in rig.data.bones for name in ('hand_r','hand_l','lowerarm_r','lowerarm_l'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert any(any(m.type=='ARMATURE' for m in o.modifiers) for o in meshes)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'MannyAuthoringBase.blend'))
print('STANDARD_BLENDER_BASE_VERIFIED',len(rig.data.bones),sum(len(o.data.vertices) for o in meshes))
