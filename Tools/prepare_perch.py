"""Inspect and prepare holmen's CC0 Fish Perch. Run with Blender --disable-autoexec."""
import bpy
import json
import hashlib
import sys
import math
import bmesh
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1] / 'ArtSource' / 'ThirdParty' / 'Perch'

def bounds(obj):
    points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return {'min': [min(p[i] for p in points) for i in range(3)],
            'max': [max(p[i] for p in points) for i in range(3)]}

def inspect():
    data = {'blender': bpy.app.version_string, 'objects': [], 'images': [], 'materials': []}
    for obj in bpy.data.objects:
        row = {'name': obj.name, 'type': obj.type, 'bounds': bounds(obj),
               'matrix_world': [list(r) for r in obj.matrix_world],
               'hide_render': obj.hide_render, 'parent': obj.parent.name if obj.parent else None}
        if obj.type == 'MESH':
            row.update(vertices=len(obj.data.vertices), polygons=len(obj.data.polygons),
                       uv_layers=[u.name for u in obj.data.uv_layers],
                       materials=[m.name if m else None for m in obj.data.materials],
                       modifiers=[{'name':m.name,'type':m.type,'show_render':m.show_render} for m in obj.modifiers])
        if obj.type == 'ARMATURE':
            row['bones'] = [{'name':b.name, 'head':list(b.head_local), 'tail':list(b.tail_local)} for b in obj.data.bones]
        data['objects'].append(row)
    for im in bpy.data.images:
        data['images'].append({'name':im.name,'filepath':im.filepath,'size':list(im.size),
                               'packed':bool(im.packed_file),'source':im.source})
    for mat in bpy.data.materials:
        row = {'name':mat.name,'use_nodes':mat.use_nodes,'nodes':[],'links':[]}
        if mat.node_tree:
            for n in mat.node_tree.nodes:
                row['nodes'].append({'name':n.name,'type':n.type,'image': n.image.name if hasattr(n,'image') and n.image else None,
                    'inputs':{s.name:list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value for s in n.inputs if hasattr(s,'default_value')}})
            row['links']=[f'{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}' for l in mat.node_tree.links]
        data['materials'].append(row)
    (ROOT/'source_inspection.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print('PERCH_INSPECTION', len(data['objects']), 'objects;', len(data['images']), 'images; see source_inspection.json')

def prepare():
    bpy.context.scene.frame_set(1)
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    textures = {}
    texture_names = {'Fish diffuse.png':'T_PerchNatural_BaseColor',
                     'Fish normal.PNG':'T_PerchNatural_SourceBump',
                     'Fish alpha.PNG':'T_PerchNatural_Opacity',
                     'Fish trans.png':'T_PerchNatural_Translucency'}
    tex_dir = ROOT/'Textures'
    tex_dir.mkdir(exist_ok=True)
    for old, new in texture_names.items():
        im = bpy.data.images[old]
        assert im.packed_file and all(im.size), f'Missing packed image: {old}'
        file = tex_dir/(new+'.png')
        file.write_bytes(bytes(im.packed_file.data))
        textures[new] = {'filename':str(file), 'source':old, 'size':list(im.size),
                         'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    # The legacy "normal" image is connected to displacement, not a Normal Map node.
    # Keep the source untouched and derive a conservative tangent normal from its luminance.
    bump = bpy.data.images['Fish normal.PNG']
    width, height = bump.size
    pixels = np.empty(width*height*4,dtype=np.float32)
    bump.pixels.foreach_get(pixels)
    pixels = pixels.reshape(height,width,4)
    height_map = pixels[:,:,:3].mean(axis=2)
    dx = (np.roll(height_map,-1,axis=1)-np.roll(height_map,1,axis=1))*1.8
    dy = (np.roll(height_map,-1,axis=0)-np.roll(height_map,1,axis=0))*1.8
    normal = np.stack((-dx,-dy,np.ones_like(dx)),axis=2)
    normal /= np.maximum(np.linalg.norm(normal,axis=2,keepdims=True),1e-8)
    rgba = np.ones((height,width,4),dtype=np.float32)
    rgba[:,:,:3] = normal*.5+.5
    normal_im = bpy.data.images.new('T_PerchNatural_Normal',width,height,alpha=False)
    normal_im.colorspace_settings.name = 'Non-Color'
    normal_im.pixels.foreach_set(rgba.ravel())
    normal_im.filepath_raw = str(tex_dir/'T_PerchNatural_Normal.png')
    normal_im.file_format = 'PNG'
    normal_im.save()
    textures['T_PerchNatural_Normal']={'filename':normal_im.filepath_raw,'size':[width,height],
        'source':'Derived from legacy displacement luminance; OpenGL +Y tangent normal',
        'sha256':hashlib.sha256(Path(normal_im.filepath_raw).read_bytes()).hexdigest()}

    # Rebuild only a copy's renderer-specific materials. Original .blend and packed pixels remain intact.
    base = bpy.data.images['Fish diffuse.png']
    alpha = bpy.data.images['Fish alpha.PNG']
    alpha.colorspace_settings.name='Non-Color'
    materials = {}
    mapping={'Fishy  :)':'M_PerchNatural_Skin','Eye inner':'M_PerchNatural_EyeInner','Eye outer':'M_PerchNatural_EyeOuter'}
    for old,new in mapping.items():
        mat=bpy.data.materials.new(new);mat.use_nodes=True
        nodes=mat.node_tree.nodes;links=mat.node_tree.links
        nodes.clear()
        bs=nodes.new('ShaderNodeBsdfPrincipled')
        output=nodes.new('ShaderNodeOutputMaterial')
        links.new(bs.outputs['BSDF'],output.inputs['Surface'])
        bs.inputs['Roughness'].default_value=.38 if old=='Fishy  :)' else .1
        bs.inputs['IOR'].default_value=1.4
        bs.inputs['Coat Weight'].default_value=.22
        if old=='Eye outer':
            bs.inputs['Base Color'].default_value=(.94,.98,1,1)
            bs.inputs['Transmission Weight'].default_value=1
            bs.inputs['Alpha'].default_value=.12
            mat.surface_render_method='DITHERED'
        else:
            tex=nodes.new('ShaderNodeTexImage');tex.image=base
            links.new(tex.outputs['Color'],bs.inputs['Base Color'])
            if old=='Fishy  :)':
                opacity=nodes.new('ShaderNodeTexImage');opacity.image=alpha
                inverse=nodes.new('ShaderNodeMath');inverse.operation='SUBTRACT';inverse.inputs[0].default_value=1
                links.new(opacity.outputs['Color'],inverse.inputs[1]);links.new(inverse.outputs[0],bs.inputs['Alpha'])
                nor=nodes.new('ShaderNodeTexImage');nor.image=normal_im
                conv=nodes.new('ShaderNodeNormalMap');conv.inputs['Strength'].default_value=.65
                links.new(nor.outputs['Color'],conv.inputs['Color']);links.new(conv.outputs['Normal'],bs.inputs['Normal'])
                mat.surface_render_method='DITHERED'
        materials[old]=mat
    source_objects=[bpy.data.objects[n] for n in ['Fish','eye inner','Eye outer']]
    deps=bpy.context.evaluated_depsgraph_get()
    copies=[]
    for source in source_objects:
        evaluated=source.evaluated_get(deps)
        mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
        mesh.transform(evaluated.matrix_world)
        ob=bpy.data.objects.new('Prepared_'+source.name,mesh)
        bpy.context.collection.objects.link(ob)
        for i, mat in enumerate(mesh.materials):
            mesh.materials[i]=materials[mat.name]
        copies.append(ob)
    all_points=[v.co.copy() for ob in copies for v in ob.data.vertices]
    y_min=min(v.y for v in all_points);y_max=max(v.y for v in all_points)
    scale=40/(y_max-y_min)
    center_y=(y_min+y_max)*.5
    center_x=bpy.data.objects['Fish armature'].matrix_world.translation.x
    center_z=bpy.data.objects['Fish armature'].matrix_world.translation.z
    # Source nose is -Y, dorsal fin +Z. Rotate +90 degrees about Z: nose becomes +X.
    conversion=Matrix(((0,-scale,0,center_y*scale),(scale,0,0,-center_x*scale),
                       (0,0,scale,-center_z*scale),(0,0,0,1)))
    for ob in copies:
        ob.data.transform(conversion)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in copies:ob.select_set(True)
    bpy.context.view_layer.objects.active=copies[0]
    bpy.ops.object.join()
    body=copies[0];body.name='SM_PerchNaturalBody'
    complete_mesh=body.data.copy()
    tail=body.copy();tail.data=body.data.copy();tail.name='SM_PerchNaturalTail'
    bpy.context.collection.objects.link(tail)
    # The base of the source s6 bone is the caudal peduncle, before the caudal fin fan.
    tail_source=bpy.data.objects['Fish armature'].matrix_world @ bpy.data.objects['Fish armature'].data.bones['s6'].head_local
    tail_pivot=conversion @ tail_source
    plane=Vector((tail_pivot.x,0,0))
    for ob,keep_front in [(body,True),(tail,False)]:
        bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,
            plane_co=plane,plane_no=Vector((1,0,0)),clear_inner=keep_front,clear_outer=not keep_front)
        if not keep_front:
            for v in bm.verts:v.co-=tail_pivot
        bm.to_mesh(ob.data);bm.free();ob.data.update()
        for p in ob.data.polygons:p.use_smooth=True
        assert len(ob.data.vertices)>0 and len(ob.data.uv_layers)==2
    tail.location=tail_pivot
    for ob in list(bpy.data.objects):
        if ob not in [body,tail]:bpy.data.objects.remove(ob,do_unlink=True)
    for text_block in list(bpy.data.texts):bpy.data.texts.remove(text_block)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
    exports=[]
    for ob in [body,tail]:
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
        bpy.context.view_layer.objects.active=ob
        saved=ob.location.copy();ob.location=(0,0,0)
        filename=ROOT/(ob.name+'.fbx')
        bpy.ops.export_scene.fbx(filepath=str(filename),use_selection=True,object_types={'MESH'},
            apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',global_scale=1,
            axis_forward='Y',axis_up='Z',bake_space_transform=False,mesh_smooth_type='FACE',
            use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='STRIP',use_tspace=True)
        exports.append({'name':ob.name,'filename':str(filename),'local_bounds_cm':bounds(ob),
            'vertices':len(ob.data.vertices),'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons),
            'uv_layers':[u.name for u in ob.data.uv_layers],
            'material_slots':[m.name for m in ob.data.materials],
            'sha256':hashlib.sha256(filename.read_bytes()).hexdigest()})
        ob.location=saved
    # A single neutral side-view QA render; all source lights/cameras and embedded text are removed.
    scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.cycles.use_denoising=True
    scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'Perch_SidePreview.png')
    scene.world=bpy.data.worlds.new('Perch_Studio');scene.world.use_nodes=True
    background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    background.inputs[0].default_value=(.055,.065,.075,1)
    background.inputs[1].default_value=.4
    camera_data=bpy.data.cameras.new('Perch_QA');camera=bpy.data.objects.new('Perch_QA',camera_data)
    bpy.context.collection.objects.link(camera);camera.location=(0,-80,3)
    camera.rotation_euler=(Vector((0,0,2))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.type='ORTHO';camera_data.ortho_scale=49;camera_data.clip_end=500
    scene.camera=camera
    for name,loc,power,size in [('Key',(5,-24,30),12000,30),('Fill',(-12,-15,5),4000,25),('Rim',(-8,15,20),9000,20)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size
        ob=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(ob);ob.location=loc
        ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler()
    scene.view_settings.view_transform='AgX'
    metadata={'author':'holmen','asset':'Fish Perch','license':'CC0 1.0',
        'source_url':'https://blendswap.com/blend/8888',
        'archive_url':'https://raw.githubusercontent.com/frankiezafe/Fish-shader/6a1c64975cd266a00797199dd7aca9ec4af72348/addons/fish-shader/assets/67777_Fish_Perch.zip',
        'archive_sha256':hashlib.sha256((ROOT/'67777_Fish_Perch.zip').read_bytes()).hexdigest(),
        'processing':{'autoexec_disabled':True,'armature_pose':'REST','source_texts_executed':False,
            'nose_axis':'+X','dorsal_axis':'+Z','units':'centimeters','full_length_cm':40,
            'fbx_axis_forward':'Y','fbx_axis_up':'Z','ue_convert_scene':False,
            'opacity_formula':'1 - T_PerchNatural_Opacity.R (original mask is black on fish)',
            'tail_split':'caudal peduncle at source s6 bone head; UVs interpolated on seam',
            'source_to_prepared_matrix':[list(r) for r in conversion],
            'source_bump_channel_difference_max':float(np.abs(pixels[:,:,0]-pixels[:,:,1]).max()),
            'notes':'Static exports. All fins and both inner/outer eye meshes retained. Tail seam open and coincident at rest.'},
        'tail_offset_cm':list(tail_pivot),'materials':mapping,'textures':textures,'meshes':exports}
    (ROOT/'perch_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    (ROOT/'SOURCE.md').write_text('''# Fish Perch — holmen\n\nAuthor source: https://blendswap.com/blend/8888\nLicense: CC0 1.0 (public domain); original archive license is in BLENDSWAP_LICENSE.txt.\nPinned redistribution: https://github.com/frankiezafe/Fish-shader/blob/6a1c64975cd266a00797199dd7aca9ec4af72348/addons/fish-shader/assets/67777_Fish_Perch.zip\n\nThe original .blend is preserved. Prepared copies were opened with --disable-autoexec; no source scripts executed.\nThe original fish, inner eyes and outer eyes are preserved in the static exports; rig/lattice/mirror evaluation is baked in rest pose.\nFull fish length is 40 cm, mouth +X, dorsal fin +Z. See perch_metadata.json for tail pivot, bounds and slots.\nLegacy Cycles shaders were replaced with simplified PBR; source packed image pixels are retained.\nThe old image named normal was used as displacement in the original graph; an OpenGL normal is derived from its luminance.\nThe source rig is not exported; tail movement is a separate static mesh pivot.\n\nRun: D:/blender.exe --background --disable-autoexec "D:/LureGame/ArtSource/ThirdParty/Perch/Fish Perch.blend" --python D:/LureGame/Tools/prepare_perch.py -- prepare\nUnreal import script is Tools/import_perch.py; it is not run by this preparation task.\n''',encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Perch_Prepared.blend'))
    bpy.ops.render.render(write_still=True)
    print('PERCH_EXPORT_COMPLETE',json.dumps(metadata))

def verify():
    data=json.loads((ROOT/'perch_metadata.json').read_text(encoding='utf-8'))
    results=[]
    for expected in data['meshes']:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.system='METRIC'
        bpy.context.scene.unit_settings.scale_length=.01
        bpy.ops.import_scene.fbx(filepath=expected['filename'],use_anim=False)
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
        assert len(objects)==1
        ob=objects[0];actual=bounds(ob)
        for key in ['min','max']:
            assert max(abs(a-b) for a,b in zip(actual[key],expected['local_bounds_cm'][key]))<.001, actual
        assert len(ob.data.uv_layers)==2
        results.append({'name':expected['name'],'fbx_roundtrip_bounds_cm':actual,
                        'uv_layers':[l.name for l in ob.data.uv_layers]})
    (ROOT/'fbx_verification.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('PERCH_FBX_VERIFIED',json.dumps(results))

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if 'verify' in args:
    verify()
else:
    inspect()
    if 'prepare' in args:prepare()
