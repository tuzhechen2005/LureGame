"""Fit the left-hand pinch midpoint to the actual crank knob in the study."""
import bpy
from pathlib import Path
from mathutils import Vector
from mathutils import Quaternion
import math
root=Path('D:/LureGame/ArtSource/RiggedArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'WeightedSleeveStudy.blend'))
scene=bpy.data.scenes['RiggedArmsReview'];bpy.context.window.scene=scene
rig=bpy.data.objects['LureArmIKRig'];crank=bpy.data.objects['RigStudyCrank']
scene.frame_set(1);scene.view_layers[0].update()
pose=rig.pose.bones;wrist=pose['wrist.L']
across=(rig.data.bones['finger2-1.L'].head_local-
        rig.data.bones['finger5-1.L'].head_local).normalized()
for digit in (3,4,5):
    for segment,angle in enumerate((70,100,65),1):
        bone=pose['finger%d-%d.L'%(digit,segment)]
        local_axis=bone.bone.matrix_local.to_quaternion().inverted()@across
        bone.rotation_mode='QUATERNION'
        bone.rotation_quaternion=Quaternion(local_axis,math.radians(angle))
scene.view_layers[0].update()
pinch=(pose['finger1-3.L'].tail+pose['finger2-3.L'].tail)/2
# Close the thumb/index pad gap before locating the grip midpoint.
# Keep the wrist fixed and limit each CCD step to avoid a single large twist.
separation=(pose['finger1-3.L'].tail-pose['finger2-3.L'].tail).normalized()
for digit,sign in ((1,1),(2,-1)):
    goal=pinch+separation*(.014*sign)
    tip=pose['finger%d-3.L'%digit]
    for iteration in range(24):
        if (tip.tail-goal).length<.0005:break
        for segment in (3,2,1):
            bone=pose['finger%d-%d.L'%(digit,segment)]
            a=tip.tail-bone.head;b=goal-bone.head
            if min(a.length,b.length)<1e-6:continue
            rotation=a.rotation_difference(b)
            axis,angle=rotation.to_axis_angle()
            rotation=Quaternion(axis,min(angle,math.radians(10)))
            matrix=bone.matrix.copy();origin=matrix.translation.copy()
            candidate=rotation.to_matrix().to_4x4()@matrix
            candidate.translation=origin
            bone.matrix=candidate
            scene.view_layers[0].update()
    print('PAD_FIT_ERROR_M',digit,(tip.tail-goal).length)
pinch=(pose['finger1-3.L'].tail+pose['finger2-3.L'].tail)/2
local_pinch=wrist.matrix.inverted()@pinch
orientation=bpy.data.objects['WristOrientation_L']
target=bpy.data.objects['WristTarget_L']
errors=[]
for frame in range(1,50):
    scene.frame_set(frame);scene.view_layers[0].update()
    contact=crank.matrix_world@Vector((.04485,.07,-.031))
    target.location=contact-orientation.rotation_quaternion@local_pinch
    target.keyframe_insert(data_path='location',frame=frame)
    scene.view_layers[0].update()
    pinch=(pose['finger1-3.L'].tail+pose['finger2-3.L'].tail)/2
    errors.append((pinch-contact).length)
print('PINCH_MIDPOINT_MAX_ERROR_M',max(errors))
for frame in (1,13,25,37):
    scene.frame_set(frame);scene.render.filepath=str(root/('PinchFit_%02d.png'%frame))
    bpy.ops.render.render(scene=scene.name,write_still=True)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'PinchFitStudy.blend'))
