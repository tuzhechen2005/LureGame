import unreal as u
lib = u.MaterialEditingLibrary
for name in ['M_PBR_tree_small_02_leaves', 'M_AnatomicalSkin']:
    m = u.load_asset('/Game/LureArt/' + name)
    print('SHADING', name, m.get_editor_property('shading_model'))
    for n in lib.get_material_expressions(m):
        if isinstance(n, u.MaterialExpressionConstant3Vector):
            print('COLOR', n.get_name(), n.get_editor_property('constant'))
        if isinstance(n, u.MaterialExpressionTextureSample):
            tex = n.get_editor_property('texture')
            print('TEXTURE', tex.get_name(), 'SRGB', tex.get_editor_property('srgb'))
    print('AUDITED', name)
