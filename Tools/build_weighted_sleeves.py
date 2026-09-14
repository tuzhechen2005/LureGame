"""Add weighted jacket sleeves to the isolated first-person arm study."""
import bpy, bmesh, math
from pathlib import Path
from mathutils import Vector

root=Path('D:/LureGame/ArtSource/RiggedArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'TransverseCrankStudy.blend'))
scene=bpy.data.scenes['RiggedArmsReview'];bpy.context.window.scene=scene
rig=bpy.data.objects['LureArmIKRig']
skin=next(o for o in scene.objects if o.type=='MESH' and
          any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers))
cloth=bpy.data.materials.new('WeightedOliveJacket');cloth.use_nodes=True
p=next(n for n in cloth.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.055,.075,.039,1)
p.inputs['Roughness'].default_value=.83
noise=cloth.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=650
bump=cloth.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.0002
cloth.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
cloth.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
for side in ('R','L'):
    obj=skin.copy();obj.data=skin.data.copy();obj.name='WeightedSleeve_'+side
    scene.collection.objects.link(obj)
    wrist=rig.data.bones['wrist.'+side].head_local
    elbow=rig.data.bones['lowerarm01.'+side].head_local
    axis=(elbow-wrist).normalized()
    bm=bmesh.new();bm.from_mesh(obj.data)
    wrong=[v for v in bm.verts if (v.co.x>0 if side=='R' else v.co.x<0)]
    bmesh.ops.delete(bm,geom=wrong,context='VERTS')
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
        plane_co=wrist+axis*.035,plane_no=axis,clear_inner=True,dist=.00001)
    bm.normal_update()
    for v in bm.verts:
        t=(v.co-wrist).dot(axis)
        phase=math.atan2(v.normal.z,v.normal.x)
        fold=.002*math.sin(t*100+phase*2)
        v.co+=v.normal*(.006+fold)
    # Close the cut shoulder boundary; keep the wrist opening for a cuff.
    shoulder_edges=[e for e in bm.edges if e.is_boundary and
                    all((v.co-wrist).length>.30 for v in e.verts)]
    if shoulder_edges:bmesh.ops.holes_fill(bm,edges=shoulder_edges,sides=0)
    bm.to_mesh(obj.data);bm.free()
    obj.data.materials.clear();obj.data.materials.append(cloth)
    for poly in obj.data.polygons:poly.material_index=0;poly.use_smooth=True
    solid=obj.modifiers.new('Cuff and cloth thickness','SOLIDIFY');solid.thickness=.0015
    solid.offset=0
    assert all(v.groups for v in obj.data.vertices),'Sleeve vertices need weights'
    print('WEIGHTED_SLEEVE',side,len(obj.data.vertices))

for frame in (1,13,25,37):
    scene.frame_set(frame)
    scene.render.filepath=str(root/('SleevedGrip_%02d.png'%frame))
    bpy.ops.render.render(scene=scene.name,write_still=True)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'WeightedSleeveStudy.blend'))
