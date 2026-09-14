"""Independent side-grip study derived from palm axes, not rejected offsets."""
import bpy, math
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
root=Path('D:/LureGame/ArtSource/RiggedArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'WeightedSleeveStudy.blend'))
s=bpy.data.scenes['RiggedArmsReview'];bpy.context.window.scene=s;s.frame_set(1)
r=bpy.data.objects['LureArmIKRig'];bones=r.data.bones;pose=r.pose.bones
for side in ('R','L'):
    wrist=bones['wrist.'+side]
    f=(bones['finger3-1.'+side].head_local-wrist.head_local).normalized()
    a=bones['finger2-1.'+side].head_local-bones['finger5-1.'+side].head_local
    a=(a-f*a.dot(f)).normalized()
    rest=Matrix((a,f,a.cross(f))).transposed()
    # Approach from below and outside; index side stays toward the rod tip.
    forward=Vector((0,0,1));across=Vector((0,-1 if side=='R' else 1,0))
    desired=Matrix((across,forward,across.cross(forward))).transposed()
    control=bpy.data.objects['WristOrientation_'+side]
    control.rotation_quaternion=(desired@rest.transposed()).to_quaternion()@wrist.matrix_local.to_quaternion()
    s.view_layers[0].update()
    for digit in range(2,6):
        for segment,angle in enumerate((65,80,45),1):
            p=pose['finger%d-%d.%s'%(digit,segment,side)]
            axis=p.bone.matrix_local.to_quaternion().inverted()@a
            p.rotation_quaternion=Quaternion(axis,math.radians(-angle if side=='R' else angle))
    s.view_layers[0].update()
    target=bpy.data.objects['WristTarget_'+side];target.animation_data_clear()
    if side=='R':
        anchor=(pose['finger3-1.R'].head+pose['finger4-1.R'].head)/2
        contact=Vector((-.072,-.345,.352))
    else:
        anchor=(pose['finger1-3.L'].tail+pose['finger2-3.L'].tail)/2
        contact=bpy.data.objects['RigStudyCrank'].matrix_world@Vector((.04485,.07,-.031))
    offset=anchor-pose['wrist.'+side].head
    target.location=contact-offset
    s.view_layers[0].update()
    print(side,'wrist',tuple(pose['wrist.'+side].head))

original=s.camera
views=[('FirstPerson',original.location.copy(),None),
       ('Side',Vector((-.65,-.28,.48)),Vector((-.03,-.34,.33))),
       ('Front',Vector((0,-1,.45)),Vector((0,-.34,.33)))]
for name,location,focus in views:
    if focus:
        camera=bpy.data.objects.new('GripCheck'+name,bpy.data.cameras.new('GripCheck'+name));s.collection.objects.link(camera)
        camera.location=location;camera.rotation_euler=(focus-location).to_track_quat('-Z','Y').to_euler();camera.data.lens=38;s.camera=camera
    else:s.camera=original
    s.render.filepath=str(root/('SideGrip_'+name+'.png'));bpy.ops.render.render(scene=s.name,write_still=True)
s.camera=original
bpy.ops.wm.save_as_mainfile(filepath=str(root/'SideGripOrientationStudy.blend'))
