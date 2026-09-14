"""Run in the isolated RiggedArmsReview Blender scene, not the game scene.

Preserve equipment-space grip anchors while changing the wrist orientation.
The reference grip still requires visual acceptance; anchor precision is not
a test of finger surface contact or skin deformation.
"""
import bpy
import math
from mathutils import Vector, Matrix

scene = bpy.data.scenes['RiggedArmsReview']
rig = bpy.data.objects['LureArmIKRig']
scene.frame_set(1)
rod = bpy.data.objects['RigStudyRod']
crank = bpy.data.objects['RigStudyCrank']
reference_wrists = {'R': Vector((-.13, -.33, .38)),
                    'L': Vector((.09, -.32, .285))}
reference_contacts = {'R': rod.matrix_world.translation.copy(),
                      'L': crank.matrix_world @ Vector((.04485, .07, -.031))}
offsets = {}
for side in ('R', 'L'):
    bones = rig.data.bones
    wrist = bones['wrist.' + side]
    forward = (bones['finger3-1.' + side].head_local - wrist.head_local).normalized()
    across = bones['finger2-1.' + side].head_local - bones['finger5-1.' + side].head_local
    across = (across - forward * across.dot(forward)).normalized()
    rest = Matrix((across, forward, across.cross(forward))).transposed()
    sign = 1 if side == 'R' else -1
    f, a = Vector((sign, 0, 0)), Vector((0, -sign, 0))
    desired = Matrix((a, f, a.cross(f))).transposed()
    reference_rotation = (desired @ rest.transposed()).to_quaternion() @ wrist.matrix_local.to_quaternion()
    offsets[side] = reference_rotation.inverted() @ (reference_contacts[side] - reference_wrists[side])

maximum_error = 0.
for frame in range(1, 50):
    scene.frame_set(frame)
    scene.view_layers[0].update()
    for side in ('R', 'L'):
        contact = (rod.matrix_world.translation.copy() if side == 'R'
                   else crank.matrix_world @ Vector((.04485, .07, -.031)))
        orientation = bpy.data.objects['WristOrientation_' + side]
        target = bpy.data.objects['WristTarget_' + side]
        target.location = contact - orientation.rotation_quaternion @ offsets[side]
        target.keyframe_insert(data_path='location', frame=frame)
        scene.view_layers[0].update()
        wrist = rig.pose.bones['wrist.' + side]
        actual_contact = wrist.matrix @ offsets[side]
        maximum_error = max(maximum_error, (actual_contact - contact).length)

scene.frame_set(1)
scene.view_layers[0].update()
print('GRIP_ANCHOR_MAX_ERROR_METRES', maximum_error)
scene.render.filepath = 'D:/LureGame/ArtSource/RiggedArms/ContactAnchorReview.png'
bpy.ops.render.render(scene=scene.name, write_still=True)
bpy.data.libraries.write('D:/LureGame/ArtSource/RiggedArms/ContactAnchorStudy.blend',
                         {scene}, path_remap='ABSOLUTE')
