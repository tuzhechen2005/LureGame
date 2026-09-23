"""Import the authored net and two small reusable surface-cue materials."""
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
dest = '/Game/Fishing/Shore'
u.EditorAssetLibrary.make_directory(dest)
lib = u.MaterialEditingLibrary

def simple(name, rgb, roughness, metal=0, emission=0):
    path = dest+'/'+name
    mat = u.load_asset(path)
    if not mat:
        mat = u.AssetToolsHelpers.get_asset_tools().create_asset(name, dest, u.Material, u.MaterialFactoryNew())
    lib.delete_all_material_expressions(mat)
    c = lib.create_material_expression(mat, u.MaterialExpressionConstant3Vector)
    c.set_editor_property('constant', u.LinearColor(*rgb, 1))
    lib.connect_material_property(c, '', u.MaterialProperty.MP_BASE_COLOR)
    for value, prop in [(roughness, u.MaterialProperty.MP_ROUGHNESS), (metal, u.MaterialProperty.MP_METALLIC)]:
        node = lib.create_material_expression(mat, u.MaterialExpressionConstant)
        node.set_editor_property('r', value)
        lib.connect_material_property(node, '', prop)
    if emission:
        n = lib.create_material_expression(mat, u.MaterialExpressionMultiply)
        n.set_editor_property('const_b', emission)
        lib.connect_material_expressions(c, '', n, 'A')
        lib.connect_material_property(n, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
    lib.recompile_material(mat)
    assert u.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

materials = {
    'Net_Anodized': simple('M_NetFrame', (.08,.10,.105), .26, .8),
    'Net_Rubber': simple('M_NetRubber', (.027,.034,.032), .72),
    'Net_Grip': simple('M_NetGrip', (.12,.105,.075), .83),
    'Net_Accent': simple('M_NetAccent', (.52,.20,.04), .4),
}
simple('M_SurfaceWake', (.30,.43,.34), .20, .15, .07)
task = u.AssetImportTask()
task.filename = str(root/'ArtSource'/'LandingNet'/'SM_LandingNet.fbx')
task.destination_path = dest
task.destination_name = 'SM_LandingNet'
task.automated = True
task.replace_existing = True
task.save = True
opt = u.FbxImportUI()
opt.import_mesh = True
opt.import_materials = False
opt.import_textures = False
opt.static_mesh_import_data.combine_meshes = True
task.options = opt
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh = u.load_asset(dest+'/SM_LandingNet')
assert isinstance(mesh, u.StaticMesh)
for index, slot in enumerate(mesh.static_materials):
    mesh.set_material(index, materials[str(slot.material_slot_name)])
assert u.EditorAssetLibrary.save_loaded_asset(mesh)
u.log('SHORE_ASSETS_IMPORTED bounds='+str(mesh.get_bounding_box()))
