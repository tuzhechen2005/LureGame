"""Build a spinning-reel crank about local Y; rod direction is local X."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

out = Path('D:/LureGame/ArtSource/RiggedArms')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
materials = {}
for name, color, metal, rough in [('Metal', (.30,.34,.37), .85,.28),
                                 ('Rubber', (.025,.028,.03), 0,.72)]:
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    materials[name]=m

parts=[]
def bar(name,a,b,radius,material):
    a,b=Vector(a),Vector(b);direction=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,
        depth=direction.length,location=(a+b)/2)
    obj=bpy.context.object;obj.name=name
    obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(materials[material])
    for p in obj.data.polygons:p.use_smooth=True
    bevel=obj.modifiers.new('Machined edges','BEVEL');bevel.width=.0008;bevel.segments=3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    parts.append(obj)

bar('Spindle',(0,0,0),(0,.028,0),.006,'Metal')
bar('CrankLever',(0,.028,0),(.04485,.057,-.031),.004,'Metal')
bar('KnobAxle',(.04485,.057,-.031),(.04485,.083,-.031),.003,'Metal')
bar('RoundGrip',(.04485,.060,-.031),(.04485,.080,-.031),.009,'Rubber')
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join();obj=bpy.context.object;obj.name='SM_ReelCrank_Transverse'
bpy.context.scene.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ReelCrankTransverse.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'SM_ReelCrank_Transverse.fbx'),
    use_selection=True,object_types={'MESH'},axis_forward='Y',axis_up='Z')
print('TRANSVERSE_CRANK_EXPORTED')
