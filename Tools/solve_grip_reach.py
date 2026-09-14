"""Choose equipment height and elbow planes jointly for the side-grip study."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
root=Path('D:/LureGame/ArtSource/RiggedArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'SideGripOrientationStudy.blend'))
s=bpy.data.scenes['RiggedArmsReview'];bpy.context.window.scene=s;s.frame_set(1)
r=bpy.data.objects['LureArmIKRig'];p=r.pose.bones
targets={side:bpy.data.objects['WristTarget_'+side] for side in ('R','L')}
initial={side:o.location.copy() for side,o in targets.items()}
constraints={side:next(c for c in p['lowerarm02.'+side].constraints if c.type=='IK') for side in targets}
best=None
for height in [i*.01 for i in range(0,23)]:
    result={};score=0
    for side in targets:
        targets[side].location=initial[side]+Vector((0,0,height))
        local_best=None
        for angle in range(-180,180,10):
            constraints[side].pole_angle=math.radians(angle);s.view_layers[0].update()
            fore=(p['lowerarm02.'+side].tail-p['lowerarm01.'+side].head).normalized()
            hand=(p['finger3-1.'+side].head-p['wrist.'+side].head).normalized()
            error=(p['wrist.'+side].head-targets[side].location).length
            bend=math.degrees(fore.angle(hand))
            value=bend+error*5000
            if local_best is None or value<local_best[0]:local_best=(value,angle,bend,error)
        result[side]=local_best;score+=local_best[0]
    if best is None or score<best[0]:best=(score,height,result)
_,height,result=best
for side in targets:
    targets[side].location=initial[side]+Vector((0,0,height))
    constraints[side].pole_angle=math.radians(result[side][1])
for name in ('RigStudyRod','RigStudyCrank'):
    o=bpy.data.objects[name];o.animation_data_clear();o.location.z+=height
s.view_layers[0].update()
report={'height_offset_m':height,'sides':result,'status':'requires visual inspection'}
(root/'GripReachMetrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('REACH_RESULT',report)
original=s.camera
for name,camname in [('FirstPerson',original.name),('Side','GripCheckSide'),('Front','GripCheckFront')]:
    s.camera=bpy.data.objects[camname]
    if name!='FirstPerson':s.camera.location.z+=height
    s.render.filepath=str(root/('GripReach_'+name+'.png'));bpy.ops.render.render(scene=s.name,write_still=True)
s.camera=original
bpy.ops.wm.save_as_mainfile(filepath=str(root/'GripReachStudy.blend'))
