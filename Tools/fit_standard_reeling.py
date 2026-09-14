"""Reuse the authored grasp and solve arm joints from anatomical joint heads.

FBX display-bone tails are not anatomical joint endpoints. This solver uses
shoulder, elbow and wrist heads, preserving segment lengths explicitly.
"""
import bpy, math, json
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
root=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'StandardRodGrip.blend'))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE')
p=rig.pose.bones;M=rig.matrix_world;Mi=M.inverted()
S=Matrix.Diagonal(Vector((-1,1,1,1)))
right_names=[b.name for b in p if b.name.endswith('_r') and
             (b.name=='upperarm_r' or any(a.name=='upperarm_r' for a in b.parent_recursive))]
for name in right_names:
    left=name[:-2]+'_l'
    if left in p:
        deformation=p[name].matrix@p[name].bone.matrix_local.inverted()
        p[left].matrix=S@deformation@S@p[left].bone.matrix_local
        bpy.context.view_layer.update()
def head(name):return M@p[name].head
def grip_center(side):
    if side=='l':
        tips=[head(d+'_03_l')+(head(d+'_03_l')-head(d+'_02_l'))*.6 for d in ('thumb','index')]
        return (tips[0]+tips[1])*.5
    axis=(head('index_01_'+side)-head('pinky_01_'+side)).normalized()
    u=axis.cross(Vector((0,0,1))).normalized();v=axis.cross(u).normalized()
    pts=[head(n+'_'+side) for n in ('middle_01','middle_02','middle_03','ring_01','ring_02','ring_03')]
    origin=sum(pts,Vector())/len(pts)
    xy=np.array([((q-origin).dot(u),(q-origin).dot(v)) for q in pts])
    A=np.column_stack([2*xy[:,0],2*xy[:,1],np.ones(len(xy))])
    fit=np.linalg.lstsq(A,np.sum(xy*xy,axis=1),rcond=None)[0]
    return origin+u*float(fit[0])+v*float(fit[1])
reference={b.name:b.matrix_basis.copy() for b in p if b.name.endswith(('_l','_r'))}
hands={side:M@p['hand_'+side].matrix for side in ('l','r')}
offsets={side:grip_center(side)-head('hand_'+side) for side in hands}
forwards={side:(head('middle_01_'+side)-head('hand_'+side)).normalized() for side in hands}
lift=Vector((0,.04,.40))
origin=grip_center('r');right_contact=origin+lift
# Hold the tip toward the water; retain the authored hand-to-handle rotation.
tilt=Quaternion((1,0,0),math.radians(35))
equipment_transform=Matrix.Translation(right_contact)@tilt.to_matrix().to_4x4()@Matrix.Translation(-origin)
for name in ('StandardGripRod','StandardGripCrank','RodBlank'):
    obj=bpy.data.objects[name];obj.matrix_world=equipment_transform@obj.matrix_world
for side in hands:
    location=hands[side].translation.copy()
    hands[side]=tilt.to_matrix().to_4x4()@hands[side];hands[side].translation=location
    offsets[side]=tilt@offsets[side];forwards[side]=tilt@forwards[side]
# Resolve the axial grasp orientation from anatomy. The wrist must approach
# the palm from below while the reel stays below the rod. A pistol's authored
# grasp has the opposite axial orientation around this straight handle.
rod_axis=(equipment_transform.to_3x3()@(head('index_01_r')-head('pinky_01_r'))).normalized()
desired_up=Vector((0,0,1));desired_up=(desired_up-rod_axis*desired_up.dot(rod_axis)).normalized()
for side in hands:
    across=forwards[side]-rod_axis*forwards[side].dot(rod_axis);across.normalize()
    angle=math.atan2(rod_axis.dot(across.cross(desired_up)),across.dot(desired_up))
    roll=Quaternion(rod_axis,angle)
    location=hands[side].translation.copy()
    hands[side]=roll.to_matrix().to_4x4()@hands[side];hands[side].translation=location
    offsets[side]=roll@offsets[side];forwards[side]=roll@forwards[side]
    print('ANATOMICAL_GRASP_AXIAL_DEG',side,math.degrees(angle))
carbon=next((m for m in bpy.data.materials if m.name=='Carbon'),None)
if carbon:
    bpy.data.objects['RodBlank'].data.materials.clear();bpy.data.objects['RodBlank'].data.materials.append(carbon)
bpy.context.view_layer.update()
s.camera.rotation_euler=(right_contact+Vector((0,-.1,.1))-s.camera.location).to_track_quat('-Z','Y').to_euler()
crank=bpy.data.objects['StandardGripCrank'];crank_base=crank.rotation_quaternion.copy()
lengths={side:((head('lowerarm_'+side)-head('upperarm_'+side)).length,
               (head('hand_'+side)-head('lowerarm_'+side)).length) for side in hands}
def rotate_about(name,from_direction,to_direction):
    bone=p[name];world=M@bone.matrix;origin=world.translation.copy()
    delta=from_direction.rotation_difference(to_direction)
    world=delta.to_matrix().to_4x4()@world;world.translation=origin
    bone.matrix=Mi@world;bpy.context.view_layer.update()
metrics=[];samples=[]
for frame in range(1,50):
    for name,matrix in reference.items():p[name].matrix_basis=matrix
    bpy.context.view_layer.update()
    crank.rotation_quaternion=crank_base@Quaternion((0,1,0),2*math.pi*(frame-1)/48)
    bpy.context.view_layer.update()
    knob=crank.matrix_world@Vector((.04485,.07,-.031))
    for side,contact in [('r',right_contact),('l',knob)]:
        length1,length2=lengths[side];desired=contact-offsets[side];hand_forward=forwards[side]
        upper,lower,hand='upperarm_'+side,'lowerarm_'+side,'hand_'+side
        shoulder=head(upper);line=desired-shoulder;distance=line.length;direction=line.normalized()
        reach=min(distance,length1+length2-.0001)
        x=(length1*length1-length2*length2+reach*reach)/(2*reach)
        radius=math.sqrt(max(0,length1*length1-x*x));circle=shoulder+direction*x
        ideal_elbow=desired-hand_forward*length2
        radial=ideal_elbow-circle;radial-=direction*radial.dot(direction)
        if radial.length<1e-5:radial=Vector((1 if side=='l' else -1,0,-1))
        elbow=circle+radial.normalized()*radius
        rotate_about(upper,head(lower)-shoulder,elbow-shoulder)
        rotate_about(lower,head(hand)-head(lower),desired-head(lower))
        wrist=head(hand);world=hands[side].copy();world.translation=wrist;p[hand].matrix=Mi@world
        bpy.context.view_layer.update()
        error=(grip_center(side)-contact).length
        bend=math.degrees((wrist-head(lower)).angle(hand_forward))
        metrics.append({'frame':frame,'side':side,'contact_error_m':error,'wrist_angle_deg':bend,'unreachable_m':max(0,distance-length1-length2)})
    samples.append(({name:p[name].matrix_basis.copy() for name in reference},crank.rotation_quaternion.copy()))
    if frame in (1,13,25,37):
        s.render.filepath=str(root/('StandardReeling_%02d.png'%frame));bpy.ops.render.render(write_still=True)
for frame,(transforms,rotation) in enumerate(samples,1):
    for name,matrix in transforms.items():
        p[name].matrix_basis=matrix
        p[name].keyframe_insert(data_path='location',frame=frame)
        p[name].keyframe_insert(data_path='rotation_quaternion' if p[name].rotation_mode=='QUATERNION' else 'rotation_euler',frame=frame)
    crank.rotation_quaternion=rotation;crank.keyframe_insert(data_path='rotation_quaternion',frame=frame)
playback_error=0.
for frame in range(1,50):
    s.frame_set(frame);bpy.context.view_layer.update()
    knob=crank.matrix_world@Vector((.04485,.07,-.031))
    playback_error=max(playback_error,(grip_center('l')-knob).length)
print('KEYFRAMED_PLAYBACK_CONTACT_MAX_M',playback_error)
(root/'StandardReelingPlayback.json').write_text(json.dumps({'frames':49,'maximum_contact_error_m':playback_error}),encoding='utf-8')
(root/'StandardReelingMetrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print('REEL_CONTACT_MAX_M',max(m['contact_error_m'] for m in metrics),'WRIST_MAX_DEG',max(m['wrist_angle_deg'] for m in metrics))
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'StandardReeling.blend'))
