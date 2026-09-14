import bpy,json
from pathlib import Path
out=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(out/'HumanStandardReeling.blend'))
s=bpy.context.scene
for o in s.objects:
    if o.type in ('MESH','ARMATURE'):o.hide_render=True;o.hide_set(True)
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(out/'A_AuthoredReel.fbx'),automatic_bone_orientation=False)
new=[o for o in bpy.data.objects if o not in before]
rig=next(o for o in new if o.type=='ARMATURE')
for f in (1,25):
    s.frame_set(f);bpy.context.view_layer.update()
    print('FBX_JOINTS',f,{n:tuple(rig.matrix_world@rig.pose.bones[n].head) for n in ('hand_r','hand_l','FP_Crank','FP_View')})
    s.render.filepath=str(out/('FbxRoundtrip_%02d.png'%f));bpy.ops.render.render(write_still=True)
