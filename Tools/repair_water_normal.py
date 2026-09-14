import unreal as u
lib = u.MaterialEditingLibrary
m = u.load_asset('/Game/LureArt/M_LakeWater')
nodes = lib.get_material_expressions(m)
normal = next(n for n in nodes if isinstance(n, u.MaterialExpressionCustom)
              and '-0.012*cos(a)' in n.get_editor_property('code'))
# Explicitly select the calibrated small ripples; older duplicate nodes remain
# in this material and must not determine the surface normal.
assert lib.connect_material_property(normal, '', u.MaterialProperty.MP_NORMAL)
m.set_editor_property('tangent_space_normal', False)
lib.recompile_material(m)
assert u.EditorAssetLibrary.save_loaded_asset(m)
print('WATER_NORMAL_CONNECTED', normal.get_name())
