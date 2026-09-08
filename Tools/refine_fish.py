import bpy,math,os,json
from mathutils import Vector
OUT='D:/LureGame/ArtSource/Realistic';bpy.ops.wm.open_mainfile(filepath='D:/LureGame/ArtSource/LureAssets.blend')
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);d.materials.append(bpy.data.materials[m]);return o
def sphere(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials[m]);return o
def tube(n,points,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(bpy.data.materials[m]);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
def export(parts,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 for p in o.data.polygons:p.use_smooth=True
 bpy.ops.export_scene.fbx(filepath=OUT+'/'+name+'.fbx',use_selection=True,object_types={'MESH'},axis_forward='Y',axis_up='Z',mesh_smooth_type='FACE')
 return o
N=48;v=[];faces=[]
# Tail peduncle, caudal body, shoulder, cheek and broad predatory jaw.
rings=[(-.225,.008,.014,0),(-.19,.012,.022,0),(-.15,.020,.040,0),(-.10,.031,.056,0),(-.04,.039,.067,.001),(.025,.041,.065,.003),(.08,.038,.057,.003),(.125,.033,.046,.002),(.165,.027,.033,-.002),(.199,.023,.023,-.004),(.211,.018,.015,-.007)]
for x,w,h,z in rings:
 for j in range(N):
  a=j*math.tau/N;v.append((x,w*math.cos(a),z+h*math.sin(a)))
for i in range(len(rings)-1):
 for j in range(N):faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
faces.extend([tuple(range(N-1,-1,-1)),tuple((len(rings)-1)*N+j for j in range(N))])
body=mesh('AnatomicalBody',v,faces,'BassSide');bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
sub=body.modifiers.new('Body continuity','SUBSURF');sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name);parts=[body]
for sign in [-1,1]:
 parts.append(sphere('EyeSocket',(.137,sign*.028,.024),(.012,.004,.010),'BassBack'))
 parts.append(sphere('Eye',(.14,sign*.031,.025),(.008,.003,.008),'Iris'))
 parts.append(sphere('Pupil',(.142,sign*.033,.025),(.004,.001,.005),'Pupil'))
 pts=[(.095-.025*math.sin(t*math.pi),sign*(.026+.01*math.sin(t*math.pi)),.043-t*.080) for t in [i/15 for i in range(16)]]
 parts.append(tube('Gill seam',pts,.00065,'BassBack'))
 parts.append(tube('Jaw seam',[(.212,sign*.018,-.006),(.187,sign*.027,-.012),(.15,sign*.031,-.028),(.12,sign*.030,-.033)],.0008,'BassBack'))
 # Pectoral fan, pelvic fan: thin continuous membrane, visible fine rays.
 for root,edge in [((.063,sign*.035,-.010),[(-.001,sign*.072,-.027),(-.025,sign*.063,-.039),(-.037,sign*.046,-.039)]),((.020,sign*.018,-.055),[(-.033,sign*.035,-.083),(-.059,sign*.015,-.075)])]:
  pp=[root]+edge;parts.append(mesh('Fin membrane',pp,[tuple(range(len(pp)))],'BassFin'))
  for dest in edge:parts.append(tube('Fin rays',[root,dest],.00035,'BassFin'))
# Two dorsal sections follow the back contour, with separate stiff and soft rays.
for xs,heights in [([.08,.06,.04,.02,0,-.02,-.04],[.015,.032,.039,.041,.037,.030,.020]),([-.04,-.065,-.09,-.115,-.14,-.16],[.024,.038,.043,.040,.030,.012])]:
 vv=[]
 for x,h in zip(xs,heights):
  base=.064 if x>-.08 else .061-(abs(x)-.08)*.33;vv += [(x,0,base),(x-.005,0,base+h)];parts.append(tube('Dorsal ray',vv[-2:],.00045,'BassFin'))
 parts.append(mesh('Dorsal membrane',vv,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(xs)-1)],'BassFin'))
base=export(parts,'SM_BassBody')
for species,scale in [('Perch',(.68,.8,1.08)),('Pike',(1.5,.65,.70)),('Trout',(.95,.75,.85))]:
 o=base.copy();o.data=base.data.copy();bpy.context.collection.objects.link(o)
 for vert in o.data.vertices:vert.co=Vector(tuple(vert.co[i]*scale[i] for i in range(3)))
 export([o],'SM_'+species+'Body')
bpy.ops.wm.save_as_mainfile(filepath='D:/LureGame/ArtSource/Fish_Refined.blend');print('FISH_REFINED')
