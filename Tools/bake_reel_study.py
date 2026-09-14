import bpy
from pathlib import Path

out = Path('D:/LureGame/ArtSource/RiggedArms')
bpy.ops.wm.open_mainfile(filepath=str(out / 'FishingArmsReelStudy.blend'))
scene = bpy.data.scenes['RiggedArmsReview']
bpy.context.window.scene = scene
rig = bpy.data.objects['LureArmIKRig']
rig.name = 'FishingArmRig'
samples = {}
for frame in range(1, 50):
    scene.frame_set(frame)
    samples[frame] = rig.pose.bones['wrist.L'].matrix.translation.copy()
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.nla.bake(frame_start=1, frame_end=49, step=1, only_selected=False,
                 visual_keying=True, clear_constraints=True, use_current_action=False,
                 bake_types={'POSE'})
rig.animation_data.action.name = 'ReelStudy'
error = 0.
for frame in range(1, 50):
    scene.frame_set(frame)
    error = max(error, (rig.pose.bones['wrist.L'].matrix.translation - samples[frame]).length)
assert error < .002, error
assert not any(b.constraints for b in rig.pose.bones)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'FishingArmsReelBaked.blend'))
bpy.ops.export_scene.fbx(filepath=str(out / 'A_ReelStudy.fbx'), use_selection=True,
    object_types={'ARMATURE'}, add_leaf_bones=False, bake_anim=True,
    bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
    bake_anim_simplify_factor=0, axis_forward='-Y', axis_up='Z')
print('REEL_BAKE_PASS', 'max_wrist_error_m', error)
