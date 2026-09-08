import unreal as u, os, json
ROOT='/Game/LureArt';SRC='D:/LureGame/ArtSource/Realistic';assets=u.AssetToolsHelpers.get_asset_tools();lib=u.MaterialEditingLibrary
manifest=json.load(open(SRC+'/manifest.json'))
built={}
def imp(fn):
 t=u.AssetImportTask();t.filename=SRC+'/'+fn;t.destination_path=ROOT;t.automated=True;t.replace_existing=True;t.save=True
 if fn.endswith('.fbx'):
  o=u.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.import_as_skeletal=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=o
 assets.import_asset_tasks([t]);print('IMPORT_REAL',fn)
for fn in os.listdir(SRC):
 if fn.endswith('.png') or fn.endswith('.fbx'):imp(fn)
def create(name):
 assetname='M_PBR_'+name
 m=u.load_asset(ROOT+'/'+assetname) or assets.create_asset(assetname,ROOT,u.Material,u.MaterialFactoryNew())
 lib.delete_all_material_expressions(m);built[name]=m;return m
def node(m,cls):return lib.create_material_expression(m,cls,0,0)
def local_position(m):
 src=node(m,u.MaterialExpressionPreSkinnedPosition);v=node(m,u.MaterialExpressionVertexInterpolator);assert lib.connect_material_expressions(src,'',v,'VS');return v
def const(m,v):
 n=node(m,u.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def prop(m,n,p,out=''):lib.connect_material_property(n,out,p)
def custom(m,code,inputs,vec=True):
 n=node(m,u.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3 if vec else u.CustomMaterialOutputType.CMOT_FLOAT1)
 aa=[]
 for name,src in inputs:
  a=u.CustomInput();a.set_editor_property('input_name',name);aa.append(a)
 n.set_editor_property('inputs',aa)
 for name,src in inputs:lib.connect_material_expressions(src,'',n,name)
 return n
def save(m):
 m.set_editor_property('used_with_instanced_static_meshes',True);lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
for name,maps in manifest.items():
 if isinstance(maps,list):continue
 m=create(name)
 if 'alpha' in maps:
  m.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED);m.set_editor_property('two_sided',True);m.set_editor_property('opacity_mask_clip_value',.35)
 for kind,texname in maps.items():
  tex=u.load_asset(ROOT+'/'+texname)
  tex.set_editor_property('srgb',kind=='diff')
  if kind=='normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);tex.set_editor_property('flip_green_channel',True)
  u.EditorAssetLibrary.save_loaded_asset(tex)
  n=node(m,u.MaterialExpressionTextureSample);n.set_editor_property('texture',tex)
  n.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if kind=='normal' else u.MaterialSamplerType.SAMPLERTYPE_COLOR if kind=='diff' else u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
  prop(m,n,{'diff':u.MaterialProperty.MP_BASE_COLOR,'normal':u.MaterialProperty.MP_NORMAL,'rough':u.MaterialProperty.MP_ROUGHNESS,'alpha':u.MaterialProperty.MP_OPACITY_MASK}[kind],'RGB' if kind in ['diff','normal'] else 'R')
 save(m)
for name,slots in manifest.items():
 if not isinstance(slots,list):continue
 mesh=u.load_asset(ROOT+'/'+name)
 for i,mat in enumerate(slots):mesh.set_material(i,built.get(mat) or u.load_asset(ROOT+'/'+mat))
 u.EditorAssetLibrary.save_loaded_asset(mesh)
# Physical small-scale surface detail on first-person equipment.
settings={'Skin':((.43,.23,.14),(.56,.33,.22),.52,0,70),'Cork':((.13,.063,.022),(.48,.30,.13),.84,0,6),'Jacket':((.021,.035,.030),(.055,.074,.058),.87,0,40),'Carbon':((.005,.008,.012),(.025,.032,.04),.28,.65,25),'Metal':((.31,.34,.36),(.58,.62,.64),.23,.9,50)}
for name,(a,b,rough,metal,freq) in settings.items():
 m=create(name);p=local_position(m)
 code='float3 q=P*'+str(freq)+'; float n=frac(sin(dot(floor(q),float3(127.1,311.7,74.7)))*43758.5453);'
 if name=='Cork':code+='n=pow(n,.35);'
 elif name in ['Jacket','Carbon']:code+='n=.5+.25*sin(q.x*3.14)*sin(q.z*3.14);'
 else:code+='n=.35+n*.3;'
 code+='return lerp(float3'+str(a)+',float3'+str(b)+',n);'
 prop(m,custom(m,code,[('P',p)]),u.MaterialProperty.MP_BASE_COLOR)
 prop(m,const(m,rough),u.MaterialProperty.MP_ROUGHNESS);prop(m,const(m,metal),u.MaterialProperty.MP_METALLIC)
 prop(m,custom(m,'float3 q=P*'+str(freq)+';return normalize(float3(.075*sin(q.x*3.14),.075*sin(q.z*3.14),1));',[('P',p)]),u.MaterialProperty.MP_NORMAL);save(m)
# Continuous pigmentation and overlapping scale highlights replace flat body bands.
for species in ['Bass','Perch','Pike','Trout']:
 m=create('M_'+species+'Skin');p=local_position(m)
 code='float z=P.z;float3 c=lerp(float3(.52,.54,.40),float3(.055,.095,.038),smoothstep(-4.,5.5,z));float row=floor(z*3.5);float2 q=float2(P.x*3.2+fmod(row,2.)*.5,z*3.5);float2 f=frac(q)-.5;float sc=smoothstep(.42,.48,length(f*float2(1.,.8)));c*=.88+.15*sc;'
 if species=='Bass':code+='float stripe=exp(-z*z*.45)*(.6+.4*sin(P.x*2.8));c*=1.-.55*stripe;'
 elif species=='Perch':code+='c*=1.-.55*pow(.5+.5*sin(P.x*2.7),8.)*smoothstep(-5.,0.,z);'
 elif species=='Pike':code+='c+=float3(.15,.14,.06)*smoothstep(.78,.88,sin(P.x*2.)*sin(z*3.));'
 else:code+='c=lerp(c,float3(.46,.50,.49),.55);c=lerp(c,float3(.44,.22,.26),exp(-z*z*.4)*.5);c*=1.-.65*smoothstep(.8,.9,sin(P.x*7.)*sin(z*6.));'
 prop(m,custom(m,code+'return c;',[('P',p)]),u.MaterialProperty.MP_BASE_COLOR);prop(m,const(m,.3),u.MaterialProperty.MP_ROUGHNESS);prop(m,const(m,.12),u.MaterialProperty.MP_METALLIC)
 prop(m,custom(m,'float row=floor(P.z*3.5);float2 q=float2(P.x*3.2+fmod(row,2.)*.5,P.z*3.5);return normalize(float3(.12*sin(q.x*6.283),.12*sin(q.y*6.283),1));',[('P',p)]),u.MaterialProperty.MP_NORMAL);save(m)
 mesh=u.load_asset(ROOT+'/SM_'+species+'Body')
 for i,slot in enumerate(mesh.static_materials):
  old=slot.material_interface.get_name() if slot.material_interface else ''
  if old in ['BassBack','BassSide','BassBelly','BassStripe','PerchSide','PikeSide','TroutSide','PerchBar','TroutSpots'] or old.endswith('Skin'):mesh.set_material(i,m)
 u.EditorAssetLibrary.save_loaded_asset(mesh)
for meshname in ['SM_RightArm','SM_LeftArm','SM_RodHandle','SM_ReelCrank','SM_Guide']:
 mesh=u.load_asset(ROOT+'/'+meshname)
 for i,slot in enumerate(mesh.static_materials):
  old=slot.material_interface.get_name() if slot.material_interface else ''
  old=old.removeprefix('M_Real_').removeprefix('M_PBR_')
  if old in settings:mesh.set_material(i,built[old])
 u.EditorAssetLibrary.save_loaded_asset(mesh)
print('REALISTIC_IMPORT_COMPLETE')

