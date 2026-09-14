import unreal as u
lib = u.MaterialEditingLibrary
leaves = u.load_asset('/Game/LureArt/M_PBR_tree_small_02_leaves')
nodes = lib.get_material_expressions(leaves)
diffuse = next(n for n in nodes if isinstance(n, u.MaterialExpressionTextureSample)
               and 'leaves_diff' in n.get_editor_property('texture').get_name())
# Transmitted light should preserve leaf pigmentation rather than using a
# uniform bright color over the entire crown.
scatter = lib.create_material_expression(leaves, u.MaterialExpressionMultiply)
scatter.set_editor_property('const_b', 0.28)
assert lib.connect_material_expressions(diffuse, 'RGB', scatter, 'A')
assert lib.connect_material_property(scatter, '', u.MaterialProperty.MP_SUBSURFACE_COLOR)
lib.recompile_material(leaves)
assert u.EditorAssetLibrary.save_loaded_asset(leaves)
skin = u.load_asset('/Game/LureArt/M_AnatomicalSkin')
for node in lib.get_material_expressions(skin):
    if isinstance(node, u.MaterialExpressionConstant) and abs(node.get_editor_property('r') - .16) < .001:
        node.set_editor_property('r', .85)
lib.recompile_material(skin)
assert u.EditorAssetLibrary.save_loaded_asset(skin)
print('SUBSURFACE_REFINED')
