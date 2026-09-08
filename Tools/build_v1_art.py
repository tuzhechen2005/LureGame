import bpy,math,random,os
from mathutils import Vector
random.seed(102)
bpy.ops.wm.open_mainfile(filepath='D:/LureGame/ArtSource/LureAssets.blend')
for o in bpy.data.objects:o.hide_set(True)
OUT='D:/LureGame/ArtSource/Export'
def mat(n,c,metal=0,rough=.6):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def uv(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 for q in o.data.polygons:q.use_smooth=True
 return o
def rod(n,a,b,r1,r2,m):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r1,radius2=r2,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y');o.data.materials.append(m)
 for q in o.data.polygons:q.use_smooth=True
 return o
def export(n,parts):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=n;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.export_scene.fbx(filepath=OUT+'/'+n+'.fbx',use_selection=True,object_types={'MESH'},axis_forward='Y',axis_up='Z',mesh_smooth_type='FACE');o.hide_set(True);return o
bark=mat('Bark',(.075,.045,.022),0,.96);leaves=[mat('Leaves'+str(i),c) for i,c in enumerate([(.035,.095,.028),(.075,.135,.035),(.10,.16,.055)])]
# Broadleaf tree with branching structure and irregular leaf clusters.
for name,height in [('SM_Birch',8),('SM_Pine',11)]:
 parts=[rod('Trunk',(0,0,0),(.15,0,height),.16,.025,bark)]
 for k in range(24):
  a=k*2.399;z=height*(.35+.6*k/24);radius=(1-k/30)*2.3
  end=(math.cos(a)*radius,math.sin(a)*radius,z+.35)
  parts.append(rod('Branch',(.05,0,z-.6),end,.035,.004,bark))
  for j in range(4):
   p=(end[0]+random.uniform(-.5,.5),end[1]+random.uniform(-.5,.5),end[2]+random.uniform(-.15,.5))
   parts.append(uv('Foliage',p,(random.uniform(.6,1.0),random.uniform(.6,1),random.uniform(.3,.65)),leaves[(j+k)%3]))
 export(name,parts)
# A gently sloping irregular bank; local coordinates preserved in centimeters by FBX.
v=[];f=[];NX=40;NY=120
for j in range(NY+1):
 y=-60+j;edge=.45*math.sin(y*.43)+.22*math.sin(y*1.1)
 for i in range(NX+1):
  x=-36+i*.94+edge;z=.70+.06*math.sin(x*.4)*math.cos(y*.6) if x<-2 else .7-(x+2)*.72
  v.append((x,y,z))
for j in range(NY):
 for i in range(NX):a=j*(NX+1)+i;f.append((a,a+1,a+NX+2,a+NX+1))
d=bpy.data.meshes.new('Bank');d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new('Bank',d);bpy.context.collection.objects.link(o);o.data.materials.append(bark)
for q in d.polygons:q.use_smooth=True
export('SM_Bank',[o])
# Minnow and alternative baits, all with a small visible hook.
metal=mat('LureMetal',(.5,.58,.6),.9,.18);orange=mat('LureOrange',(.75,.24,.025),.3,.32);green=mat('LureGreen',(.14,.22,.025),.25,.43)
def hook(x,z):
 parts=[]
 for k in range(12):
  a=k/12*math.pi*1.6;b=(k+1)/12*math.pi*1.6
  parts.append(rod('Hook',(x+.006*math.cos(a),0,z+.006*math.sin(a)),(x+.006*math.cos(b),0,z+.006*math.sin(b)),.0006,.0006,metal))
 return parts
for i,n in enumerate(['SM_Minnow','SM_SoftBait','SM_Spinner','SM_Popper','SM_Jig']):
 parts=[]
 if i in [0,3]:
  parts=[uv('Body',(0,0,0),(.052 if i==0 else .033,.009,.012),orange),uv('Back',(-.004,0,.006),(.045 if i==0 else .027,.008,.008),green)]
  for sg in [-1,1]:parts.append(uv('Eye',(.029,sg*.008,.003),(.0025,.001,.0025),metal))
 elif i==1:
  for k in range(12):parts.append(uv('Worm',(-k*.008,math.sin(k*.6)*.005,0),(.009,.005-k*.0002,.005-k*.0002),green))
 elif i==2:
  parts=[rod('Wire',(-.04,0,0),(.03,0,0),.0008,.0008,metal),uv('Blade',(-.01,0,.008),(.025,.009,.002),metal),uv('Weight',(.018,0,0),(.012,.004,.004),orange)]
 else:
  parts=[uv('JigHead',(.02,0,0),(.008,.008,.008),orange)]
  for k in range(12):a=k/12*math.tau;parts.append(rod('Skirt',(.02,0,0),(-.04,math.cos(a)*.016,math.sin(a)*.016),.0009,.0004,green))
 parts+=hook(-.018,-.017);export(n,parts)
# Species variants retain individual fins/eyes and gain species-specific proportions and coloring.
source=bpy.data.objects['SM_BassBody'];tail=bpy.data.objects['SM_BassTail']
for name,scale,c in [('Perch',(.68,.8,1.08),(.40,.43,.14)),('Pike',(1.5,.65,.70),(.24,.30,.11)),('Trout',(.95,.75,.85),(.38,.42,.42))]:
 o=source.copy();o.data=source.data.copy();bpy.context.collection.objects.link(o);o.hide_set(False);o.scale=scale
 m=mat(name+'Side',c,.2,.37)
 for k,old in enumerate(o.data.materials):
  if old and old.name=='BassSide':o.data.materials[k]=m
 parts=[o]
 if name=='Perch':
  for k in range(7):
   x=-.12+k*.034
   for sg in [-1,1]:parts.append(uv('Bar',(x,sg*.037,0),(.007,.0015,.049),mat('PerchBar',(.055,.1,.04))))
 if name=='Trout':
  spot=mat('TroutSpots',(.03,.05,.06))
  for k in range(50):
   x=random.uniform(-.15,.1);z=random.uniform(-.015,.035);w=.038*math.sqrt(max(.1,1-(x/.24)**2))
   for sg in [-1,1]:parts.append(uv('Spot',(x,sg*w,z),(.002,.001,.002),spot))
 export('SM_'+name+'Body',parts)
for o in bpy.data.objects:o.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath='D:/LureGame/ArtSource/LureAssets.blend')
print('V1_MODELS_COMPLETE')
