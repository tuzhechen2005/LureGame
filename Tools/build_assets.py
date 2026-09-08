import bpy, math, random, os
from mathutils import Vector
OUT='D:/LureGame/ArtSource'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(51)
def mat(name,c,metal=0,rough=.5):
 m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
skin=mat('Skin',(0.48,.27,.16),0,.55); nail=mat('Nails',(.66,.46,.33)); cloth=mat('Jacket',(.075,.12,.105),0,.85)
cork=mat('Cork',(.38,.23,.105),0,.85); black=mat('Carbon',(.015,.023,.03),.65,.27); silver=mat('Metal',(.42,.5,.52),.85,.23); gold=mat('Gold',(.46,.31,.1),.75,.3); rubber=mat('Rubber',(.023,.024,.02),0,.8)
back=mat('BassBack',(.095,.16,.055),.12,.4);side=mat('BassSide',(.32,.39,.16),.18,.38); belly=mat('BassBelly',(.66,.66,.43),.05,.5);stripe=mat('BassStripe',(.04,.08,.03),.05,.6);fin=mat('BassFin',(.22,.26,.1),.05,.6); iris=mat('Iris',(.55,.31,.07),.5,.22); pupil=mat('Pupil',(.003,.005,.004),.3,.12)
def smooth(o):
 for p in o.data.polygons:p.use_smooth=True
 return o
def uv(name,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return smooth(o)
def rod(name,a,b,r1,r2,m,verts=24):
 a,b=Vector(a),Vector(b);d=b-a
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=d.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y');o.data.materials.append(m); return smooth(o)
def torus(name,loc,major,minor,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=loc,major_radius=major,minor_radius=minor,rotation=rot);o=bpy.context.object;o.name=name;o.data.materials.append(m);return smooth(o)
def mesh(name,v,f,m):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.export_scene.fbx(filepath=OUT+'/Export/'+name+'.fbx',use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='Y',axis_up='Z',bake_space_transform=False)
 o.hide_set(True);return o
# Bass oriented along +X, body length 46 cm; anatomical cross sections, dorsal stripe and belly.
v=[];f=[];nr=32
rings=[(-.225,.013,.018),(-.19,.022,.035),(-.14,.035,.061),(-.08,.047,.082),(0,.048,.078),(.07,.037,.061),(.14,.027,.041),(.19,.021,.027),(.205,.012,.022)]
for x,w,h in rings:
 for j in range(nr):
  a=j*2*math.pi/nr;v.append((x,w*math.cos(a),h*math.sin(a)))
for i in range(len(rings)-1):
 for j in range(nr): f.append((i*nr+j,i*nr+(j+1)%nr,(i+1)*nr+(j+1)%nr,(i+1)*nr+j))
f.extend([tuple(range(nr-1,-1,-1)),tuple((len(rings)-1)*nr+j for j in range(nr))])
body=mesh('BassBody',v,f,side)
for m in [back,belly,stripe]:body.data.materials.append(m)
for poly in body.data.polygons:
 z=sum(body.data.vertices[k].co.z for k in poly.vertices)/len(poly.vertices)
 if z>.032:poly.material_index=1
 elif z<-.023:poly.material_index=2
 elif abs(z)<.01:poly.material_index=3
smooth(body);sub=body.modifiers.new('Body smooth','SUBSURF');sub.levels=2;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=sub.name)
parts=[body]
for sign in [-1,1]:
 parts += [uv('Eye',(.141,sign*.025,.018),(.012,.005,.011),iris),uv('Pupil',(.144,sign*.029,.019),(.006,.002,.007),pupil)]
 # Gill plate rim and subtle lateral markings.
 parts += [rod('Gill',(.086,sign*.036,.036),(.055,sign*.042,-.025),.0015,.001,back)]
 for k in range(16):
  x=-.14+k*.015; w=.035+ .01*math.sin(k/16*math.pi)
  parts.append(uv('ScaleMark',(x,sign*w,.008+random.uniform(-.009,.009)),(.006,.001,.003),back))
 # Pectoral and pelvic fins, separate fine rays.
 parts.append(mesh('Pectoral',[(.07,sign*.03,-.014),(-.01,sign*.095,-.035),(-.05,sign*.065,-.05)],[(0,1,2),(2,1,0)],fin))
 for k in range(5):parts.append(rod('FinRay',(.07,sign*.03,-.014),(-.01-k*.009,sign*(.095-k*.006),-.035-k*.003),.0006,.0002,back,8))
# Dorsal spines and membrane.
verts=[]
for i in range(13):
 x=-.15+i*.019; base=.066 if x<.05 else .05; top=base+.025+ .023*math.sin(i/12*math.pi)
 verts.extend([(x,0,base),(x,0,top)])
 parts.append(rod('DorsalRay',(x,0,base),(x,0,top),.0007,.0002,back,8))
faces=[]
for i in range(12):faces.extend([(i*2,i*2+1,i*2+3,i*2+2),(i*2+2,i*2+3,i*2+1,i*2)])
parts.append(mesh('Dorsal',verts,faces,fin));parts.append(uv('LowerJaw',(.172,0,-.018),(.041,.024,.013),belly))
parts.append(rod('MouthLine',(.2,-.016,0),(.2,.016,0),.001,.001,back))
export('SM_BassBody',parts)
# Tail pivot origin = body tail socket.
parts=[mesh('Tail',[(0,-.003,-.018),(0,.003,.018),(-.095,0,.062),(-.071,0,0),(-.095,0,-.062)],[(0,1,2,3,4),(4,3,2,1,0)],fin)]
for i in range(11):parts.append(rod('TailRay',(0,0,0),(-.08-abs(i-5)*.003,0,(i-5)*.011),.0007,.0002,back,8))
export('SM_BassTail',parts)
# Cork grip, reel seat and spinning reel. Rod points +X.
parts=[rod('RearCork',(-.25,0,0),(-.06,0,0),.016,.013,cork),rod('Seat',(-.06,0,0),(.09,0,0),.012,.012,black),rod('ForeCork',(.09,0,0),(.18,0,0),.014,.01,cork)]
for x in [-.25,-.065,.08,.17]:parts.append(rod('Band',(x,0,0),(x+.008,0,0),.016,.016,gold))
parts.extend([rod('ReelStem',(.015,0,-.009),(.015,0,-.07),.008,.006,silver),uv('ReelBody',(-.015,0,-.075),(.045,.023,.033),black),rod('Spool',(.018,0,-.075),(.064,0,-.075),.026,.026,silver)])
for x in [.023,.061]:parts.append(torus('SpoolLip',(x,0,-.075),.027,.003,gold,(0,math.pi/2,0)))
for x in [.03,.035,.04,.045,.05]:parts.append(torus('FishingLine',(x,0,-.075),.025,.0015,belly,(0,math.pi/2,0)))
parts += [torus('Bail',(.054,0,-.075),.038,.0015,silver,(0,math.pi/2,.25))]
export('SM_RodHandle',parts)
parts=[rod('Crank',(0,0,0),(0,.065,-.028),.004,.003,silver),uv('Knob',(0,.069,-.031),(.017,.008,.008),rubber)]
export('SM_ReelCrank',parts)
export('SM_Guide',[torus('Guide',(0,0,0),.01,.0012,silver,(0,math.pi/2,0))])
# First person hands: forearms flow from screen bottom towards grip; curved fingers wrap around X-axis handle.
for name,sgn in [('SM_RightArm',1),('SM_LeftArm',-1)]:
 parts=[rod('Sleeve',(-.42,sgn*.09,-.22),(-.13,sgn*.025,-.025),.052,.035,cloth),rod('Cuff',(-.15,sgn*.03,-.04),(-.105,sgn*.02,-.008),.036,.033,rubber),uv('Palm',(-.048,sgn*.028,-.002),(.058,.026,.022),skin)]
 for i in range(4):
  x=-.082+i*.023
  a=(x,sgn*.029,.013);b=(x,sgn*.007,.026);c=(x,-sgn*.014,.015);d=(x,-sgn*.014,-.009)
  parts.extend([rod('Finger',a,b,.009,.008,skin),uv('Knuckle',b,(.009,.009,.009),skin),rod('Finger',b,c,.008,.007,skin),rod('Tip',c,d,.007,.006,skin),uv('Fingertip',d,(.007,.007,.008),skin)])
 parts += [rod('Thumb',(-.087,sgn*.043,-.01),(-.017,sgn*.025,-.025),.012,.009,skin),uv('ThumbTip',(-.017,sgn*.025,-.025),(.012,.01,.009),skin)]
 export(name,parts)
# Dense grid allows material-driven low amplitude water displacement.
N=100;v=[(i/N,j/N,0) for j in range(N+1) for i in range(N+1)];f=[]
for j in range(N):
 for i in range(N):a=j*(N+1)+i;f.append((a,a+1,a+N+2,a+N+1))
export('SM_WaterGrid',[mesh('Grid',v,f,side)])
# Natural irregular rock, reusable with instancing.
parts=[]
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1);o=bpy.context.object
for v in o.data.vertices:
 v.co*=random.uniform(.85,1.12);v.co.z*=.65
smooth(o);o.data.materials.append(mat('Stone',(.17,.19,.16),0,.95));export('SM_Rock',[o])
# Preserve all models in one source file, laid out only via viewport hiding.
for o in bpy.data.objects:o.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/LureAssets.blend')
print('LURE_ASSETS_COMPLETE')
