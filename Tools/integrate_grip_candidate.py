import bpy, bmesh
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath='D:/LureGame/ArtSource/Anatomical/GripCandidate/FishingHands.blend')
with bpy.data.libraries.load('D:/LureGame/ArtSource/Anatomical/FishingHandsWithSleeves.blend', link=False) as (src, dst):
    dst.objects = [name for name in src.objects if name.startswith('Sleeve')]
for sleeve in dst.objects:
    bpy.context.scene.collection.objects.link(sleeve)
for name, sign in [('SM_AnatomicalRight', 1), ('SM_AnatomicalLeft', -1)]:
    hand = bpy.data.objects[name]
    sleeve = next(o for o in dst.objects if sum(v.co.y for v in o.data.vertices) * sign > 0)
    # The source forearm ends in an open boundary. Close that cut with jacket
    # material so first-person camera angles cannot see inside the arm.
    hand.data.materials.append(sleeve.data.materials[0])
    cap_material = len(hand.data.materials) - 1
    bm = bmesh.new()
    bm.from_mesh(hand.data)
    boundary = [edge for edge in bm.edges if edge.is_boundary]
    assert boundary and all(vertex.co.x < -.30 for edge in boundary for vertex in edge.verts)
    result = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    for face in result['faces']:
        face.material_index = cap_material
        face.smooth = False
    assert not any(edge.is_boundary for edge in bm.edges)
    bm.to_mesh(hand.data)
    bm.free()
    offset = Vector((0, -.015 * sign, .035))
    for obj in [hand, sleeve]:
        for vertex in obj.data.vertices:
            vertex.co += offset
        obj.data.update()
    bpy.ops.object.select_all(action='DESELECT')
    hand.select_set(True)
    sleeve.select_set(True)
    bpy.context.view_layer.objects.active = hand
    bpy.ops.export_scene.fbx(filepath='D:/LureGame/ArtSource/Anatomical/' + name + '.fbx', use_selection=True, object_types={'MESH'}, axis_forward='Y', axis_up='Z', mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath='D:/LureGame/ArtSource/Anatomical/GripIntegrated.blend')
print('GRIP_CANDIDATE_INTEGRATED')
