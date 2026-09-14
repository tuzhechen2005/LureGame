import bpy,json,math,pathlib,os
from mathutils import Vector,Matrix
src=pathlib.Path('D:/LureGame/ArtSource/HumanBase');out=pathlib.Path(os.environ.get('LURE_HAND_OUTPUT','D:/LureGame/ArtSource/Anatomical'));out.mkdir(exist_ok=True)
grip_angles=json.loads(os.environ.get('LURE_GRIP_ANGLES','[43,74,43]'))
verts=[];uvs=[];faces=[];faceuv=[];group=''
for line in (src/'base.obj').read_text(encoding='utf-8').splitlines():
 a=line.split()
 if not a:continue
 if a[0]=='v':verts.append(Vector(tuple(map(float,a[1:4]))))
 elif a[0]=='vt':uvs.append(tuple(map(float,a[1:3])))
 elif a[0]=='g':group=a[1]
 elif a[0]=='f' and group=='body':
  faces.append([int(x.split('/')[0])-1 for x in a[1:]]);faceuv.append([int(x.split('/')[1])-1 for x in a[1:]])
sk=json.loads((src/'default.mhskel').read_text(encoding='utf-8'));weights=json.loads((src/'default_weights.mhw').read_text(encoding='utf-8'))['weights']
def joint(key):return sum((verts[i] for i in sk['joints'][key]),Vector())/len(sk['joints'][key])
def head(name):return joint(sk['bones'][name]['head'])
W=head('wrist.R');E=head('lowerarm01.R');F=(head('finger3-1.R')-W).normalized();A=(head('finger2-1.R')-head('finger5-1.R'));A=(A-F*A.dot(F)).normalized();N=A.cross(F).normalized()
transforms={}
def transform(name):
 if name in transforms:return transforms[name]
 b=sk['bones'][name];parent=b['parent'];p=transform(parent) if parent else Matrix.Identity(4);r=Matrix.Identity(4)
 if name.startswith('finger') and name.endswith('.R'):
  digit,segment=map(int,name[6:-2].split('-'));angle=([0,26,42,35] if digit==1 else [0]+grip_angles)[segment]
  h=head(name);rot=Matrix.Rotation(math.radians(-angle),4,A)
  if digit==1 and segment==1:rot=Matrix.Rotation(math.radians(-28),4,N)@rot
  r=Matrix.Translation(h)@rot@Matrix.Translation(-h)
 transforms[name]=p@r;return transforms[name]
for name in sk['bones']:transform(name)
pervertex=[[] for v in verts];eligible=[0.]*len(verts)
for bone,items in weights.items():
 for i,w in items:
  pervertex[i].append((bone,w))
  if bone.endswith('.R') and (bone.startswith('finger') or bone.startswith('lowerarm') or bone.startswith('wrist') or bone.startswith('metacarpal')):eligible[i]+=w
kept=[k for k,face in enumerate(faces) if all(eligible[i]>.35 for i in face)]
ids=sorted({i for k in kept for i in faces[k]});idx={old:new for new,old in enumerate(ids)}
def canonical(v):
 q=v-W;return Vector((q.dot(A)*.1,-q.dot(F)*.1,q.dot(N)*.1))
wrist=Vector((-.025,.080,-.012));elbow=Vector((-.42,.15,-.25));elbow_delta=elbow-wrist-canonical(E)
new=[]
for i in ids:
 vv=Vector();total=0
 for bone,weight in pervertex[i]:vv+=(transforms.get(bone,Matrix.Identity(4))@verts[i])*weight;total+=weight
 if total>0:vv/=total
 else:vv=verts[i]
 t=max(0,min(1,(verts[i]-W).dot(E-W)/(E-W).length_squared));t=t*t*(3-2*t)
 new.append(canonical(vv)+wrist+elbow_delta*t)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
skin=bpy.data.materials.new('AnatomicalSkin');skin.diffuse_color=(.53,.32,.23,1);skin.use_nodes=True
bsdf=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=(.53,.32,.23,1)
bsdf.inputs['Roughness'].default_value=.48;bsdf.inputs['Subsurface Weight'].default_value=.07
texture_root=src/'Skins/skins/mindfront_aksel_skin'
tex=skin.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture_root/'Aksel_Skin_diffuse.png'));skin.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
norm=skin.node_tree.nodes.new('ShaderNodeTexImage');norm.image=bpy.data.images.load(str(texture_root/'Aksel_Skin_NRM.png'));norm.image.colorspace_settings.name='Non-Color'
nm=skin.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.55;skin.node_tree.links.new(norm.outputs['Color'],nm.inputs['Color']);skin.node_tree.links.new(nm.outputs['Normal'],bsdf.inputs['Normal'])
for name,mirror in [('SM_AnatomicalRight',1),('SM_AnatomicalLeft',-1)]:
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([(v.x,v.y*mirror,v.z) for v in new],[],[[idx[i] for i in faces[k]][::mirror] for k in kept]);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(skin)
 layer=mesh.uv_layers.new(name='UVMap')
 for poly,k in zip(mesh.polygons,kept):
  poly.use_smooth=True
  for loop,uv in zip(poly.loop_indices,faceuv[k][::mirror]):layer.data[loop].uv=uvs[uv]
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 sub=o.modifiers.new('Anatomical surface','SUBSURF');sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name)
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='Y',axis_up='Z',mesh_smooth_type='FACE')
 print('ANATOMICAL_HAND',name,len(mesh.vertices),tuple(o.dimensions))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'FishingHands.blend'))
# Close-up review render of the right hand only, before committing it to the game rig.
bpy.data.objects['SM_AnatomicalLeft'].hide_render=True
bpy.ops.object.camera_add(location=(.23,-.40,.24));cam=bpy.context.object;cam.rotation_euler=(Vector((-.07,.03,-.045))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;bpy.context.scene.camera=cam
for loc,power,size in [((.15,-.2,.6),25,.4),((-.3,.5,.3),15,.4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((-.08,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'HandReview.png');scene.world.color=(.12,.12,.12);bpy.ops.render.render(write_still=True)
print('ANATOMICAL_REVIEW_COMPLETE')
