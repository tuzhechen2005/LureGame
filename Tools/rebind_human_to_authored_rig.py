"""Fit the licensed human rest mesh to semantic Manny joints, retaining its UVs.

The successful authored animation remains unchanged. Display bone tails from
the FBX are never treated as finger joint positions.
"""
import bpy, math, bmesh
from pathlib import Path
from mathutils import Vector,Matrix
out=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(out/'StandardReeling.blend'))
s=bpy.context.scene; rig=next(o for o in s.objects if o.type=='ARMATURE')
with bpy.data.libraries.load('D:/LureGame/ArtSource/RiggedArms/FishingArmsRig.blend',link=False) as (src,dst):
    dst.objects=['FishingArmRig','SK_FishingArms']
for o in dst.objects:s.collection.objects.link(o)
human=next(o for o in dst.objects if o.type=='ARMATURE')
skin=next(o for o in dst.objects if o.type=='MESH')
H=human.matrix_world.copy(); M=rig.matrix_world.copy(); Mi=M.inverted()
def hh(n):return H@human.data.bones[n].head_local
def ht(n):return H@human.data.bones[n].tail_local
def mh(n):return M@rig.data.bones[n].head_local
def frame(head,y,across):
    y=y.normalized();x=across-y*across.dot(y)
    if x.length<1e-5:x=Vector((0,0,1)).cross(y)
    x.normalize();z=x.cross(y).normalized()
    mat=Matrix((x,y,z)).transposed().to_4x4();mat.translation=head
    return mat
maps={}; transforms={}
for hs,ms in [('L','l'),('R','r')]:
    hw=hh('wrist.'+hs);mw=mh('hand_'+ms)
    hf=hh('finger3-1.'+hs)-hw;mf=mh('middle_01_'+ms)-mw
    ha=hh('finger2-1.'+hs)-hh('finger5-1.'+hs)
    ma=mh('index_01_'+ms)-mh('pinky_01_'+ms)
    scale=mf.length/hf.length
    palm=frame(mw,mf,ma)@Matrix.Diagonal((scale,scale,scale,1))@frame(hw,hf,ha).inverted()
    maps['wrist.'+hs]='hand_'+ms;transforms['wrist.'+hs]=palm
    def segment(name,target,sh,st,th,tt,thickness=scale):
        maps[name]=target
        length=(tt-th).length/(st-sh).length
        transforms[name]=frame(th,tt-th,ma)@Matrix.Diagonal((thickness,length,thickness,1))@frame(sh,st-sh,ha).inverted()
    for n,digit in enumerate(('index','middle','ring','pinky'),1):
        h='metacarpal%d.%s'%(n,hs);t=digit+'_metacarpal_'+ms
        segment(h,t,hh(h),ht(h),mh(t),mh(digit+'_01_'+ms))
    for n,digit in enumerate(('thumb','index','middle','ring','pinky'),1):
        for k in (1,2,3):
            h='finger%d-%d.%s'%(n,k,hs);t='%s_%02d_%s'%(digit,k,ms)
            th=mh(t)
            tt=mh('%s_%02d_%s'%(digit,k+1,ms)) if k<3 else th+(th-mh('%s_02_%s'%(digit,ms))).normalized()*(ht(h)-hh(h)).length*scale
            segment(h,t,hh(h),ht(h),th,tt)
    for group,start,end in [('upperarm','upperarm','lowerarm'),('lowerarm','lowerarm','hand')]:
        sh=hh(group+'01.'+hs); st=hh('lowerarm01.'+hs) if group=='upperarm' else hw
        th=mh(start+'_'+ms);tt=mh(end+'_'+ms)
        for k in (1,2):
            h=group+'%02d.'%k+hs
            a=(hh(h)-sh).dot(st-sh)/(st-sh).length_squared
            b=(ht(h)-sh).dot(st-sh)/(st-sh).length_squared
            segment(h,start+'_'+ms,hh(h),ht(h),th+(tt-th)*a,th+(tt-th)*b,1.)
            if group=='lowerarm' and k==2:maps[h]='lowerarm_twist_01_'+ms
names={g.index:g.name for g in skin.vertex_groups}
weights=[];coords=[]
for vertex in skin.data.vertices:
    entries=[(names[g.group],g.weight) for g in vertex.groups if names[g.group] in maps]
    total=sum(w for _,w in entries)
    assert total>0,vertex.index
    entries=[(n,w/total) for n,w in entries]
    position=sum((transforms[n]@(H@vertex.co)*w for n,w in entries),Vector())
    coords.append(Mi@position)
    combined={}
    for n,w in entries:combined[maps[n]]=combined.get(maps[n],0)+w
    weights.append(combined)
for v,co in zip(skin.data.vertices,coords):v.co=co
skin.vertex_groups.clear()
for name in sorted(set(maps.values())):
    g=skin.vertex_groups.new(name=name)
    for i,weights_i in enumerate(weights):
        if name in weights_i:g.add([i],weights_i[name],'REPLACE')
skin.modifiers.clear();mod=skin.modifiers.new('Authored fishing motion','ARMATURE');mod.object=rig
skin.parent=None;skin.matrix_world=M;skin.name='SK_RealFishingArms'
for o in s.objects:
    if o!=skin and o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers):o.hide_render=True;o.hide_set(True)
human.hide_render=True;human.hide_set(True)
mat=bpy.data.materials.new('AnatomicalSkin');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links
p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.48;p.inputs['Subsurface Weight'].default_value=.06
texroot=Path('D:/LureGame/ArtSource/HumanBase/Skins/skins/mindfront_aksel_skin')
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texroot/'Aksel_Skin_diffuse.png'));links.new(tex.outputs['Color'],p.inputs['Base Color'])
normal=nodes.new('ShaderNodeTexImage');normal.image=bpy.data.images.load(str(texroot/'Aksel_Skin_NRM.png'));normal.image.colorspace_settings.name='Non-Color'
nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.55;links.new(normal.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
skin.data.materials.clear();skin.data.materials.append(mat)
sub=skin.modifiers.new('Human surface','SUBSURF');sub.levels=1
cloth=bpy.data.materials.new('OliveJacket');cloth.use_nodes=True
cp=next(n for n in cloth.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
cp.inputs['Base Color'].default_value=(.052,.073,.035,1);cp.inputs['Roughness'].default_value=.84
for side in ('l','r'):
    sleeve=skin.copy();sleeve.data=skin.data.copy();sleeve.name='FishingSleeve_'+side;s.collection.objects.link(sleeve)
    wrist=rig.data.bones['hand_'+side].head_local
    elbow=rig.data.bones['lowerarm_'+side].head_local
    axis=(elbow-wrist).normalized()
    bm=bmesh.new();bm.from_mesh(sleeve.data)
    wrong=[v for v in bm.verts if (v.co.x<0 if side=='l' else v.co.x>0)]
    bmesh.ops.delete(bm,geom=wrong,context='VERTS')
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=wrist+axis*3.5,plane_no=axis,clear_inner=True,dist=.0001)
    bm.normal_update()
    for v in bm.verts:
        distance=(v.co-wrist).dot(axis);phase=math.atan2(v.normal.z,v.normal.x)
        v.co+=v.normal*(.6+.15*math.sin(distance*.9+phase*2))
    bm.to_mesh(sleeve.data);bm.free()
    sleeve.data.materials.clear();sleeve.data.materials.append(cloth)
    for poly in sleeve.data.polygons:poly.material_index=0;poly.use_smooth=True
    solid=sleeve.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.08
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.cycles.samples=12
for frame_number in (1,25):
    s.frame_set(frame_number);bpy.context.view_layer.update()
    s.render.filepath=str(out/('HumanAuthored_%02d.png'%frame_number));bpy.ops.render.render(write_still=True)
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'HumanStandardReeling.blend'))
print('HUMAN_REBIND_SAVED',len(skin.data.vertices),len(maps))
