"""Export the reviewed arm motion and reel as one skeletal coordinate system."""
import bpy, json
from pathlib import Path
from mathutils import Vector,Matrix

out=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(out/'HumanStandardReeling.blend'))
s=bpy.context.scene
rig=next(o for o in s.objects if o.type=='ARMATURE' and 'hand_r' in o.data.bones)
rig.name='FishingArmature'
M=rig.matrix_world.copy(); Mi=M.inverted()
rod=bpy.data.objects['StandardGripRod']; crank=bpy.data.objects['StandardGripCrank']
s.frame_set(1); bpy.context.view_layer.update()
rod_base=rod.matrix_world.copy(); crank_base=crank.matrix_world.copy()
camera=s.camera.matrix_world.copy()
crank_samples=[]
for frame in range(1,50):
    s.frame_set(frame); bpy.context.view_layer.update()
    crank_samples.append(crank.matrix_world.copy())
s.frame_set(1)
crank.animation_data_clear()
crank.matrix_world=crank_base
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
root=next(b for b in rig.data.edit_bones if b.parent is None)
def marker(name,head,direction):
    b=rig.data.edit_bones.new(name)
    b.head=Mi@head; b.tail=Mi@(head+direction.normalized()*.03)
    b.parent=root; b.use_deform=True
    return b
axis=rod_base.to_3x3()@Vector((1,0,0))
marker('FP_Rod',rod_base.translation,axis)
marker('FP_Crank',crank_base.translation,crank_base.to_3x3()@Vector((0,1,0)))
marker('FP_Tip',rod_base@Vector((2.1,0,0)),axis)
eye=camera.translation; forward=camera.to_3x3()@Vector((0,0,-1)); up=camera.to_3x3()@Vector((0,1,0))
marker('FP_View',eye,forward)
marker('FP_Aim',eye+forward,forward)
marker('FP_Up',eye+up,forward)
bpy.ops.object.mode_set(mode='OBJECT')
for obj,bone in ((rod,'FP_Rod'),(crank,'FP_Crank')):
    geometry_transform=Mi@obj.matrix_world
    obj.data=obj.data.copy()
    for vertex in obj.data.vertices:vertex.co=geometry_transform@vertex.co
    group=obj.vertex_groups.new(name=bone)
    group.add(list(range(len(obj.data.vertices))),1.,'REPLACE')
    modifier=obj.modifiers.new('Fishing skeleton','ARMATURE'); modifier.object=rig
    obj.parent=rig; obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
rest=rig.data.bones['FP_Crank'].matrix_local.copy()
for frame,current in enumerate(crank_samples,1):
    s.frame_set(frame)
    for name in ('FP_Rod','FP_Tip','FP_View','FP_Aim','FP_Up'):
        fixed=rig.pose.bones[name];fixed.matrix=fixed.bone.matrix_local;fixed.rotation_mode='QUATERNION'
        fixed.keyframe_insert('location',frame=frame);fixed.keyframe_insert('rotation_quaternion',frame=frame)
    rig.pose.bones['FP_Crank'].matrix=Mi@current@crank_base.inverted()@M@rest
    b=rig.pose.bones['FP_Crank']; b.rotation_mode='QUATERNION'
    b.keyframe_insert('location',frame=frame); b.keyframe_insert('rotation_quaternion',frame=frame)
s.frame_start=1; s.frame_end=49; s.render.fps=24; s.frame_set(1)
meshes=[o for o in s.objects if o.type=='MESH' and not o.hide_render and not o.name.endswith(('LOD1','LOD2'))
        and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
for mesh in meshes:mesh.select_set(True)
for mesh in meshes:
    mesh.parent=rig;mesh.matrix_parent_inverse=Matrix.Identity(4);mesh.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.objects.active=rig
opts=dict(use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,
          axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',
          bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.,
          bake_anim_force_startend_keying=True,mesh_smooth_type='FACE')
bpy.ops.export_scene.fbx(filepath=str(out/'SK_AuthoredFishingRig.fbx'),bake_anim=False,**opts)
bpy.ops.export_scene.fbx(filepath=str(out/'A_AuthoredReel.fbx'),bake_anim=True,**opts)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ExportedFishingRig.blend'))
(out/'ExportedFishingRig.json').write_text(json.dumps({'meshes':[o.name for o in meshes],
    'bones':len(rig.data.bones),'frames':49,'fps':24,
    'rig_matrix':[list(row) for row in M],'unit_scale':s.unit_settings.scale_length,
    'camera':[list(row) for row in camera]},indent=2),encoding='utf-8')
print('FISHING_RIG_EXPORTED',len(rig.data.bones),[o.name for o in meshes])
