import bpy,math,pathlib
out=pathlib.Path('D:/LureGame/ArtSource/Cove');out.mkdir(exist_ok=True)
def height(x,y):
 r=math.sqrt(((x-3500)/3500)**2+(y/5600)**2);d=(r-1)*3500
 if d<0:return max(-580,d*.3)
 fade=max(0,min(1,d/800));hill=1000*math.exp(-((x-9500)/4200)**2-((y+4500)/5000)**2)
 return min(d*.12,450)+fade*(hill+65*math.sin(x*.0012)*math.cos(y*.0009)+18*math.sin(x*.0041+y*.0023))
# New file, independently authored terrain, never touches the open rod catalogue.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
N=256;vertices=[];faces=[]
for j in range(N+1):
 y=-11000+22000*j/N
 for i in range(N+1):
  x=-4500+18000*i/N;vertices.append((x/100,-y/100,height(x,y)/100))
for j in range(N):
 for i in range(N):
  a=j*(N+1)+i;faces.append((a,a+N+1,a+N+2,a+1))
mesh=bpy.data.meshes.new('CoveLandform');mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new('SM_CoveTerrain',mesh);bpy.context.collection.objects.link(obj)
for p in mesh.polygons:p.use_smooth=True
obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(out/'SM_CoveTerrain.fbx'),use_selection=True,object_types={'MESH'},axis_forward='Y',axis_up='Z',mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'CoveLandform.blend'));print('COVE_TERRAIN_COMPLETE')
