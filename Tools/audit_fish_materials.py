import unreal as u
lib = u.MaterialEditingLibrary
for name in ['SM_BassBody', 'SM_BassTail']:
    mesh = u.load_asset('/Game/LureArt/' + name)
    for slot in mesh.static_materials:
        m = slot.material_interface
        print('FISH_SLOT', name, str(slot.material_slot_name), m.get_name())
for name in ['M_FinRealistic', 'M_PBR_M_BassSkin']:
    m = u.load_asset('/Game/LureArt/' + name)
    print('FISH_MATERIAL', name, m.get_editor_property('shading_model'), m.get_editor_property('blend_mode'))
    for n in lib.get_material_expressions(m):
        if isinstance(n, u.MaterialExpressionCustom):
            print('FISH_CODE', n.get_editor_property('code'))
        if isinstance(n, u.MaterialExpressionConstant):
            print('FISH_CONSTANT', n.get_editor_property('r'))
print('FISH_AUDIT_COMPLETE')
