import unreal as u
lib=u.MaterialEditingLibrary
m=u.load_asset('/Game/LureArt/M_LakeWater')
backup='/Game/LureArt/M_LakeWater_PreRippleSpectrum'
if not u.EditorAssetLibrary.does_asset_exist(backup):
    assert u.EditorAssetLibrary.duplicate_asset(m.get_path_name().split('.')[0],backup)
nodes=lib.get_material_expressions(m)
normal=next((n for n in nodes if isinstance(n,u.MaterialExpressionCustom)
             and n.get_editor_property('description')=='Lake ripple spectrum'),None)
if normal is None:
    normal=lib.create_material_expression(m,u.MaterialExpressionCustom,0,0)
    args=[]
    for name,kind in [('P',u.MaterialExpressionWorldPosition),('T',u.MaterialExpressionTime)]:
        arg=u.CustomInput();arg.set_editor_property('input_name',name);args.append(arg)
    normal.set_editor_property('inputs',args)
    for name,kind in [('P',u.MaterialExpressionWorldPosition),('T',u.MaterialExpressionTime)]:
        source=lib.create_material_expression(m,kind,-300,0)
        assert lib.connect_material_expressions(source,'',normal,name)
normal.set_editor_property('description','Lake ripple spectrum')
args=list(normal.get_editor_property('inputs'))
if not any(str(a.get_editor_property('input_name'))=='WaveStrength' for a in args):
    arg=u.CustomInput();arg.set_editor_property('input_name','WaveStrength');args.append(arg)
    normal.set_editor_property('inputs',args)
strength=lib.create_material_expression(m,u.MaterialExpressionScalarParameter,-300,200)
strength.set_editor_property('parameter_name','WaveStrength');strength.set_editor_property('default_value',1.0)
assert lib.connect_material_expressions(strength,'',normal,'WaveStrength')
normal.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
normal.set_editor_property('code','''
float2 slope = float2(0,0);
[unroll] for(int i=0;i<8;i++) {
    float fi=float(i);
    float angle=0.65+1.15*sin(fi*2.39996);
    float2 direction=float2(cos(angle),sin(angle));
    float k=0.012*pow(1.57,fi);
    float phase=dot(P.xy,direction)*k-sqrt(980*k)*T+fi*7.13;
    slope += direction*cos(phase)*(0.012*pow(0.78,fi));
}
return normalize(float3(-slope*WaveStrength,1));
''')
assert lib.connect_material_property(normal,'',u.MaterialProperty.MP_NORMAL)
m.set_editor_property('tangent_space_normal',False)
# Coarse lake vertices cannot represent centimetre-scale geometric ripples.
# Keep the shoreline elevation stable; shade the small surface waves instead.
zero=lib.create_material_expression(m,u.MaterialExpressionConstant)
zero.set_editor_property('r',0)
assert lib.connect_material_property(zero,'',u.MaterialProperty.MP_WORLD_POSITION_OFFSET)
rough=lib.create_material_expression(m,u.MaterialExpressionScalarParameter)
rough.set_editor_property('parameter_name','WaterRoughness');rough.set_editor_property('default_value',.12)
assert lib.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
lib.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
print('LAKE_RIPPLE_SPECTRUM_SAVED')
