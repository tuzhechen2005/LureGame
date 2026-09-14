import unreal as u
m = u.load_asset('/Game/LureArt/M_LakeWater')
for key in ['blend_mode', 'shading_model', 'translucency_lighting_mode', 'tangent_space_normal']:
    print('WATER_SETTING', key, m.get_editor_property(key))
for n in u.MaterialEditingLibrary.get_material_expressions(m):
    if isinstance(n, u.MaterialExpressionCustom):
        print('WATER_CODE', n.get_name(), n.get_editor_property('code'))
print('WATER_GRAPH_AUDITED')
