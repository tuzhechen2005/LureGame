"""Author a rubber-mesh landing net in an isolated Blender background scene."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'ArtSource' / 'LandingNet'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, rgb, roughness, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return mat

rim = material('Net_Anodized', (.08, .10, .105), .26, .8)
rubber = material('Net_Rubber', (.027, .034, .032), .72)
grip = material('Net_Grip', (.12, .105, .075), .83)
orange = material('Net_Accent', (.52, .20, .04), .4)
parts = []

def cord(name, points, radius, mat, cyclic=False):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 1
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, v in zip(spline.points, points):
        p.co = (*v, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    curve.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)
    parts.append(obj)

def ellipse(z, shrink=1):
    return [(.38*shrink*math.cos(i*math.tau/96),
             .245*shrink*math.sin(i*math.tau/96), z) for i in range(96)]

cord('Continuous oval frame', ellipse(0), .008, rim, True)
cord('Protective lip', ellipse(.006), .0032, rubber, True)
# A regular 2cm rubber lattice cups down from the rim. Actual geometry makes
# the holes readable without alpha sorting and catches the fish physically.
for axis in (0, 1):
    width, height = (.38, .245) if axis == 0 else (.245, .38)
    for i in range(-int(width/.018), int(width/.018)+1):
        fixed = i*.018
        extent = height*math.sqrt(max(0, 1-(fixed/width)**2))
        points = []
        for j in range(49):
            sliding = -extent + 2*extent*j/48
            x, y = (fixed, sliding) if axis == 0 else (sliding, fixed)
            radial = (x/.38)**2 + (y/.245)**2
            z = -.16*min(1, max(0, (1-radial)*2.2))
            points.append((x, y, z))
        cord('Rubber basket grid', points, .0013, rubber)
cord('Net neck', [(0,.24,-.005),(-.02,.32,-.012),(-.055,.40,-.016)], .015, rim)
cord('Carbon handle', [(-.055,.38,-.016),(-.09,1.08,-.036)], .010, rim)
cord('Cork handle grip', [(-.079,.88,-.031),(-.09,1.09,-.036)], .018, grip)
cord('Handle collar', [(-.063,.53,-.020),(-.065,.56,-.021)], .014, orange)
for i in range(10):
    y = .89 + i*.019
    x = -.079-(y-.88)*.052
    cord('Grip grooves', [(x+.018*math.cos(a),y,-.032+.018*math.sin(a))
         for a in [j*math.tau/32 for j in range(32)]], .00065, rubber, True)
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
net = bpy.context.object
net.name = 'SM_LandingNet'
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
for poly in net.data.polygons:
    poly.use_smooth = True
bpy.ops.export_scene.fbx(filepath=str(OUT/'SM_LandingNet.fbx'), use_selection=True,
    object_types={'MESH'}, axis_forward='Y', axis_up='Z', mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'LandingNet.blend'))
print('LANDING_NET_EXPORTED', len(net.data.vertices), len(net.data.polygons))
