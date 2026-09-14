"""Use UE's water volume shading while preserving the existing ripple normal."""
import unreal as u
lib=u.MaterialEditingLibrary
path='/Game/LureArt/M_LakeWater'
backup='/Game/LureArt/M_LakeWater_PreSingleLayer'
if not u.EditorAssetLibrary.does_asset_exist(backup):
    assert u.EditorAssetLibrary.duplicate_asset(path,backup)
m=u.load_asset(path)
m.set_editor_property('blend_mode',u.BlendMode.BLEND_OPAQUE)
water_enum=next(name for name in dir(u.MaterialShadingModel) if 'SINGLE' in name and 'WATER' in name)
m.set_editor_property('shading_model',getattr(u.MaterialShadingModel,water_enum))
nodes=lib.get_material_expressions(m)
output=next((n for n in nodes if isinstance(n,u.MaterialExpressionSingleLayerWaterMaterialOutput)),None)
if output is None:output=lib.create_material_expression(m,u.MaterialExpressionSingleLayerWaterMaterialOutput,600,300)
def scalar(value,x,y):
    n=lib.create_material_expression(m,u.MaterialExpressionConstant,x,y);n.set_editor_property('r',value);return n
def vector(value,x,y):
    n=lib.create_material_expression(m,u.MaterialExpressionConstant3Vector,x,y)
    n.set_editor_property('constant',u.LinearColor(*value,1));return n
# Coefficients are inverse centimetres, not per-metre values.
for name,value in [('ScatteringCoefficients',(.00025,.0006,.00065)),
                   ('AbsorptionCoefficients',(.0028,.0008,.0005))]:
    assert lib.connect_material_expressions(vector(value,200,300),'',output,name)
assert lib.connect_material_expressions(scalar(.2,200,500),'',output,'PhaseG')
for prop,value in [(u.MaterialProperty.MP_ROUGHNESS,.08),
                   (u.MaterialProperty.MP_METALLIC,0),
                   (u.MaterialProperty.MP_SPECULAR,.5),
                   (u.MaterialProperty.MP_OPACITY,.25)]:
    assert lib.connect_material_property(scalar(value,200,650),'',prop)
assert lib.connect_material_property(vector((0,0,0),200,750),'',u.MaterialProperty.MP_BASE_COLOR)
lib.recompile_material(m)
assert u.EditorAssetLibrary.save_loaded_asset(m)
print('SINGLE_LAYER_LAKE_SAVED')
