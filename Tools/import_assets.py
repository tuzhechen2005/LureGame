import unreal as u, os
ROOT='/Game/LureArt'
assets=u.AssetToolsHelpers.get_asset_tools(); lib=u.MaterialEditingLibrary
for fn in os.listdir('D:/LureGame/ArtSource/Export'):
 if not fn.endswith('.fbx'):continue
 if u.EditorAssetLibrary.does_asset_exist(ROOT+'/'+fn[:-4]):continue
 task=u.AssetImportTask(); task.filename='D:/LureGame/ArtSource/Export/'+fn;task.destination_path=ROOT;task.automated=True;task.replace_existing=True;task.save=True
 opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=True;opts.import_textures=False;opts.import_as_skeletal=False
 opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.generate_lightmap_u_vs=False
 task.options=opts;assets.import_asset_tasks([task])
 print('IMPORTED',fn,task.imported_object_paths)
# Explicit procedural materials, editable as ordinary UE material graphs.
def create(name):
 p=ROOT+'/'+name
 m=u.load_asset(p)
 if not m:m=assets.create_asset(name,ROOT,u.Material,u.MaterialFactoryNew())
 lib.delete_all_material_expressions(m)
 return m
def node(m,typ,x=0,y=0):return lib.create_material_expression(m,typ,x,y)
def scalar(m,v):
 n=node(m,u.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def color(m,c):
 n=node(m,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*c,1));return n
def prop(m,n,p):lib.connect_material_property(n,'',p)
def custom(m,code,inputs,output):
 n=node(m,u.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',output)
 args=[]
 for name,src in inputs:
  a=u.CustomInput();a.set_editor_property('input_name',name);args.append(a)
 n.set_editor_property('inputs',args)
 for name,src in inputs:lib.connect_material_expressions(src,'',n,name)
 return n
m=create('M_LakeWater');m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True)
m.set_editor_property('translucency_lighting_mode',u.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
p=node(m,u.MaterialExpressionWorldPosition);t=node(m,u.MaterialExpressionTime)
w=custom(m,'return float3(0,0,1.7*sin(P.x*0.019+P.y*0.012+T*1.4)+0.85*sin(P.x*0.043-P.y*0.027-T*1.9));',[('P',p),('T',t)],u.CustomMaterialOutputType.CMOT_FLOAT3)
n=custom(m,'float a=P.x*0.026+P.y*0.018+T*1.4; float b=P.x*0.061-P.y*0.047-T*2.0; float c=P.x*0.15+P.y*0.11+T*2.8; return normalize(float3(-0.11*cos(a)-0.07*cos(b)-0.025*cos(c),-0.10*cos(a)+0.08*cos(b)-0.035*cos(c),1));',[('P',p),('T',t)],u.CustomMaterialOutputType.CMOT_FLOAT3)
prop(m,w,u.MaterialProperty.MP_WORLD_POSITION_OFFSET);prop(m,n,u.MaterialProperty.MP_NORMAL)
prop(m,color(m,(.025,.115,.105)),u.MaterialProperty.MP_BASE_COLOR);prop(m,scalar(m,.16),u.MaterialProperty.MP_ROUGHNESS);prop(m,scalar(m,.65),u.MaterialProperty.MP_SPECULAR)
f=node(m,u.MaterialExpressionFresnel);f.set_editor_property('exponent',3)
lerp=node(m,u.MaterialExpressionLinearInterpolate);lerp.set_editor_property('const_a',.64);lerp.set_editor_property('const_b',.92);lib.connect_material_expressions(f,'',lerp,'Alpha');prop(m,lerp,u.MaterialProperty.MP_OPACITY)
lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
# Procedural earth variation avoids a single flat-color shore.
m=create('M_Shore');p=node(m,u.MaterialExpressionWorldPosition)
c=custom(m,'struct FN{float h(float2 p){return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453);}float n(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(h(i),h(i+float2(1,0)),f.x),lerp(h(i+float2(0,1)),h(i+1),f.x),f.y);}};FN g;float v=g.n(P.xy*.015)*.65+g.n(P.xy*.13)*.25+g.n(P.xy*.65)*.1;return lerp(float3(.07,.078,.031),float3(.20,.16,.083),v);',[('P',p)],u.CustomMaterialOutputType.CMOT_FLOAT3)
prop(m,c,u.MaterialProperty.MP_BASE_COLOR);prop(m,scalar(m,.95),u.MaterialProperty.MP_ROUGHNESS);lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
for name in ['SM_BassBody','SM_RodHandle','SM_RightArm','SM_WaterGrid']:
 o=u.load_asset(ROOT+'/'+name); print('BOUNDS',name,o.get_bounds().box_extent)
print('LURE_IMPORT_COMPLETE')

