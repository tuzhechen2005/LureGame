"""Choose the grip's axial rotation using arm reach and anatomical constraints."""
import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
out=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(out/'StandardRodGrip.blend'))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');p=rig.pose.bones
M=rig.matrix_world.copy();Mi=M.inverted();S=Matrix.Diagonal((-1,1,1,1))
for b in p:
    if b.name.endswith('_r') and (b.name=='upperarm_r' or any(a.name=='upperarm_r' for a in b.parent_recursive)):
        name=b.name[:-2]+'_l'
        if name in p:p[name].matrix=S@b.matrix@b.bone.matrix_local.inverted()@S@p[name].bone.matrix_local;bpy.context.view_layer.update()
def head(n):return M@p[n].head
def center(side):
    if side=='l':return sum((head(d+'_03_l')+(head(d+'_03_l')-head(d+'_02_l'))*.6 for d in ('thumb','index')),Vector())*.5
    axis=(head('index_01_r')-head('pinky_01_r')).normalized();u=axis.cross(Vector((0,0,1))).normalized();v=axis.cross(u)
    pts=[head(n+'_r') for n in ('middle_01','middle_02','middle_03','ring_01','ring_02','ring_03')]
    origin=sum(pts,Vector())/len(pts);xy=np.array([((q-origin).dot(u),(q-origin).dot(v)) for q in pts])
    fit=np.linalg.lstsq(np.column_stack((2*xy[:,0],2*xy[:,1],np.ones(len(xy)))),np.sum(xy*xy,axis=1),rcond=None)[0]
    return origin+u*float(fit[0])+v*float(fit[1])
reference={b.name:b.matrix_basis.copy() for b in p if b.name.endswith(('_l','_r'))}
hands={side:M@p['hand_'+side].matrix for side in ('l','r')}
offset={side:center(side)-head('hand_'+side) for side in hands}
forward={side:(head('middle_01_'+side)-head('hand_'+side)).normalized() for side in hands}
palm={}
for side in hands:
    n=(head('index_01_'+side)-head('pinky_01_'+side)).cross(forward[side]).normalized()
    if n.dot(head('middle_03_'+side)-head('middle_01_'+side))<0:n=-n
    palm[side]=n
shoulder={side:head('upperarm_'+side) for side in hands}
lengths={side:((head('lowerarm_'+side)-shoulder[side]).length,(head('hand_'+side)-head('lowerarm_'+side)).length) for side in hands}
origin=center('r');rod=bpy.data.objects['StandardGripRod'];crank=bpy.data.objects['StandardGripCrank']
rod_base=rod.matrix_world.copy();crank_base=crank.matrix_world.copy();tilt=Quaternion((1,0,0),math.radians(25))
rod_axis=tilt@(rod_base.to_3x3()@Vector((1,0,0))).normalized()
def solve(side,wrist,fwd):
    start=shoulder[side];a,b=lengths[side];delta=wrist-start;d=delta.length;axis=delta.normalized()
    reach=min(d,a+b-.00001);x=(a*a-b*b+reach*reach)/(2*reach);radius=math.sqrt(max(0,a*a-x*x));mid=start+axis*x
    radial=wrist-fwd*b-mid;radial-=axis*radial.dot(axis)
    if radial.length<1e-5:radial=axis.cross(Vector((1,0,0)))
    radial.normalize();best=None
    for k in range(-4,5):
        elbow=mid+(Quaternion(axis,k*math.pi/8)@radial)*radius
        angle=math.degrees((wrist-elbow).angle(fwd))
        cross=max(0,elbow.x+.025) if side=='r' else max(0,.025-elbow.x)
        high=max(0,elbow.z-min(start.z-.10,wrist.z+.025))
        cost=angle*angle+cross*cross*180000+high*high*240000+max(0,.27-(elbow-s.camera.location).length)**2*500000+max(0,d-a-b)*1000000
        if best is None or cost<best[0]:best=(cost,elbow,angle,max(0,d-a-b))
    return best
best=None
direction_file=out/'GripArtDirection.json'
art=json.loads(direction_file.read_text(encoding='utf-8')) if direction_file.exists() else None
for z in ([art['lift_m'][2]] if art else (.28,.33,.38)):
    for y in ([art['lift_m'][1]] if art else (.04,.10)):
        lift=Vector((0,y,z));T=Matrix.Translation(origin+lift)@tilt.to_matrix().to_4x4()@Matrix.Translation(-origin)
        side_choices={}
        for side in ('r','l'):
            choice=None
            for deg in ([art['axial_roll_degrees'][side]] if art else range(-180,180,10)):
                rot=Quaternion(rod_axis,math.radians(deg))@tilt;off=rot@offset[side];fwd=rot@forward[side]
                costs=[]
                for k in ([0] if side=='r' else range(0,48,8)):
                    contact=origin+lift if side=='r' else T@crank_base@Quaternion((0,1,0),2*math.pi*k/48).to_matrix().to_4x4()@Vector((.04485,.07,-.031))
                    costs.append(solve(side,contact-off,fwd)[0])
                    # In first person the back/side of the hand faces the eye;
                    # reject a comfortable but palm-up grip aimed at the player.
                    toward_eye=(s.camera.location-contact).normalized()
                    exposure=max(0,(rot@palm[side]).dot(toward_eye)-.05)
                    costs[-1]+=exposure*exposure*16000
                score=max(costs)+sum(costs)/len(costs)*.1
                if choice is None or score<choice[0]:choice=(score,rot,deg)
            side_choices[side]=choice
        score=sum(c[0] for c in side_choices.values())
        if best is None or score<best[0]:best=(score,lift,T,side_choices)
score,lift,T,choices=best
for name in ('StandardGripRod','StandardGripCrank','RodBlank'):
    o=bpy.data.objects[name];o.matrix_world=T@o.matrix_world
crank.rotation_mode='QUATERNION';base_rotation=crank.rotation_quaternion.copy()
carbon=bpy.data.materials.get('Carbon')
if carbon:bpy.data.objects['RodBlank'].data.materials.clear();bpy.data.objects['RodBlank'].data.materials.append(carbon)
# Keep hands in the lower part of the first-person frame.
target=origin+lift+Vector((0,-.08,0))
s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.camera.data.lens=22
def rotate(name,old,new):
    bone=p[name];world=M@bone.matrix;loc=world.translation.copy()
    world=old.rotation_difference(new).to_matrix().to_4x4()@world;world.translation=loc;bone.matrix=Mi@world;bpy.context.view_layer.update()
samples=[];metrics=[]
for frame in range(1,50):
    for name,matrix in reference.items():p[name].matrix_basis=matrix
    bpy.context.view_layer.update()
    crank.rotation_quaternion=base_rotation@Quaternion((0,1,0),2*math.pi*(frame-1)/48);bpy.context.view_layer.update()
    for side in ('r','l'):
        contact=origin+lift if side=='r' else crank.matrix_world@Vector((.04485,.07,-.031))
        rot=choices[side][1];desired=contact-rot@offset[side];fwd=rot@forward[side]
        cost,elbow,angle,unreachable=solve(side,desired,fwd)
        upper,lower,hand='upperarm_'+side,'lowerarm_'+side,'hand_'+side
        rotate(upper,head(lower)-head(upper),elbow-head(upper));rotate(lower,head(hand)-head(lower),desired-head(lower))
        world=rot.to_matrix().to_4x4()@hands[side];world.translation=head(hand);p[hand].matrix=Mi@world;bpy.context.view_layer.update()
        # Distribute pronation along the forearm instead of collapsing the
        # wrist between a fully rotated hand and an untwisted forearm.
        twist='lowerarm_twist_01_'+side
        if twist in p:
            qlow=(p[lower].matrix@p[lower].bone.matrix_local.inverted()).to_quaternion()
            qhand=(p[hand].matrix@p[hand].bone.matrix_local.inverted()).to_quaternion()
            delta=qlow.inverted()@qhand
            axis=(p[hand].bone.head_local-p[lower].bone.head_local).normalized()
            projection=Vector((delta.x,delta.y,delta.z)).dot(axis)
            twist_angle=2*math.atan2(projection,delta.w)
            if twist_angle>math.pi:twist_angle-=2*math.pi
            if twist_angle<-math.pi:twist_angle+=2*math.pi
            loc,q,scale=p[twist].matrix.decompose()
            q=qlow@Quaternion(axis,twist_angle*.5)@p[twist].bone.matrix_local.to_quaternion()
            p[twist].matrix=Matrix.LocRotScale(loc,q,scale);bpy.context.view_layer.update()
        metrics.append({'frame':frame,'side':side,'wrist_angle_deg':angle,'unreachable_m':unreachable,'contact_error_m':(center(side)-contact).length,
                        'palm_toward_camera':(rot@palm[side]).dot((s.camera.location-contact).normalized())})
    samples.append(({name:p[name].matrix_basis.copy() for name in reference},crank.rotation_quaternion.copy()))
for frame,(pose,q) in enumerate(samples,1):
    for name,matrix in pose.items():
        p[name].matrix_basis=matrix;p[name].keyframe_insert('location',frame=frame)
        p[name].keyframe_insert('rotation_quaternion' if p[name].rotation_mode=='QUATERNION' else 'rotation_euler',frame=frame)
    crank.rotation_quaternion=q;crank.keyframe_insert('rotation_quaternion',frame=frame)
s.frame_start=1;s.frame_end=49;s.render.fps=24
for f in (1,25):
    s.frame_set(f);s.render.filepath=str(out/('SolvedGrasp_%02d.png'%f));bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'StandardReeling.blend'))
result={'lift':list(lift),'roll_degrees':{side:c[2] for side,c in choices.items()},'metrics':metrics}
(out/'AnatomicalGraspSolve.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('SOLVED_GRASP',list(lift),result['roll_degrees'],'WRIST_MAX',max(m['wrist_angle_deg'] for m in metrics),'CONTACT_MAX',max(m['contact_error_m'] for m in metrics))
