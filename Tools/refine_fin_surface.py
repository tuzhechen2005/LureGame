import unreal as u
lib = u.MaterialEditingLibrary
m = u.load_asset('/Game/LureArt/M_FinRealistic')
color = lib.create_material_expression(m, u.MaterialExpressionConstant3Vector)
color.set_editor_property('constant', u.LinearColor(.075, .095, .043, 1))
assert lib.connect_material_property(color, '', u.MaterialProperty.MP_BASE_COLOR)
for value, prop in [(.62, u.MaterialProperty.MP_ROUGHNESS), (.25, u.MaterialProperty.MP_SPECULAR)]:
    node = lib.create_material_expression(m, u.MaterialExpressionConstant)
    node.set_editor_property('r', value)
    assert lib.connect_material_property(node, '', prop)
lib.recompile_material(m)
assert u.EditorAssetLibrary.save_loaded_asset(m)
print('FIN_SURFACE_REFINED')
