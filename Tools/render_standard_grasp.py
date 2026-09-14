import bpy
from pathlib import Path
from mathutils import Vector
root=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'MannyGraspReference.blend'))
s=bpy.context.scene;s.frame_set(1)
material=bpy.data.materials.new('GraspReviewClay');material.diffuse_color=(.35,.42,.48,1)
material.use_nodes=True
p=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.35,.42,.48,1);p.inputs['Roughness'].default_value=.65
for o in s.objects:
    if o.type=='MESH':
        o.data.materials.clear();o.data.materials.append(material)
        for poly in o.data.polygons:poly.material_index=0
s.render.engine='CYCLES';s.cycles.samples=12
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100
s.world.color=(.13,.13,.13)
for name,pos,power in [('Key',(-1,-2,3),220),('Fill',(1,0,2),100)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=2
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,-.4,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.objects.new('GraspCamera',bpy.data.cameras.new('GraspCamera'));s.collection.objects.link(camera);s.camera=camera
for name,pos,target in [('Side',(-1.1,-.45,1.7),(0,-.35,1.45)),('FirstPerson',(0,-.07,1.7),(0,-.65,1.35))]:
    camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=32
    s.render.filepath=str(root/('OfficialGrasp_'+name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'MannyGraspReview.blend'))
