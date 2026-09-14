"""Fit the rod to an authored grasp without independently twisting the wrist."""
import bpy, math, bmesh
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'MannyGraspReview.blend'))
s=bpy.context.scene;s.frame_set(1)
rig=next(o for o in s.objects if o.type=='ARMATURE')
rig.animation_data_clear()
# This review mesh is first-person arms only; the full source remains separate.
for obj in list(s.objects):
    if obj.type!='MESH' or not any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers):continue
    obj.data=obj.data.copy()
    group_ids={g.index for g in obj.vertex_groups if g.name.startswith(('upperarm','lowerarm','hand_','thumb_','index_','middle_','ring_','pinky_'))}
    bm=bmesh.new();bm.from_mesh(obj.data);deform=bm.verts.layers.deform.active
    remove=[v for v in bm.verts if sum(w for g,w in v[deform].items() if g in group_ids)<.5]
    bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(obj.data);bm.free()
for side in ('r','l'):
    bone=rig.pose.bones['upperarm_'+side]
    matrix=bone.matrix.copy();origin=matrix.translation.copy()
    matrix=Quaternion((1,0,0),math.radians(52)).to_matrix().to_4x4()@matrix
    matrix.translation=origin;bone.matrix=matrix
    bpy.context.view_layer.update()
def joint(name):return rig.matrix_world@rig.pose.bones[name].head
axis=(joint('index_01_r')-joint('pinky_01_r')).normalized()
u=axis.cross(Vector((0,0,1))).normalized();v=axis.cross(u).normalized()
points=[joint(n) for n in ('middle_01_r','middle_02_r','middle_03_r','ring_01_r','ring_02_r','ring_03_r')]
origin=sum(points,Vector())/len(points)
xy=np.array([((p-origin).dot(u),(p-origin).dot(v)) for p in points])
A=np.column_stack([2*xy[:,0],2*xy[:,1],np.ones(len(xy))])
solution=np.linalg.lstsq(A,np.sum(xy*xy,axis=1),rcond=None)[0]
center=origin+u*float(solution[0])+v*float(solution[1])
print('ROD_AXIS',tuple(axis),'GRIP_CENTER',tuple(center))
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath='D:/LureGame/ArtSource/Export/SM_RodHandle.fbx')
rod=next(o for o in bpy.data.objects if o not in before and o.type=='MESH')
rod.name='StandardGripRod';rod.rotation_mode='QUATERNION';rod.rotation_quaternion=axis.to_track_quat('X','Z')
rod.location=center-axis*.015
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath='D:/LureGame/ArtSource/RiggedArms/SM_ReelCrank_Transverse.fbx')
crank=next(o for o in bpy.data.objects if o not in before and o.type=='MESH')
crank.name='StandardGripCrank';crank.rotation_mode='QUATERNION';crank.rotation_quaternion=rod.rotation_quaternion
bpy.context.view_layer.update();crank.location=rod.matrix_world@Vector((-.01,.028,-.075))
start=rod.matrix_world@Vector((.18,0,0));end=rod.matrix_world@Vector((1.7,0,0))
bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=.004,radius2=.001,depth=(end-start).length,location=(end+start)/2)
blank=bpy.context.object;blank.name='RodBlank';blank.rotation_euler=(end-start).to_track_quat('Z','Y').to_euler()
blank.data.materials.append(rod.data.materials[0])
camera=s.camera
for name,pos,target,lens in [('Side',(-1.1,-.55,1.6),center,40),('FirstPerson',(0,-.07,1.7),center+axis*.05,25)]:
    camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens
    s.render.filepath=str(root/('StandardRodGrip_'+name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'StandardRodGrip.blend'))
