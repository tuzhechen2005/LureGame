import bpy
from pathlib import Path
root=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'MannyAuthoringBase.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
original_matrix=rig.matrix_world.copy()
print('ORIGINAL_SCALE',tuple(rig.scale))
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(root/'PistolGraspReference.fbx'),automatic_bone_orientation=False)
donor=next(o for o in bpy.data.objects if o not in before and o.type=='ARMATURE')
assert donor.animation_data and donor.animation_data.action
rig.animation_data_create();rig.animation_data.action=donor.animation_data.action
rig.animation_data.action_slot=donor.animation_data.action_slot
action=rig.animation_data.action.copy();rig.animation_data.action=action
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in list(bag.fcurves):
                if not curve.data_path.startswith('pose.bones['):
                    print('OBJECT_TRACK_REMOVED',curve.data_path,curve.array_index)
                    bag.fcurves.remove(curve)
rig.matrix_world=original_matrix
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
print('RIG',rig.name,'TRANSFORM',rig.matrix_world)
for n in ('head','upperarm_r','lowerarm_r','hand_r','index_01_r','pinky_01_r','thumb_03_r','hand_l'):
    b=rig.pose.bones[n];print(n,tuple(rig.matrix_world@b.head),tuple(rig.matrix_world@b.tail))
for o in list(bpy.data.objects):
    if o not in before:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'MannyGraspReference.blend'))
print('GRASP_ACTION_ATTACHED')
