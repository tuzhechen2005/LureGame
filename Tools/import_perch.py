"""Import only prepared CC0 perch assets into /Game/Fishing/Perch.

Run inside Unreal Editor after prepare_perch.py. No C++ or unrelated assets are touched.
The script deliberately constructs materials instead of trusting automatic FBX materials.
"""
import json
from pathlib import Path
import unreal as u

SOURCE = Path(__file__).resolve().parents[1] / 'ArtSource' / 'ThirdParty' / 'Perch'
DESTINATION = '/Game/Fishing/Perch'
METADATA = json.loads((SOURCE/'perch_metadata.json').read_text(encoding='utf-8'))
ASSETS = u.AssetToolsHelpers.get_asset_tools()
LIB = u.MaterialEditingLibrary


def import_one(filename, name, options=None):
    assert Path(filename).is_file(), filename
    assert name in [x['name'] for x in METADATA['meshes']] or name in METADATA['textures'], name
    task = u.AssetImportTask()
    task.filename = str(filename)
    task.destination_path = DESTINATION
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.replace_existing_settings = True
    task.save = True
    if options:
        task.options = options
    ASSETS.import_asset_tasks([task])
    result = u.load_asset(DESTINATION+'/'+name)
    assert result, f'Import failed: {name}; {task.imported_object_paths}'
    return result


def expression(material, kind, x=0, y=0):
    return LIB.create_material_expression(material, kind, x, y)


def constant(material, value, prop, x=-200, y=300):
    node = expression(material, u.MaterialExpressionConstant, x, y)
    node.set_editor_property('r', value)
    assert LIB.connect_material_property(node, '', prop)


def sample(material, texture, sampler, x=-600, y=0):
    node = expression(material, u.MaterialExpressionTextureSample, x, y)
    node.set_editor_property('texture', texture)
    node.set_editor_property('sampler_type', sampler)
    return node


u.EditorAssetLibrary.make_directory(DESTINATION)
textures = {}
for name, entry in METADATA['textures'].items():
    texture = import_one(SOURCE/'Textures'/(name+'.png'), name)
    assert isinstance(texture, u.Texture2D)
    is_normal = name == 'T_PerchNatural_Normal'
    is_color = name == 'T_PerchNatural_BaseColor'
    texture.set_editor_property('srgb', is_color)
    texture.set_editor_property('compression_settings',
        u.TextureCompressionSettings.TC_NORMALMAP if is_normal else
        u.TextureCompressionSettings.TC_DEFAULT if is_color else u.TextureCompressionSettings.TC_MASKS)
    if is_normal:
        # Preparation stores OpenGL +Y normals; Unreal expects DirectX -Y.
        texture.set_editor_property('flip_green_channel', True)
    assert u.EditorAssetLibrary.save_loaded_asset(texture)
    textures[name] = texture

materials = {}
for name in METADATA['materials'].values():
    material = u.load_asset(DESTINATION+'/'+name)
    if material:
        assert isinstance(material, u.Material), name
        LIB.delete_all_material_expressions(material)
    else:
        material = ASSETS.create_asset(name, DESTINATION, u.Material, u.MaterialFactoryNew())
    assert material
    material.set_editor_property('two_sided', True)
    is_skin = name == 'M_PerchNatural_Skin'
    is_outer_eye = name == 'M_PerchNatural_EyeOuter'
    material.set_editor_property('blend_mode', u.BlendMode.BLEND_TRANSLUCENT if is_outer_eye else
        u.BlendMode.BLEND_MASKED if is_skin else u.BlendMode.BLEND_OPAQUE)
    if is_outer_eye:
        color = expression(material, u.MaterialExpressionConstant3Vector, -200, 0)
        color.set_editor_property('constant', u.LinearColor(.94,.98,1,1))
        assert LIB.connect_material_property(color, '', u.MaterialProperty.MP_BASE_COLOR)
        constant(material, .12, u.MaterialProperty.MP_OPACITY)
    else:
        color = sample(material, textures['T_PerchNatural_BaseColor'], u.MaterialSamplerType.SAMPLERTYPE_COLOR)
        assert LIB.connect_material_property(color, 'RGB', u.MaterialProperty.MP_BASE_COLOR)
    constant(material, .38 if is_skin else .1, u.MaterialProperty.MP_ROUGHNESS, -200, 360)
    constant(material, .45, u.MaterialProperty.MP_SPECULAR, -200, 430)
    constant(material, 0, u.MaterialProperty.MP_METALLIC, -200, 500)
    if is_skin:
        material.set_editor_property('opacity_mask_clip_value', .35)
        opacity = sample(material, textures['T_PerchNatural_Opacity'], u.MaterialSamplerType.SAMPLERTYPE_MASKS, -600, 150)
        invert = expression(material, u.MaterialExpressionOneMinus, -350, 150)
        assert LIB.connect_material_expressions(opacity, 'R', invert, '')
        assert LIB.connect_material_property(invert, '', u.MaterialProperty.MP_OPACITY_MASK)
        normal = sample(material, textures['T_PerchNatural_Normal'], u.MaterialSamplerType.SAMPLERTYPE_NORMAL, -600, 300)
        assert LIB.connect_material_property(normal, 'RGB', u.MaterialProperty.MP_NORMAL)
    LIB.recompile_material(material)
    assert u.EditorAssetLibrary.save_loaded_asset(material)
    materials[name] = material

report = {'destination':DESTINATION, 'tail_offset_cm':METADATA['tail_offset_cm'], 'meshes':[]}
for entry in METADATA['meshes']:
    options = u.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = False
    options.mesh_type_to_import = u.FBXImportType.FBXIT_STATIC_MESH
    options.import_materials = False
    options.import_textures = False
    options.import_animations = False
    options.automated_import_should_detect_type = False
    static = options.static_mesh_import_data
    static.combine_meshes = True
    static.auto_generate_collision = False
    static.generate_lightmap_u_vs = False
    static.convert_scene = False
    static.convert_scene_unit = True
    static.force_front_x_axis = False
    static.transform_vertex_to_absolute = True
    static.import_uniform_scale = 1
    static.normal_import_method = u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
    mesh = import_one(SOURCE/(entry['name']+'.fbx'), entry['name'], options)
    assert isinstance(mesh, u.StaticMesh)
    assigned = []
    for index, slot in enumerate(mesh.static_materials):
        key = str(slot.material_slot_name)
        material_name = key if key in materials else METADATA['materials'].get(key)
        assert material_name in materials, f'Unknown material slot {key}'
        mesh.set_material(index, materials[material_name])
        assigned.append(material_name)
    # Axis/unit checks stop immediately if the importer silently changes conventions.
    box = mesh.get_bounding_box()
    expected = entry['local_bounds_cm']
    got_min = [box.min.x, box.min.y, box.min.z]
    got_max = [box.max.x, box.max.y, box.max.z]
    for axis in range(3):
        assert abs(got_min[axis]-expected['min'][axis]) < .15, (entry['name'], got_min, expected)
        assert abs(got_max[axis]-expected['max'][axis]) < .15, (entry['name'], got_max, expected)
    assert u.EditorAssetLibrary.save_loaded_asset(mesh)
    report['meshes'].append({'name':entry['name'],'bounds_min':got_min,'bounds_max':got_max,'materials':assigned})

(SOURCE/'unreal_import_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PERCH_IMPORT_COMPLETE', json.dumps(report))
