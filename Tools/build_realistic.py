import bpy, os, json, math
from mathutils import Vector
ROOT='D:/LureGame/ArtSource'; OUT=ROOT+'/Realistic';os.makedirs(OUT,exist_ok=True)
manifest={}
def select(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.hide_viewport=False;o.select_set(True);bpy.context.view_layer.objects.active=o
def export(o,name):
 select(o);o.name=name
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.export_scene.fbx(filepath=OUT+'/'+name+'.fbx',use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='Y',axis_up='Z')
 manifest[name]=[m.name for m in o.data.materials]
 print('EXPORTED',name,len(o.data.vertices),tuple(o.dimensions),flush=True)
def textures(asset):
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  maps={}
  for n in m.node_tree.nodes:
   if n.type!='TEX_IMAGE' or not n.image:continue
   im=n.image;fn=os.path.basename(im.filepath.replace('\\','/'));src=ROOT+'/Nature/'+asset+'/textures/'+fn
   if not os.path.exists(src):continue
   kind='diff' if '_diff_' in fn and '_dry_' not in fn else 'rough' if '_rough_' in fn else 'normal' if '_nor_gl_' in fn else 'alpha' if '_alpha_' in fn else None
   if not kind:continue
   im.filepath=src;im.reload()
   if kind!='diff':im.colorspace_settings.name='Non-Color'
   name=fn.rsplit('.',1)[0];dst=OUT+'/'+name+'.png';im.filepath_raw=dst;im.file_format='PNG';im.save()
   maps[kind]=name
  if maps:manifest[m.name]=maps
for asset in ['rock_moss_set_01','tree_small_02','grass_medium_01']:
 bpy.ops.wm.open_mainfile(filepath=ROOT+'/Nature/'+asset+'/'+asset+'.blend')
 textures(asset)
 if asset.startswith('rock'):
  for i,o in enumerate(sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)):
   select(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
   # Recenter scan at its ground contact, retain UV coordinates.
   coords=[v.co.copy() for v in o.data.vertices];lo=Vector(tuple(min(v[k] for v in coords) for k in range(3)));hi=Vector(tuple(max(v[k] for v in coords) for k in range(3)))
   center=(lo+hi)/2;center.z=lo.z;fac=2/max(hi.x-lo.x,hi.y-lo.y)
   for v in o.data.vertices:v.co=(v.co-center)*fac
   o.location=(0,0,-.4);bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
   export(o,'SM_Rock' if i==0 else 'SM_ScanRock'+str(i))
 elif asset.startswith('tree'):
  o=bpy.data.objects['tree_small_02_LOD1'];select(o)
  dec=o.modifiers.new('Game silhouette reduction','DECIMATE');dec.ratio=.18;bpy.ops.object.modifier_apply(modifier=dec.name)
  coords=[v.co.copy() for v in o.data.vertices];lo=Vector(tuple(min(v[k] for v in coords) for k in range(3)));hi=Vector(tuple(max(v[k] for v in coords) for k in range(3)));center=(lo+hi)/2;center.z=lo.z
  for v in o.data.vertices:v.co=(v.co-center)*(8.5/(hi.z-lo.z))
  o.location=(0,0,0);export(o,'SM_Birch')
 else:
  o=bpy.data.objects['grass_medium_01_geonodes_large_a_LOD1'];o.location=(0,0,0);o.scale=(3,3,3);export(o,'SM_Grass')
bpy.ops.wm.open_mainfile(filepath=ROOT+'/LureAssets.blend')
for name in ['SM_RightArm','SM_LeftArm']:
 o=bpy.data.objects[name];select(o)
 # Separate skin from sleeve so the union cannot bridge cloth to fingers.
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT');bpy.ops.object.mode_set(mode='OBJECT')
 for p in o.data.polygons:p.select=o.data.materials[p.material_index].name=='Skin'
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.separate(type='SELECTED');bpy.ops.object.mode_set(mode='OBJECT')
 skin=next(x for x in bpy.context.selected_objects if x!=o);select(skin)
 rem=skin.modifiers.new('Continuous anatomical skin','REMESH');rem.mode='VOXEL';rem.voxel_size=.0012;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
 sm=skin.modifiers.new('Skin relaxation','SMOOTH');sm.factor=.6;sm.iterations=5;bpy.ops.object.modifier_apply(modifier=sm.name)
 sub=skin.modifiers.new('Hand surface','SUBSURF');sub.levels=1;bpy.ops.object.modifier_apply(modifier=sub.name)
 for p in skin.data.polygons:p.use_smooth=True
 # Cloth folds use continuous surface displacement rather than extra floating rings.
 select(o);sub=o.modifiers.new('Sleeve smooth','SUBSURF');sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name)
 for v in o.data.vertices:
  if v.co.x<-.15:
   v.co.y+=.0018*math.sin(v.co.x*145+v.co.z*35);v.co.z+=.0016*math.sin(v.co.x*132+v.co.y*30)
 select(o);skin.select_set(True);bpy.ops.object.join();export(o,name)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/LureAssets_Realistic.blend')
with open(OUT+'/manifest.json','w') as f:json.dump(manifest,f,indent=2)
