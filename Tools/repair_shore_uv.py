import unreal as u

lib = u.MaterialEditingLibrary
material = u.load_asset('/Game/LureArt/M_Shore')
nodes = lib.get_material_expressions(material)
uv = next(n for n in nodes if isinstance(n, u.MaterialExpressionCustom))
samples = [n for n in nodes if isinstance(n, u.MaterialExpressionTextureSample)]
assert len(samples) == 3
for sample in samples:
    assert lib.connect_material_expressions(uv, '', sample, 'UVs')
lib.recompile_material(material)
assert u.EditorAssetLibrary.save_loaded_asset(material)
terrain = u.load_asset('/Game/LureArt/SM_CoveTerrain')
terrain.set_material(0, material)
assert u.EditorAssetLibrary.save_loaded_asset(terrain)
print('SHORE_UV_REPAIRED: three texture coordinates connected; terrain material assigned')
