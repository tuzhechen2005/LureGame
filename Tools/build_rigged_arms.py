"""Build an isolated, weighted arm rig from the retained CC0 human source."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

src = Path('D:/LureGame/ArtSource/HumanBase')
out = Path('D:/LureGame/ArtSource/RiggedArms')
out.mkdir(exist_ok=True)
vertices, uvs, faces, face_uvs = [], [], [], []
group = ''
for line in (src / 'base.obj').read_text(encoding='utf-8').splitlines():
    parts = line.split()
    if not parts:
        continue
    if parts[0] == 'v':
        x, y, z = map(float, parts[1:4])
        vertices.append(Vector((x, -z, y)) * .1)
    elif parts[0] == 'vt':
        uvs.append(tuple(map(float, parts[1:3])))
    elif parts[0] == 'g':
        group = parts[1]
    elif parts[0] == 'f' and group == 'body':
        faces.append([int(p.split('/')[0]) - 1 for p in parts[1:]])
        face_uvs.append([int(p.split('/')[1]) - 1 for p in parts[1:]])
rig_data = json.loads((src / 'default.mhskel').read_text(encoding='utf-8'))
weights = json.loads((src / 'default_weights.mhw').read_text(encoding='utf-8'))['weights']
def joint(key):
    ids = rig_data['joints'][key]
    return sum((vertices[i] for i in ids), Vector()) / len(ids)
arm_weight = [0.] * len(vertices)
for name, entries in weights.items():
    if name.startswith(('upperarm', 'lowerarm', 'wrist', 'metacarpal', 'finger')):
        for index, weight in entries:
            arm_weight[index] += weight
kept_faces = [i for i, f in enumerate(faces) if all(arm_weight[v] > .5 for v in f)]
ids = sorted({v for i in kept_faces for v in faces[i]})
mapping = {old: new for new, old in enumerate(ids)}
# This script runs in a separate background Blender process.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
data = bpy.data.armatures.new('FishingArmSkeleton')
rig = bpy.data.objects.new('FishingArmRig', data)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name, spec in rig_data['bones'].items():
    bone = data.edit_bones.new(name)
    bone.head, bone.tail = joint(spec['head']), joint(spec['tail'])
    if (bone.tail - bone.head).length < .0001:
        bone.tail.z += .001
for name, spec in rig_data['bones'].items():
    if spec['parent']:
        data.edit_bones[name].parent = data.edit_bones[spec['parent']]
bpy.ops.object.mode_set(mode='OBJECT')
mesh = bpy.data.meshes.new('WeightedArms')
mesh.from_pydata([vertices[i] for i in ids], [], [[mapping[v] for v in faces[i]] for i in kept_faces])
mesh.update()
arms = bpy.data.objects.new('SK_FishingArms', mesh)
bpy.context.collection.objects.link(arms)
layer = mesh.uv_layers.new(name='UVMap')
for polygon, original in zip(mesh.polygons, kept_faces):
    polygon.use_smooth = True
    for loop, uv in zip(polygon.loop_indices, face_uvs[original]):
        layer.data[loop].uv = uvs[uv]
totals = {i: 0. for i in ids}
for name, entries in weights.items():
    if name not in data.bones:
        continue
    for index, weight in entries:
        if index in mapping:
            totals[index] += weight
assert all(v > 0 for v in totals.values())
for name, entries in weights.items():
    if name not in data.bones:
        continue
    relevant = [(i, w) for i, w in entries if i in mapping]
    if not relevant:
        continue
    group = arms.vertex_groups.new(name=name)
    for index, weight in relevant:
        group.add([mapping[index]], weight / totals[index], 'REPLACE')
modifier = arms.modifiers.new('Weighted skeletal deformation', 'ARMATURE')
modifier.object = rig
arms.parent = rig
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
baseline = [v.co.copy() for v in arms.evaluated_get(deps).data.vertices]
bone = rig.pose.bones['lowerarm01.R']
bone.rotation_mode = 'XYZ'
bone.rotation_euler.x = .5
bpy.context.view_layer.update()
deformed = arms.evaluated_get(deps).data.vertices
movement = max((v.co - baseline[i]).length for i, v in enumerate(deformed))
assert movement > .005, 'Elbow must deform the weighted arm mesh'
bone.rotation_euler.x = 0
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
arms.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'FishingArmsRig.blend'))
bpy.ops.export_scene.fbx(filepath=str(out / 'SK_FishingArms.fbx'), use_selection=True,
    object_types={'MESH', 'ARMATURE'}, add_leaf_bones=False, bake_anim=False,
    axis_forward='-Y', axis_up='Z')
print('RIGGED_ARMS_PASS', 'vertices', len(ids), 'bones', len(data.bones), 'elbow_deformation_m', movement)
