import bpy,math,random,json,pathlib
from mathutils import Vector
ROOT=pathlib.Path('D:/LureGame');OUT=ROOT/'ArtSource/Cove';random.seed(904)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CoveLandform.blend'))
scene=bpy.context.scene;scene.name='Cove_ConceptMatch'
def h(x,y):
 r=math.sqrt(((x-3500)/3500)**2+(y/5600)**2);d=(r-1)*3500
 if d<0:return max(-580,d*.3)
 return min(d*.12,450)+min(1,d/800)*(1000*math.exp(-((x-9500)/4200)**2-((y+4500)/5000)**2)+65*math.sin(x*.0012)*math.cos(y*.0009)+18*math.sin(x*.0041+y*.0023))
def coast(y):return 3500-3500*math.sqrt(max(0,1-(y/5600)**2))
def material(name,maps):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.8
 for kind,stem in maps.items():
  fn=ROOT/'ArtSource/Realistic'/(stem+'.png')
  if not fn.exists():fn=fn.with_suffix('.jpg')
  if not fn.exists():continue
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(fn),check_existing=True)
  if kind!='diff':t.image.colorspace_settings.name='Non-Color'
  if kind=='normal':
   n=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
  else:m.node_tree.links.new(t.outputs['Color'],p.inputs[{'diff':'Base Color','rough':'Roughness','alpha':'Alpha'}[kind]])
 return m
manifest=json.loads((ROOT/'ArtSource/Realistic/manifest.json').read_text(encoding='utf-8'))
for n,maps in manifest.items():
 if isinstance(maps,dict):material(n,maps)
base={}
for name in ['SM_Birch','SM_Grass','SM_Rock','SM_ScanRock1','SM_ScanRock2','SM_ScanRock3','SM_ScanRock4','SM_ScanRock5']:
 old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT/'ArtSource/Realistic'/(name+'.fbx')))
 o=next(o for o in bpy.data.objects if o not in old and o.type=='MESH');o.name=name+'_SOURCE';base[name]=o;o.hide_render=True;o.hide_set(True)
 for i,n in enumerate(manifest[name]):o.data.materials[i]=bpy.data.materials[n]
placements=[{'asset':'SM_CoveTerrain','location':[0,0,0],'rotation':[0,0,0],'scale':[1,1,1],'material':'M_Shore'}]
def put(asset,x,y,z,scale,yaw):
 o=base[asset].copy();o.data=base[asset].data;scene.collection.objects.link(o);o.hide_render=False;o.hide_set(False);o.name=asset+'_Placed';o.location=(x/100,-y/100,z/100);o.rotation_euler=(0,0,-math.radians(yaw));o.scale=scale
 placements.append({'asset':asset,'location':[x,y,z],'rotation':[0,yaw,0],'scale':list(scale)})
# Clustered forest follows the terrain instead of a level row along the horizon.
count=0
while count<420:
 x=random.uniform(-2100,12300);y=random.uniform(-8400,7000);r=math.sqrt(((x-3500)/3500)**2+(y/5600)**2)
 if r<1.075 or r>2.30 or math.hypot(x+420,y)<650:continue
 if math.sin(x*.0019+y*.0013)>.70:continue
 size=random.uniform(.72,1.65);put('SM_Birch',x,y,h(x,y)-12,(size*random.uniform(.85,1.15),size,size),random.uniform(0,360));count+=1
# Foreground framing trees on the left side of the composition.
for x,y,size in [(-360,-700,1.25),(-610,-1400,1.4),(-120,-2100,1.3)]:put('SM_Birch',x,y,h(x,y),(size,size,size),random.uniform(0,360))
rocks=['SM_Rock']+['SM_ScanRock'+str(i) for i in range(1,6)]
for i in range(95):
 y=random.uniform(-5100,5100);x=coast(y)+random.uniform(-90,90)
 if i>65:x=7000-coast(y)+random.uniform(-80,80)
 s=random.uniform(.28,.8);put(random.choice(rocks),x,y,h(x,y)+10,(s,s*random.uniform(.8,1.3),s),random.uniform(0,360))
for x,y,s in [(-20,-200,.65),(-120,-500,.55),(-200,-820,.7),(80,-1050,.5)]:put(random.choice(rocks),x,y,h(x,y),(s,s,s),random.uniform(0,360))
for i in range(1200):
 y=random.uniform(-5000,4200);x=coast(y)-random.uniform(80,900)
 if math.hypot(x+420,y)<110:continue
 s=random.uniform(.45,1.1);put('SM_Grass',x,y,h(x,y),(s,s,s),random.uniform(0,360))
# A clearly marked concept image in the authoring scene, excluded from renders and export.
ref=bpy.data.objects.new('REFERENCE_ONLY_AI_Concept',None);scene.collection.objects.link(ref);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(ROOT/'ArtDirection/Cove-Target-v1.png'));ref.empty_display_size=12;ref.location=(-14,0,7);ref.rotation_euler=(math.pi/2,0,0);ref.hide_render=True
bpy.ops.object.camera_add(location=(-4.2,0,h(-420,0)/100+1.7));cam=bpy.context.view_layer.objects.active;cam.name='ReferenceMatchedCamera';direction=Vector((math.cos(math.radians(-40)),-math.sin(math.radians(-40)),-.12));cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.lens=24;scene.camera=cam
scene.render.resolution_x=1664;scene.render.resolution_y=936;scene.render.resolution_percentage=100
(OUT/'placements.json').write_text(json.dumps(placements),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CoveComposition.blend'))
print('COVE_COMPOSED',len(placements),'objects',len(scene.objects))

